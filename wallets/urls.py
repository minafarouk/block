from django.urls import path
from . import views

urlpatterns = [
    path('landing/', views.wallet_landing, name='wallet-landing'),
    path('login/', views.login, name='login'),
    path('wallet/', views.wallet, name='wallet-dashboard'),
#    path('import/', views.import_address, name='import-wallet'),
    path('create/', views.create, name='create'),
    path('send_asset/', views.transfer_asset, name='send_asset'),
    path('cred_cert/<cred_txid>', views.cred_to_verify, name='cred_to_cert'),
]
