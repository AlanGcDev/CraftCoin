from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps

def login_required_with_message(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            action = view_func.__name__.replace('_', ' ').capitalize()
            return redirect(f"{reverse('login')}?next={request.path}&action={action}")
    return _wrapped_view