# forms.py
from django import forms

class TransactionForm(forms.Form):
    CATEGORY_CHOICES = [
        ('topup', 'TopUp MyPay'),
        ('service_payment', 'Bayar Transaksi Jasa'),
        ('transfer', 'Transfer MyPay'),
        ('withdrawal', 'Withdrawal')
    ]
    
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, label="Kategori Transaksi", required=True)
    nominal = forms.DecimalField(label="Nominal", required=False, min_value=0)
    jasa = forms.ChoiceField(label="Jasa", required=False)  # Populate choices in the view
    service_price = forms.DecimalField(label="Harga Jasa", required=False, min_value=0, disabled=True)
    phone_number = forms.CharField(label="No HP Tujuan", required=False, max_length=15)
    bank_name = forms.ChoiceField(label="Nama Bank", required=False)  # Populate choices in the view
    bank_account = forms.CharField(label="No Rekening Bank", required=False, max_length=20)
    
    def __init__(self, *args, **kwargs):
        user_type = kwargs.pop('user_type', None)
        super().__init__(*args, **kwargs)
        
        # Conditional field requirements based on user type and category
        if user_type == 'pekerja':
            self.fields['jasa'].widget = forms.HiddenInput()
            self.fields['service_price'].widget = forms.HiddenInput()
