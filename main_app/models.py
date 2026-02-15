from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime,timedelta
from uuid import uuid4




class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(email, password, **extra_fields)


class Session(models.Model):
    start_year = models.DateField()
    end_year = models.DateField()

    def __str__(self):
        return "From " + str(self.start_year) + " to " + str(self.end_year)


class CustomUser(AbstractUser):
    USER_TYPE = ((1, "Authority"), (2, "Faculty"), (3, "Student"))
    GENDER = [("M", "Male"), ("F", "Female")]
    
    
    username = None  # Removed username, using email instead
    email = models.EmailField(unique=True)
    user_type = models.CharField(default=1, choices=USER_TYPE, max_length=1)
    gender = models.CharField(max_length=1, choices=GENDER)
    profile_pic = models.ImageField()
    address = models.TextField()
    fcm_token = models.TextField(default="")  # For firebase notifications
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return  self.first_name + " " + self.last_name


class Admin(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)



class Course(models.Model):
    name = models.CharField(max_length=120)
    course_code = models.CharField("Course Code", max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.course_code:
            return f"{self.name} ({self.course_code})"
        return self.name

class Book(models.Model):
    name = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.PositiveIntegerField()
    category = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name) + " ["+str(self.isbn)+']'


class Student(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=False)
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return self.admin.last_name + ", " + self.admin.first_name

class Library(models.Model):
    student = models.ForeignKey(Student,  on_delete=models.CASCADE, null=True, blank=False)
    book = models.ForeignKey(Book,  on_delete=models.CASCADE, null=True, blank=False)
    def __str__(self):
        return str(self.student)

def expiry():
    return datetime.today() + timedelta(days=14)
class IssuedBook(models.Model):
    student_id = models.CharField(max_length=100, blank=True) 
    isbn = models.CharField(max_length=13)
    issued_date = models.DateField(auto_now=True)
    expiry_date = models.DateField(default=expiry)



class Staff(models.Model):
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=False)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.admin.first_name + " " +  self.admin.last_name


class Subject(models.Model):
    name = models.CharField(max_length=120)
    staff = models.ForeignKey(Staff,on_delete=models.CASCADE,)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Attendance(models.Model):
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AttendanceReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StudentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    test_1 = models.FloatField(default=0)
    test_2 = models.FloatField(default=0)
    test_3 = models.FloatField(default=0)
    mid_sem = models.FloatField(default=0)
    exam = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Grievance(models.Model):
    STATUS_CHOICES = (
        ("submitted", "Submitted"),
        ("under_review", "Under Review"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
    )
    CATEGORY_CHOICES = (
        ("academics", "Academics"),
        ("infrastructure", "Infrastructure"),
        ("harassment", "Harassment"),
        ("finance", "Finance"),
        ("other", "Other"),
    )
    TYPE_CHOICES = (
        ("complaint", "Complaint"),
        ("query", "Query"),
        ("suggestion", "Suggestion"),
    )
    LEVEL_CHOICES = (
        ("department", "Department"),
        ("college", "College"),
        ("university", "University"),
    )

    def generate_tracking_code():
        return uuid4().hex[:12].upper()

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES)
    subcategory = models.CharField(max_length=120, blank=True)
    complaint_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="complaint")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="department")
    department = models.CharField(max_length=120, blank=True)
    proof = models.FileField(upload_to="grievances/proofs/", null=True, blank=True)
    is_anonymous = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="submitted")
    tracking_code = models.CharField(max_length=12, unique=True, default=generate_tracking_code)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="grievances")
    assigned_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_grievances",
    )
    escalation_level = models.PositiveSmallIntegerField(default=0)
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class GrievanceUpdate(models.Model):
    grievance = models.ForeignKey(Grievance, on_delete=models.CASCADE, related_name="updates")
    status = models.CharField(max_length=20, choices=Grievance.STATUS_CHOICES)
    note = models.TextField(blank=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.grievance_id} - {self.get_status_display()}"


