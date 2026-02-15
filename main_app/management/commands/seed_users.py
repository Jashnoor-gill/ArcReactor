from django.core.management.base import BaseCommand
from main_app.models import CustomUser


class Command(BaseCommand):
    help = "Create or reset default Admin/Authority/Faculty/Student users."

    def add_arguments(self, parser):
        parser.add_argument("--admin-email", default="adminx@aegis.local")
        parser.add_argument("--admin-password", default="xyz")
        parser.add_argument("--authority-email", default="authorityx@aegis.local")
        parser.add_argument("--authority-password", default="xyz")
        parser.add_argument("--faculty-email", default="facultyx@aegis.local")
        parser.add_argument("--faculty-password", default="xyz")
        parser.add_argument("--student-email", default="studentx@aegis.local")
        parser.add_argument("--student-password", default="xyz")
        parser.add_argument("--force", action="store_true", help="Force reset even if users exist")

    def _ensure_profile(self, user):
        if user.user_type == '1' and not hasattr(user, 'admin'):
            from main_app.models import Admin
            Admin.objects.create(admin=user)
        elif user.user_type == '4' and not hasattr(user, 'authority'):
            from main_app.models import Authority
            Authority.objects.create(admin=user)
        elif user.user_type == '2' and not hasattr(user, 'staff'):
            from main_app.models import Staff
            Staff.objects.create(admin=user)
        elif user.user_type == '3' and not hasattr(user, 'student'):
            from main_app.models import Student
            Student.objects.create(admin=user)

    def _create_or_update(self, user_type, email, password, first_name, last_name, force=False):
        user = CustomUser.objects.filter(user_type=user_type).first()
        if user and not force:
            self._ensure_profile(user)
            return user, False

        if not user:
            # Try matching by email if user_type not found
            user = CustomUser.objects.filter(email=email).first()

        if user:
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = True
            user.set_password(password)
            user.save()
            self._ensure_profile(user)
            return user, True

        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            user_type=str(user_type),
            gender="M",
            address="Auto-created account",
            profile_pic="defaults/profile.png",
            first_name=first_name,
            last_name=last_name,
        )
        self._ensure_profile(user)
        return user, True

    def handle(self, *args, **options):
        admin_email = options["admin_email"]
        admin_password = options["admin_password"]
        authority_email = options["authority_email"]
        authority_password = options["authority_password"]
        faculty_email = options["faculty_email"]
        faculty_password = options["faculty_password"]
        student_email = options["student_email"]
        student_password = options["student_password"]
        force = options["force"]

        accounts = [
            ("1", admin_email, admin_password, "Admin", "User"),
            ("4", authority_email, authority_password, "Authority", "User"),
            ("2", faculty_email, faculty_password, "Faculty", "User"),
            ("3", student_email, student_password, "Student", "User"),
        ]

        for user_type, email, password, first_name, last_name in accounts:
            user, updated = self._create_or_update(
                user_type, email, password, first_name, last_name, force=force
            )
            status = "updated" if updated else "skipped"
            self.stdout.write(f"{email}: {status} (type={user.user_type})")
