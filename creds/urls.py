from django.urls import path
from . import views
from django.conf.urls import include

urlpatterns = [
    path('issue', views.issue, name='issue-cert'),
    path('download/<cert_name>/', views.download_cert, name='downloadcert'),
    path('qr/<cert_name>/', views.qr_cert, name='qrcert'),
    path('mail/<sname>/<cname>/<dep>/', views.mail_cert, name='mailcert'),
    path('short-cert/<cert_name>/', views.url_cert, name='urlcert'),
    path('verifylink/<id>/', views.verifylink, name='verify-cert-link'),
    path('verify', views.verify, name='verify-cert'),
#    path('', include('landing.urls')),
]
