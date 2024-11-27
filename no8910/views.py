from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from no8910.models import Voucher, Promo, Subkategori, Testimoni
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

def show_halaman_diskon(request):
    vouchers = Voucher.objects.all()
    all_promo = Promo.objects.all()

    context = {
        'vouchers': vouchers,
        'all_promo': all_promo
    }

    return render(request, "diskon_page.html", context)


@csrf_exempt
@require_POST
def beli_voucher_by_ajax(request, id):
    voucher = Voucher.objects.get(pk=id)
    user = request.user

    return HttpResponse(b"CREATED", status=201) 

def get_voucher_data_to_buy(request, id):
    voucher = Voucher.objects.get(pk=id)
    data = {
        'kode': voucher.kode,
        'harga': voucher.harga,
        'jumlah_hari_berlaku': voucher.jumlah_hari_berlaku,
        'kuota_penggunaan': voucher.kuota_penggunaan,
    }
    return JsonResponse(data)

def tes_testimoni(request):
    return render(request, "tes_testimoni.html")


def show_subkategori_page(request, id):
    subkategori = Subkategori.objects.get(pk=id)

    context = {'subkategori': subkategori}

    return render(request, 'subkategori_page.html', context)

@csrf_exempt
@require_POST
def create_testimony_by_ajax(request, subkategori_id):
    subkategori = Subkategori.objects.get(pk=subkategori_id)
    user = request.user
    rating = request.POST.get("rating")
    testimony_text = request.POST.get("testimony_text")

    new_testimony = Testimoni(
       subkategori = subkategori,
       user = user,
       rating = rating,
       testimony_text = testimony_text,
    )
    new_testimony.save()

    return HttpResponse(b"CREATED", status=201) 
