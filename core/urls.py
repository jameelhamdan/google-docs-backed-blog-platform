from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('@', include('core.profile.urls')),
    path('article/', include('core.articles.urls')),
]
