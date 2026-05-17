from django.shortcuts import redirect
from django.contrib import messages


class StaffRequiredMiddleware:
    """
    Bloqueia acesso às URLs /dashboard/* por usuários não-staff.
    """
    PROTECTED_PREFIXES = ('/dashboard/',)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        for prefix in self.PROTECTED_PREFIXES:
            if request.path.startswith(prefix):
                if not request.user.is_authenticated:
                    return redirect(f'/accounts/login/?next={request.path}')
                if not request.user.is_staff:
                    messages.error(request, 'Acesso restrito a funcionários.')
                    return redirect('home')
        return self.get_response(request)