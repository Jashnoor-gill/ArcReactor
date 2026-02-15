import json
import requests
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView

from .forms import *
from .models import *
from .import_utils import import_students_from_excel


def admin_home(request):
    total_staff = Staff.objects.all().count()
    total_students = Student.objects.all().count()
    subjects = Subject.objects.all()
    total_subject = subjects.count()
    total_course = Course.objects.all().count()
    courses_for_attendance = Course.objects.all()
    attendance_list = Attendance.objects.filter(course__in=courses_for_attendance)
    total_attendance = attendance_list.count()
    attendance_list = []
    subject_list = []
    for course in courses_for_attendance:
        attendance_count = Attendance.objects.filter(course=course).count()
        subject_list.append(course.name[:7])
        attendance_list.append(attendance_count)

    # Total Subjects and students in Each Course
    course_all = Course.objects.all()
    course_name_list = []
    subject_count_list = []
    student_count_list_in_course = []

    for course in course_all:
        subjects = Subject.objects.filter(course_id=course.id).count()
        students = Student.objects.filter(course_id=course.id).count()
        course_name_list.append(course.name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)
    
    subject_all = Subject.objects.all()
    subject_list = []
    student_count_list_in_subject = []
    for subject in subject_all:
        course = Course.objects.get(id=subject.course.id)
        student_count = Student.objects.filter(course_id=course.id).count()
        subject_list.append(subject.name)
        student_count_list_in_subject.append(student_count)


    # For Students
    student_attendance_present_list=[]
    student_attendance_leave_list=[]
    student_name_list=[]

    students = Student.objects.all()
    for student in students:
        
        attendance = AttendanceReport.objects.filter(student_id=student.id, status="present").count()
        absent = AttendanceReport.objects.filter(student_id=student.id, status="absent").count()
        medical = AttendanceReport.objects.filter(student_id=student.id, status="medical").count()
        leave = LeaveReportStudent.objects.filter(student_id=student.id, status=1).count()
        student_attendance_present_list.append(attendance)
        student_attendance_leave_list.append(leave + absent + medical)
        student_name_list.append(student.admin.first_name)

    context = {
        'page_title': "Administrative Dashboard",
        'total_students': total_students,
        'total_staff': total_staff,
        'total_course': total_course,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': attendance_list,
        'student_attendance_present_list': student_attendance_present_list,
        'student_attendance_leave_list': student_attendance_leave_list,
        "student_name_list": student_name_list,
        "student_count_list_in_subject": student_count_list_in_subject,
        "student_count_list_in_course": student_count_list_in_course,
        "course_name_list": course_name_list,

    }
    return render(request, 'hod_template/home_content.html', context)


def authority_home(request):
    if request.user.user_type != '4':
        return redirect(reverse('admin_home'))

    total_grievances = Grievance.objects.count()
    submitted_count = Grievance.objects.filter(status='submitted').count()
    under_review_count = Grievance.objects.filter(status='under_review').count()
    in_progress_count = Grievance.objects.filter(status='in_progress').count()
    resolved_count = Grievance.objects.filter(status='resolved').count()

    context = {
        'page_title': 'Authority Dashboard',
        'total_grievances': total_grievances,
        'submitted_count': submitted_count,
        'under_review_count': under_review_count,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count,
    }
    return render(request, 'hod_template/authority_home.html', context)

def add_staff(request):
    form = StaffForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Add Faculty'}
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password')
            course = form.cleaned_data.get('course')
            passport = request.FILES.get('profile_pic')
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=2, first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.staff.course = course
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_staff'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Please fulfil all requirements")

    return render(request, 'hod_template/add_staff_template.html', context)


def add_student(request):
    student_form = StudentAddForm(request.POST or None, request.FILES or None)
    context = {'form': student_form, 'page_title': 'Add Student'}
    if request.method == 'POST':
        if student_form.is_valid():
            first_name = student_form.cleaned_data.get('first_name')
            last_name = student_form.cleaned_data.get('last_name')
            address = student_form.cleaned_data.get('address')
            email = student_form.cleaned_data.get('email')
            gender = student_form.cleaned_data.get('gender')
            password = student_form.cleaned_data.get('password')
            session = student_form.cleaned_data.get('session')
            branch = student_form.cleaned_data.get('branch')
            passport = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=3, first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.student.session = session
                user.student.branch = branch
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_student'))
            except Exception as e:
                messages.error(request, "Could Not Add: " + str(e))
        else:
            messages.error(request, "Could Not Add: ")
    return render(request, 'hod_template/add_student_template.html', context)


