from django.db import models
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

# class Voucher(models.Model):
#     id = models.UUIDField(primary_key=True, default = uuid.uuid4, editable = False)
#     kode = models.CharField(max_length=20)
#     potongan = models.IntegerField()
#     min_transaksi_pemesanan = models.IntegerField()
#     jumlah_hari_berlaku = models.IntegerField()
#     kuota_penggunaan = models.IntegerField()
#     harga = models.IntegerField()

# class Promo(models.Model):
#     id = models.UUIDField(primary_key=True, default = uuid.uuid4, editable = False)
#     kode = models.CharField(max_length=20)
#     tanggal_akhir_berlaku = models.DateField()

# class Subkategori(models.Model):
#     id = models.UUIDField(primary_key=True, default = uuid.uuid4, editable = False)


# class Transaksi(models.Model):
#     id = models.UUIDField(primary_key=True, default = uuid.uuid4, editable = False)
    

# class Testimoni(models.Model):
#     transaksi = models.ForeignKey(Transaksi, related_name='testimonies', on_delete=models.CASCADE)  
#     user = models.ForeignKey(User, on_delete=models.CASCADE)  
#     rating = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(5.0)])
#     testimony_text = models.TextField()

#     class Meta:
#         unique_together = ('transaksi', 'user')
