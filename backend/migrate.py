#!/usr/bin/env python
"""
Database Migration CLI
Run this script to execute pending database migrations.

Usage:
    python migrate.py              # Run pending migrations
    python migrate.py --status     # Show migration status
"""
import sys
from src.migrator import MigrationRunner
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def show_status():
    """Show migration status"""
    runner = MigrationRunner()
    status = runner.get_migration_status()

    logger.info("\n" + "=" * 70)
    logger.info("MIGRATION STATUS")
    logger.info("=" * 70)
    logger.info(f"{'Version':<10} {'Status':<15} {'Name'}")
    logger.info("-" * 70)

    for migration in status:
        version = migration['version']
        name = migration['name']
        executed = '✓ Executed' if migration['executed'] else '⏳ Pending'
        logger.info(f"{version:<10} {executed:<15} {name}")

    logger.info("=" * 70)

    pending_count = sum(1 for m in status if not m['executed'])
    logger.info(f"\nTotal: {len(status)} migrations")
    logger.info(f"Pending: {pending_count} migrations")
    logger.info("")


def main():
    """Main CLI function"""
    if '--status' in sys.argv or '-s' in sys.argv:
        show_status()
    else:
        runner = MigrationRunner()
        executed, failed = runner.run_pending_migrations()

        if failed > 0:
            sys.exit(1)
        sys.exit(0)


if __name__ == '__main__':
    main()
