from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile or user_profile.role != 'ADMIN':
            messages.error(
                request,
                'Acesso negado: apenas Administradores podem realizar esta ação.',
            )
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)

    return _wrapped_view