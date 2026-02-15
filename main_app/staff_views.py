import json

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .models import *
from . import forms, models
from datetime import date

def staff_home(request):
    staff, _ = Staff.objects.get_or_create(admin=request.user)
    if not staff.course:
        messages.warning(request, "Your profile is not fully assigned yet. Please contact the admin to add your course.")
    total_students = Student.objects.filter(course=staff.course).count()
    total_leave = LeaveReportStaff.objects.filter(staff=staff).count()
    
    attendance_list = Attendance.objects.filter(course=staff.course)
    total_attendance = attendance_list.count()
    attendance_per_date = []
    date_list = []
    for attendance in attendance_list:
        if attendance.date not in date_list:
            attendance_count = Attendance.objects.filter(course=staff.course, date=attendance.date).count()
            date_list.append(attendance.date)
            attendance_per_date.append(attendance_count)
    
    last_initial = staff.admin.last_name[:1] if staff.admin.last_name else ""
    context = {
        'page_title': 'Faculty Panel - ' + str(staff.admin.first_name) + ' ' + last_initial + '' + ' (' + str(staff.course) + ')',
        'total_students': total_students,
        'total_attendance': total_attendance,
        'total_leave': total_leave,
        'attendance_per_date': attendance_per_date,
        'date_list': date_list
    }
    return render(request, "staff_template/erpnext_staff_home.html", context)


def staff_take_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    course = staff.course
    sessions = Session.objects.all()
    context = {
        'course': course,
        'sessions': sessions,
        'page_title': 'Take Attendance'
    }

    return render(request, 'staff_template/staff_take_attendance.html', context)


@csrf_exempt
def get_students(request):
    course_id = request.POST.get('course')
    session_id = request.POST.get('session')
    try:
        course = get_object_or_404(Course, id=course_id)
        session = get_object_or_404(Session, id=session_id)
        students = Student.objects.filter(course_id=course.id, session=session)
        student_data = []
        for student in students:
            data = {
                    "id": student.id,
                    "name": student.admin.last_name + " " + student.admin.first_name
                    }
            student_data.append(data)
        return JsonResponse(json.dumps(student_data), content_type='application/json', safe=False)
    except Exception as e:
        return e


@csrf_exempt
def save_attendance(request):
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    course_id = request.POST.get('course')
    session_id = request.POST.get('session')
    students = json.loads(student_data)
    try:
        session = get_object_or_404(Session, id=session_id)
        course = get_object_or_404(Course, id=course_id)
        attendance = Attendance(session=session, course=course, date=date)
        attendance.save()

        for student_dict in students:
            student = get_object_or_404(Student, id=student_dict.get('id'))
            attendance_report = AttendanceReport(student=student, attendance=attendance, status=student_dict.get('status'))
            attendance_report.save()
    except Exception as e:
        return None

    return HttpResponse("OK")


def staff_update_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    course = staff.course
    sessions = Session.objects.all()
    context = {
        'course': course,
        'sessions': sessions,
        'page_title': 'Update Attendance'
    }

    return render(request, 'staff_template/staff_update_attendance.html', context)


@csrf_exempt
def get_student_attendance(request):
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        date = get_object_or_404(Attendance, id=attendance_date_id)
        attendance_data = AttendanceReport.objects.filter(attendance=date)
        student_data = []
        for attendance in attendance_data:
            data = {"id": attendance.student.admin.id,
                    "name": attendance.student.admin.last_name + " " + attendance.student.admin.first_name,
                    "status": attendance.status}
            student_data.append(data)
        return JsonResponse(json.dumps(student_data), content_type='application/json', safe=False)
    except Exception as e:
        return e


@csrf_exempt
def update_attendance(request):
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    students = json.loads(student_data)
    try:
        attendance = get_object_or_404(Attendance, id=date)

        for student_dict in students:
            student = get_object_or_404(
                Student, admin_id=student_dict.get('id'))
            attendance_report = get_object_or_404(AttendanceReport, student=student, attendance=attendance)
            attendance_report.status = student_dict.get('status')
            attendance_report.save()
    except Exception as e:
        return None

    return HttpResponse("OK")


