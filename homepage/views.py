# views.py
import psycopg2
import uuid
from utils.db_utils import get_db_connection
from django.shortcuts import render, redirect
from django.http import JsonResponse

# from .models import Subcategory, ServiceSession, Worker, Testimonial


def homepage(request):
    try:
        user_role = request.user.role if hasattr(request.user, "role") else "guest"
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
            request, "homepage.html", {"categories": categories, "user_role": user_role}
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


def order(request):
    return render(
        request, "order.html"
    )  # Change path if you use project-level templates


def subcategory_detail(request, subcategory_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Retrieve user ID from session
        user_id = request.session.get("user_id")  # Ensure this key is set during login
        print(f"User ID from session: {user_id}")
        if not user_id:
            print("User not logged in. Redirecting to login.")
            return redirect("login")  # Redirect to login if user_id is not found

        # Determine the user's role
        cursor.execute("SELECT 1 FROM pekerja WHERE id = %s", [user_id])
        is_worker = cursor.fetchone()
        print(f"Is Worker: {is_worker}")

        cursor.execute("SELECT 1 FROM pelanggan WHERE id = %s", [user_id])
        is_customer = cursor.fetchone()
        print(f"Is Customer: {is_customer}")

        if is_worker:
            role = "pekerja"
        elif is_customer:
            role = "pengguna"
        else:
            role = "guest"
        print(f"Determined Role: {role}")

        # Fetch subcategory info
        cursor.execute("""
            SELECT sj.Id, sj.NamaSubkategori, sj.Deskripsi, kj.NamaKategori
            FROM SUBKATEGORI_JASA sj
            LEFT JOIN KATEGORI_JASA kj ON sj.KategoriJasaId = kj.Id
            WHERE sj.Id = %s
        """, [subcategory_id])
        subcategory = cursor.fetchone()
        if not subcategory:
            raise ValueError("Subcategory not found")

        # Fetch service sessions
        cursor.execute("""
            SELECT Sesi, Harga
            FROM SESI_LAYANAN
            WHERE SubkategoriId = %s
        """, [subcategory_id])
        sessions = cursor.fetchall()

        # Fetch workers
        cursor.execute("SELECT NamaBank, Rating FROM pekerja")
        workers = cursor.fetchall()

        # Fetch testimonials
        cursor.execute("""
            SELECT T.tgl, T.teks, P.NamaBank AS NamaPekerja, T.rating
            FROM TESTIMONI T
            LEFT JOIN TR_PEMESANAN_JASA TPJ ON T.idtrpemesananan = TPJ.Id
            LEFT JOIN PEKERJA P ON TPJ.IdPekerja = P.Id
        """)
        testimonials = cursor.fetchall()

        # Prepare context
        context = {
            "role": role,
            "subcategory": {
                "name": subcategory[1],
                "description": subcategory[2],
                "category": subcategory[3],
            },
            "sessions": [{"name": session[0], "price": session[1]} for session in sessions],
            "workers": [{"name": worker[0], "rating": worker[1]} for worker in workers],
            "testimonials": [
                {
                    "date": testimonial[0],
                    "text": testimonial[1],
                    "worker": testimonial[2],
                    "rating": testimonial[3],
                }
                for testimonial in testimonials
            ],
        }

        return render(request, "subcategory_detail.html", context)

    except Exception as e:
        print(f"Error in subcategory_detail: {e}")
        return render(request, "500.html", {"error": str(e)}, status=500)
    finally:
        cursor.close()
        connection.close()