def bulk_import_students(request):
    """Import students from Excel file"""
    form = BulkStudentImportForm(request.POST or None, request.FILES or None)
    context = {
        'form': form,
        'page_title': 'Bulk Import Students'
    }
    
    if request.method == 'POST':
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            # Save file temporarily
            fs = FileSystemStorage()
            filename = fs.save(excel_file.name, excel_file)
            file_path = fs.path(filename)
            
            try:
                # Import students
                results = import_students_from_excel(file_path)
                
                if results['errors']:
                    for error in results['errors']:
                        messages.warning(request, error)
                
                messages.success(
                    request, 
                    f"Import completed: {results['success']} successful, {results['failed']} failed"
                )
                return redirect(reverse('manage_student'))
            except Exception as e:
                messages.error(request, f"Import failed: {str(e)}")
            finally:
                # Delete temp file
                import os
                if os.path.exists(file_path):
                    os.remove(file_path)
        else:
            messages.error(request, "Invalid form data")
    
    return render(request, 'hod_template/bulk_import_students.html', context)


def add_course(request):
    form = CourseForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Course'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            course_code = form.cleaned_data.get('course_code')
            try:
                course = Course()
                course.name = name
                course.course_code = course_code
                course.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_course'))
            except:
                messages.error(request, "Could Not Add")
        else:
            messages.error(request, "Could Not Add")
    return render(request, 'hod_template/add_course_template.html', context)


def add_branch(request):
    form = BranchForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Branch'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_branch'))
            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Could Not Add")
    return render(request, 'hod_template/add_branch_template.html', context)


def add_subject(request):
    form = SubjectForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Subject'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            course = form.cleaned_data.get('course')
            staff = form.cleaned_data.get('staff')
            try:
                subject = Subject()
                subject.name = name
                subject.staff = staff
                subject.course = course
                subject.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_subject'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")

    return render(request, 'hod_template/add_subject_template.html', context)


def manage_staff(request):
    allStaff = CustomUser.objects.filter(user_type=2).select_related('staff').filter(staff__isnull=False)
    search_query = request.GET.get('search', '')
    course_filter = request.GET.get('course', '')
    
    if search_query:
        allStaff = allStaff.filter(
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query) |
            models.Q(email__icontains=search_query)
        )
    
    if course_filter:
        allStaff = allStaff.filter(staff__course__id=course_filter)
    
    courses = Course.objects.all()
    context = {
        'allStaff': allStaff,
        'courses': courses,
        'search_query': search_query,
        'selected_course': course_filter,
        'page_title': 'Manage Faculty',
        'staff_count': allStaff.count()
    }
    return render(request, "hod_template/manage_staff.html", context)


def manage_student(request):
    students = CustomUser.objects.filter(user_type=3).select_related('student').filter(student__isnull=False)
    search_query = request.GET.get('search', '')
    branch_filter = request.GET.get('branch', '')
    
    if search_query:
        students = students.filter(
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query) |
            models.Q(email__icontains=search_query)
        )
    
    if branch_filter:
        students = students.filter(student__branch__id=branch_filter)
    
    branches = Branch.objects.all()
    context = {
        'students': students,
        'branches': branches,
        'search_query': search_query,
        'selected_branch': branch_filter,
        'page_title': 'Manage Students',
        'student_count': students.count()
    }
    return render(request, "hod_template/manage_student.html", context)


def manage_course(request):
    courses = Course.objects.all()
    context = {
        'courses': courses,
        'page_title': 'Manage Courses'
    }
    return render(request, "hod_template/manage_course.html", context)


def manage_branch(request):
    branches = Branch.objects.all().order_by('name')
    context = {
        'branches': branches,
        'page_title': 'Manage Branches'
    }
    return render(request, "hod_template/manage_branch.html", context)


def manage_subject(request):
    subjects = Subject.objects.all()
    context = {
        'subjects': subjects,
        'page_title': 'Manage Subjects'
    }
    return render(request, "hod_template/manage_subject.html", context)


