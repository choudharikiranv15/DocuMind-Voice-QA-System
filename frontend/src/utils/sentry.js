import * as Sentry from "@sentry/react";

export const initSentry = () => {
  const dsn = import.meta.env.VITE_SENTRY_DSN;

  // Silently skip if not configured (expected in development)
  if (!dsn || dsn === 'your_sentry_dsn_here') {
    return false;
  }

  try {
    Sentry.init({
      dsn,
      environment: import.meta.env.MODE || 'development',
      integrations: [
        new Sentry.BrowserTracing(),
        new Sentry.Replay(),
      ],
      // Performance Monitoring
      tracesSampleRate: import.meta.env.MODE === 'production' ? 0.1 : 1.0,
      // Session Replay
      replaysSessionSampleRate: 0.1,
      replaysOnErrorSampleRate: 1.0,
      // Release tracking
      release: import.meta.env.VITE_APP_VERSION || 'dev',
    });

    if (import.meta.env.DEV) console.log('✅ Sentry initialized');
    return true;
  } catch (error) {
    // Error logged server-side only - silent failure for tracking service
    return false;
  }
};

export const setUser = (user) => {
  if (user) {
    Sentry.setUser({
      id: user.id,
      email: user.email,
    });
  } else {
    Sentry.setUser(null);
  }
};

export const captureException = (error, context = {}) => {
  Sentry.captureException(error, { extra: context });
};

export const captureMessage = (message, level = 'info') => {
  Sentry.captureMessage(message, level);
};