class Opportunity(models.Model):
    TYPE_CHOICES = (
        ("internship", "Internship"),
        ("research", "Research"),
    )

    title = models.CharField(max_length=200)
    organization = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    domain = models.CharField(max_length=100)
    stipend = models.CharField(max_length=100, blank=True)
    duration = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    deadline = models.DateField(null=True, blank=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="opportunities")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.organization}"


class OpportunityApplication(models.Model):
    STATUS_CHOICES = (
        ("applied", "Applied"),
        ("shortlisted", "Shortlisted"),
        ("rejected", "Rejected"),
        ("accepted", "Accepted"),
    )

    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name="applications")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="applications")
    resume = models.FileField(upload_to="opportunities/resumes/", null=True, blank=True)
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="applied")
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.opportunity_id} - {self.student_id}"


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == '1':
            Admin.objects.create(admin=instance)
        if instance.user_type == '2':
            Staff.objects.create(admin=instance)
        if instance.user_type == '3':
            Student.objects.create(admin=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == '1' and hasattr(instance, 'admin'):
        instance.admin.save()
    if instance.user_type == '2' and hasattr(instance, 'staff'):
        instance.staff.save()
    if instance.user_type == '3' and hasattr(instance, 'student'):
        instance.student.save()


# ==================== ADMISSIONS & REGISTRATION MODULE ====================

class AdmissionSession(models.Model):
    """Academic year/session for admissions"""
    name = models.CharField(max_length=100)  # e.g., "2026-2027"
    start_date = models.DateField()
    end_date = models.DateField()
    application_start = models.DateField()
    application_end = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-start_date']


class AdmissionCourse(models.Model):
    """Courses available for admission"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    session = models.ForeignKey(AdmissionSession, on_delete=models.CASCADE)
    total_seats = models.PositiveIntegerField()
    seats_filled = models.PositiveIntegerField(default=0)
    eligibility_criteria = models.TextField()
    entrance_test_required = models.BooleanField(default=False)
    application_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.name} - {self.session.name}"

    @property
    def seats_available(self):
        return self.total_seats - self.seats_filled


class AdmissionApplication(models.Model):
    """Student admission applications"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('test_scheduled', 'Test Scheduled'),
        ('test_completed', 'Test Completed'),
        ('shortlisted', 'Shortlisted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('enrolled', 'Enrolled'),
    )

    application_number = models.CharField(max_length=20, unique=True, editable=False)
    admission_course = models.ForeignKey(AdmissionCourse, on_delete=models.CASCADE)
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=CustomUser.GENDER)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    nationality = models.CharField(max_length=100, default='Indian')
    
    # Guardian Information
    guardian_name = models.CharField(max_length=200)
    guardian_phone = models.CharField(max_length=15)
    guardian_email = models.EmailField(blank=True)
    guardian_relation = models.CharField(max_length=50)
    
    # Academic Information
    previous_school = models.CharField(max_length=200)
    previous_percentage = models.FloatField()
    previous_board = models.CharField(max_length=100)
    previous_year_of_passing = models.IntegerField()
    
    # Documents
    photo = models.ImageField(upload_to='admissions/photos/', null=True, blank=True)
    marksheet = models.FileField(upload_to='admissions/marksheets/', null=True, blank=True)
    id_proof = models.FileField(upload_to='admissions/id_proofs/', null=True, blank=True)
    
    # Application Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    remarks = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')
    
    # Entrance Test
    entrance_test_date = models.DateTimeField(null=True, blank=True)
    entrance_test_score = models.FloatField(null=True, blank=True)
    entrance_test_max_score = models.FloatField(null=True, blank=True)
    
    # Linked Student (after enrollment)
    student = models.OneToOneField(Student, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.application_number} - {self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.application_number:
            # Generate unique application number
            year = self.admission_course.session.start_date.year
            count = AdmissionApplication.objects.filter(
                admission_course__session=self.admission_course.session
            ).count() + 1
            self.application_number = f"ADM{year}{count:05d}"
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']


class EntranceTest(models.Model):
    """Entrance test scheduling"""
    name = models.CharField(max_length=200)
    admission_course = models.ForeignKey(AdmissionCourse, on_delete=models.CASCADE)
    test_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    venue = models.CharField(max_length=200)
    max_marks = models.FloatField()
    passing_marks = models.FloatField()
    instructions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.test_date.strftime('%Y-%m-%d')}"


