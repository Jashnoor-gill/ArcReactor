import json
import math
from datetime import datetime

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .models import *


def student_home(request):
    student, _ = Student.objects.get_or_create(admin=request.user)
    if not student.course or not student.session:
        messages.warning(request, "Your profile is not fully assigned yet. Please contact the admin to add your course/session.")
    total_attendance = AttendanceReport.objects.filter(student=student).count()
    total_present = AttendanceReport.objects.filter(student=student, status=True).count()
    if total_attendance == 0:  # Don't divide. DivisionByZero
        percent_absent = percent_present = 0
    else:
        percent_present = math.floor((total_present/total_attendance) * 100)
        percent_absent = math.ceil(100 - percent_present)
    
    context = {
        'total_attendance': total_attendance,
        'total_present': total_present,
        'percent_present': percent_present,
        'percent_absent': percent_absent,
        'page_title': 'Student Homepage'

    }
    return render(request, 'student_template/erpnext_student_home.html', context)


@ csrf_exempt
def student_view_attendance(request):
    student = get_object_or_404(Student, admin=request.user)
    if not student.course:
        messages.warning(request, "Your course is not assigned yet. Please contact the admin.")
        context = {
            'course': None,
            'page_title': 'View Attendance'
        }
        return render(request, 'student_template/student_view_attendance.html', context)
    if request.method != 'POST':
        course = get_object_or_404(Course, id=student.course.id)
        context = {
            'course': course,
            'page_title': 'View Attendance'
        }
        return render(request, 'student_template/student_view_attendance.html', context)
    else:
        course_id = request.POST.get('course')
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        try:
            if not course_id:
                return JsonResponse(json.dumps([]), safe=False)
            course = get_object_or_404(Course, id=course_id)
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            attendance = Attendance.objects.filter(
                date__range=(start_date, end_date), course=course)
            attendance_reports = AttendanceReport.objects.filter(
                attendance__in=attendance, student=student)
            json_data = []
            for report in attendance_reports:
                data = {
                    "date":  str(report.attendance.date),
                    "status": report.status
                }
                json_data.append(data)
            return JsonResponse(json.dumps(json_data), safe=False)
        except Exception:
            return JsonResponse(json.dumps([]), safe=False)


def student_apply_leave(request):
    form = LeaveReportStudentForm(request.POST or None)
    student = get_object_or_404(Student, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStudent.objects.filter(student=student),
        'page_title': 'Apply for leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.student = student
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('student_apply_leave'))
            except Exception:
                messages.error(request, "Could not submit")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "student_template/student_apply_leave.html", context)


