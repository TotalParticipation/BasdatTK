# views.py
import psycopg2
import uuid
import json
from utils.db_utils import get_db_connection
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse

# from .models import Subcategory, ServiceSession, Worker, Testimonial


def homepage(request):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Get the user ID from the session
        user_id = request.session.get("user_id")
        if not user_id:
            role = "guest"
        else:
            # Determine the user's role from the database
            cursor.execute("""
                SELECT CASE 
                    WHEN EXISTS (SELECT 1 FROM pekerja WHERE id = %s) THEN 'pekerja'
                    WHEN EXISTS (SELECT 1 FROM pelanggan WHERE id = %s) THEN 'pelanggan'
                    ELSE 'guest'
                END AS role
            """, [user_id, user_id])
            role_result = cursor.fetchone()
            role = role_result[0] if role_result else "guest"

        # Print the determined role for debugging
        print(f"Determined Role: {role}")
               
        
        connection = get_db_connection()
        cursor = connection.cursor()

    
        # Fetch categories and subcategories
        cursor.execute(
            """
            SELECT kj.Id, kj.NamaKategori, sj.Id, sj.NamaSubkategori
            FROM KATEGORI_JASA kj
            LEFT JOIN SUBKATEGORI_JASA sj ON kj.Id = sj.KategoriJasaId
            ORDER BY kj.Id, sj.Id
        """
        )
        data = cursor.fetchall()

        # Structure data for template
        categories = []
        category_map = {}

        for category_id, category_name, subcategory_id, subcategory_name in data:
            if category_id not in category_map:
                category = {
                    "id": category_id,
                    "name": category_name,
                    "subcategories": [],
                }
                categories.append(category)
                category_map[category_id] = category

            if subcategory_id:
                category_map[category_id]["subcategories"].append(
                    {"id": subcategory_id, "name": subcategory_name}
                )

        return render(
            request, "homepage.html", {"categories": categories, "role": role}
        )
    except Exception as e:
        return render(request, "homepage.html", {"error": str(e)})
    finally:
        cursor.close()
        connection.close()


