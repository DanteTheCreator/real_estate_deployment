"""
Migration script to update user roles from tenant/landlord to unified 'user' role
Run this after updating the schema to ensure existing users work with the new system
"""

from sqlalchemy.orm import Session
from database import SessionLocal, User

def migrate_user_roles():
    """Update all existing users to use the new unified role system"""
    db = SessionLocal()
    try:
        # Update all tenant and landlord users to 'user' role
        updated_count = db.query(User).filter(
            User.role.in_(["tenant", "landlord"])
        ).update(
            {"role": "user"}, 
            synchronize_session=False
        )
        
        db.commit()
        print(f"✅ Successfully updated {updated_count} users to unified 'user' role")
        
        # Verify the changes
        user_count = db.query(User).filter(User.role == "user").count()
        admin_count = db.query(User).filter(User.role == "admin").count()
        
        print(f"📊 Current user distribution:")
        print(f"   - Users: {user_count}")
        print(f"   - Admins: {admin_count}")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_user_roles()
