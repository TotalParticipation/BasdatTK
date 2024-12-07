# views.py
from utils.db_utils import get_db_connection
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from .forms import TransactionForm
from datetime import datetime
import uuid
from uuid import UUID

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

def transaction_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user_phone, user_balance, jasa_options, user_role = None, 0, [], None

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Fetch user details
            cursor.execute("""SELECT nohp, saldomypay FROM "user" WHERE id = %s;""", [user_id])
            user_data = cursor.fetchone()
            if user_data:
                user_phone, user_balance = user_data

            # Determine user role
            cursor.execute("""SELECT * FROM PELANGGAN WHERE id = %s;""", [user_id])
            pelanggan = cursor.fetchone()
            if pelanggan:
                user_role = "pelanggan"
                # Fetch jasa options only for pelanggan
                cursor.execute("""
                               SELECT sj.namasubkategori, tpj.totalbiaya, tpj.id
                               FROM SUBKATEGORI_JASA sj
                               JOIN TR_PEMESANAN_JASA tpj ON sj.id = tpj.idkategorijasa
                               JOIN TR_PEMESANAN_STATUS tps ON tpj.id = tps.idtrpemesanan
                               JOIN STATUS_PESANAN sp ON tps.idstatus = sp.id
                               WHERE status LIKE 'Menunggu Pembayaran' AND tpj.idpelanggan = %s;
                               """, [user_id])
                jasa_options = cursor.fetchall()
            else:
                user_role = "pekerja"

    except Exception as e:
        print(f"Error fetching data: {e}")
    finally:
        connection.close()

    print("transaction_form.html")
    context = {
        'user_phone': user_phone,
        'user_balance': user_balance,
        'current_date': datetime.now().strftime("%A, %B %d, %Y"),
        'jasa_options': jasa_options,
        'user_role': user_role,
    }
    return render(request, 'transaction_form.html', context)

