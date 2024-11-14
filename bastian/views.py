# views.py
from .helpers import process_topup, process_service_payment, process_transfer, process_withdrawal
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import TransactionForm

def transaction_view(request):
    user_type = 'pengguna'  # Or 'pekerja' based on the logged-in user type
    form = TransactionForm(user_type=user_type)

    if request.method == 'POST':
        form = TransactionForm(request.POST, user_type=user_type)
        
        if form.is_valid():
            category = form.cleaned_data['category']
            nominal = form.cleaned_data.get('nominal')
            phone_number = form.cleaned_data.get('phone_number')
            bank_name = form.cleaned_data.get('bank_name')
            bank_account = form.cleaned_data.get('bank_account')
            jasa = form.cleaned_data.get('jasa')
            service_price = form.cleaned_data.get('service_price')

            # Process each transaction type
            if category == 'topup':
                # Process TopUp
                if nominal:
                    # Assume some function like `process_topup` handles the logic
                    process_topup(user=request.user, amount=nominal)
                    messages.success(request, f"TopUp of {nominal} MyPay was successful.")
                else:
                    messages.error(request, "Nominal is required for TopUp.")

            elif category == 'service_payment' and user_type == 'pengguna':
                # Process Service Payment
                if jasa and service_price:
                    # Assume a function like `process_service_payment`
                    process_service_payment(user=request.user, service_id=jasa, amount=service_price)
                    messages.success(request, f"Payment of {service_price} for service {jasa} was successful.")
                else:
                    messages.error(request, "Jasa and service price are required for Service Payment.")

            elif category == 'transfer':
                # Process Transfer
                if phone_number and nominal:
                    # Assume a function like `process_transfer`
                    process_transfer(sender=request.user, recipient_phone=phone_number, amount=nominal)
                    messages.success(request, f"Transfer of {nominal} MyPay to {phone_number} was successful.")
                else:
                    messages.error(request, "Phone number and nominal are required for Transfer.")

            elif category == 'withdrawal':
                # Process Withdrawal
                if bank_name and bank_account and nominal:
                    # Assume a function like `process_withdrawal`
                    process_withdrawal(user=request.user, bank_name=bank_name, bank_account=bank_account, amount=nominal)
                    messages.success(request, f"Withdrawal of {nominal} to bank {bank_name} was successful.")
                else:
                    messages.error(request, "Bank details and nominal are required for Withdrawal.")

            # Redirect to a success page or re-render the form with a success message
            return render(request, 'transaction_form.html', {'form': form})

    return render(request, 'transaction_form.html', {'form': form})
