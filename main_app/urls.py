"""college_management_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from main_app.EditResultView import EditResultView

from . import hod_views, staff_views, student_views, views

urlpatterns = [
    path("", views.login_page, name='login_page'),
     path("register/", views.register, name='register'),
    path("get_attendance", views.get_attendance, name='get_attendance'),
    path("firebase-messaging-sw.js", views.showFirebaseJS, name='showFirebaseJS'),
    path("doLogin/", views.doLogin, name='user_login'),
    path("logout_user/", views.logout_user, name='user_logout'),
    path("admin/home/", hod_views.admin_home, name='admin_home'),
    path("staff/add", hod_views.add_staff, name='add_staff'),
    path("course/add", hod_views.add_course, name='add_course'),
    path("send_student_notification/", hod_views.send_student_notification,
         name='send_student_notification'),
    path("send_staff_notification/", hod_views.send_staff_notification,
         name='send_staff_notification'),
    path("add_session/", hod_views.add_session, name='add_session'),
    path("admin_notify_student", hod_views.admin_notify_student,
         name='admin_notify_student'),
    path("admin_notify_staff", hod_views.admin_notify_staff,
         name='admin_notify_staff'),
    path("admin_view_profile", hod_views.admin_view_profile,
         name='admin_view_profile'),
    path("check_email_availability", hod_views.check_email_availability,
         name="check_email_availability"),
    path("session/manage/", hod_views.manage_session, name='manage_session'),
    path("session/edit/<int:session_id>",
         hod_views.edit_session, name='edit_session'),
    path("student/view/feedback/", hod_views.student_feedback_message,
         name="student_feedback_message",),
    path("staff/view/feedback/", hod_views.staff_feedback_message,
         name="staff_feedback_message",),
    path("student/view/leave/", hod_views.view_student_leave,
         name="view_student_leave",),
    path("staff/view/leave/", hod_views.view_staff_leave, name="view_staff_leave",),
    path("attendance/view/", hod_views.admin_view_attendance,
         name="admin_view_attendance",),
    path("attendance/fetch/", hod_views.get_admin_attendance,
         name='get_admin_attendance'),
    path("student/add/", hod_views.add_student, name='add_student'),
    path("student/import/", hod_views.bulk_import_students, name='bulk_import_students'),
    path("staff/manage/", hod_views.manage_staff, name='manage_staff'),
    path("student/manage/", hod_views.manage_student, name='manage_student'),
    path("course/manage/", hod_views.manage_course, name='manage_course'),
    path("staff/edit/<int:staff_id>", hod_views.edit_staff, name='edit_staff'),
    path("staff/delete/<int:staff_id>",
         hod_views.delete_staff, name='delete_staff'),

    path("course/delete/<int:course_id>",
         hod_views.delete_course, name='delete_course'),


    path("session/delete/<int:session_id>",
         hod_views.delete_session, name='delete_session'),

    path("student/delete/<int:student_id>",
         hod_views.delete_student, name='delete_student'),
    path("student/edit/<int:student_id>",
         hod_views.edit_student, name='edit_student'),
    path("course/edit/<int:course_id>",
         hod_views.edit_course, name='edit_course'),


    # Staff
    path("staff/home/", staff_views.staff_home, name='staff_home'),
    path("staff/apply/leave/", staff_views.staff_apply_leave,
         name='staff_apply_leave'),
    path("staff/feedback/", staff_views.staff_feedback, name='staff_feedback'),
    path("staff/view/profile/", staff_views.staff_view_profile,
         name='staff_view_profile'),
    path("staff/attendance/take/", staff_views.staff_take_attendance,
         name='staff_take_attendance'),
    path("staff/attendance/update/", staff_views.staff_update_attendance,
         name='staff_update_attendance'),
    path("staff/get_students/", staff_views.get_students, name='get_students'),
     path("staff/addbook/", staff_views.add_book, name="add_book"),
    path("staff/issue_book/", staff_views.issue_book, name="issue_book"),
    path("staff/view_issued_book/", staff_views.view_issued_book, name="view_issued_book"),

     path("staff/grievances/", staff_views.staff_grievance_list, name='staff_grievance_list'),
     path("staff/grievances/<int:grievance_id>/", staff_views.staff_grievance_update, name='staff_grievance_update'),
     path("staff/opportunities/", staff_views.staff_opportunity_list, name='staff_opportunity_list'),
     path("staff/opportunities/add/", staff_views.staff_opportunity_create, name='staff_opportunity_create'),
     path("staff/opportunities/<int:opportunity_id>/applications/", staff_views.staff_opportunity_applications, name='staff_opportunity_applications'),
     path("staff/applications/<int:application_id>/", staff_views.staff_application_update, name='staff_application_update'),



    path("staff/attendance/fetch/", staff_views.get_student_attendance,
         name='get_student_attendance'),
    path("staff/attendance/save/",
         staff_views.save_attendance, name='save_attendance'),
    path("staff/attendance/update_save/",
         staff_views.update_attendance, name='update_attendance'),
    path("staff/fcmtoken/", staff_views.staff_fcmtoken, name='staff_fcmtoken'),
    path("staff/view/notification/", staff_views.staff_view_notification,
         name="staff_view_notification"),
    path("staff/result/add/", staff_views.staff_add_result, name='staff_add_result'),
    path("staff/result/edit/", EditResultView.as_view(),
         name='edit_student_result'),
    path('staff/result/fetch/', staff_views.fetch_student_result,
         name='fetch_student_result'),



    # Student
    path("student/home/", student_views.student_home, name='student_home'),
    path("student/view/attendance/", student_views.student_view_attendance,
         name='student_view_attendance'),
    path("student/apply/leave/", student_views.student_apply_leave,
         name='student_apply_leave'),
    path("student/feedback/", student_views.student_feedback,
         name='student_feedback'),
    path("student/view/profile/", student_views.student_view_profile,
         name='student_view_profile'),
    path("student/fcmtoken/", student_views.student_fcmtoken,
         name='student_fcmtoken'),
     # path('student/todo',student_views.todo,name='todo'),

     
     path("student/viewbooks/", student_views.view_books, name="view_books"),

    path("student/view/notification/", student_views.student_view_notification,
         name="student_view_notification"),
    path('student/view/result/', student_views.student_view_result,
         name='student_view_result'),

     path("student/grievances/submit/", student_views.student_grievance_submit, name='student_grievance_submit'),
     path("student/grievances/", student_views.student_grievance_list, name='student_grievance_list'),
     path("student/opportunities/", student_views.student_opportunity_list, name='student_opportunity_list'),
     path("student/opportunities/<int:opportunity_id>/apply/", student_views.student_apply_opportunity, name='student_apply_opportunity'),
     path("student/applications/", student_views.student_my_applications, name='student_my_applications'),

     path("authority/grievances/", hod_views.authority_grievance_list, name='authority_grievance_list'),
     path("authority/grievances/<int:grievance_id>/", hod_views.authority_grievance_update, name='authority_grievance_update'),
     path("authority/opportunities/", hod_views.authority_opportunity_list, name='authority_opportunity_list'),
     path("authority/opportunities/<int:opportunity_id>/applications/", hod_views.authority_opportunity_applications, name='authority_opportunity_applications'),
     path("authority/applications/<int:application_id>/", hod_views.authority_application_update, name='authority_application_update'),

     # Admissions & Registration
     path("admissions/sessions/", hod_views.manage_admission_sessions, name='manage_admission_sessions'),
     path("admissions/session/add/", hod_views.add_admission_session, name='add_admission_session'),
     path("admissions/applications/", hod_views.manage_admission_applications, name='manage_admission_applications'),
     path("admissions/application/<int:application_id>/", hod_views.view_admission_application, name='view_admission_application'),
     path("admissions/application/<int:application_id>/update-status/", hod_views.update_admission_status, name='update_admission_status'),
     path("admissions/application/<int:application_id>/enroll/", hod_views.approve_and_enroll, name='approve_and_enroll'),
     
     # Fee & Finance Management
     path("fees/structures/", hod_views.manage_fee_structures, name='manage_fee_structures'),
     path("fees/structure/add/", hod_views.add_fee_structure, name='add_fee_structure'),
     path("fees/students/", hod_views.student_fee_management, name='student_fee_list'),
     path("fees/student/<int:student_id>/", hod_views.student_fee_management, name='student_fee_management'),
     path("fees/assign/", hod_views.assign_fees_to_students, name='assign_fees_to_students'),
     path("fees/collect/<int:student_id>/", hod_views.collect_fee_payment, name='collect_fee_payment'),
     path("fees/payments/history/", hod_views.fee_payment_history, name='fee_payment_history'),
     path("fees/invoice/generate/<int:student_id>/", hod_views.generate_fee_invoice, name='generate_fee_invoice'),
     path("fees/defaulters/", hod_views.fee_defaulters_report, name='fee_defaulters_report'),

]

