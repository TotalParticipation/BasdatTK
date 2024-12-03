# views.py
from utils.db_utils import get_db_connection
from .helpers import process_topup, process_service_payment, process_transfer, process_withdrawal
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import TransactionForm
from datetime import datetime

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
                               SELECT sj.namasubkategori, tpj.totalbiaya
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
                    nominal = float(request.POST.get('nominal', 0))
                    cursor.execute("""
                        UPDATE "user" 
                        SET saldomypay = saldomypay + %s 
                        WHERE id = %s;
                    """, [nominal, user_id])
                    messages.success(request, "TopUp berhasil ditambahkan!")

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
                ORDER BY trmp.tgl DESC;
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
    return render(request, 'pekerjaan_jasa.html')

def status_pekerjaan_dashboard(request):
    return render(request, 'status_pekerjaan.html')

