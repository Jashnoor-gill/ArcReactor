from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.shortcuts import redirect


class LoginCheckMiddleWare(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user # Who is the current user ?
        if user.is_authenticated:
            if user.user_type == '1': # Is it the HOD/Admin
                if modulename == 'main_app.student_views':
                    return redirect(reverse('admin_home'))
            elif user.user_type == '4': # Authority
                if not request.path.startswith('/authority/'):
                    if modulename in ['main_app.student_views', 'main_app.staff_views', 'main_app.hod_views']:
                        return redirect(reverse('authority_home'))
            elif user.user_type == '2': #  Staff :-/ ?
                if modulename == 'main_app.student_views' or modulename == 'main_app.hod_views':
                    return redirect(reverse('staff_home'))
            elif user.user_type == '3': # ... or Student ?
                if modulename == 'main_app.hod_views' or modulename == 'main_app.staff_views':
                    return redirect(reverse('student_home'))
            else: # None of the aforementioned ? Please take the user to login page
                return redirect(reverse('login_page'))
        else:
            static_prefix = getattr(settings, 'STATIC_URL', '/static/')
            media_prefix = getattr(settings, 'MEDIA_URL', '/media/')
            if (
                request.path.startswith(static_prefix)
                or request.path.startswith(media_prefix)
                or request.path == reverse('login_page')
                or request.path == reverse('register')
                or modulename == 'django.contrib.auth.views'
                or request.path == reverse('user_login')
            ):
                pass
            else:
                return redirect(reverse('login_page'))