def subcategory_worker(request):
    subcategory_id = request.GET.get(
        "subcategory_id"
    )  # Assuming `subcategory_id` is passed as a query parameter

    if not subcategory_id:
        return JsonResponse({"error": "subcategory_id is required"}, status=400)

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Fetch the subcategory details
        cursor.execute("SELECT * FROM SUBKATEGORI_JASA WHERE id = %s", [subcategory_id])
        subcategory = cursor.fetchone()

        # Fetch the sessions related to this subcategory
        cursor.execute(
            "SELECT * FROM SESI_LAYANAN WHERE SubkategoriId = %s", [subcategory_id]
        )
        sessions = cursor.fetchall()

        # Fetch all workers
        cursor.execute("SELECT * FROM PEKERJA")
        workers = cursor.fetchall()

        # Fetch testimonials for the workers
        worker_ids = [
            worker[0] for worker in workers
        ]  # Assuming `id` is the first column
        if worker_ids:
            cursor.execute(
                "SELECT * FROM TESTIMONI WHERE IdTrPemesanan IN (SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPekerja = ANY(%s))",
                [worker_ids],
            )
            testimonials = cursor.fetchall()
        else:
            testimonials = []

        # Prepare the context
        context = {
            "subcategory": (
                {
                    "id": subcategory[0],
                    "name": subcategory[1],
                    "description": subcategory[2],
                }
                if subcategory
                else None
            ),
            "sessions": [
                {"SubkategoriId": row[0], "Sesi": row[1], "Harga": row[2]}
                for row in sessions
            ],
            "workers": [
                {"id": row[0], "NamaBank": row[1], "NomorRekening": row[2]}
                for row in workers
            ],
            "testimonials": [
                {
                    "IdTrPemesanan": row[0],
                    "Tgl": row[1],
                    "Teks": row[2],
                    "Rating": row[3],
                }
                for row in testimonials
            ],
            "is_worker": True,
        }

        return JsonResponse(context, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    finally:
        cursor.close()
        connection.close()


def subcategory_user(request):
    subcategory_id = request.GET.get(
        "subcategory_id"
    )  # Assuming subcategory_id is passed as a query parameter

    if not subcategory_id:
        return JsonResponse({"error": "subcategory_id is required"}, status=400)

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Fetch the subcategory details
        cursor.execute("SELECT * FROM SUBKATEGORI_JASA WHERE id = %s", [subcategory_id])
        subcategory = cursor.fetchone()

        # Fetch sessions related to this subcategory
        cursor.execute(
            "SELECT * FROM SESI_LAYANAN WHERE SubkategoriId = %s", [subcategory_id]
        )
        sessions = cursor.fetchall()

        # Fetch all workers
        cursor.execute("SELECT * FROM PEKERJA")
        workers = cursor.fetchall()

        # Fetch testimonials for the workers
        worker_ids = [
            worker[0] for worker in workers
        ]  # Assuming `id` is the first column
        if worker_ids:
            cursor.execute(
                "SELECT * FROM TESTIMONI WHERE IdTrPemesanan IN (SELECT Id FROM TR_PEMESANAN_JASA WHERE IdPekerja = ANY(%s))",
                [worker_ids],
            )
            testimonials = cursor.fetchall()
        else:
            testimonials = []

        # Prepare the context
        context = {
            "subcategory": (
                {
                    "id": subcategory[0],
                    "name": subcategory[1],
                    "description": subcategory[2],
                }
                if subcategory
                else None
            ),
            "sessions": [
                {"SubkategoriId": row[0], "Sesi": row[1], "Harga": row[2]}
                for row in sessions
            ],
            "workers": [
                {"id": row[0], "NamaBank": row[1], "NomorRekening": row[2]}
                for row in workers
            ],
            "testimonials": [
                {
                    "IdTrPemesanan": row[0],
                    "Tgl": row[1],
                    "Teks": row[2],
                    "Rating": row[3],
                }
                for row in testimonials
            ],
            "is_worker": False,
        }

        return JsonResponse(context, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    finally:
        cursor.close()
        connection.close()


def get_categories_and_subcategories(request):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Fetch categories and subcategories
        cursor.execute(
            """
SELECT kj.Id AS category_id, kj.NamaKategori AS category_name, 
       sj.Id AS subcategory_id, sj.NamaSubkategori AS subcategory_name
FROM KATEGORI_JASA kj
LEFT JOIN SUBKATEGORI_JASA sj ON kj.Id = sj.KategoriJasaId
ORDER BY kj.Id, sj.Id;
        """
        )
        data = cursor.fetchall()

        # Format the response
        categories = {}
        for category_id, category_name, subcategory_id, subcategory_name in data:
            str_category_id = str(category_id)  # Convert UUID to string
            if str_category_id not in categories:
                categories[str_category_id] = {
                    "name": category_name,
                    "subcategories": [],
                }
            if subcategory_id:
                categories[str_category_id]["subcategories"].append(
                    {
                        "id": str(subcategory_id),  # Convert UUID to string
                        "name": subcategory_name,
                    }
                )

        return JsonResponse({"categories": categories}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    finally:
        cursor.close()
        connection.close()


def create_order(request):
    if request.method == "POST":
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # Extract data from the POST request
            user_id = request.session.get("user_id")
            subcategory_id = request.POST.get("subcategory_id")
            sesi = request.POST.get("sesi")
            tanggal_pemesanan = request.POST.get("tanggal_pemesanan")
            diskon = request.POST.get("diskon")

            # Fetch the payment method ID for "MyPay"
            cursor.execute(
                """
                SELECT id FROM metode_bayar WHERE nama = 'MyPay'
            """
            )
            metode_bayar_result = cursor.fetchone()

            if not metode_bayar_result:
                return JsonResponse(
                    {"error": "Payment method 'MyPay' not found"}, status=500
                )

            metode_bayar = metode_bayar_result[0]

            # Validate required fields
            if not user_id or not subcategory_id or not sesi or not tanggal_pemesanan:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Calculate total biaya (dummy logic for now)
            cursor.execute(
                """
                SELECT harga FROM sesi_layanan
                WHERE subkategoriid = %s AND sesi = %s
            """,
                [subcategory_id, sesi],
            )
            result = cursor.fetchone()

            if not result:
                return JsonResponse(
                    {"error": "Invalid subkategoriid or sesi"}, status=400
                )

            total_biaya = result[0]  # Harga from sesi_layanan

            # Apply discount if provided
            if diskon:
                cursor.execute(
                    """
                    SELECT potongan FROM diskon WHERE kode = %s
                """,
                    [diskon],
                )
                discount_result = cursor.fetchone()
                if discount_result:
                    total_biaya -= discount_result[0]

            # Insert into tr_pemesanan_jasa
            cursor.execute(
                """
                INSERT INTO tr_pemesanan_jasa (
                    id, tglpemesanan, tglpekerjaan, waktupekerjaan, totalbiaya,
                    idpelanggan, idkategorijasa, sesi, iddiskon, idmetodebayar
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                [
                    str(uuid.uuid4()),  # Generate a new UUID for the order
                    tanggal_pemesanan,
                    tanggal_pemesanan,  # Assuming tglpekerjaan is the same for now
                    f"{tanggal_pemesanan} 10:00:00",  # Dummy time for waktupekerjaan
                    total_biaya,
                    user_id,
                    subcategory_id,
                    sesi,
                    diskon if diskon else None,
                    metode_bayar,  # Dynamically fetched from the database
                ],
            )

            connection.commit()

            return redirect(reverse("homepage"))
        except Exception as e:
            print(f"Error creating order: {e}")
            return JsonResponse({"error": str(e)}, status=500)

        finally:
            cursor.close()
            connection.close()
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


def view_orders(request):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        user_id = request.session.get("user_id")  # Get logged-in user ID

        # Fetch all orders for the user
        cursor.execute(
            """
            SELECT 
                TPJ.Id, KJ.NamaKategori, SL.Sesi, TPJ.TotalBiaya, TPJ.Status,
                COALESCE(P.NamaBank, '-') AS NamaPekerja
            FROM TR_PEMESANAN_JASA TPJ
            LEFT JOIN KATEGORI_JASA KJ ON TPJ.IdKategoriJasa = KJ.Id
            LEFT JOIN PEKERJA P ON TPJ.IdPekerja = P.Id
            LEFT JOIN SESI_LAYANAN SL ON TPJ.Sesi = SL.Sesi
            WHERE TPJ.IdPelanggan = %s
        """,
            [user_id],
        )
        orders = cursor.fetchall()

        # Prepare data for the template
        orders_data = []
        for order in orders:
            order_data = {
                "id": order[0],
                "subkategori": order[1],
                "sesi": order[2],
                "harga": order[3],
                "status": order[4],
                "nama_pekerja": order[5],
                "button": None,
            }

            # Determine button actions based on status
            if order[4] in ["Menunggu Pembayaran", "Mencari Pekerja Terdekat"]:
                order_data["button"] = "Batalkan"
            elif order[4] == "Pesanan Selesai":
                # Check if a testimonial exists
                cursor.execute(
                    "SELECT 1 FROM TESTIMONI WHERE IdTrPemesanan = %s", [order[0]]
                )
                has_testimonial = cursor.fetchone()
                if not has_testimonial:
                    order_data["button"] = "Buat Testimoni"

            orders_data.append(order_data)

        return render(request, "order.html", {"orders": orders_data})

    except Exception as e:
        print(f"Error fetching orders: {e}")
        return JsonResponse({"error": str(e)}, status=500)
    finally:
        cursor.close()
        connection.close()


def subcategory_detail(request, subcategory_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Fetch subcategory details
        cursor.execute("""
            SELECT id, namasubkategori, deskripsi
            FROM subkategori_jasa
            WHERE id = %s
        """, [subcategory_id])
        subcategory = cursor.fetchone()

        if not subcategory:
            return render(request, "error.html", {"message": "Subcategory not found"})

        # Get user ID and determine role
        user_id = request.session.get("user_id")
        if not user_id:
            user_role = "guest"
            is_joined = False
        else:
            # Check role
            cursor.execute("""
                SELECT 'pekerja' AS role
                FROM pekerja
                WHERE id = %s
                UNION
                SELECT 'pelanggan' AS role
                FROM pelanggan
                WHERE id = %s
            """, [user_id, user_id])
            role_result = cursor.fetchone()
            user_role = role_result[0] if role_result else "guest"

            # Check if pekerja is already joined
            is_joined = False
            if user_role == "pekerja":
                cursor.execute("""
                    SELECT 1
                    FROM pekerja_kategori_jasa
                    WHERE pekerjaid = %s AND kategorijasaid = %s
                """, [user_id, subcategory_id])
                is_joined = cursor.fetchone() is not None

        # Fetch workers related to the subcategory
        cursor.execute("""
            SELECT pekerja.id, pekerja.namabank, pekerja.nomorrekening, pekerja.npwp, pekerja.rating
            FROM pekerja
            JOIN pekerja_kategori_jasa pkj ON pekerja.id = pkj.pekerjaid
            WHERE pkj.kategorijasaid = %s
        """, [subcategory_id])
        workers = cursor.fetchall()

        # Fetch sessions related to the subcategory
        cursor.execute("""
            SELECT subkategoriid, sesi, harga
            FROM sesi_layanan
            WHERE subkategoriid = %s
        """, [subcategory_id])
        sessions = cursor.fetchall()

        # Prepare context
        context = {
            "subcategory": {
                "id": subcategory[0],
                "name": subcategory[1],
                "description": subcategory[2],
            },
            "workers": [
                {
                    "id": worker[0],
                    "namabank": worker[1],
                    "nomorrekening": worker[2],
                    "npwp": worker[3],
                    "rating": worker[4],
                }
                for worker in workers
            ],
            "sessions": [
                {
                    "sesi": session[1],
                    "harga": session[2],
                }
                for session in sessions
            ],
            "user_role": user_role,
            "is_joined": is_joined,
        }

        return render(request, "subcategory_detail.html", context)

    finally:
        cursor.close()
        connection.close()



def join_category(request):
    if request.method == "POST":
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            user_id = request.session.get("user_id")
            data = json.loads(request.body)
            subcategory_id = data.get("subcategory_id")

            # Ensure the user is a worker
            cursor.execute("""
                SELECT 1 FROM pekerja WHERE id = %s
            """, [user_id])
            if cursor.fetchone() is None:
                return JsonResponse({"success": False, "message": "User is not a worker."}, status=403)

            # Check if already joined
            cursor.execute("""
                SELECT 1
                FROM pekerja_kategori_jasa
                WHERE pekerjaid = %s AND kategorijasaid = %s
            """, [user_id, subcategory_id])
            if cursor.fetchone():
                return JsonResponse({"success": False, "message": "Already joined this category."}, status=400)

            # Insert into pekerja_kategori_jasa
            cursor.execute("""
                INSERT INTO pekerja_kategori_jasa (pekerjaid, kategorijasaid)
                VALUES (%s, %s)
            """, [user_id, subcategory_id])
            connection.commit()

            return JsonResponse({"success": True})

        except Exception as e:
            print(f"Error joining category: {e}")
            return JsonResponse({"success": False, "message": "An error occurred."}, status=500)

        finally:
            cursor.close()
            connection.close()

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)