def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    form = StaffForm(request.POST or None, instance=staff)
    context = {
        'form': form,
        'staff_id': staff_id,
        'page_title': 'Edit Faculty'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=staff.admin.id)
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.first_name = first_name
                user.last_name = last_name
                user.gender = gender
                user.address = address
                staff.course = course
                user.save()
                staff.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_staff', args=[staff_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please fil form properly")
    else:
        user = CustomUser.objects.get(id=staff_id)
        staff = Staff.objects.get(id=user.id)
        return render(request, "hod_template/edit_staff_template.html", context)


def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    form = StudentForm(request.POST or None, instance=student)
    context = {
        'form': form,
        'student_id': student_id,
        'page_title': 'Edit Student'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            session = form.cleaned_data.get('session')
            branch = form.cleaned_data.get('branch')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=student.admin.id)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                student.session = session
                user.gender = gender
                user.address = address
                student.course = course
                student.branch = branch
                user.save()
                student.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_student', args=[student_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please Fill Form Properly!")
    else:
        return render(request, "hod_template/edit_student_template.html", context)


def edit_course(request, course_id):
    instance = get_object_or_404(Course, id=course_id)
    form = CourseForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'course_id': course_id,
        'page_title': 'Edit Course'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            course_code = form.cleaned_data.get('course_code')
            try:
                course = Course.objects.get(id=course_id)
                course.name = name
                course.course_code = course_code
                course.save()
                messages.success(request, "Successfully Updated")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_course_template.html', context)


def edit_subject(request, subject_id):
    instance = get_object_or_404(Subject, id=subject_id)
    form = SubjectForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'subject_id': subject_id,
        'page_title': 'Edit Subject'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            course = form.cleaned_data.get('course')
            staff = form.cleaned_data.get('staff')
            try:
                subject = Subject.objects.get(id=subject_id)
                subject.name = name
                subject.staff = staff
                subject.course = course
                subject.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_subject', args=[subject_id]))
            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")
    return render(request, 'hod_template/edit_subject_template.html', context)


