from django.urls import path
from no8910.views import show_halaman_diskon, beli_voucher, get_voucher_data_to_buy, tes_testimoni, create_testimony, printTables

urlpatterns = [
   path('show-halaman-diskon', show_halaman_diskon, name='show_halaman_diskon'),
   path('beli-voucher/<str:kode_voucher>/', beli_voucher, name='beli_voucher'),
   path('get-voucher-data-to-buy/<str:kode_voucher>/', get_voucher_data_to_buy, name='get_voucher_data_to_buy'),
   path('tes-testimoni/', tes_testimoni, name='tes_testimoni'),
   path('create-testimony/<uuid:id>/', create_testimony, name='create_testimony'),
   path('print-tables', printTables, name='printTables')
]