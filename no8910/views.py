import uuid
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
# from no8910.models import Voucher, Promo, Subkategori, Testimoni
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

    user_id = request.session.get('user_id')
    cursor.execute("SELECT * FROM public.user WHERE id = %s", [user_id])
    user = cursor.fetchone()

    context = {
        'nama': user[1],
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
        # print("user id: " + request.session['user_id'])
        
        user_id = request.session.get('user_id')
        print(user_id)
        

        
        id_metode_pembayaran = request.POST.get('metodePembayaran')

        cursor.execute("SELECT * FROM metode_bayar where id = %s", [id_metode_pembayaran])

        metode_bayar = cursor.fetchone()
        
        if(metode_bayar[1] == "MyPay"):
            try:
                cursor.execute("SELECT * FROM public.user where id = %s", [user_id])
                user = cursor.fetchone()
                # print(user)
                saldo_user = user[7]
                harga_voucher = voucher[3]
                print(saldo_user)
                print(harga_voucher)

                if(saldo_user >= harga_voucher):
                    print("masuk")
                    cursor.execute("UPDATE public.user SET saldomypay=saldomypay - %s WHERE id=%s", [harga_voucher, user_id])
                    
                    
                else:
                    cursor.close()
                    print("saldo ga cukup")
                    return JsonResponse({"status": "FAILED", "message": "Saldo tidak cukup."}, status=400)
            except Exception as e:
                print(f"Error: {e}")
                return JsonResponse({"status": "FAILED", "message": "Terjadi kesalahan server."}, status=500)

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


def tes(request):
    return render(request, "tes.html")



@csrf_exempt
def create_testimony(request, id_tr_pemesanan_jasa):
    if request.method == "POST":
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM tr_pemesanan_jasa WHERE id = %s", [id_tr_pemesanan_jasa])
        tr_pemesanan_jasa = cursor.fetchone()

       
        rating = request.POST.get("rating")
        testimony_text = request.POST.get("testimony_text")

        
        tr_pemesanan_jasa_id = tr_pemesanan_jasa[0]
        print("ID PEMESANAN :"+str(tr_pemesanan_jasa_id))
        tanggal_buat_testimoni = datetime.now().date()
        testimony_text = request.POST.get('testimony_text')
        
        rating = request.POST.get('rating')

        cursor.execute("""
                       INSERT INTO testimoni(idtrpemesananan, tgl, teks, rating) 
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
