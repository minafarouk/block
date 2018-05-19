from django.urls import path
from . import views
from django.conf.urls import include

urlpatterns = [
    path('', views.home, name='home'),
    path('faq/', views.faq, name='faq'),
    path('creds/', include('creds.urls')),
]