def process_transaction(request):
    if request.method == 'POST':
        print("Processing transaction...")  # For debugging
        try:
            # Log POST data for debugging
            print(f"POST data: {request.POST}")

            # Get the 'category' and 'user_id' from the form and session
            state = request.POST.get('category')
            user_id = request.session.get('user_id')

            # DB connection (ensure you have a function for this)
            connection = get_db_connection()

            with connection.cursor() as cursor:
                if state == 'topup':
                    # Process TopUp transaction
                    nominal_list = request.POST.getlist('nominal')  # Use getlist to handle all values

                    # Check if the list is non-empty and contains valid nominal
                    if nominal_list and nominal_list[0].isdigit():  # Check if the first value is a valid number
                        nominal = float(nominal_list[0])  # Convert the first value to float
                        cursor.execute("""
                            UPDATE "user" 
                            SET saldomypay = saldomypay + %s 
                            WHERE id = %s;
                        """, [nominal, user_id])

                        cursor.execute("""
                            INSERT INTO TR_MYPAY (id, UserId, Tgl, Nominal, KategoriId) 
                            VALUES (%s, %s, %s, %s, (SELECT id from KATEGORI_TR_MYPAY WHERE nama = 'topup'));
                        """, [str(uuid.uuid4()), user_id, datetime.now().strftime("%Y-%m-%d"), nominal])
                        messages.success(request, "TopUp berhasil ditambahkan!")
                    else:
                        messages.error(request, "Nominal TopUp tidak valid!")

                elif state == 'service_payment':
                    # Process service payment
                    service_price = request.POST.get('service_price')  # Price of the service
                    service_name = request.POST.get('service_name')  # Name of the service
                    tr_pemesanan_jasa_id = request.POST.get('tpj_id')

                    print(service_price, service_name)
                    # Validate input
                    if service_price and service_name:  
                        service_price = float(service_price)

                        # Deduct the service price from the user's balance
                        cursor.execute("""
                            UPDATE "user" 
                            SET saldomypay = saldomypay - %s 
                            WHERE id = %s AND saldomypay >= %s;
                        """, [service_price, user_id, service_price])

                        if cursor.rowcount == 0:  # No rows affected means insufficient balance
                            messages.error(request, "Saldo tidak cukup untuk membayar jasa!")
                        else:
                            # Record the service payment
                            cursor.execute("""
                                INSERT INTO TR_MYPAY (id, UserId, Tgl, Nominal, KategoriId) 
                                VALUES (%s, %s, %s, %s, (SELECT id from KATEGORI_TR_MYPAY WHERE nama = 'membayar jasa'));
                            """, [str(uuid.uuid4()), user_id, datetime.now().strftime("%Y-%m-%d"), service_price])
                            messages.success(request, "Pembayaran jasa berhasil dilakukan!")

                            cursor.execute("""
                                UPDATE TR_PEMESANAN_STATUS 
                                SET IdStatus = (SELECT id from STATUS_PESANAN WHERE status = 'Pesanan Selesai')
                                WHERE IdTrPemesanan = %s;
                            """, [tr_pemesanan_jasa_id])
                            messages.success(request, "Pembayaran jasa berhasil dilakukan!")
                    else:
                        messages.error(request, "Data pembayaran jasa tidak valid!")
                
                elif state == 'transfer':
                    nohp_tujuan = request.POST.get('phone_number')
                    nominal_list = request.POST.getlist('nominal')

                    if nominal_list and nominal_list[1].isdigit() and nohp_tujuan:
                        nominal = float(nominal_list[1])
                        cursor.execute("""
                            UPDATE "user" 
                            SET saldomypay = saldomypay - %s 
                            WHERE id = %s AND saldomypay >= %s;
                        """, [nominal, user_id, nominal])

                        if cursor.rowcount == 0:  # No rows affected means insufficient balance
                            messages.error(request, "Saldo tidak cukup untuk transfer!")
                        else:
                            cursor.execute("""
                            UPDATE "user" 
                            SET saldomypay = saldomypay + %s 
                            WHERE nohp = %s;
                        """, [nominal, nohp_tujuan])
                            
                            cursor.execute("""
                                INSERT INTO TR_MYPAY (id, UserId, Tgl, Nominal, KategoriId) 
                                VALUES (%s, %s, %s, %s, (SELECT id from KATEGORI_TR_MYPAY WHERE nama = 'transfer'));
                        """, [str(uuid.uuid4()), user_id, datetime.now().strftime("%Y-%m-%d"), nominal])
                
                elif state == 'withdrawal':
                    nominal_list = request.POST.getlist('nominal')

                    if nominal_list and nominal_list[2].isdigit():
                        nominal = float(nominal_list[2])
                        cursor.execute("""
                            UPDATE "user" 
                            SET saldomypay = saldomypay - %s 
                            WHERE id = %s AND saldomypay >= %s;
                        """, [nominal, user_id, nominal])

                        if cursor.rowcount == 0:  # No rows affected means insufficient balance
                            messages.error(request, "Saldo tidak cukup untuk Withdrawal!")
                        else:                            
                            cursor.execute("""
                                INSERT INTO TR_MYPAY (id, UserId, Tgl, Nominal, KategoriId) 
                                VALUES (%s, %s, %s, %s, (SELECT id from KATEGORI_TR_MYPAY WHERE nama = 'withdraw'));
                        """, [str(uuid.uuid4()), user_id, datetime.now().strftime("%Y-%m-%d"), nominal])
                            
            connection.commit()
        except Exception as e:
            print(f"Error processing transaction: {e}")
            messages.error(request, "Terjadi kesalahan pada transaksi!")
        finally:
            connection.close()

    return redirect('transaction_view')

