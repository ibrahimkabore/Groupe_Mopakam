import os
import requests

def initiate_payment(payment_data):
    """
    Initier un paiement avec CinetPay
    
    Args:
        payment_data (dict): Dictionnaire contenant les informations de paiement
        
    Returns:
        str: URL de paiement si succès, None sinon
    """
    api_key = os.getenv('CINETPAY_API_KEY')
    site_id = os.getenv('CINETPAY_SITE_ID')
    
    url = "https://api.cinetpay.com/v1/payments/initiate"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "amount": payment_data['amount'],
        "currency": payment_data['currency'],
        "description": payment_data['description'],
        "site_id": site_id,
        "transaction_id": payment_data['transaction_id'],
        "return_url": os.getenv('CINETPAY_RETURN_URL', 'https://votredomaine.com/payment-callback'),
        "notify_url": os.getenv('CINETPAY_NOTIFY_URL', 'https://votredomaine.com/payment-notification'),
        "channels": payment_data['channels'],
        "customer_name": payment_data['customer_name'],
        "customer_email": payment_data['customer_email'],
        "customer_phone": payment_data['customer_phone']
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Soulever une exception pour les erreurs HTTP
        
        result = response.json()
        
        if result.get('code') == '201' and result.get('data', {}).get('payment_url'):
            return result['data']['payment_url']
        else:
            # Journaliser l'erreur
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erreur CinetPay: {result}")
            return None
            
    except Exception as e:
        # Journaliser l'exception
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erreur de requête CinetPay: {str(e)}")
        return None