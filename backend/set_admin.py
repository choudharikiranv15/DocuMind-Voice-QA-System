#!/usr/bin/env python3
"""
Set admin access for a user
Run this script to grant admin privileges to your account
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def set_admin_user(email: str):
    """Set a user as admin by email"""
    from src.database import Database

    try:
        db = Database()

        # Get user by email
        user = db.get_user_by_email(email)

        if not user:
            print(f"❌ User not found: {email}")
            print("\nAvailable users:")
            users = db.get_all_users(limit=10)
            for u in users:
                print(f"  - {u['email']} (ID: {u['id']}, Admin: {u.get('is_admin', False)})")
            return False

        # Check if already admin
        if user.get('is_admin'):
            print(f"✅ User {email} is already an admin")
            return True

        # Update user to admin
        success = db.update_user(user['id'], {
            'is_admin': True,
            'admin_notes': 'Admin access granted via set_admin.py script'
        })

        if success:
            print(f"✅ Successfully granted admin access to: {email}")
            print(f"\n⚠️  IMPORTANT: You must LOG OUT and LOG IN again to get a new JWT token with admin privileges!")
            return True
        else:
            print(f"❌ Failed to update user")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def list_admins():
    """List all admin users"""
    from src.database import Database

    try:
        db = Database()
        users = db.get_all_users(limit=1000)
        admins = [u for u in users if u.get('is_admin')]

        if not admins:
            print("No admin users found")
        else:
            print(f"Found {len(admins)} admin user(s):")
            for admin in admins:
                print(f"  - {admin['email']} (ID: {admin['id']})")
                if admin.get('admin_notes'):
                    print(f"    Notes: {admin['admin_notes']}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("="*70)
    print("DokGuru Voice - Admin User Setup")
    print("="*70)

    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python set_admin.py <email>          - Grant admin access to user")
        print("  python set_admin.py --list           - List current admin users")
        print("\nExample:")
        print("  python set_admin.py user@example.com")
        sys.exit(1)

    command = sys.argv[1]

    if command == "--list":
        list_admins()
    else:
        email = command
        set_admin_user(email)
