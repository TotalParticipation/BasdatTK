*GUIDE CONNECT DATABESE PSQL LOCAL*

# pertama nyalain virtual env dulu
jalankan di terminal
***env\scripts\activate**

# kedua bikin file bernama .env
dan isikan dalamnya sesuai di png contoh_env
    DB_NAME=tugaskelompok1
    DB_USER=postgres
    DB_PASSWORD=passwordxxx
    DB_HOST=localhost
    DB_PORT=5432
    SECRET_KEY=my-django-secret-key
    DEBUG=True
    TEST_VAR=HelloWorld

sesuaikan ama Nama DB lu, kalo gw pilih db dengan nama tugas kelompok1(pake db yg dari tugas kemaren yg udh lengkap)
user postgres gw juga default jadinya postgres 
password gw passwordxxx (password yg sama buat masuk terminal)
bisa dilihat di image dbpqg4

# step 3 make migrations 
jalankan di terminal
**python manage.py makemigrations**
**python manage.py migrate**

setelah di run harusnya 
<!-- 
django_migrations
django_content_type
auth_permission
auth_group
auth_group_permissions
auth_user_groups
auth_user_user_permissions
django_admin_log
auth_user
django_session
System check identified no issues (0 silenced). -->

akan muncul di terminal

# step 4 check kalo udh konek
bikin views baru
tambahin kode 

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

pastikan urls,py udh bener dan apps.py udh bener
saat lu masuk ke urls itu
<!-- 
Tables in the database:
kategori_tr_mypay
sesi_layanan
pekerja
metode_bayar
pekerja_kategori_jasa
diskon
tr_pemesanan_jasa
testimoni
pelanggan
status_pesanan
tr_mypay
kategori_jasa
subkategori_jasa
promo
tr_pembelian_voucher
tr_pemesanan_status
voucher
user
django_migrations
django_content_type
auth_permission
auth_group
auth_group_permissions
auth_user_groups
auth_user_user_permissions
django_admin_log
auth_user
django_session
System check identified no issues (0 silenced).
November 27, 2024 - 16:52:38
Django version 5.1.3, using settings 'TK_BASDAT.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK. -->

kalau sudah seperti ini maka lu sudah successfully konek ke database 
sisanya belajar sendiri