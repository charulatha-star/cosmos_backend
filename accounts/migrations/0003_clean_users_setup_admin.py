from django.db import migrations
from django.contrib.auth.hashers import make_password

def clean_and_setup_admin(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    Space = apps.get_model('rooms', 'Space')
    SpaceMember = apps.get_model('rooms', 'SpaceMember')

    # Remove all mock users except charulatha@billiontags.co
    User.objects.exclude(email__iexact='charulatha@billiontags.co').delete()

    # Ensure charulatha@billiontags.co exists with superuser privileges
    admin_user = User.objects.filter(email__iexact='charulatha@billiontags.co').first()
    if not admin_user:
        admin_user = User.objects.create(
            email='charulatha@billiontags.co',
            name='Charulatha',
            password=make_password('Charun@123'),
            role='Admin',
            is_staff=True,
            is_superuser=True,
            is_active=True,
            status='offline',
        )
    else:
        admin_user.name = 'Charulatha'
        admin_user.password = make_password('Charun@123')
        admin_user.role = 'Admin'
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.save()

    # Ensure primary space exists
    space = Space.objects.filter(id='space-002115').first()
    if not space:
        space = Space.objects.create(
            id='space-002115',
            name='Billiontags Virtual Office',
            owner=admin_user,
            team_size='50+',
            style='minimal',
            allow_link_join=True,
        )
    else:
        space.owner = admin_user
        space.save()

    # Clean orphaned space memberships
    SpaceMember.objects.filter(user=None).delete()

    # Ensure admin has SpaceMember membership
    if not SpaceMember.objects.filter(space=space, user=admin_user).exists():
        SpaceMember.objects.create(
            space=space,
            user=admin_user,
            role='Owner',
            access='all_offices',
        )

def reverse_noop(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_role'),
        ('rooms', '0005_spacemember_allowed_rooms_guestroomaccessrequest'),
    ]

    operations = [
        migrations.RunPython(clean_and_setup_admin, reverse_noop),
    ]
