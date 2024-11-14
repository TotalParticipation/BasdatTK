from django.urls import path
from . import views

urlpatterns = [
    path('transaksi', views.transaction_view, name='transaction_view'),  # Using '' to handle /transaksi/
]   