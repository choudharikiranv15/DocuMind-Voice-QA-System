"""
Database Migration Runner
Executes SQL migration files in order and tracks which have been run.
"""
import os
import re
from pathlib import Path
from typing import List, Tuple
from src.database import get_supabase_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MigrationRunner:
    """Handles database migrations"""

    def __init__(self):
        self.client = get_supabase_client()
        self.migrations_dir = Path(__file__).parent.parent / 'migrations'

    def _get_migration_files(self) -> List[Tuple[str, Path]]:
        """Get all migration files sorted by version"""
        migrations = []

        for file in self.migrations_dir.glob('*.sql'):
            # Extract version from filename (e.g., 001_create_users.sql -> 001)
            match = re.match(r'^(\d+)_.*\.sql$', file.name)
            if match:
                version = match.group(1)
                migrations.append((version, file))

        # Sort by version number
        migrations.sort(key=lambda x: int(x[0]))
        return migrations

    def _ensure_migrations_table(self):
        """Create the schema_migrations table if it doesn't exist"""
        try:
            # Try to query the table
            self.client.table('schema_migrations').select('version').limit(1).execute()
            logger.info("✓ Migrations table exists")
        except Exception:
            # Table doesn't exist, create it
            logger.info("Creating migrations tracking table...")
            migrations_table_sql = """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                version VARCHAR(255) UNIQUE NOT NULL,
                executed_at TIMESTAMP DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_migrations_version ON schema_migrations(version);
            """
            self._execute_sql(migrations_table_sql)
            logger.info("✓ Migrations table created")

    def _get_executed_migrations(self) -> set:
        """Get list of already executed migrations"""
        try:
            response = self.client.table('schema_migrations').select('version').execute()
            if response.data:
                return {row['version'] for row in response.data}
            return set()
        except Exception as e:
            logger.warning(f"Could not fetch executed migrations: {e}")
            return set()

    def _execute_sql(self, sql: str) -> bool:
        """Execute raw SQL using Supabase RPC"""
        try:
            # Use Supabase's SQL execution via RPC
            # Note: This requires a custom RPC function in Supabase
            # For direct SQL execution, we'll use the PostgREST API
            from supabase import Client
            import httpx

            # Get the database connection URL from environment
            db_url = os.getenv('SUPABASE_URL')
            db_key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')

            if not db_url or not db_key:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

            # Execute SQL using psycopg2 for direct database access
            import psycopg2
            db_connection_string = os.getenv('DATABASE_URL')

            if db_connection_string:
                conn = psycopg2.connect(db_connection_string)
                cur = conn.cursor()
                cur.execute(sql)
                conn.commit()
                cur.close()
                conn.close()
                return True
            else:
                logger.error("DATABASE_URL not set. Cannot execute SQL migrations.")
                logger.info("Please set DATABASE_URL in your .env file")
                logger.info("You can find it in Supabase Dashboard -> Settings -> Database -> Connection String")
                return False

        except Exception as e:
            logger.error(f"Error executing SQL: {e}")
            return False

    def _mark_migration_executed(self, version: str) -> bool:
        """Mark a migration as executed"""
        try:
            self.client.table('schema_migrations').insert({
                'version': version
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Error marking migration {version} as executed: {e}")
            return False

    def run_pending_migrations(self) -> Tuple[int, int]:
        """
        Run all pending migrations
        Returns: (executed_count, failed_count)
        """
        logger.info("=" * 60)
        logger.info("DATABASE MIGRATION RUNNER")
        logger.info("=" * 60)

        # Ensure migrations table exists
        self._ensure_migrations_table()

        # Get migration files
        migrations = self._get_migration_files()
        logger.info(f"\nFound {len(migrations)} migration files")

        # Get already executed migrations
        executed = self._get_executed_migrations()
        logger.info(f"Already executed: {len(executed)} migrations")

        # Filter pending migrations
        pending = [(v, p) for v, p in migrations if v not in executed]

        if not pending:
            logger.info("\n✓ No pending migrations. Database is up to date!")
            return 0, 0

        logger.info(f"\nPending migrations: {len(pending)}")
        logger.info("-" * 60)

        executed_count = 0
        failed_count = 0

        for version, path in pending:
            logger.info(f"\nExecuting migration {version}: {path.name}")

            try:
                # Read migration file
                with open(path, 'r', encoding='utf-8') as f:
                    sql = f.read()

                # Execute migration
                if self._execute_sql(sql):
                    # Mark as executed
                    if self._mark_migration_executed(version):
                        logger.info(f"✓ Migration {version} executed successfully")
                        executed_count += 1
                    else:
                        logger.error(f"✗ Migration {version} executed but failed to mark as complete")
                        failed_count += 1
                else:
                    logger.error(f"✗ Migration {version} failed to execute")
                    failed_count += 1

            except Exception as e:
                logger.error(f"✗ Migration {version} failed with error: {e}")
                failed_count += 1

        logger.info("\n" + "=" * 60)
        logger.info(f"MIGRATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✓ Executed: {executed_count}")
        logger.info(f"✗ Failed: {failed_count}")
        logger.info("=" * 60)

        return executed_count, failed_count

    def get_migration_status(self):
        """Get status of all migrations"""
        migrations = self._get_migration_files()
        executed = self._get_executed_migrations()

        status = []
        for version, path in migrations:
            status.append({
                'version': version,
                'name': path.name,
                'executed': version in executed
            })

        return status


def run_migrations():
    """Main function to run migrations"""
    runner = MigrationRunner()
    executed, failed = runner.run_pending_migrations()

    if failed > 0:
        logger.error(f"\n⚠️  {failed} migration(s) failed. Please check the errors above.")
        exit(1)
    else:
        logger.info("\n✅ All migrations completed successfully!")
        exit(0)


if __name__ == '__main__':
    run_migrations()