def mypay_dashboard(request):
    # Retrieve the logged-in user's ID from the session
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')  # Redirect to the login page if not logged in

    # Initialize variables
    user_phone = None
    user_balance = 0
    transactions = []

    # Connect to the database
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            # Query to get the user's phone number and balance
            cursor.execute("""
                SELECT nohp, saldomypay
                FROM "user" u  -- Replace 'user' with your actual table storing user info
                WHERE u.id = %s;
            """, [user_id])
            user_data = cursor.fetchone()
            
            if user_data:
                user_phone, user_balance = user_data  # Extract phone and balance

            # Query to get the user's transaction history
            cursor.execute("""
                SELECT trmp.nominal, trmp.tgl, ktrmp.nama 
                FROM TR_MYPAY trmp
                JOIN KATEGORI_TR_MYPAY ktrmp ON trmp.KategoriId = ktrmp.id
                WHERE trmp.UserId = %s
                ORDER BY trmp.tgl DESC, trmp.nominal;
            """, [user_id])
            transactions = cursor.fetchall()
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        connection.close()

    # Render the template with dynamic data
    context = {
        'user_phone': user_phone,
        'user_balance': user_balance,
        'transactions': transactions
    }
    return render(request, 'mypay.html', context)

def pekerjaan_dashboard(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    connection = get_db_connection()
    categories = []
    try:
        with connection.cursor() as cursor:
            # Fetch pekerja details
            cursor.execute("""SELECT * FROM PEKERJA WHERE id = %s;""", [user_id])
            pekerja = cursor.fetchone()
            if not pekerja:
                return redirect('login')

            # Fetch categories
            cursor.execute("""
                SELECT DISTINCT kj.Id, kj.namakategori
                FROM KATEGORI_JASA kj
                JOIN PEKERJA_KATEGORI_JASA pkj ON pkj.KategoriJasaId = kj.id
                WHERE pkj.pekerjaid = %s;
            """, [user_id])
            categories = cursor.fetchall()

    except Exception as e:
        print(f"Database error: {e}")
    finally:
        connection.close()

    context = {
        'categories': categories,
    }
    return render(request, 'pekerjaan_jasa.html', context)

def fetch_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = []
    connection = get_db_connection()
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, namasubkategori 
                FROM SUBKATEGORI_JASA 
                WHERE KategoriJasaId = %s;
            """, [category_id])
            subcategories = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching subcategories: {e}")
    finally:
        connection.close()
    
    return JsonResponse({'subcategories': subcategories})

def fetch_orders(request):
    subcategory_id = request.GET.get('subcategory_id')
    orders = []
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            if subcategory_id:
                cursor.execute("""
                    SELECT tpj.id, u.nama, sj.namasubkategori, tpj.tglpemesanan, tpj.sesi, tpj.totalbiaya
                    FROM TR_PEMESANAN_JASA tpj
                    JOIN SUBKATEGORI_JASA sj ON tpj.idkategorijasa = sj.id
                    JOIN TR_PEMESANAN_STATUS tps ON tps.IdTrPemesanan = tpj.id
                    JOIN STATUS_PESANAN sp ON sp.Id = tps.IdStatus
                    JOIN "user" u ON u.id = tpj.idpelanggan
                    WHERE sp.status = 'Mencari Pekerja Terdekat' AND sj.id = %s
                """, [subcategory_id])
                rows = cursor.fetchall()

                # Format the results into a list of dictionaries
                for row in rows:
                    order = {
                        'id': row[0],
                        'nama': row[1],
                        'namasubkategori': row[2],
                        'tglpemesanan': row[3],
                        'sesi': row[4],
                        'biaya': row[5]
                    }
                    orders.append(order)
        print(orders)  # Make sure this prints correctly
    except Exception as e:
        print(f"Error fetching orders: {e}")
    finally:
        connection.close()

    return JsonResponse({'orders': orders})  # Ensure this returns the correct structure

def change_status(request):
    if request.method == 'POST':  # Ensure only POST requests are handled
        # print("View reached!")  # Debugging

        user_id = request.session.get('user_id')
        id_tpj = request.POST.get('id_tpj')  # Changed to POST
        # print("User ID:", user_id, "Order ID:", id_tpj)  # Debugging

        connection = get_db_connection()
        try:
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE tr_pemesanan_jasa tpj
                SET idpekerja = %s, tglpekerjaan = %s
                WHERE tpj.id = %s;
            """, [user_id, datetime.now().strftime("%Y-%m-%d"), id_tpj])

            cursor.execute("""
                UPDATE tr_pemesanan_status tps
                SET idstatus = (SELECT id FROM STATUS_PESANAN WHERE status = 'Menunggu Pekerja Berangkat' LIMIT 1)
                WHERE tps.idtrpemesanan = %s;
            """, [id_tpj])

            connection.commit()
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'status': 'error', 'message': 'Database error'}, status=500)
        finally:
            connection.close()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