def student_feedback(request):
    form = FeedbackStudentForm(request.POST or None)
    student = get_object_or_404(Student, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStudent.objects.filter(student=student),
        'page_title': 'Student Feedback'

    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.student = student
                obj.save()
                messages.success(
                    request, "Feedback submitted for review")
                return redirect(reverse('student_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "student_template/student_feedback.html", context)


def student_view_profile(request):
    student = get_object_or_404(Student, admin=request.user)
    form = StudentEditForm(request.POST or None, request.FILES or None,
                           instance=student)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = student.admin
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
                student.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('student_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(request, "Error Occured While Updating Profile " + str(e))

    return render(request, "student_template/student_view_profile.html", context)


@csrf_exempt
def student_fcmtoken(request):
    token = request.POST.get('token')
    student_user = get_object_or_404(CustomUser, id=request.user.id)
    try:
        student_user.fcm_token = token
        student_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def student_view_notification(request):
    student = get_object_or_404(Student, admin=request.user)
    notifications = NotificationStudent.objects.filter(student=student)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "student_template/student_view_notification.html", context)


def student_view_result(request):
    student = get_object_or_404(Student, admin=request.user)
    results = StudentResult.objects.filter(student=student)
    
    # Calculate analytics with all test types
    total_courses = results.count()
    if total_courses > 0:
        total_marks = sum([r.test_1 + r.test_2 + r.test_3 + r.mid_sem + r.exam for r in results])
        avg_marks = total_marks / total_courses if total_courses > 0 else 0
        max_marks = total_courses * 500  # Assuming each course has max 500 (100 each for 5 tests)
        percentage = (total_marks / max_marks * 100) if max_marks > 0 else 0
    else:
        avg_marks = 0
        percentage = 0
        total_marks = 0
    
    # By status (pass/fail) count - using 250 as passing score for 500 max per course
    passed = sum(1 for r in results if (r.test_1 + r.test_2 + r.test_3 + r.mid_sem + r.exam) >= 250)
    failed = total_courses - passed
    
    context = {
        'results': results,
        'page_title': "View Results",
        'total_subjects': total_courses,
        'total_marks': round(total_marks, 2),
        'avg_marks': round(avg_marks, 2),
        'percentage': round(percentage, 2),
        'passed': passed,
        'failed': failed
    }
    return render(request, "student_template/student_view_result.html", context)


#library

def view_books(request):
    books = Book.objects.all()
    context = {
        'books': books,
        'page_title': "Library"
    }
    return render(request, "student_template/view_books.html", context)


def student_grievance_submit(request):
    form = GrievanceForm(request.POST or None, request.FILES or None)
    context = {
        'form': form,
        'page_title': 'Submit Grievance'
    }
    if request.method == 'POST':
        if form.is_valid():
            grievance = form.save(commit=False)
            grievance.created_by = request.user
            grievance.save()
            GrievanceUpdate.objects.create(
                grievance=grievance,
                status=grievance.status,
                note='Submitted',
                updated_by=request.user
            )
            messages.success(request, "Grievance submitted successfully")
            return redirect(reverse('student_grievance_submit'))
        messages.error(request, "Please correct the errors in the form")
    return render(request, "student_template/grievance_submit.html", context)


def student_grievance_list(request):
    grievances = Grievance.objects.filter(created_by=request.user).order_by('-created_at')
    context = {
        'grievances': grievances,
        'page_title': 'My Grievances'
    }
    return render(request, "student_template/grievance_list.html", context)


def student_opportunity_list(request):
    opportunities = Opportunity.objects.filter(is_active=True).order_by('-created_at')
    domain = request.GET.get('domain')
    type_filter = request.GET.get('type')
    organization = request.GET.get('organization')
    if domain:
        opportunities = opportunities.filter(domain__icontains=domain)
    if type_filter:
        opportunities = opportunities.filter(type=type_filter)
    if organization:
        opportunities = opportunities.filter(organization__icontains=organization)

    context = {
        'opportunities': opportunities,
        'page_title': 'Opportunities',
        'filters': {
            'domain': domain or '',
            'type': type_filter or '',
            'organization': organization or ''
        }
    }
    return render(request, "student_template/opportunity_list.html", context)


def student_apply_opportunity(request, opportunity_id):
    opportunity = get_object_or_404(Opportunity, id=opportunity_id, is_active=True)
    student = get_object_or_404(Student, admin=request.user)
    existing = OpportunityApplication.objects.filter(
        opportunity=opportunity,
        student=student
    ).first()
    if existing:
        messages.info(request, "You have already applied for this opportunity")
        return redirect(reverse('student_opportunity_list'))

    form = OpportunityApplicationForm(request.POST or None, request.FILES or None)
    context = {
        'form': form,
        'opportunity': opportunity,
        'page_title': 'Apply for Opportunity'
    }
    if request.method == 'POST':
        if form.is_valid():
            application = form.save(commit=False)
            application.opportunity = opportunity
            application.student = student
            application.save()
            messages.success(request, "Application submitted")
            return redirect(reverse('student_my_applications'))
        messages.error(request, "Please correct the errors in the form")
    return render(request, "student_template/opportunity_apply.html", context)


def student_my_applications(request):
    student = get_object_or_404(Student, admin=request.user)
    applications = OpportunityApplication.objects.filter(student=student).order_by('-applied_at')
    context = {
        'applications': applications,
        'page_title': 'My Applications'
    }
    return render(request, "student_template/opportunity_applications.html", context)


def student_request_course(request):
    """Student can request to enroll in a course"""
    student = get_object_or_404(Student, admin=request.user)
    
    # Get courses student hasn't requested yet or can re-request
    existing_requests = CourseEnrollmentRequest.objects.filter(
        student=student
    ).values_list('course_id', flat=True)
    
    available_courses = Course.objects.exclude(id__in=existing_requests)
    
    form = CourseEnrollmentRequestForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            enrollment_request = form.save(commit=False)
            enrollment_request.student = student
            
            # Check if student already requested this course
            existing = CourseEnrollmentRequest.objects.filter(
                student=student,
                course=enrollment_request.course
            ).first()
            
            if existing:
                messages.warning(request, "You have already requested this course")
                return redirect(reverse('student_request_course'))
            
            enrollment_request.save()
            messages.success(request, f"Course enrollment request for {enrollment_request.course.name} has been submitted")
            return redirect(reverse('student_course_requests'))
        else:
            messages.error(request, "Please correct the errors")
    
    # Override queryset to show only available courses
    form.fields['course'].queryset = available_courses
    
    context = {
        'form': form,
        'page_title': 'Request Course Enrollment',
        'available_courses': available_courses
    }
    return render(request, 'student_template/student_request_course.html', context)


def student_course_requests(request):
    """View all course enrollment requests by student"""
    student = get_object_or_404(Student, admin=request.user)
    requests = CourseEnrollmentRequest.objects.filter(student=student).order_by('-created_at')
    
    context = {
        'requests': requests,
        'page_title': 'My Course Requests'
    }
    return render(request, 'student_template/student_course_requests.html', context)


# Company Internship Views
def student_view_internships(request):
    """View all active company internships"""
    internships = CompanyInternship.objects.filter(is_active=True).order_by('-created_at')
    student = get_object_or_404(Student, admin=request.user)
    
    # Filter options
    company = request.GET.get('company')
    location = request.GET.get('location')
    
    if company:
        internships = internships.filter(company_name__icontains=company)
    if location:
        internships = internships.filter(location__icontains=location)
    
    # Get student's applications to mark already applied internships
    applied_ids = InternshipApplication.objects.filter(student=student).values_list('internship_id', flat=True)
    
    context = {
        'internships': internships,
        'applied_ids': list(applied_ids),
        'page_title': 'Company Internships',
        'filters': {
            'company': company or '',
            'location': location or ''
        }
    }
    return render(request, 'student_template/student_view_internships.html', context)


def student_apply_internship(request, internship_id):
    """Apply for a company internship"""
    internship = get_object_or_404(CompanyInternship, id=internship_id, is_active=True)
    student = get_object_or_404(Student, admin=request.user)
    
    # Check if already applied
    existing = InternshipApplication.objects.filter(
        internship=internship,
        student=student
    ).first()
    
    if existing:
        messages.info(request, "You have already applied for this internship")
        return redirect(reverse('student_view_internships'))
    
    form = InternshipApplicationForm(request.POST or None, request.FILES or None)
    context = {
        'form': form,
        'internship': internship,
        'page_title': f'Apply for {internship.position}'
    }
    
    if request.method == 'POST':
        if form.is_valid():
            application = form.save(commit=False)
            application.internship = internship
            application.student = student
            application.save()
            messages.success(request, "Application submitted successfully")
            return redirect(reverse('student_internship_applications'))
        messages.error(request, "Please correct the errors in the form")
    
    return render(request, 'student_template/student_apply_internship.html', context)


def student_internship_applications(request):
    """View all internship applications by student"""
    student = get_object_or_404(Student, admin=request.user)
    applications = InternshipApplication.objects.filter(student=student).order_by('-applied_at')
    
    context = {
        'applications': applications,
        'page_title': 'My Internship Applications'
    }
    return render(request, 'student_template/student_internship_applications.html', context)