def staff_apply_leave(request):
    form = LeaveReportStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStaff.objects.filter(staff=staff),
        'page_title': 'Apply for Leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('staff_apply_leave'))
            except Exception:
                messages.error(request, "Could not apply!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "staff_template/staff_apply_leave.html", context)


def staff_feedback(request):
    form = FeedbackStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStaff.objects.filter(staff=staff),
        'page_title': 'Add Feedback'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(request, "Feedback submitted for review")
                return redirect(reverse('staff_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "staff_template/staff_feedback.html", context)


def staff_view_profile(request):
    staff = get_object_or_404(Staff, admin=request.user)
    form = StaffEditForm(request.POST or None, request.FILES or None,instance=staff)
    context = {'form': form, 'page_title': 'View/Update Profile'}
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = staff.admin
                if password != None:
                    admin.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    admin.profile_pic = passport_url
                admin.first_name = first_name
                admin.last_name = last_name
                admin.address = address
                admin.gender = gender
                admin.save()
                staff.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('staff_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
                return render(request, "staff_template/staff_view_profile.html", context)
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
            return render(request, "staff_template/staff_view_profile.html", context)

    return render(request, "staff_template/staff_view_profile.html", context)


@csrf_exempt
def staff_fcmtoken(request):
    token = request.POST.get('token')
    try:
        staff_user = get_object_or_404(CustomUser, id=request.user.id)
        staff_user.fcm_token = token
        staff_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def staff_view_notification(request):
    staff = get_object_or_404(Staff, admin=request.user)
    notifications = NotificationStaff.objects.filter(staff=staff)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "staff_template/staff_view_notification.html", context)


def staff_add_result(request):
    staff = get_object_or_404(Staff, admin=request.user)
    course = staff.course
    sessions = Session.objects.all()
    context = {
        'page_title': 'Result Upload',
        'course': course,
        'sessions': sessions
    }
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student_list')
            course_id = request.POST.get('course')
            test_1 = request.POST.get('test_1')
            test_2 = request.POST.get('test_2')
            test_3 = request.POST.get('test_3')
            mid_sem = request.POST.get('mid_sem')
            exam = request.POST.get('exam')
            student = get_object_or_404(Student, id=student_id)
            course = get_object_or_404(Course, id=course_id)
            try:
                data = StudentResult.objects.get(
                    student=student, course=course)
                data.test_1 = test_1 or 0
                data.test_2 = test_2 or 0
                data.test_3 = test_3 or 0
                data.mid_sem = mid_sem or 0
                data.exam = exam
                data.save()
                messages.success(request, "Scores Updated")
            except:
                result = StudentResult(student=student, course=course, test_1=test_1 or 0, test_2=test_2 or 0, test_3=test_3 or 0, mid_sem=mid_sem or 0, exam=exam)
                result.save()
                messages.success(request, "Scores Saved")
        except Exception as e:
            messages.warning(request, "Error Occured While Processing Form")
    return render(request, "staff_template/staff_add_result.html", context)


@csrf_exempt
def fetch_student_result(request):
    try:
        course_id = request.POST.get('course')
        student_id = request.POST.get('student')
        student = get_object_or_404(Student, id=student_id)
        course = get_object_or_404(Course, id=course_id)
        result = StudentResult.objects.get(student=student, course=course)
        result_data = {
            'exam': result.exam,
            'test_1': result.test_1,
            'test_2': result.test_2,
            'test_3': result.test_3,
            'mid_sem': result.mid_sem
        }
        return HttpResponse(json.dumps(result_data))
    except Exception as e:
        return HttpResponse('False')

#library
def add_book(request):
    if request.method == "POST":
        name = request.POST['name']
        author = request.POST['author']
        isbn = request.POST['isbn']
        category = request.POST['category']


        books = Book.objects.create(name=name, author=author, isbn=isbn, category=category )
        books.save()
        alert = True
        return render(request, "staff_template/add_book.html", {'alert':alert})
    context = {
        'page_title': "Add Book"
    }
    return render(request, "staff_template/add_book.html",context)

#issue book


def issue_book(request):
    form = forms.IssueBookForm()
    if request.method == "POST":
        form = forms.IssueBookForm(request.POST)
        if form.is_valid():
            obj = models.IssuedBook()
            obj.student_id = request.POST['name2']
            obj.isbn = request.POST['isbn2']
            obj.save()
            alert = True
            return render(request, "staff_template/issue_book.html", {'obj':obj, 'alert':alert})
    return render(request, "staff_template/issue_book.html", {'form':form})

def view_issued_book(request):
    issuedBooks = IssuedBook.objects.all()
    details = []
    for i in issuedBooks:
        days = (date.today()-i.issued_date)
        d=days.days
        fine=0
        if d>14:
            day=d-14
            fine=day*5
        books = list(models.Book.objects.filter(isbn=i.isbn))
        # students = list(models.Student.objects.filter(admin=i.admin))
        i=0
        for l in books:
            t=(books[i].name,books[i].isbn,issuedBooks[0].issued_date,issuedBooks[0].expiry_date,fine)
            i=i+1
            details.append(t)
    return render(request, "staff_template/view_issued_book.html", {'issuedBooks':issuedBooks, 'details':details})


def staff_grievance_list(request):
    status_filter = request.GET.get('status')
    grievances = Grievance.objects.all().order_by('-created_at')
    if status_filter:
        grievances = grievances.filter(status=status_filter)
    context = {
        'grievances': grievances,
        'page_title': 'Grievance Review'
    }
    return render(request, "staff_template/grievance_list.html", context)


def staff_grievance_update(request, grievance_id):
    grievance = get_object_or_404(Grievance, id=grievance_id)
    form = GrievanceUpdateForm(request.POST or None, instance=grievance)
    context = {
        'form': form,
        'grievance': grievance,
        'page_title': 'Update Grievance'
    }
    if request.method == 'POST':
        if form.is_valid():
            updated = form.save()
            GrievanceUpdate.objects.create(
                grievance=updated,
                status=updated.status,
                note=updated.resolution_notes,
                updated_by=request.user
            )
            messages.success(request, "Grievance updated")
            return redirect(reverse('staff_grievance_list'))
        messages.error(request, "Please correct the errors in the form")
    return render(request, "staff_template/grievance_update.html", context)


def staff_opportunity_list(request):
    opportunities = Opportunity.objects.all().order_by('-created_at')
    context = {
        'opportunities': opportunities,
        'page_title': 'Manage Opportunities'
    }
    return render(request, "staff_template/opportunity_list.html", context)


def staff_opportunity_create(request):
    form = OpportunityForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Post Opportunity'
    }
    if request.method == 'POST':
        if form.is_valid():
            opportunity = form.save(commit=False)
            opportunity.created_by = request.user
            opportunity.save()
            messages.success(request, "Opportunity posted")
            return redirect(reverse('staff_opportunity_list'))
        messages.error(request, "Please correct the errors in the form")
    return render(request, "staff_template/opportunity_create.html", context)


def staff_opportunity_applications(request, opportunity_id):
    opportunity = get_object_or_404(Opportunity, id=opportunity_id)
    applications = OpportunityApplication.objects.filter(opportunity=opportunity).order_by('-applied_at')
    context = {
        'opportunity': opportunity,
        'applications': applications,
        'page_title': 'Opportunity Applications'
    }
    return render(request, "staff_template/opportunity_applications.html", context)


def staff_application_update(request, application_id):
    application = get_object_or_404(OpportunityApplication, id=application_id)
    form = OpportunityStatusForm(request.POST or None, instance=application)
    context = {
        'form': form,
        'application': application,
        'page_title': 'Update Application Status'
    }
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Application status updated")
            return redirect(reverse('staff_opportunity_applications', args=[application.opportunity.id]))
        messages.error(request, "Please correct the errors in the form")
    return render(request, "staff_template/opportunity_application_update.html", context)


def staff_course_requests(request):
    """View all course enrollment requests for faculty's course"""
    staff = get_object_or_404(Staff, admin=request.user)
    
    if not staff.course:
        messages.warning(request, "Your course is not assigned yet. Please contact the admin.")
        return redirect(reverse('staff_home'))
    
    # Get all pending and approved/rejected requests for faculty's course
    requests = CourseEnrollmentRequest.objects.filter(
        course=staff.course
    ).select_related('student__admin', 'course').order_by('status', '-created_at')
    
    pending_count = requests.filter(status='pending').count()
    
    context = {
        'requests': requests,
        'pending_count': pending_count,
        'page_title': f'Course Enrollment Requests - {staff.course.name}'
    }
    return render(request, 'staff_template/staff_course_requests.html', context)


def staff_approve_course_request(request, request_id):
    """Approve or reject a course enrollment request"""
    staff = get_object_or_404(Staff, admin=request.user)
    enrollment_request = get_object_or_404(CourseEnrollmentRequest, id=request_id)
    
    # Verify this request is for faculty's course
    if enrollment_request.course != staff.course:
        messages.error(request, "You can only manage requests for your course")
        return redirect(reverse('staff_course_requests'))
    
    form = CourseEnrollmentApprovalForm(request.POST or None, instance=enrollment_request)
    
    if request.method == 'POST':
        if form.is_valid():
            enrollment_request = form.save()
            
            # If approved, assign the course to student
            if enrollment_request.status == 'approved':
                student = enrollment_request.student
                student.course = enrollment_request.course
                student.save()
                messages.success(
                    request, 
                    f"Request approved. {student.admin.get_full_name()} has been enrolled in {enrollment_request.course.name}"
                )
                
                # Send notification to student
                NotificationStudent.objects.create(
                    student=student,
                    message=f"Your course enrollment request for {enrollment_request.course.name} has been approved!"
                )
            else:
                messages.success(request, "Request has been updated")
                
                # Send notification if rejected
                if enrollment_request.status == 'rejected':
                    NotificationStudent.objects.create(
                        student=enrollment_request.student,
                        message=f"Your course enrollment request for {enrollment_request.course.name} has been rejected."
                    )
            
            return redirect(reverse('staff_course_requests'))
        else:
            messages.error(request, "Please correct the errors")
    
    context = {
        'form': form,
        'enrollment_request': enrollment_request,
        'page_title': 'Review Course Request'
    }
    return render(request, 'staff_template/staff_approve_course_request.html', context)
