from django.urls import path
from no8910.views import show_halaman_diskon, beli_voucher, get_voucher_data_to_buy, create_testimony, printTables, tes

urlpatterns = [
   path('diskon', show_halaman_diskon, name='diskon'),
   path('beli-voucher/<str:kode_voucher>/', beli_voucher, name='beli_voucher'),
   path('get-voucher-data-to-buy/<str:kode_voucher>/', get_voucher_data_to_buy, name='get_voucher_data_to_buy'),
   path('create-testimony/<uuid:id_tr_pemesanan_jasa>/', create_testimony, name='create_testimony'),
   path('print-tables', printTables, name='printTables'),
   path('tes', tes, name='tes')
]