import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from rooms.models import Space, SpaceMember

def seed():
    print("Setting up Clean Workspace and Admin Account...")

    # 1. Primary Owner & Admin Account
    admin_email = 'charulatha@billiontags.co'
    primary_admin, created = User.objects.get_or_create(
        email=admin_email,
        defaults={
            'name': 'Charulatha',
            'role': 'Admin',
            'is_staff': True,
            'is_superuser': True,
            'status': 'offline',
        }
    )
    primary_admin.name = 'Charulatha'
    primary_admin.role = 'Admin'
    primary_admin.is_staff = True
    primary_admin.is_superuser = True
    primary_admin.set_password('Charun@123')
    primary_admin.save()
    print(f"[ADMIN READY] {primary_admin.email} (Role: Admin/Owner, Password: Charun@123)")

    # 2. Company Primary Virtual Office Space
    space_id = 'space-002115'
    space, _ = Space.objects.get_or_create(
        id=space_id,
        defaults={
            'name': 'Billiontags Virtual Office',
            'owner': primary_admin,
            'team_size': '50+',
            'style': 'minimal',
            'allow_link_join': True,
        }
    )
    space.owner = primary_admin
    space.name = 'Billiontags Virtual Office'
    space.save()

    SpaceMember.objects.get_or_create(
        space=space,
        user=primary_admin,
        defaults={'role': 'Owner', 'access': 'all_offices'}
    )
    print(f"[SPACE READY] {space.name} (ID: {space.id})")
    print("\nDatabase is clean! You can now add your company employees directly via Django Admin panel.")

if __name__ == '__main__':
    seed()
