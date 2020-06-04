from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('login/social', views.SocialLoginView.as_view(), name='social_login'),
    path('complete/social', views.SocialLoginCompleteView.as_view(), name='social_complete'),
]
