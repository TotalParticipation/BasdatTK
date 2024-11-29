from django.shortcuts import render
import psycopg2
from utils.db_utils import get_db_connection
from django.http import HttpResponse
from django.contrib import messages 
from django.contrib.auth import logout
import uuid
# Create your views here.
#show login
from django.shortcuts import redirect
from django.shortcuts import render, redirect

# def printTables():
#     connection = get_db_connection()

#     with connection.cursor() as cursor:
#         # Execute the equivalent of \dt
#         cursor.execute("""
#             SELECT table_name
#             FROM information_schema.tables
#             WHERE table_schema = 'public';
#         """)
#         rows = cursor.fetchall()
    
#     # Print the result
#     print("Tables in the database:")
#     for row in rows:
#         print(row[0])
# printTables()

def login_view(request):
    connection = get_db_connection()
    if request.method == "POST":
        # Get the username/email and password from the form
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use raw SQL to query the user by username
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, nama, pwd FROM "user" WHERE nama = %s
            """, [username])
            user = cursor.fetchone()

        if user:
            # user[0] is the user ID, user[1] is the name, user[2] is the stored password
            user_id, user_name, stored_password = user

            # Compare the entered password with the stored password (plain text comparison)
            if password == stored_password:
                # If passwords match, proceed to check if the user is Pelanggan or Pekerja
                request.session['user_id'] = str(user_id)  # Store user ID in the session
                request.session['username'] = user_name  # Store username in the session

                with connection.cursor() as cursor:
                    # Check if the user is a "Pelanggan"
                    cursor.execute("""
                        SELECT * FROM pelanggan WHERE id = %s
                    """, [user_id])
                    pelanggan = cursor.fetchone()

                    if pelanggan:
                        # If the user is a Pelanggan, redirect to their profile
                        
                        return redirect("profile_pelanggan")

                    # Check if the user is a "Pekerja"
                    cursor.execute("""
                        SELECT * FROM pekerja WHERE id = %s
                    """, [user_id])
                    pekerja = cursor.fetchone()

                    if pekerja:
                        # If the user is a Pekerja, redirect to their profile
                       
                        return redirect("profile_pekerja")

                # If neither, you can show an error or redirect to a default page
                return  # Default redirect if user is neither Pelanggan nor Pekerja

            else:
                # If passwords don't match
                error_message = "Invalid password"
                return render(request, "login.html", {"error": error_message})

        else:
            # If no user found
            error_message = "User not found"
            return render(request, "login.html", {"error": error_message})

    return render(request, "login.html")


def view_profile_pelanggan(request):
    connection = get_db_connection()
    # Check if the user is logged in (assuming you are storing user ID in the session)
    user_id = request.session.get('user_id')  # Get the user ID from session, adjust if necessary
    print(f"user id = {user_id}")
    if not user_id:
        return redirect('login')  # Redirect to login if the user is not logged in
        # Redirect to avoid resubmitting the form on refresh
    # Fetch user data from Pelanggan table
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT u.id, nama, jeniskelamin, nohp, tgllahir, alamat, saldomypay, p.level
        FROM "user" u
        JOIN "pelanggan" p ON u.id = p.id
        WHERE u.id = %s
        """, [user_id])
        pelanggan = cursor.fetchone()

    if pelanggan:
        # Create a dictionary to pass to the template
        context = {
            'id': pelanggan[0],
            'nama': pelanggan[1],
            'jeniskelamin': pelanggan[2],
            'nohp': pelanggan[3],
            'tgllahir': pelanggan[4],
            'alamat': pelanggan[5],
            'saldomypay': pelanggan[6],
            'level' : pelanggan[7]
        }
        if request.method == 'POST':
            print(f"Updating ID: {user_id}")

            updated_nama = request.POST.get('nama')
            updated_jenis_kelamin = request.POST.get('jenis_kelamin')
            updated_nohp = request.POST.get('nohp')
            updated_tanggal_lahir = request.POST.get('tanggal_lahir')
            updated_alamat = request.POST.get('alamat')
            if not updated_nama or not updated_jenis_kelamin or not updated_nohp or not updated_tanggal_lahir or not updated_alamat:
                print("field kosong")
                # Add a red warning message if a field is missing
                messages.error(request, "All fields are required. Please fill in all fields.")
                return render(request, "profile_pelanggan.html",context)
            else:
                print(f"executing: {updated_nama},{updated_jenis_kelamin},{updated_alamat},{updated_nohp},{updated_tanggal_lahir}")
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            UPDATE "user"
                            SET nama = %s, jeniskelamin = %s, nohp = %s, tgllahir = %s, alamat = %s
                            WHERE id = %s
                            """, [updated_nama, updated_jenis_kelamin, updated_nohp, updated_tanggal_lahir, updated_alamat, user_id]
                        )
                    connection.commit()  # Commit the transaction to save changes permanently
                    return redirect('profile_pelanggan')
                
                except psycopg2.errors.UniqueViolation as e:  # Handle the exception and give a user-friendly message

                    error_message = "Nomor HP sudah terdaftar. Silakan coba nomor lain. Mohon refresh page anda"
                    return render(request, "profile_pelanggan.html", {'error': error_message})
                

                except Exception as e:# Catch other exceptions

                    error_message = f"Terjadi kesalahan: {str(e)} Mohon refresh page anda"
                    return render(request, "profile_pelanggan.html", {'error': error_message})
                
        return render(request, "profile_pelanggan.html", context)


def view_profile_pekerja(request):
    connection = get_db_connection()
    # Check if the user is logged in (assuming you are storing user ID in the session)
    user_id = request.session.get('user_id')  # Get the user ID from session, adjust if necessary
    print(f"user id = {user_id}")
    if not user_id:
        return redirect('login')  # Redirect to login if the user is not logged in
    
    # Fetch user data from Pekerja table
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT u.id, nama, jeniskelamin, nohp, tgllahir, alamat, saldomypay, p.namabank, p.nomorrekening, p.npwp, p.linkfoto, p.rating, p.jmlpsnananselesai
        FROM "user" u
        JOIN "pekerja" p ON u.id = p.id
        WHERE u.id = %s
        """, [user_id])
        pekerja = cursor.fetchone()

    with connection.cursor() as cursor:

        cursor.execute( """
        SELECT kj.namakategori
        FROM kategori_jasa kj
        JOIN pekerja_kategori_jasa pkj ON kj.id = pkj.kategorijasaid
        WHERE pkj.pekerjaid = %s;
        """, [user_id])
        categories = [row[0] for row in cursor.fetchall()] 
  
    if pekerja:
        # Create a dictionary to pass to the template
        context = {
            'id': pekerja[0],
            'nama': pekerja[1],
            'jeniskelamin': pekerja[2],
            'nohp': pekerja[3],
            'tgllahir': pekerja[4],
            'alamat': pekerja[5],
            'saldomypay': pekerja[6],
            'namabank' : pekerja[7],
            'noRekening': pekerja[8],
            'npwp': pekerja[9],
            'linkfoto':pekerja[10],
            'rating':pekerja[11],
            'jmlpsnananselesai': pekerja[12],
            'categories' : categories
        }
        if request.method == 'POST':
            print(f"Updating ID: {user_id}")

            updated_nama = request.POST.get('nama')
            updated_jenis_kelamin = request.POST.get('jenis_kelamin')
            updated_nohp = request.POST.get('nohp')
            updated_tanggal_lahir = request.POST.get('tanggal_lahir')
            updated_alamat = request.POST.get('alamat')
            updated_nama_bank = request.POST.get('nama_bank')
            updated_no_rekening = request.POST.get('no_rekening')
            updated_npwp = request.POST.get('npwp')
            updated_url_foto = request.POST.get('url_foto')
            if not updated_nama or not updated_jenis_kelamin or not updated_nohp or not updated_tanggal_lahir or not updated_alamat:
                print("field kosong")
                # Add a red warning message if a field is missing
                messages.error(request, "All fields are required. Please fill in all fields.")
                return render(request, "profile_pekerja.html",context)
            else:
                print(f"executing: {updated_nama},{updated_jenis_kelamin},{updated_alamat},{updated_nohp},{updated_tanggal_lahir}")
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            UPDATE "user"
                            SET nama = %s, jeniskelamin = %s, nohp = %s, tgllahir = %s, alamat = %s
                            WHERE id = %s
                            """, [updated_nama, updated_jenis_kelamin, updated_nohp, updated_tanggal_lahir, updated_alamat, user_id]
                        )

                    with connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE pekerja
                                SET namabank = %s,
                                nomorrekening = %s,
                                npwp = %s,
                                linkfoto = %s
                                WHERE id = %s
                            """, [updated_nama_bank, updated_no_rekening, updated_npwp, updated_url_foto, user_id]
                        )
                    connection.commit()  # Commit the transaction to save changes permanently
                    print("pekerja successfully altered")
                    return redirect('profile_pekerja')
                
                except psycopg2.errors.UniqueViolation as e:  # Handle the exception and give a user-friendly message

                    error_message = "Nomor HP sudah terdaftar. Silakan coba nomor lain. Mohon refresh page anda"
                    print(error_message)
                    return render(request, "profile_pekerja.html", {'error': error_message})
                

                except Exception as e:# Catch other exceptions

                    error_message = f"Terjadi kesalahan: {str(e)} Mohon refresh page anda"
                    print(error_message)
                    return render(request, "profile_pekerja.html", {'error': error_message})
        return render(request, "profile_pekerja.html", context)