def add_session(request):
    form = SessionForm(request.POST or None)
    context = {'form': form, 'page_title': 'Add Session'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Session Created")
                return redirect(reverse('add_session'))
            except Exception as e:
                messages.error(request, 'Could Not Add ' + str(e))
        else:
            messages.error(request, 'Fill Form Properly ')
    return render(request, "hod_template/add_session_template.html", context)


def manage_session(request):
    sessions = Session.objects.all()
    context = {'sessions': sessions, 'page_title': 'Manage Sessions'}
    return render(request, "hod_template/manage_session.html", context)


def edit_session(request, session_id):
    instance = get_object_or_404(Session, id=session_id)
    form = SessionForm(request.POST or None, instance=instance)
    context = {'form': form, 'session_id': session_id,
               'page_title': 'Edit Session'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Session Updated")
                return redirect(reverse('edit_session', args=[session_id]))
            except Exception as e:
                messages.error(
                    request, "Session Could Not Be Updated " + str(e))
                return render(request, "hod_template/edit_session_template.html", context)
        else:
            messages.error(request, "Invalid Form Submitted ")
            return render(request, "hod_template/edit_session_template.html", context)

    else:
        return render(request, "hod_template/edit_session_template.html", context)


@csrf_exempt
def check_email_availability(request):
    email = request.POST.get("email")
    try:
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)


@csrf_exempt
def student_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStudent.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Student Feedback Messages'
        }
        return render(request, 'hod_template/student_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStudent, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def staff_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStaff.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Faculty Feedback Messages'
        }
        return render(request, 'hod_template/staff_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStaff, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def view_staff_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStaff.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Faculty'
        }
        return render(request, "hod_template/staff_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStaff, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


@csrf_exempt
def view_student_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStudent.objects.all()
        status_filter = request.GET.get('status', '')
        
        if status_filter:
            allLeave = allLeave.filter(status=int(status_filter))
        
        # Calculate statistics
        total_leaves = allLeave.count()
        approved_leaves = allLeave.filter(status=1).count()
        rejected_leaves = allLeave.filter(status=-1).count()
        pending_leaves = allLeave.filter(status=0).count()
        
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Students',
            'total_leaves': total_leaves,
            'approved_leaves': approved_leaves,
            'rejected_leaves': rejected_leaves,
            'pending_leaves': pending_leaves,
            'status_filter': status_filter
        }
        return render(request, "hod_template/student_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStudent, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


def admin_view_attendance(request):
    courses = Course.objects.all()
    sessions = Session.objects.all()
    context = {
        'courses': courses,
        'sessions': sessions,
        'page_title': 'View Attendance'
    }

    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def get_admin_attendance(request):
    course_id = request.POST.get('course')
    session_id = request.POST.get('session')
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        course = get_object_or_404(Course, id=course_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = get_object_or_404(
            Attendance, id=attendance_date_id, session=session, course=course)
        attendance_reports = AttendanceReport.objects.filter(
            attendance=attendance)
        json_data = []
        for report in attendance_reports:
            data = {
                "status": report.status,
                "name": str(report.student)
            }
            json_data.append(data)
        return JsonResponse(json.dumps(json_data), safe=False)
    except Exception as e:
        return None


def admin_view_profile(request):
    admin, _created = Admin.objects.get_or_create(admin=request.user)
    form = AdminForm(request.POST or None, request.FILES or None,
                     instance=admin)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                passport = request.FILES.get('profile_pic') or None
                custom_user = admin.admin
                if password != None:
                    custom_user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    custom_user.profile_pic = passport_url
                custom_user.first_name = first_name
                custom_user.last_name = last_name
                custom_user.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('admin_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
    return render(request, "hod_template/admin_view_profile.html", context)


def authority_view_profile(request):
    if request.user.user_type != '4':
        return redirect(reverse('admin_home'))
    authority, _created = Authority.objects.get_or_create(admin=request.user)
    form = AuthorityForm(request.POST or None, request.FILES or None,
                         instance=authority)
    context = {'form': form,
               'page_title': 'Authority Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                passport = request.FILES.get('profile_pic') or None
                custom_user = authority.admin
                if password != None:
                    custom_user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    custom_user.profile_pic = passport_url
                custom_user.first_name = first_name
                custom_user.last_name = last_name
                custom_user.save()
                messages.success(request, "Profile updated")
                return redirect(reverse('authority_view_profile'))
        except Exception:
            messages.error(request, "Could not update profile")
    return render(request, "hod_template/authority_view_profile.html", context)


def admin_notify_staff(request):
    staff = CustomUser.objects.filter(user_type=2)
    context = {
        'page_title': "Send Notifications To Faculty",
        'allStaff': staff
    }
    return render(request, "hod_template/staff_notification.html", context)


def admin_notify_student(request):
    student = CustomUser.objects.filter(user_type=3)
    context = {
        'page_title': "Send Notifications To Students",
        'students': student
    }
    return render(request, "hod_template/student_notification.html", context)


@csrf_exempt
def send_student_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    student = get_object_or_404(Student, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Student Management System",
                'body': message,
                'click_action': reverse('student_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': student.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStudent(student=student, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


@csrf_exempt
def send_staff_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    staff = get_object_or_404(Staff, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Student Management System",
                'body': message,
                'click_action': reverse('staff_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': staff.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStaff(staff=staff, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def delete_staff(request, staff_id):
    staff = get_object_or_404(CustomUser, staff__id=staff_id)
    staff.delete()
    messages.success(request, "Staff deleted successfully!")
    return redirect(reverse('manage_staff'))


def delete_student(request, student_id):
    student = get_object_or_404(CustomUser, student__id=student_id)
    student.delete()
    messages.success(request, "Student deleted successfully!")
    return redirect(reverse('manage_student'))


def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    try:
        course.delete()
        messages.success(request, "Course deleted successfully!")
    except Exception:
        messages.error(
            request, "Sorry, some students are assigned to this course already. Kindly change the affected student course and try again")
    return redirect(reverse('manage_course'))


def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    subject.delete()
    messages.success(request, "Subject deleted successfully!")
    return redirect(reverse('manage_subject'))


def delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    try:
        session.delete()
        messages.success(request, "Session deleted successfully!")
    except Exception:
        messages.error(
            request, "There are students assigned to this session. Please move them to another session.")
    return redirect(reverse('manage_session'))


def authority_grievance_list(request):
    if request.user.user_type != '4':
        return redirect(reverse('admin_home'))
    status_filter = request.GET.get('status')
    grievances = Grievance.objects.all().order_by('-created_at')
    if status_filter:
        grievances = grievances.filter(status=status_filter)
    context = {
        'grievances': grievances,
        'page_title': 'Authority Grievance Desk'
    }
    return render(request, "hod_template/grievance_list.html", context)


def authority_grievance_update(request, grievance_id):
    if request.user.user_type != '4':
        return redirect(reverse('admin_home'))
    grievance = get_object_or_404(Grievance, id=grievance_id)
    form = GrievanceAssignForm(request.POST or None, instance=grievance)
    context = {
        'form': form,
        'grievance': grievance,
        'page_title': 'Resolve Grievance'
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
            return redirect(reverse('authority_grievance_list'))
        messages.error(request, "Please correct the errors in the form")
    return render(request, "hod_template/grievance_update.html", context)


def authority_opportunity_list(request):
    if request.user.user_type != '4':
        return redirect(reverse('admin_home'))
    opportunities = Opportunity.objects.all().order_by('-created_at')
    context = {
        'opportunities': opportunities,
        'page_title': 'Opportunities Overview'
    }
    return render(request, "hod_template/opportunity_list.html", context)


def authority_opportunity_applications(request, opportunity_id):
    if request.user.user_type != '4':
        return redirect(reverse('admin_home'))
    opportunity = get_object_or_404(Opportunity, id=opportunity_id)
    applications = OpportunityApplication.objects.filter(opportunity=opportunity).order_by('-applied_at')
    context = {
        'opportunity': opportunity,
        'applications': applications,
        'page_title': 'Opportunity Applications'
    }
    return render(request, "hod_template/opportunity_applications.html", context)


def authority_application_update(request, application_id):
    if request.user.user_type != '4':
        return redirect(reverse('admin_home'))
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
            return redirect(reverse('authority_opportunity_applications', args=[application.opportunity.id]))
        messages.error(request, "Please correct the errors in the form")
    return render(request, "hod_template/opportunity_application_update.html", context)


# ====================  ADMISSIONS & REGISTRATION VIEWS ====================

def manage_admission_sessions(request):
    """View all admission sessions"""
    sessions = AdmissionSession.objects.all().order_by('-start_date')
    context = {
        'sessions': sessions,
        'page_title': 'Manage Admission Sessions'
    }
    return render(request, 'hod_template/manage_admission_sessions.html', context)


def add_admission_session(request):
    """Create new admission session"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            application_start = request.POST.get('application_start')
            application_end = request.POST.get('application_end')
            
            session = AdmissionSession.objects.create(
                name=name,
                start_date=start_date,
                end_date=end_date,
                application_start=application_start,
                application_end=application_end
            )
            messages.success(request, "Admission session created successfully!")
            return redirect(reverse('manage_admission_sessions'))
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    context = {'page_title': 'Add Admission Session'}
    return render(request, 'hod_template/add_admission_session.html', context)


def manage_admission_applications(request):
    """View and manage all admission applications"""
    status_filter = request.GET.get('status')
    applications = AdmissionApplication.objects.all().order_by('-created_at')
    
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    context = {
        'applications': applications,
        'page_title': 'Manage Admissions',
        'status_choices': AdmissionApplication.STATUS_CHOICES
    }
    return render(request, 'hod_template/manage_admissions.html', context)


def view_admission_application(request, application_id):
    """View single admission application details"""
    application = get_object_or_404(AdmissionApplication, id=application_id)
    context = {
        'application': application,
        'page_title': f'Application - {application.application_number}'
    }
    return render(request, 'hod_template/view_admission_application.html', context)


@csrf_exempt
def update_admission_status(request, application_id):
    """Update application status via AJAX"""
    if request.method == 'POST':
        try:
            application = get_object_or_404(AdmissionApplication, id=application_id)
            status = request.POST.get('status')
            remarks = request.POST.get('remarks', '')
            
            application.status = status
            application.remarks = remarks
            application.reviewed_by = request.user
            application.save()
            
            return JsonResponse({'success': True, 'message': 'Status updated successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


def approve_and_enroll(request, application_id):
    """Approve application and create student account"""
    application = get_object_or_404(AdmissionApplication, id=application_id)
    
    if request.method == 'POST':
        try:
            # Create user account
            user = CustomUser.objects.create_user(
                email=application.email,
                password='student@123',  # Default password
                user_type=3,
                first_name=application.first_name,
                last_name=application.last_name,
                gender=application.gender,
                address=application.address
            )
            
            if application.photo:
                user.profile_pic = application.photo
            user.save()
            
            # Update student with course and session
            student = user.student
            student.course = application.admission_course.course
            student.session = Session.objects.first()  # You may want to select the right session
            student.save()
            
            # Link application to student
            application.student = student
            application.status = 'enrolled'
            application.reviewed_by = request.user
            application.save()
            
            # Update seats filled
            admission_course = application.admission_course
            admission_course.seats_filled += 1
            admission_course.save()
            
            messages.success(request, f"Student enrolled successfully! Email: {application.email}, Password: student@123")
            return redirect(reverse('manage_admission_applications'))
            
        except Exception as e:
            messages.error(request, f"Enrollment failed: {str(e)}")
            return redirect(reverse('view_admission_application', args=[application_id]))
    
    context = {
        'application': application,
        'page_title': 'Confirm Enrollment'
    }
    return render(request, 'hod_template/confirm_enrollment.html', context)


# ==================== FEE & FINANCE VIEWS ====================

def manage_fee_structures(request):
    """View and manage fee structures"""
    structures = FeeStructure.objects.all().select_related('course', 'session').order_by('-created_at')
    courses = Course.objects.all()
    sessions = Session.objects.all()

    context = {
        'structures': structures,
        'courses': courses,
        'sessions': sessions,
        'page_title': 'Manage Fee Structure',
        'fee_types': FeeStructure.FEE_TYPE_CHOICES,
    }
    return render(request, 'hod_template/manage_fee_structures.html', context)


def add_fee_structure(request):
    """Add new fee structure"""
    if request.method == 'POST':
        try:
            course_id = request.POST.get('course')
            session_id = request.POST.get('session')
            fee_type = request.POST.get('fee_type')
            amount = request.POST.get('amount')
            is_mandatory = request.POST.get('is_mandatory') == 'on'
            description = request.POST.get('description', '')
            
            course = Course.objects.get(id=course_id)
            session = Session.objects.get(id=session_id)
            
            FeeStructure.objects.create(
                course=course,
                session=session,
                fee_type=fee_type,
                amount=amount,
                is_mandatory=is_mandatory,
                description=description
            )
            
            messages.success(request, "Fee structure added successfully!")
            return redirect(reverse('manage_fee_structures'))
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    courses = Course.objects.all()
    sessions = Session.objects.all()
    context = {
        'courses': courses,
        'sessions': sessions,
        'fee_types': FeeStructure.FEE_TYPE_CHOICES,
        'page_title': 'Add Fee Structure'
    }
    return render(request, 'hod_template/add_fee_structure.html', context)


def student_fee_management(request, student_id=None):
    """Manage fees for students"""
    if student_id:
        student = get_object_or_404(Student, id=student_id)
        student_fees = StudentFee.objects.filter(student=student).select_related('fee_structure')
        invoices = FeeInvoice.objects.filter(student=student).order_by('-created_at')
        payments = FeePayment.objects.filter(student=student).order_by('-payment_date')[:10]
        
        total_fees = sum(fee.net_amount for fee in student_fees)
        total_paid = sum(fee.paid_amount for fee in student_fees)
        balance = total_fees - total_paid
        
        context = {
            'student': student,
            'student_fees': student_fees,
            'invoices': invoices,
            'payments': payments,
            'total_fees': total_fees,
            'total_paid': total_paid,
            'balance': balance,
            'page_title': f'Fee Management - {student.admin.get_full_name()}'
        }
        return render(request, 'hod_template/student_fee_detail.html', context)
    else:
        students = Student.objects.all().select_related('admin', 'course')
        # Attach total fees to each student
        for student in students:
            total_fees = sum(fee.net_amount for fee in StudentFee.objects.filter(student=student))
            student.total_fees = total_fees
        context = {
            'students': students,
            'page_title': 'Student Fee Management'
        }
        return render(request, 'hod_template/student_fee_list.html', context)


def assign_fees_to_students(request):
    """Assign fee structures to students (bulk operation)"""
    if request.method == 'POST':
        try:
            course_id = request.POST.get('course')
            session_id = request.POST.get('session')
            academic_year = request.POST.get('academic_year')
            
            course = Course.objects.get(id=course_id)
            session_obj = Session.objects.get(id=session_id)
            
            # Get all students in this course and session
            students = Student.objects.filter(course=course, session=session_obj)
            
            # Get fee structures for this course and session
            fee_structures = FeeStructure.objects.filter(course=course, session=session_obj)
            
            count = 0
            for student in students:
                for fee_structure in fee_structures:
                    # Only create if doesn't exist
                    obj, created = StudentFee.objects.get_or_create(
                        student=student,
                        fee_structure=fee_structure,
                        academic_year=academic_year,
                        defaults={'amount': fee_structure.amount}
                    )
                    if created:
                        count += 1
            
            messages.success(request, f"Fees assigned to {students.count()} students ({count} fee items created)")
            return redirect(reverse('manage_fee_structures'))
            
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    courses = Course.objects.all()
    sessions = Session.objects.all()
    context = {
        'courses': courses,
        'sessions': sessions,
        'page_title': 'Assign Fees to Students'
    }
    return render(request, 'hod_template/assign_fees.html', context)


def collect_fee_payment(request, student_id):
    """Record fee payment from student"""
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        try:
            student_fee_id = request.POST.get('student_fee_id')
            amount = request.POST.get('amount')
            payment_method = request.POST.get('payment_method')
            transaction_id = request.POST.get('transaction_id', '')
            cheque_number = request.POST.get('cheque_number', '')
            bank_name = request.POST.get('bank_name', '')
            remarks = request.POST.get('remarks', '')
            
            student_fee = StudentFee.objects.get(id=student_fee_id)
            
            payment = FeePayment.objects.create(
                student=student,
                student_fee=student_fee,
                amount=amount,
                payment_method=payment_method,
                transaction_id=transaction_id,
                cheque_number=cheque_number,
                bank_name=bank_name,
                remarks=remarks,
                collected_by=request.user,
                status='success'
            )
            
            messages.success(request, f"Payment recorded successfully! Receipt No: {payment.receipt_number}")
            return redirect(reverse('student_fee_management', args=[student_id]))
            
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    student_fees = StudentFee.objects.filter(student=student).select_related('fee_structure')
    pending_fees = [fee for fee in student_fees if fee.balance > 0]
    
    context = {
        'student': student,
        'pending_fees': pending_fees,
        'payment_methods': FeePayment.PAYMENT_METHOD_CHOICES,
        'page_title': 'Collect Fee Payment'
    }
    return render(request, 'hod_template/collect_fee_payment.html', context)


def fee_payment_history(request):
    """View all fee payment transactions"""
    payments = FeePayment.objects.all().select_related('student', 'collected_by').order_by('-payment_date')
    
    # Filter by date range if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        payments = payments.filter(payment_date__gte=start_date)
    if end_date:
        payments = payments.filter(payment_date__lte=end_date)
    
    total_collected = payments.filter(status='success').aggregate(
        total=models.Sum('amount')
    )['total'] or 0
    
    context = {
        'payments': payments,
        'total_collected': total_collected,
        'page_title': 'Fee Payment History'
    }
    return render(request, 'hod_template/fee_payment_history.html', context)


def generate_fee_invoice(request, student_id):
    """Generate fee invoice for a student"""
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        try:
            session_id = request.POST.get('session')
            due_date = request.POST.get('due_date')
            installment_id = request.POST.get('installment_id') or None
            selected_fees = request.POST.getlist('fee_ids')
            
            session_obj = Session.objects.get(id=session_id)
            installment = FeeInstallment.objects.get(id=installment_id) if installment_id else None
            
            # Calculate totals
            student_fees = StudentFee.objects.filter(id__in=selected_fees)
            total_amount = sum(fee.amount for fee in student_fees)
            discount_amount = sum(fee.discount for fee in student_fees)
            net_amount = total_amount - discount_amount
            
            # Create invoice
            invoice = FeeInvoice.objects.create(
                student=student,
                session=session_obj,
                installment=installment,
                total_amount=total_amount,
                discount_amount=discount_amount,
                net_amount=net_amount,
                due_date=due_date,
                status='sent',
                generated_by=request.user
            )
            
            # Add invoice items
            for fee in student_fees:
                FeeInvoiceItem.objects.create(
                    invoice=invoice,
                    student_fee=fee,
                    amount=fee.net_amount
                )
            
            messages.success(request, f"Invoice {invoice.invoice_number} generated successfully!")
            return redirect(reverse('student_fee_management', args=[student_id]))
            
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    student_fees = StudentFee.objects.filter(student=student).select_related('fee_structure')
    sessions = Session.objects.all()
    installments = FeeInstallment.objects.filter(course=student.course)
    
    context = {
        'student': student,
        'student_fees': student_fees,
        'sessions': sessions,
        'installments': installments,
        'page_title': 'Generate Invoice'
    }
    return render(request, 'hod_template/generate_fee_invoice.html', context)


def fee_defaulters_report(request):
    """Report of students with pending fees"""
    course_id = request.GET.get('course')
    session_id = request.GET.get('session')
    
    student_fees = StudentFee.objects.all().select_related('student', 'fee_structure')
    
    if course_id:
        student_fees = student_fees.filter(student__course_id=course_id)
    if session_id:
        student_fees = student_fees.filter(student__session_id=session_id)
    
    # Group by student and calculate balances
    defaulters = {}
    for fee in student_fees:
        student_id = fee.student.id
        if student_id not in defaulters:
            defaulters[student_id] = {
                'student': fee.student,
                'total_fees': 0,
                'total_paid': 0,
                'balance': 0
            }
        defaulters[student_id]['total_fees'] += fee.net_amount
        defaulters[student_id]['total_paid'] += fee.paid_amount
        defaulters[student_id]['balance'] += fee.balance
    
    # Filter only defaulters (balance > 0)
    defaulters_list = [d for d in defaulters.values() if d['balance'] > 0]
    
    courses = Course.objects.all()
    sessions = Session.objects.all()
    
    context = {
        'defaulters': defaulters_list,
        'courses': courses,
        'sessions': sessions,
        'page_title': 'Fee Defaulters Report'
    }
    return render(request, 'hod_template/fee_defaulters_report.html', context)


# Company Internship Management
def add_company_internship(request):
    form = CompanyInternshipForm(request.POST or None, request.FILES or None)
    context = {
        'form': form,
        'page_title': 'Add Company Internship'
    }
    if request.method == 'POST':
        if form.is_valid():
            internship = form.save(commit=False)
            internship.posted_by = request.user
            internship.save()
            messages.success(request, "Company internship added successfully")
            return redirect(reverse('manage_company_internships'))
        messages.error(request, "Please correct the errors in the form")
    return render(request, 'hod_template/add_company_internship.html', context)


def manage_company_internships(request):
    internships = CompanyInternship.objects.all().order_by('-created_at')
    context = {
        'internships': internships,
        'page_title': 'Manage Company Internships'
    }
    return render(request, 'hod_template/manage_company_internships.html', context)


def edit_company_internship(request, internship_id):
    internship = get_object_or_404(CompanyInternship, id=internship_id)
    form = CompanyInternshipForm(request.POST or None, request.FILES or None, instance=internship)
    context = {
        'form': form,
        'internship': internship,
        'page_title': 'Edit Company Internship'
    }
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Internship updated successfully")
            return redirect(reverse('manage_company_internships'))
        messages.error(request, "Please correct the errors in the form")
    return render(request, 'hod_template/edit_company_internship.html', context)


def delete_company_internship(request, internship_id):
    internship = get_object_or_404(CompanyInternship, id=internship_id)
    try:
        internship.delete()
        messages.success(request, "Internship deleted successfully")
    except Exception as e:
        messages.error(request, f"Error deleting internship: {str(e)}")
    return redirect(reverse('manage_company_internships'))


def view_internship_applications(request, internship_id):
    internship = get_object_or_404(CompanyInternship, id=internship_id)
    applications = InternshipApplication.objects.filter(internship=internship).order_by('-applied_at')
    context = {
        'internship': internship,
        'applications': applications,
        'page_title': f'{internship.position} Applications'
    }
    return render(request, 'hod_template/view_internship_applications.html', context)


def update_internship_application(request, application_id):
    application = get_object_or_404(InternshipApplication, id=application_id)
    form = InternshipApplicationStatusForm(request.POST or None, instance=application)
    context = {
        'form': form,
        'application': application,
        'page_title': 'Update Application Status'
    }
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Application status updated successfully")
            
            # Send notification to student
            notification = NotificationStudent(
                student=application.student,
                message=f"Your application for {application.internship.position} at {application.internship.company_name} has been updated to: {application.get_status_display()}"
            )
            notification.save()
            
            return redirect(reverse('view_internship_applications', args=[application.internship.id]))
        messages.error(request, "Please correct the errors in the form")
    return render(request, 'hod_template/update_internship_application.html', context)