# ==================== FEE & FINANCE MODULE ====================

class FeeStructure(models.Model):
    """Fee structure for courses"""
    FEE_TYPE_CHOICES = (
        ('tuition', 'Tuition Fee'),
        ('admission', 'Admission Fee'),
        ('exam', 'Examination Fee'),
        ('library', 'Library Fee'),
        ('sports', 'Sports Fee'),
        ('transport', 'Transport Fee'),
        ('hostel', 'Hostel Fee'),
        ('development', 'Development Fee'),
        ('misc', 'Miscellaneous Fee'),
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_mandatory = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.name} - {self.get_fee_type_display()} - ₹{self.amount}"

    class Meta:
        unique_together = ['course', 'session', 'fee_type']


class FeeInstallment(models.Model):
    """Fee installment schedule"""
    name = models.CharField(max_length=100)  # e.g., "First Installment"
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    due_date = models.DateField()
    percentage = models.FloatField(help_text="Percentage of total fee")
    late_fee_applicable = models.BooleanField(default=True)
    late_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.course.name} ({self.session})"

    class Meta:
        ordering = ['due_date']


class StudentFee(models.Model):
    """Fee assigned to individual students"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_reason = models.CharField(max_length=200, blank=True)
    is_waived = models.BooleanField(default=False)
    waiver_reason = models.TextField(blank=True)
    academic_year = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student} - {self.fee_structure.get_fee_type_display()}"

    @property
    def net_amount(self):
        """Amount after discount"""
        if self.is_waived:
            return 0
        return self.amount - self.discount

    @property
    def paid_amount(self):
        """Total amount paid"""
        return self.payments.filter(status='success').aggregate(
            total=models.Sum('amount')
        )['total'] or 0

    @property
    def balance(self):
        """Remaining balance"""
        return self.net_amount - self.paid_amount


class FeePayment(models.Model):
    """Fee payment transactions"""
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('dd', 'Demand Draft'),
        ('online', 'Online Transfer'),
        ('upi', 'UPI'),
        ('card', 'Card Payment'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    receipt_number = models.CharField(max_length=20, unique=True, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_payments')
    student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True)
    cheque_number = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='success')
    remarks = models.TextField(blank=True)
    collected_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='collected_payments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.receipt_number} - {self.student} - ₹{self.amount}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            # Generate unique receipt number
            year = datetime.now().year
            count = FeePayment.objects.filter(
                payment_date__year=year
            ).count() + 1
            self.receipt_number = f"RCP{year}{count:06d}"
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-payment_date']


class FeeInvoice(models.Model):
    """Fee invoices for students"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    )

    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='invoices')
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    installment = models.ForeignKey(FeeInstallment, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    generated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.invoice_number} - {self.student}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate unique invoice number
            year = datetime.now().year
            count = FeeInvoice.objects.filter(
                created_at__year=year
            ).count() + 1
            self.invoice_number = f"INV{year}{count:06d}"
        super().save(*args, **kwargs)

    @property
    def balance(self):
        """Remaining balance"""
        return self.net_amount - self.paid_amount

    class Meta:
        ordering = ['-created_at']


class FeeInvoiceItem(models.Model):
    """Individual items in fee invoice"""
    invoice = models.ForeignKey(FeeInvoice, on_delete=models.CASCADE, related_name='items')
    student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.student_fee.fee_structure.get_fee_type_display()}"


