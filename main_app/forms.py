from django import forms
from django.forms.widgets import DateInput, TextInput

from .models import *
from . import models


class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        # Here make some changes such as:
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


class CustomUserForm(FormSettings):
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')])
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    address = forms.CharField(widget=forms.Textarea)
    password = forms.CharField(widget=forms.PasswordInput)
    widget = {
        'password': forms.PasswordInput(),
    }
    profile_pic = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)

        if kwargs.get('instance'):
            instance = kwargs.get('instance').admin.__dict__
            self.fields['password'].required = False
            for field in CustomUserForm.Meta.fields:
                self.fields[field].initial = instance.get(field)
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"

    def clean_email(self, *args, **kwargs):
        formEmail = self.cleaned_data['email'].lower()
        if self.instance.pk is None:  # Insert
            if CustomUser.objects.filter(email=formEmail).exists():
                raise forms.ValidationError(
                    "The given email is already registered")
        else:  # Update
            dbEmail = self.Meta.model.objects.get(
                id=self.instance.pk).admin.email.lower()
            if dbEmail != formEmail:  # There has been changes
                if CustomUser.objects.filter(email=formEmail).exists():
                    raise forms.ValidationError("The given email is already registered")

        return formEmail

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'gender',  'password','profile_pic', 'address' ]


class StudentForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields + \
            ['course', 'session', 'branch']


class StudentAddForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentAddForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields + ['session', 'branch']


class AdminForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Admin
        fields = CustomUserForm.Meta.fields


class AuthorityForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(AuthorityForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Authority
        fields = CustomUserForm.Meta.fields


class StaffForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields + \
            ['course' ]


class CourseForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['name', 'course_code']
        model = Course


class BranchForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(BranchForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['name', 'department']
        model = Branch


class CourseNoteForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(CourseNoteForm, self).__init__(*args, **kwargs)

    class Meta:
        model = CourseNote
        fields = ['title', 'description', 'reference_url', 'attachment']


class RideSharePostForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(RideSharePostForm, self).__init__(*args, **kwargs)

    class Meta:
        model = RideSharePost
        fields = ['origin', 'destination', 'ride_time', 'seats_available', 'contact_info', 'notes']
        widgets = {
            'ride_time': DateInput(attrs={'type': 'datetime-local'}),
        }


class LostFoundPostForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LostFoundPostForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LostFoundPost
        fields = ['post_type', 'title', 'description', 'location', 'contact_info', 'image']


class DiscussionPostForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(DiscussionPostForm, self).__init__(*args, **kwargs)

    class Meta:
        model = DiscussionPost
        fields = ['title', 'body']


class DiscussionReplyForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(DiscussionReplyForm, self).__init__(*args, **kwargs)

    class Meta:
        model = DiscussionReply
        fields = ['body']


class SubjectForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Subject
        fields = ['name', 'staff', 'course']


class SessionForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(SessionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Session
        fields = '__all__'
        widgets = {
            'start_year': DateInput(attrs={'type': 'date'}),
            'end_year': DateInput(attrs={'type': 'date'}),
        }


class LeaveReportStaffForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStaff
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackStaffForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStaff
        fields = ['feedback']


class LeaveReportStudentForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStudent
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackStudentForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStudent
        fields = ['feedback']


class StudentEditForm(CustomUserForm):
    """Form for students to edit their own profile - excludes course, session, and branch"""
    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields 


class StaffEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields


class EditResultForm(FormSettings):
    session_list = Session.objects.all()
    session_year = forms.ModelChoiceField(
        label="Session Year", queryset=session_list, required=True)

    def __init__(self, *args, **kwargs):
        super(EditResultForm, self).__init__(*args, **kwargs)

    class Meta:
        model = StudentResult
        fields = ['session_year', 'course', 'student', 'test_1', 'test_2', 'test_3', 'mid_sem', 'exam']


class GrievanceForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(GrievanceForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Grievance
        fields = [
            'title',
            'category',
            'subcategory',
            'complaint_type',
            'level',
            'department',
            'description',
            'proof',
            'is_anonymous',
        ]


class GrievanceUpdateForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(GrievanceUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Grievance
        fields = ['status', 'resolution_notes']


class GrievanceAssignForm(FormSettings):
    assigned_to = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(user_type='4'),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(GrievanceAssignForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Grievance
        fields = ['status', 'resolution_notes', 'assigned_to', 'escalation_level']


class OpportunityForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(OpportunityForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Opportunity
        fields = [
            'title',
            'organization',
            'type',
            'domain',
            'stipend',
            'duration',
            'location',
            'deadline',
            'description',
            'is_active',
        ]
        widgets = {
            'deadline': DateInput(attrs={'type': 'date'}),
        }


class OpportunityApplicationForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(OpportunityApplicationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = OpportunityApplication
        fields = ['resume', 'cover_letter']


class OpportunityStatusForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(OpportunityStatusForm, self).__init__(*args, **kwargs)

    class Meta:
        model = OpportunityApplication
        fields = ['status']

#todos
# class TodoForm(forms.ModelForm):
#     class Meta:
#         model=Todo
#         fields=["title","is_finished"]

#issue book

class IssueBookForm(forms.Form):
    isbn2 = forms.ModelChoiceField(queryset=models.Book.objects.all(), empty_label="Book Name [ISBN]", to_field_name="isbn", label="Book (Name and ISBN)")
    name2 = forms.ModelChoiceField(queryset=models.Student.objects.all(), empty_label="Name ", to_field_name="", label="Student Details")
    
    isbn2.widget.attrs.update({'class': 'form-control'})
    name2.widget.attrs.update({'class':'form-control'})


class BulkStudentImportForm(forms.Form):
    """Form for bulk student import from Excel"""
    excel_file = forms.FileField(
        label='Upload Excel File',
        help_text='Expected columns: Email, First Name, Last Name, Gender (M/F), Course Code, Password',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls'
        })
    )
    
    def clean_excel_file(self):
        file = self.cleaned_data.get('excel_file')
        if file:
            if not file.name.endswith(('.xlsx', '.xls')):
                raise forms.ValidationError('Only Excel files (.xlsx, .xls) are allowed')
        return file


class CourseEnrollmentRequestForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(CourseEnrollmentRequestForm, self).__init__(*args, **kwargs)
        self.fields['message'].required = False
    
    class Meta:
        model = CourseEnrollmentRequest
        fields = ['course', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Why do you want to enroll in this course? (optional)'}),
        }


class CourseEnrollmentApprovalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CourseEnrollmentApprovalForm, self).__init__(*args, **kwargs)
        self.fields['faculty_remarks'].widget.attrs['class'] = 'form-control'
        self.fields['faculty_remarks'].widget.attrs['rows'] = 3
        self.fields['status'].widget.attrs['class'] = 'form-control'
    
    class Meta:
        model = CourseEnrollmentRequest
        fields = ['status', 'faculty_remarks']
        widgets = {
            'faculty_remarks': forms.Textarea(attrs={'placeholder': 'Add remarks (optional)'}),
        }


class CompanyInternshipForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(CompanyInternshipForm, self).__init__(*args, **kwargs)

    class Meta:
        model = CompanyInternship
        fields = [
            'company_name',
            'company_logo',
            'position',
            'description',
            'requirements',
            'location',
            'duration',
            'stipend',
            'application_deadline',
            'is_active',
        ]
        widgets = {
            'application_deadline': DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
        }


class InternshipApplicationForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(InternshipApplicationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = InternshipApplication
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Why are you interested in this internship?'}),
        }


class InternshipApplicationStatusForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(InternshipApplicationStatusForm, self).__init__(*args, **kwargs)

    class Meta:
        model = InternshipApplication
        fields = ['status', 'admin_remarks']
        widgets = {
            'admin_remarks': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add remarks (optional)'}),
        }
