import os
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from rooms.models import Space, SpaceMember

def seed():
    print("Seeding Company Workspace and 50+ Employees into Cosmos Database...")

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
    print(f"[ADMIN CREATED/UPDATED] {primary_admin.email} (Role: Admin/Owner, Password: Charun@123)")

    # Also support alternate .com domain if needed
    alt_admin, _ = User.objects.get_or_create(
        email='charulatha@billiontags.com',
        defaults={
            'name': 'Charulatha',
            'role': 'Admin',
            'is_staff': True,
            'is_superuser': True,
            'status': 'offline',
        }
    )
    alt_admin.set_password('Charun@123')
    alt_admin.save()

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
    print(f"[SPACE READY] {space.name} (ID: {space.id})")

    # Add primary owner as SpaceMember
    SpaceMember.objects.get_or_create(
        space=space,
        user=primary_admin,
        defaults={'role': 'Owner', 'access': 'all_offices'}
    )

    # 3. 50 Company Employees across Departments
    default_emp_password = 'Billiontags@2026'

    employees_data = [
        # Leadership & Admins
        ('ramkarthi@billiontags.com', 'Ramkarthi', 'Admin', 'Chief Technology Officer'),
        ('sarah.admin@billiontags.com', 'Sarah Connor', 'Admin', 'Operations Director'),
        
        # Team Leaders
        ('swathishri@billiontags.com', 'Swathishri', 'Team Leader', 'Frontend Lead'),
        ('arun.lead@billiontags.com', 'Arun Kumar', 'Team Leader', 'Backend Lead'),
        ('priya.lead@billiontags.com', 'Priya Sharma', 'Team Leader', 'UI/UX Design Lead'),
        ('david.lead@billiontags.com', 'David Miller', 'Team Leader', 'DevOps & Cloud Lead'),
        ('ananya.lead@billiontags.com', 'Ananya Patel', 'Team Leader', 'QA & Automation Lead'),
        ('karthik.lead@billiontags.com', 'Karthik Raja', 'Team Leader', 'Product Manager'),

        # Engineering Team
        ('alex.rivera@billiontags.com', 'Alex Rivera', 'Employee', 'Senior Fullstack Engineer'),
        ('kavitha.m@billiontags.com', 'Kavitha Murugan', 'Employee', 'Frontend Engineer'),
        ('vignesh.s@billiontags.com', 'Vignesh Sundaram', 'Employee', 'Frontend Engineer'),
        ('deepak.k@billiontags.com', 'Deepak Krishnan', 'Employee', 'React Specialist'),
        ('suresh.b@billiontags.com', 'Suresh Babu', 'Employee', 'Backend Python Engineer'),
        ('manoj.r@billiontags.com', 'Manoj Rajan', 'Employee', 'Django / API Developer'),
        ('siddharth.v@billiontags.com', 'Siddharth Verma', 'Employee', 'Microservices Engineer'),
        ('divya.n@billiontags.com', 'Divya Narayanan', 'Employee', 'WebRTC & LiveKit Engineer'),
        ('rahul.t@billiontags.com', 'Rahul Tripathi', 'Employee', 'WebSockets / Realtime Dev'),
        ('aakash.g@billiontags.com', 'Aakash Gupta', 'Employee', 'Cloud Infrastructure Engineer'),
        ('sneha.r@billiontags.com', 'Sneha Roy', 'Employee', 'Database Administrator'),
        ('mohammed.f@billiontags.com', 'Mohammed Fazil', 'Employee', 'Security Engineer'),
        ('harish.p@billiontags.com', 'Harish Prasad', 'Employee', 'Site Reliability Engineer'),

        # UI/UX & Creative Design Team
        ('meera.k@billiontags.com', 'Meera Kapoor', 'Employee', 'Lead Product Designer'),
        ('rohit.j@billiontags.com', 'Rohit Joshi', 'Employee', '3D Avatar & Graphic Artist'),
        ('tanvi.s@billiontags.com', 'Tanvi Shah', 'Employee', 'UI Designer'),
        ('nathan.d@billiontags.com', 'Nathan Drake', 'Employee', 'Motion & Visual Designer'),
        ('pooja.b@billiontags.com', 'Pooja Bhatt', 'Employee', 'User Researcher'),

        # QA & Automation Team
        ('dinesh.k@billiontags.com', 'Dinesh Kumar', 'Employee', 'Senior QA Automation Engineer'),
        ('shweta.p@billiontags.com', 'Shweta Pandey', 'Employee', 'Test Lead'),
        ('gautam.m@billiontags.com', 'Gautam Menon', 'Employee', 'Performance Testing Engineer'),
        ('lavanya.r@billiontags.com', 'Lavanya Ramesh', 'Employee', 'QA Analyst'),
        ('vijay.s@billiontags.com', 'Vijay Subramanian', 'Employee', 'Mobile & Web QA'),

        # Product, Data & Analytics
        ('neha.c@billiontags.com', 'Neha Choudhury', 'Employee', 'Associate Product Manager'),
        ('ashwin.n@billiontags.com', 'Ashwin Nair', 'Employee', 'Data Analyst'),
        ('rithika.d@billiontags.com', 'Rithika Das', 'Employee', 'Business Intelligence Analyst'),
        ('aditya.k@billiontags.com', 'Aditya Kulkarni', 'Employee', 'Scrum Master'),

        # People & Human Resources
        ('kavya.hr@billiontags.com', 'Kavya Reddy', 'Employee', 'HR Operations Manager'),
        ('shalini.m@billiontags.com', 'Shalini Mathur', 'Employee', 'Talent Acquisition Specialist'),
        ('arvind.hr@billiontags.com', 'Arvind Swamy', 'Employee', 'People Partner'),

        # Sales, Marketing & Customer Success
        ('rajesh.v@billiontags.com', 'Rajesh Varma', 'Employee', 'Enterprise Account Executive'),
        ('simran.k@billiontags.com', 'Simran Kaur', 'Employee', 'Growth Marketing Specialist'),
        ('prateek.s@billiontags.com', 'Prateek Singhania', 'Employee', 'Content & Brand Strategist'),
        ('amrita.j@billiontags.com', 'Amrita Joseph', 'Employee', 'Customer Success Manager'),
        ('bharath.c@billiontags.com', 'Bharath Chandran', 'Employee', 'Customer Support Specialist'),
        ('farhan.a@billiontags.com', 'Farhan Ali', 'Employee', 'Client Solutions Architect'),
        ('nisha.g@billiontags.com', 'Nisha Gowda', 'Employee', 'Operations Coordinator'),
        ('varun.m@billiontags.com', 'Varun Mohan', 'Employee', 'Technical Support Engineer'),
        ('ishaan.b@billiontags.com', 'Ishaan Banerjee', 'Employee', 'Implementation Consultant'),
        ('sandhya.t@billiontags.com', 'Sandhya Tiwari', 'Employee', 'Account Manager'),
        ('yash.p@billiontags.com', 'Yash Pathak', 'Employee', 'Community Manager'),
        ('tarun.k@billiontags.com', 'Tarun Khanna', 'Employee', 'Office Manager'),
    ]

    total_created = 0
    for email_addr, name, role, title in employees_data:
        emp, created = User.objects.get_or_create(
            email=email_addr,
            defaults={
                'name': name,
                'role': role,
                'status': 'offline',
                'is_staff': (role == 'Admin'),
            }
        )
        emp.name = name
        emp.role = role
        emp.is_staff = (role == 'Admin')
        emp.set_password(default_emp_password)
        emp.save()

        # Add to SpaceMember
        member_role = 'Admin' if role == 'Admin' else 'Member'
        SpaceMember.objects.get_or_create(
            space=space,
            user=emp,
            defaults={'role': member_role, 'access': 'all_offices'}
        )
        total_created += 1

    print(f"\n[SUCCESS] Seeded {total_created} employees in Billiontags Virtual Office space!")
    print(f"Primary Admin: charulatha@billiontags.co / Charun@123")
    print(f"Employee default password: {default_emp_password}")

if __name__ == '__main__':
    seed()