class FeeDiscount(models.Model):
    """Fee discounts/scholarships"""
    DISCOUNT_TYPE_CHOICES = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    applicable_courses = models.ManyToManyField(Course, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class FeeReminder(models.Model):
    """Fee payment reminders"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    invoice = models.ForeignKey(FeeInvoice, on_delete=models.CASCADE)
    reminder_date = models.DateTimeField()
    message = models.TextField()
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reminder for {self.student} - {self.invoice.invoice_number}"

    class Meta:
        ordering = ['reminder_date']


# ==================== ENHANCED EXAMINATION MANAGEMENT ====================

class ExamType(models.Model):
    """Types of exams (Midterm, Final, Quiz, etc.)"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class ExamSession(models.Model):
    """Exam session to group multiple exams"""
    STATE_CHOICES = (
        ('draft', 'Draft'),
        ('schedule', 'Scheduled'),
        ('held', 'Held'),
        ('cancel', 'Cancelled'),
        ('done', 'Done'),
    )

    EVALUATION_TYPE = (
        ('normal', 'Normal'),
        ('grade', 'Grade'),
    )

    name = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    exam_code = models.CharField(max_length=20, unique=True)
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    evaluation_type = models.CharField(max_length=20, choices=EVALUATION_TYPE, default='normal')
    venue = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='draft')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.course.name}"

    @property
    def exams_count(self):
        return self.exams.count()

    class Meta:
        ordering = ['-start_date']


class Exam(models.Model):
    """Individual exam details"""
    STATE_CHOICES = (
        ('draft', 'Draft'),
        ('schedule', 'Scheduled'),
        ('held', 'Held'),
        ('result_updated', 'Result Updated'),
        ('cancel', 'Cancelled'),
        ('done', 'Done'),
    )

    exam_session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='exams')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_marks = models.IntegerField()
    min_marks = models.IntegerField(help_text='Passing marks')
    exam_room = models.CharField(max_length=100, blank=True)
    responsible = models.ManyToManyField(Staff, related_name='responsible_exams', blank=True)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='draft')
    note = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.subject.name}"

    @property
    def course(self):
        return self.exam_session.course

    @property
    def session_obj(self):
        return self.exam_session.session

    @property
    def attendees_count(self):
        return self.attendees.count()

    @property
    def results_entered(self):
        """Check if any results have been entered"""
        return self.attendees.filter(marks__isnull=False).exists()

    class Meta:
        ordering = ['start_time']


class ExamAttendees(models.Model):
    """Students attending an exam"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='attendees')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    marks = models.FloatField(null=True, blank=True)
    is_present = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    result_status = models.CharField(max_length=20, blank=True)  # Pass/Fail/Absent
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student} - {self.exam.name}"

    @property
    def percentage(self):
        if self.marks is not None and self.exam.total_marks > 0:
            return (self.marks / self.exam.total_marks) * 100
        return 0

    @property
    def is_pass(self):
        return self.marks is not None and self.marks >= self.exam.min_marks

    def save(self, *args, **kwargs):
        # Auto-calculate result status
        if self.marks is not None:
            if self.is_present:
                self.result_status = 'Pass' if self.is_pass else 'Fail'
            else:
                self.result_status = 'Absent'
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ['exam', 'student']
        ordering = ['student']


class GradeConfiguration(models.Model):
    """Grade configuration for marking"""
    name = models.CharField(max_length=100)
    grade = models.CharField(max_length=5)
    min_percentage = models.FloatField()
    max_percentage = models.FloatField()
    grade_point = models.FloatField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.grade} ({self.min_percentage}% - {self.max_percentage}%)"

    class Meta:
        ordering = ['-min_percentage']


class ExamRoom(models.Model):
    """Exam rooms/halls"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    capacity = models.IntegerField()
    floor = models.CharField(max_length=50, blank=True)
    building = models.CharField(max_length=100, blank=True)
    facilities = models.TextField(blank=True, help_text='Available facilities in the room')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Capacity: {self.capacity})"

    class Meta:
        ordering = ['name']


# ==================== TRANSPORT MANAGEMENT ====================

class TransportRoute(models.Model):
    """Transport routes"""
    name = models.CharField(max_length=200)
    route_code = models.CharField(max_length=20, unique=True)
    start_location = models.CharField(max_length=200)
    end_location = models.CharField(max_length=200)
    distance_km = models.FloatField()
    estimated_duration = models.IntegerField(help_text='Duration in minutes')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.route_code})"

    class Meta:
        ordering = ['name']


