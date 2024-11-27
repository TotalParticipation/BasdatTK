from django.urls import path
from no8910.views import show_halaman_diskon, beli_voucher_by_ajax, get_voucher_data_to_buy, tes_testimoni, create_testimony_by_ajax

urlpatterns = [
   path('show-halaman-diskon', show_halaman_diskon, name='show_halaman_diskon'),
   path('beli-voucher-by-ajax/<uuid:id>/', beli_voucher_by_ajax, name='beli_voucher_by_ajax'),
   path('get-voucher-data-to-buy/<uuid:id>/', get_voucher_data_to_buy, name='get_voucher_data_to_buy'),
   path('tes-testimoni/', tes_testimoni, name='tes_testimoni'),
   path('create-testimony-by-ajax/<uuid:id>/', create_testimony_by_ajax, name='create_testimony_by_ajax'),
]