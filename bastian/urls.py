from django.urls import path
from . import views

urlpatterns = [
    path('transaksi', views.transaction_view, name='transaction_view'),
    path('process_transaction/', views.process_transaction, name='process_transaction'),
    path('mypay/', views.mypay_dashboard, name='mypay_dashboard'),
    path('pekerjaan/', views.pekerjaan_dashboard, name='pekerjaan_dashboard'),
    path('statuspekerjaan/', views.status_pekerjaan_dashboard, name='status_pekerjaan_dashboard'),
]