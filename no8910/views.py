import uuid
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from no8910.models import Voucher, Promo, Subkategori, Testimoni
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from utils.db_utils import get_db_connection
import psycopg2
from datetime import datetime, timedelta

from django.http import JsonResponse

def show_halaman_diskon(request):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM VOUCHER")
    vouchers = cursor.fetchall()

    cursor.execute("SELECT * FROM PROMO")
    all_promo = cursor.fetchall()

    cursor.execute("SELECT * FROM METODE_BAYAR")
    list_metode_bayar = cursor.fetchall()

    context = {
        'vouchers': vouchers,
        'all_promo': all_promo,
        'list_metode_bayar': list_metode_bayar
    }

    cursor.close()
    return render(request, "diskon_page.html", context)


@csrf_exempt
def beli_voucher(request, kode_voucher):
    if request.method == "POST":
        # if not request.user.is_authenticated:
            # return redirect('login')
        
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM VOUCHER WHERE KODE = %s", [kode_voucher])
        voucher = cursor.fetchone()

        tr_pembelian_voucher_id = uuid.uuid4()
        print("user id: " + request.session['user_id'])
        user_id = request.session['user_id']
        # print("id user: " + user_id)

        
        
        id_metode_pembayaran = request.POST.get('metodePembayaran')
        # perbaiki id metode bayar tidak terambil
        # print("id metode: " + id_metode_pembayaran)
        id_voucher = voucher[0]
        tgl_awal = datetime.now().date()
        tgl_akhir = tgl_awal + timedelta(days=voucher[1])
        telah_digunakan = 0

        # blom bikin pengecekan saldo user kalo pilih metode MyPay!

        cursor.execute("""
                       INSERT INTO TR_PEMBELIAN_VOUCHER(id, tglawal, tglakhir, telahdigunakan, idpelanggan, idvoucher, idmetodebayar)
                       VALUES(%s, %s, %s, %s, %s, %s, %s)""", 
                       [tr_pembelian_voucher_id, tgl_awal, tgl_akhir, telah_digunakan, user_id, id_voucher, id_metode_pembayaran])

        connection.commit()



    
    
    cursor.close()
    return JsonResponse({"status": "CREATED", "message": "Voucher berhasil dibeli."}, status=201)

def get_voucher_data_to_buy(request, kode_voucher):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM VOUCHER WHERE KODE = %s", [kode_voucher])
    voucher = cursor.fetchone()

    data = {
        'kode': voucher[0],
        'jumlah_hari_berlaku': voucher[1],
        'kuota_penggunaan': voucher[2],
        'harga': voucher[3],
    }

    cursor.close()
    return JsonResponse(data)

def tes_testimoni(request):

    return render(request, "tes_testimoni.html")


def show_subkategori_page(request, id):
    subkategori = Subkategori.objects.get(pk=id)

    context = {'subkategori': subkategori}

    return render(request, 'subkategori_page.html', context)

@csrf_exempt
def create_testimony(request, id_tr_pemesanan_jasa):
    if request.method == "POST":
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM tr_pemesanan_jasa WHERE id = %s", [id_tr_pemesanan_jasa])
        tr_pemesanan_jasa = cursor.fetchone()

        user = request.user
        rating = request.POST.get("rating")
        testimony_text = request.POST.get("testimony_text")

        
        tr_pemesanan_jasa_id = tr_pemesanan_jasa[0]
        tanggal_buat_testimoni = datetime.now().date()
        testimony_text = request.POST.get('testimony_text')
        rating = request.POST.get('rating')

        cursor.execute("""
                       INSERT INTO testimoni(idtrpemesanan, tgl, teks, rating) 
                       VALUES(%s, %s, %s, %s)""",
                       [tr_pemesanan_jasa_id, tanggal_buat_testimoni, testimony_text, rating])
        
        connection.commit()

    cursor.close()
    return JsonResponse({"status": "CREATED", "message": "Berhasil buat testimoni."}, status=201) 


def printTables():
    connection = get_db_connection()

    with connection.cursor() as cursor:
        # Execute the equivalent of \dt
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public';
        """)
        rows = cursor.fetchall()
    
    # Print the result
    print("Tables in the database:")
    for row in rows:
        print(row[0])
printTables()