def logout_view(request):
    logout(request)  # Logs out the user
    return redirect('login')  # Redirect to the login page (or any other page)


def view_register_pekerja(request):
    connection = get_db_connection()
    if request.method == 'POST':
            updated_nama = request.POST.get('nama')
            updated_password = request.POST.get('password')
            updated_jenis_kelamin = request.POST.get('jenis_kelamin')
            updated_nohp = request.POST.get('nohp')
            updated_tanggal_lahir = request.POST.get('tanggal_lahir')
            updated_alamat = request.POST.get('alamat')
            updated_nama_bank = request.POST.get('nama_bank')
            updated_no_rekening = request.POST.get('no_rekening')
            updated_npwp = request.POST.get('npwp')
            updated_url_foto = request.POST.get('url_foto')
            new_user_id = uuid.uuid4()
            if not updated_nama or not updated_jenis_kelamin or not updated_nohp or not updated_tanggal_lahir or not updated_alamat:
                print("field kosong")
                # Add a red warning message if a field is missing
                messages.error(request, "All fields are required. Please fill in all fields.")
                return redirect("register_pekerja")
            else:
                print(f"executing: {updated_nama},{updated_jenis_kelamin},{updated_alamat},{updated_nohp},{updated_tanggal_lahir}")
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(
                        """
                        INSERT INTO "user" (id, nama, pwd, jeniskelamin, nohp, tgllahir, alamat)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, [new_user_id, updated_nama, updated_password, updated_jenis_kelamin, updated_nohp, updated_tanggal_lahir, updated_alamat]
                        )
                        
                    with connection.cursor() as cursor:
                        cursor.execute(
                        """
                        INSERT INTO pekerja (id, namabank, nomorrekening, npwp, linkfoto)
                        VALUES (%s, %s, %s, %s, %s)
                        """, [new_user_id, updated_nama_bank, updated_no_rekening, updated_npwp, updated_url_foto]
                        )
                    connection.commit()  # Commit the transaction to save changes permanently
                    print("pekerja successfully created")
                    return redirect('login')
                
                except psycopg2.errors.UniqueViolation as e:  # Handle the exception and give a user-friendly message

                    error_message = "Nomor HP sudah terdaftar. Silakan coba nomor lain. Mohon refresh page anda"
                    print(error_message)
                    return redirect("register_pekerja")
                

                except Exception as e:# Catch other exceptions

                    error_message = f"Terjadi kesalahan: {str(e)} Mohon refresh page anda"
                    print(error_message)
                    return redirect("register_pekerja")
    return render(request, "register_pekerja.html")


def view_register_pelanggan(request):
    connection = get_db_connection()
    if request.method == 'POST':
            updated_nama = request.POST.get('nama')
            updated_password = request.POST.get('password')
            updated_jenis_kelamin = request.POST.get('jenis_kelamin')
            updated_nohp = request.POST.get('nohp')
            updated_tanggal_lahir = request.POST.get('tanggal_lahir')
            updated_alamat = request.POST.get('alamat')
            new_user_id = uuid.uuid4()
            if not updated_nama or not updated_jenis_kelamin or not updated_nohp or not updated_tanggal_lahir or not updated_alamat:
                print("field kosong")
                # Add a red warning message if a field is missing
                messages.error(request, "All fields are required. Please fill in all fields.")
                return redirect("register_pelanggan")
            else:
                print(f"executing: {updated_nama},{updated_jenis_kelamin},{updated_alamat},{updated_nohp},{updated_tanggal_lahir}")
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(
                        """
                        INSERT INTO "user" (id, nama, pwd, jeniskelamin, nohp, tgllahir, alamat)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, [new_user_id, updated_nama, updated_password, updated_jenis_kelamin, updated_nohp, updated_tanggal_lahir, updated_alamat]
                        )

                        
                        cursor.execute(
                        """
                        INSERT INTO pelanggan (id, level)
                        VALUES (%s, %s)
                        """, [new_user_id,"basic"]
                        )
                    connection.commit()  # Commit the transaction to save changes permanently
                    print("pelanggan successfully created")
                    return redirect('login')
                
                except psycopg2.errors.UniqueViolation as e:  # Handle the exception and give a user-friendly message

                    error_message = "Nomor HP sudah terdaftar. Silakan coba nomor lain. Mohon refresh page anda"
                    print(error_message)
                    return redirect("register_pelanggan")
                

                except Exception as e:# Catch other exceptions

                    error_message = f"Terjadi kesalahan: {str(e)} Mohon refresh page anda"
                    print(error_message)
                    return redirect("register_pelanggan")
    return render(request, "register_pelanggan.html")

# Call the function



