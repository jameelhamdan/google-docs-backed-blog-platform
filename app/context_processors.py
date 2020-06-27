from django.urls import reverse_lazy
from users import forms


def auth_forms(request):
    if not request.user.is_authenticated:
        return {
            'auth_forms':
                {
                    'login_form': forms.LoginForm(),
                    'login_url': reverse_lazy('users:login'),
                    'register_form': forms.RegisterForm(),
                    'register_url': reverse_lazy('users:register'),
                }
        }
    else:
        return {}