def status_pekerjaan_dashboard(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    categories = []
    status = []
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM PEKERJA WHERE id = %s;""", [user_id])
            pekerja = cursor.fetchone()
            if not pekerja:
                return redirect('login')

            # Fetch categories
            cursor.execute("""
                SELECT DISTINCT kj.Id, kj.namakategori
                FROM KATEGORI_JASA kj
                JOIN PEKERJA_KATEGORI_JASA pkj ON pkj.KategoriJasaId = kj.id
                WHERE pkj.pekerjaid = %s;
            """, [user_id])
            categories = cursor.fetchall()

            cursor.execute("""
                SELECT id, status
                FROM STATUS_PESANAN
                WHERE status <> 'Mencari Pekerja Terdekat';
            """, [user_id])
            status = cursor.fetchall()

    except Exception as e:
        print(f"Database error: {e}")
    finally:
        connection.close()

    print(categories)
    print(status)
    context = {
        'categories': categories,
        'status': status,
    }

    return render(request, 'status_pekerjaan.html', context)

def fetch_status_order(request):
    category_id = request.GET.get('category_id')
    status_id = request.GET.get('status_id')
    user_id = request.session.get('user_id')
    orders = []
    connection = get_db_connection()
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                    SELECT tpj.id, u.nama, sj.namasubkategori, tpj.tglpemesanan, tpj.sesi, tpj.totalbiaya, sp.status
                    FROM TR_PEMESANAN_JASA tpj
                    JOIN SUBKATEGORI_JASA sj ON tpj.idkategorijasa = sj.id
                    JOIN TR_PEMESANAN_STATUS tps ON tps.IdTrPemesanan = tpj.id
                    JOIN STATUS_PESANAN sp ON sp.Id = tps.IdStatus
                    JOIN "user" u ON u.id = tpj.idpelanggan
                    WHERE tps.idstatus = %s AND sj.kategorijasaid = %s AND tpj.idpekerja = %s;
                """, [status_id, category_id, user_id])
            rows = cursor.fetchall()

            # Format the results into a list of dictionaries
            for row in rows:
                order = {
                    'id': row[0],
                    'nama': row[1],
                    'namasubkategori': row[2],
                    'tglpemesanan': row[3],
                    'sesi': row[4],
                    'biaya': row[5],
                    'status': row[6]
                }
                orders.append(order)
    except Exception as e:
        print(f"Error fetching subcategories: {e}")
    finally:
        connection.close()
    
    return JsonResponse({'orders': orders})

from django.http import JsonResponse
import json

def update_status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            status_id = request.GET.get('status_id')
            next_status = ''

            connection = get_db_connection()
            try:
                with connection.cursor() as cursor:
                    # Fetch the current status of the order
                    cursor.execute("""
                        SELECT sp.status
                        FROM STATUS_PESANAN sp
                        JOIN TR_PEMESANAN_STATUS ON tps.IdStatus = sp.id
                        WHERE tps.IdTrPemesanan = %s;
                    """, [order_id])
                    result = cursor.fetchone()

                    if result == 'Menunggu Pekerja Berangkat':
                        next_status = 'Pekerja Tiba Di Lokasi'

                    elif result == 'Pekerja Tiba Di Lokasi':
                        next_status = 'Pelayanan Jasa Sedang Dilakukan'

                    elif result == 'Pelayanan Jasa Sedang Dilakukan':
                        next_status = 'Pesanan Selesai'

                    cursor.execute("""
                        SELECT sp.id
                        FROM STATUS_PESANAN
                        WHERE status = %s;
                    """, [next_status])
                    new_status_id = cursor.fetchone()

                    # Update the order's status
                    cursor.execute("""
                        UPDATE TR_PEMESANAN_STATUS
                        SET IdStatus = %s
                        WHERE IdTrPemesanan = %s;
                    """, [new_status_id, order_id])
                    connection.commit()

            finally:
                connection.close()

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})
