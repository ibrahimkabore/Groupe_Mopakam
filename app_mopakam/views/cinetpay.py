from django.shortcuts import render
import hashlib
def cinetpay(request):
    return render(request, 'commande/cinetpay.html')