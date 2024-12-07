from django.urls import path
from . import views

urlpatterns = [
    path('transaksi', views.transaction_view, name='transaction_view'),
    path('process_transaction', views.process_transaction, name='process_transaction'),
    path('mypay/', views.mypay_dashboard, name='mypay_dashboard'),
    path('kelola-pekerjaan/', views.pekerjaan_dashboard, name='pekerjaan_dashboard'),
    path('statuspekerjaan/', views.status_pekerjaan_dashboard, name='status_pekerjaan_dashboard'),
    path('fetch_subcategories/', views.fetch_subcategories, name='fetch_subcategories'),
    path('fetch_orders/', views.fetch_orders, name='fetch_orders'),
    path('change_status/', views.change_status, name='change_status'),
    path('fetch_status_order/', views.fetch_status_order, name='fetch_status_order'),
    path('update_status/', views.fetch_status_order, name='update_status'),

]