class TransportStop(models.Model):
    """Stops along a route"""
    route = models.ForeignKey(TransportRoute, on_delete=models.CASCADE, related_name='stops')
    stop_name = models.CharField(max_length=200)
    stop_order = models.IntegerField()
    arrival_time = models.TimeField()
    departure_time = models.TimeField()
    address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.stop_name} - {self.route.name}"

    class Meta:
        ordering = ['route', 'stop_order']
        unique_together = ['route', 'stop_order']


class Vehicle(models.Model):
    """Transport vehicles"""
    VEHICLE_TYPE = (
        ('bus', 'Bus'),
        ('van', 'Van'),
        ('car', 'Car'),
    )

    vehicle_number = models.CharField(max_length=50, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    capacity = models.IntegerField()
    insurance_number = models.CharField(max_length=100, blank=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    fitness_certificate = models.CharField(max_length=100, blank=True)
    fitness_expiry = models.DateField(null=True, blank=True)
    route = models.ForeignKey(TransportRoute, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicles')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vehicle_number} ({self.vehicle_type})"

    class Meta:
        ordering = ['vehicle_number']


class Driver(models.Model):
    """Transport drivers"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry = models.DateField()
    license_type = models.CharField(max_length=50)
    emergency_contact = models.CharField(max_length=15)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='drivers')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.license_number}"

    class Meta:
        ordering = ['user__first_name']


class StudentTransport(models.Model):
    """Student transport allocation"""
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    route = models.ForeignKey(TransportRoute, on_delete=models.CASCADE)
    stop = models.ForeignKey(TransportStop, on_delete=models.CASCADE)
    transport_fee = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student} - {self.route.name}"

    class Meta:
        ordering = ['student']


# ==================== HOSTEL MANAGEMENT ====================

class Hostel(models.Model):
    """Hostel blocks"""
    HOSTEL_TYPE = (
        ('boys', 'Boys'),
        ('girls', 'Girls'),
        ('co-ed', 'Co-Ed'),
    )

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    hostel_type = models.CharField(max_length=20, choices=HOSTEL_TYPE)
    total_rooms = models.IntegerField()
    address = models.TextField()
    warden_name = models.CharField(max_length=200)
    warden_phone = models.CharField(max_length=15)
    facilities = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.hostel_type})"

    @property
    def occupied_rooms(self):
        return self.rooms.filter(is_occupied=True).count()

    @property
    def available_rooms(self):
        return self.total_rooms - self.occupied_rooms

    class Meta:
        ordering = ['name']


class HostelRoom(models.Model):
    """Hostel rooms"""
    ROOM_TYPE = (
        ('single', 'Single'),
        ('double', 'Double'),
        ('triple', 'Triple'),
        ('quad', 'Quad'),
    )

    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE)
    floor = models.IntegerField()
    capacity = models.IntegerField()
    rent_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    is_occupied = models.BooleanField(default=False)
    facilities = models.TextField(blank=True, help_text='AC, Attached Bathroom, etc.')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hostel.name} - Room {self.room_number}"

    @property
    def current_occupancy(self):
        return self.allocations.filter(is_active=True).count()

    @property
    def available_beds(self):
        return self.capacity - self.current_occupancy

    class Meta:
        unique_together = ['hostel', 'room_number']
        ordering = ['hostel', 'floor', 'room_number']


class HostelAllocation(models.Model):
    """Student hostel room allocation"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='hostel_allocations')
    room = models.ForeignKey(HostelRoom, on_delete=models.CASCADE, related_name='allocations')
    bed_number = models.CharField(max_length=10)
    allocation_date = models.DateField()
    vacation_date = models.DateField(null=True, blank=True)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    remarks = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student} - {self.room}"

    class Meta:
        ordering = ['-allocation_date']


class HostelFeePayment(models.Model):
    """Hostel fee payments"""
    allocation = models.ForeignKey(HostelAllocation, on_delete=models.CASCADE, related_name='payments')
    month = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=FeePayment.PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.allocation.student} - {self.month.strftime('%B %Y')}"

    class Meta:
        ordering = ['-month']


class MessMenu(models.Model):
    """Mess menu for hostels"""
    DAY_CHOICES = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    )

    MEAL_TYPE = (
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('snacks', 'Snacks'),
        ('dinner', 'Dinner'),
    )

    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='mess_menus')
    day_of_week = models.CharField(max_length=20, choices=DAY_CHOICES)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE)
    menu_items = models.TextField()
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hostel.name} - {self.day_of_week} - {self.meal_type}"

    class Meta:
        unique_together = ['hostel', 'day_of_week', 'meal_type', 'effective_from']
        ordering = ['day_of_week', 'meal_type']


