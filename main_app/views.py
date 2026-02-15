import json
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt

from .EmailBackend import EmailBackend
from .models import Attendance, CustomUser, Session, Subject, Admin, Staff, Student

# Create your views here.


def login_page(request):
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect(reverse("admin_home"))
        elif request.user.user_type == '2':
            return redirect(reverse("staff_home"))
        else:
            return redirect(reverse("student_home"))
    context = {
        'recaptcha_site_key': settings.RECAPTCHA_SITE_KEY,
        'demo_login_enabled': settings.DEMO_LOGIN_ENABLED,
    }
    return render(request, 'main_app/login.html', context)


def _get_demo_user():
    email = settings.DEMO_LOGIN_EMAIL or "demo@aegis.local"
    user = CustomUser.objects.filter(email=email).first()
    if user:
        return user
    user = CustomUser.objects.filter(is_superuser=True).first()
    if user:
        return user
    user = CustomUser.objects.filter(user_type='1').first()
    if user:
        return user
    user = CustomUser.objects.first()
    if user:
        return user

    password = get_random_string(32)
    return CustomUser.objects.create_superuser(
        email=email,
        password=password,
        user_type='1',
        gender='M',
        address='Demo account',
        profile_pic='defaults/profile.png',
        first_name='Demo',
        last_name='Admin',
    )


def doLogin(request, **kwargs):
    if request.method != 'POST':
        return HttpResponse("<h4>Denied</h4>")
    else:
        if settings.DEMO_LOGIN_ENABLED and request.POST.get('demo') == '1':
            user = _get_demo_user()
            login(request, user)
            if user.user_type == '1':
                return redirect(reverse("admin_home"))
            elif user.user_type == '2':
                return redirect(reverse("staff_home"))
            else:
                return redirect(reverse("student_home"))
        # Google reCAPTCHA (optional in production)
        if settings.RECAPTCHA_SECRET_KEY:
            captcha_token = request.POST.get('g-recaptcha-response')
            if not captcha_token:
                messages.error(request, 'Captcha required. Try Again')
                return redirect('/')
            captcha_url = "https://www.google.com/recaptcha/api/siteverify"
            data = {
                'secret': settings.RECAPTCHA_SECRET_KEY,
                'response': captcha_token
            }
            try:
                captcha_server = requests.post(url=captcha_url, data=data)
                response = json.loads(captcha_server.text)
                if response.get('success') is False:
                    messages.error(request, 'Invalid Captcha. Try Again')
                    return redirect('/')
            except Exception:
                messages.error(request, 'Captcha could not be verified. Try Again')
                return redirect('/')
        
        portal_type = request.POST.get('portal_type')
        if portal_type not in ['admin', 'staff', 'student']:
            messages.error(request, 'Please select a portal to sign in.')
            return redirect('/')

        # Authenticate
        user = EmailBackend.authenticate(request, username=request.POST.get('email'), password=request.POST.get('password'))
        if user != None:
            if portal_type == 'admin' and user.user_type != '1':
                messages.error(request, 'Admin portal allows admin accounts only.')
                return redirect('/')
            if portal_type == 'staff' and user.user_type != '2':
                messages.error(request, 'Faculty portal allows staff accounts only.')
                return redirect('/')
            if portal_type == 'student' and user.user_type != '3':
                messages.error(request, 'Student portal allows student accounts only.')
                return redirect('/')

            login(request, user)
            
            # Handle "Remember Me" functionality
            remember_me = request.POST.get('remember')
            if remember_me:
                # Set session to expire when browser closes = False
                # Session will last for 30 days
                request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days in seconds
            else:
                # Set session to expire when browser closes
                request.session.set_expiry(0)
            
            if user.user_type == '1':
                return redirect(reverse("admin_home"))
            elif user.user_type == '2':
                return redirect(reverse("staff_home"))
            else:
                return redirect(reverse("student_home"))
        else:
            messages.error(request, "Invalid details")
            return redirect("/")



def logout_user(request):
    if request.user != None:
        logout(request)
    return redirect("/")


def register(request):
    if request.user.is_authenticated:
        return redirect(reverse("login_page"))

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        role = request.POST.get("role", "")

        if not email or not password or not confirm_password or not role:
            messages.error(request, "Please fill all fields.")
            return redirect(reverse("register"))

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect(reverse("register"))

        if role not in ["1", "2", "3"]:
            messages.error(request, "Please select a valid role.")
            return redirect(reverse("register"))

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect(reverse("register"))

        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            user_type=role,
            gender="M",
            address="Registered user",
            profile_pic="defaults/profile.png",
        )

        if role == "1":
            Admin.objects.get_or_create(admin=user)
        elif role == "2":
            Staff.objects.get_or_create(admin=user)
        elif role == "3":
            Student.objects.get_or_create(admin=user)

        messages.success(request, "Registration successful. Please log in.")
        return redirect(reverse("login_page"))

    return render(request, "registration/register.html")


@csrf_exempt
def get_attendance(request):
    course_id = request.POST.get('course')
    session_id = request.POST.get('session')
    try:
        course = get_object_or_404(Course, id=course_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = Attendance.objects.filter(course=course, session=session)
        attendance_list = []
        for attd in attendance:
            data = {
                    "id": attd.id,
                    "attendance_date": str(attd.date),
                    "session": attd.session.id
                    }
            attendance_list.append(data)
        return JsonResponse(json.dumps(attendance_list), safe=False)
    except Exception as e:
        return None


def showFirebaseJS(request):
    data = """
    // Give the service worker access to Firebase Messaging.
// Note that you can only use Firebase Messaging here, other Firebase libraries
// are not available in the service worker.
importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-messaging.js');

// Initialize the Firebase app in the service worker by passing in
// your app's Firebase config object.
// https://firebase.google.com/docs/web/setup#config-object
firebase.initializeApp({
    apiKey: "AIzaSyBarDWWHTfTMSrtc5Lj3Cdw5dEvjAkFwtM",
    authDomain: "sms-with-django.firebaseapp.com",
    databaseURL: "https://sms-with-django.firebaseio.com",
    projectId: "sms-with-django",
    storageBucket: "sms-with-django.appspot.com",
    messagingSenderId: "945324593139",
    appId: "1:945324593139:web:03fa99a8854bbd38420c86",
    measurementId: "G-2F2RXTL9GT"
});

// Retrieve an instance of Firebase Messaging so that it can handle background
// messages.
const messaging = firebase.messaging();
messaging.setBackgroundMessageHandler(function (payload) {
    const notification = JSON.parse(payload);
    const notificationOption = {
        body: notification.body,
        icon: notification.icon
    }
    return self.registration.showNotification(payload.notification.title, notificationOption);
});
    """
    return HttpResponse(data, content_type='application/javascript')

