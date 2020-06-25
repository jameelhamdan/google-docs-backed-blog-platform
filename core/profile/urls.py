from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views


app_name = 'profile'
urlpatterns = [
    path('me', login_required(views.MyProfileRedirect.as_view()), name='me'),
    path('<str:username>', views.ProfileView.as_view(), name='profile'),
]