# ==================== HR & PAYROLL ====================

class Department(models.Model):
    """Academic and administrative departments"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    head = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_department')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Designation(models.Model):
    """Staff designations"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    level = models.IntegerField(help_text='Hierarchy level')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['level', 'name']


class StaffDetails(models.Model):
    """Extended staff details for HR"""
    EMPLOYMENT_TYPE = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
    )

    staff = models.OneToOneField(Staff, on_delete=models.CASCADE, related_name='hr_details')
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, blank=True)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE)
    joining_date = models.DateField()
    qualification = models.CharField(max_length=200)
    experience_years = models.IntegerField(default=0)
    bank_account = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    ifsc_code = models.CharField(max_length=20, blank=True)
    pan_number = models.CharField(max_length=20, blank=True)
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.staff.admin.get_full_name()} - {self.employee_id}"

    class Meta:
        verbose_name = 'Staff Details'
        verbose_name_plural = 'Staff Details'


class SalaryStructure(models.Model):
    """Salary structure templates"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10, decimal_places=2, help_text='House Rent Allowance')
    da = models.DecimalField(max_digits=10, decimal_places=2, help_text='Dearness Allowance')
    transport_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    special_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    provident_fund = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    professional_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    income_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - ₹{self.gross_salary}"

    @property
    def gross_salary(self):
        return (self.basic_salary + self.hra + self.da + 
                self.transport_allowance + self.medical_allowance + 
                self.special_allowance)

    @property
    def total_deductions(self):
        return self.provident_fund + self.professional_tax + self.income_tax

    @property
    def net_salary(self):
        return self.gross_salary - self.total_deductions

    class Meta:
        ordering = ['name']


class StaffSalary(models.Model):
    """Individual staff salary assignment"""
    staff_details = models.OneToOneField(StaffDetails, on_delete=models.CASCADE, related_name='salary')
    salary_structure = models.ForeignKey(SalaryStructure, on_delete=models.CASCADE)
    custom_basic = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    custom_hra = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    custom_da = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    effective_from = models.DateField()
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.staff_details.staff.admin.get_full_name()} Salary"

    @property
    def basic_salary(self):
        return self.custom_basic or self.salary_structure.basic_salary

    @property
    def gross_salary(self):
        return (self.basic_salary + 
                (self.custom_hra or self.salary_structure.hra) +
                (self.custom_da or self.salary_structure.da) +
                self.salary_structure.transport_allowance +
                self.salary_structure.medical_allowance +
                self.salary_structure.special_allowance)

    class Meta:
        verbose_name = 'Staff Salary'
        verbose_name_plural = 'Staff Salaries'


class Payroll(models.Model):
    """Monthly payroll records"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('processed', 'Processed'),
        ('paid', 'Paid'),
    )

    staff_salary = models.ForeignKey(StaffSalary, on_delete=models.CASCADE, related_name='payrolls')
    month = models.DateField()
    working_days = models.IntegerField()
    present_days = models.IntegerField()
    leaves_taken = models.IntegerField(default=0)
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    remarks = models.TextField(blank=True)
    generated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.staff_salary.staff_details.staff.admin.get_full_name()} - {self.month.strftime('%B %Y')}"

    class Meta:
        unique_together = ['staff_salary', 'month']
        ordering = ['-month']


class PayrollSlip(models.Model):
    """Payslip generation"""
    payroll = models.OneToOneField(Payroll, on_delete=models.CASCADE, related_name='slip')
    slip_number = models.CharField(max_length=50, unique=True)
    generated_date = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='payslips/', null=True, blank=True)

    def __str__(self):
        return f"Payslip {self.slip_number}"

    class Meta:
        ordering = ['-generated_date']

