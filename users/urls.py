from django.urls import path
from social_django import views as auth_views
from . import views

app_name = 'social'
urlpatterns = [
    path(f'login/<str:backend>/', auth_views.auth, name='begin'),
    path(f'logout/<str:backend>/', views.LogoutView.as_view(), name='logout'),
    path(f'complete/<str:backend>/', auth_views.complete, name='complete'),
    # disconnection
    path(f'disconnect/<str:backend>/', auth_views.disconnect, name='disconnect'),
    path(f'disconnect/<association_id>/', auth_views.disconnect, name='disconnect_individual'),
]
