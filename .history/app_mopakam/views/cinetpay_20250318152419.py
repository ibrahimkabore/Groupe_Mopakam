from django.shortcuts import render
import hashlib
def cinetpay(request):

    
   
    if request.method == "POST":
        inputtxt = request.POST['getrow']
        api_key_sha256 = request.POST['api_key_sha256'];
        api_secret_sha256 = request.POST['api_secret_sha256']
        my_api_secret_sha256 = hashlib.sha256(b'here my api secret').hexdigest()
    my_api_key_sha256 = hashlib.sha256(b'here my api key').hexdigest()
    if my_api_key_sha256 == api_key_sha256 and my_api_secret_sha256 == api_secret_sha256:
        # from paytech
        

    return render(request, 'commande/cinetpay.html')