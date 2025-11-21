"""
Lazy loading system for heavy dependencies
This allows Flask app to start immediately and load ML models on-demand
"""
import logging
import threading
from typing import Optional, Callable, Any

logger = logging.getLogger(__name__)


class LazyLoader:
    """Lazy loader for heavy dependencies"""

    def __init__(self, name: str, init_func: Callable, *args, **kwargs):
        """
        Initialize lazy loader

        Args:
            name: Name of the component (for logging)
            init_func: Function to call to initialize the component
            *args, **kwargs: Arguments to pass to init_func
        """
        self.name = name
        self.init_func = init_func
        self.args = args
        self.kwargs = kwargs
        self._instance: Optional[Any] = None
        self._lock = threading.Lock()
        self._initialized = False
        self._error: Optional[Exception] = None

    def get(self) -> Optional[Any]:
        """
        Get the instance, initializing if necessary
        Thread-safe lazy initialization
        """
        if self._initialized:
            return self._instance

        with self._lock:
            # Double-check locking pattern
            if self._initialized:
                return self._instance

            try:
                logger.info(f"🔄 Lazy loading {self.name}...")
                self._instance = self.init_func(*self.args, **self.kwargs)
                self._initialized = True
                logger.info(f"✓ {self.name} initialized successfully")
                return self._instance
            except Exception as e:
                self._error = e
                self._initialized = True  # Mark as initialized to avoid retrying
                logger.error(f"❌ {self.name} initialization failed: {e}")
                return None

    @property
    def is_initialized(self) -> bool:
        """Check if component has been initialized (successfully or not)"""
        return self._initialized

    @property
    def has_error(self) -> bool:
        """Check if initialization failed"""
        return self._error is not None

    @property
    def error(self) -> Optional[Exception]:
        """Get initialization error if any"""
        return self._error

    def warmup(self) -> None:
        """Warmup the component in background (non-blocking)"""
        def _warmup():
            try:
                self.get()
            except Exception as e:
                logger.error(f"Warmup failed for {self.name}: {e}")

        thread = threading.Thread(target=_warmup, daemon=True)
        thread.start()


class SystemComponents:
    """Container for all system components with lazy loading"""

    def __init__(self):
        self._components = {}

    def register(self, name: str, loader: LazyLoader):
        """Register a lazy-loaded component"""
        self._components[name] = loader

    def get(self, name: str) -> Optional[Any]:
        """Get a component by name"""
        loader = self._components.get(name)
        if loader:
            return loader.get()
        return None

    def warmup_all(self):
        """Start warming up all components in background"""
        logger.info("🔥 Starting background warmup of heavy components...")
        for name, loader in self._components.items():
            loader.warmup()

    def get_status(self) -> dict:
        """Get initialization status of all components"""
        status = {}
        for name, loader in self._components.items():
            status[name] = {
                "initialized": loader.is_initialized,
                "has_error": loader.has_error,
                "error": str(loader.error) if loader.error else None
            }
        return status
