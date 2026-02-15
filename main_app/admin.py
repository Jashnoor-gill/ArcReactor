from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
# Register your models here.


class UserModel(UserAdmin):
    ordering = ('email',)


admin.site.register(CustomUser, UserModel)
admin.site.register(Staff)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Branch)
admin.site.register(Book)
admin.site.register(IssuedBook)
admin.site.register(Library)
admin.site.register(Subject)
admin.site.register(Session)
admin.site.register(Grievance)
admin.site.register(GrievanceUpdate)
admin.site.register(Opportunity)
admin.site.register(OpportunityApplication)

# Admissions & Registration
admin.site.register(AdmissionSession)
admin.site.register(AdmissionCourse)
admin.site.register(AdmissionApplication)
admin.site.register(EntranceTest)

# Fee & Finance Management
admin.site.register(FeeStructure)
admin.site.register(FeeInstallment)
admin.site.register(StudentFee)
admin.site.register(FeePayment)
admin.site.register(FeeInvoice)
admin.site.register(FeeInvoiceItem)
admin.site.register(FeeDiscount)
admin.site.register(FeeReminder)

# Examination Management
admin.site.register(ExamType)
admin.site.register(ExamSession)
admin.site.register(Exam)
admin.site.register(ExamAttendees)
admin.site.register(GradeConfiguration)
admin.site.register(ExamRoom)

# Transport Management
admin.site.register(TransportRoute)
admin.site.register(TransportStop)
admin.site.register(Vehicle)
admin.site.register(Driver)
admin.site.register(StudentTransport)

# Hostel Management
admin.site.register(Hostel)
admin.site.register(HostelRoom)
admin.site.register(HostelAllocation)
admin.site.register(HostelFeePayment)
admin.site.register(MessMenu)

# HR & Payroll
admin.site.register(Department)
admin.site.register(Designation)
admin.site.register(StaffDetails)
admin.site.register(SalaryStructure)
admin.site.register(StaffSalary)
admin.site.register(Payroll)
admin.site.register(PayrollSlip)

