import openpyxl
from django.contrib.auth.hashers import make_password
from .models import CustomUser, Student, Session, Course


def import_students_from_excel(file_path):
    """
    Import students from Excel file
    Expected columns: Email, First Name, Last Name, Gender, Course Code, Password
    """
    results = {'success': 0, 'failed': 0, 'errors': []}
    
    try:
        workbook = openpyxl.load_workbook(file_path)
        worksheet = workbook.active
        
        # Skip header row
        for row_idx, row in enumerate(worksheet.iter_rows(min_row=2, values_only=True), start=2):
            try:
                if not row[0]:  # Skip empty rows
                    continue
                
                email, first_name, last_name, gender, course_code, password = row[0:6]
                
                # Validate required fields
                if not all([email, first_name, last_name, gender, course_code, password]):
                    results['errors'].append(f"Row {row_idx}: Missing required fields")
                    results['failed'] += 1
                    continue
                
                # Check if user already exists
                if CustomUser.objects.filter(email=email).exists():
                    results['errors'].append(f"Row {row_idx}: Email {email} already exists")
                    results['failed'] += 1
                    continue
                
                # Get course
                try:
                    course = Course.objects.get(course_code=course_code)
                except Course.DoesNotExist:
                    results['errors'].append(f"Row {row_idx}: Course code {course_code} not found")
                    results['failed'] += 1
                    continue
                
                # Create user
                user = CustomUser.objects.create_user(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    gender=gender,
                    user_type=3,  # Student
                    profile_pic='',
                    address=''
                )
                
                # Create student profile
                Session.objects.get_or_create(
                    start_year__month=1,
                    defaults={'start_year': '2026-01-01', 'end_year': '2026-12-31'}
                )
                session = Session.objects.first()
                
                Student.objects.create(
                    admin=user,
                    course=course,
                    session=session
                )
                
                results['success'] += 1
                
            except Exception as e:
                results['errors'].append(f"Row {row_idx}: {str(e)}")
                results['failed'] += 1
        
        return results
    
    except Exception as e:
        return {'success': 0, 'failed': 1, 'errors': [f"File error: {str(e)}"]}
