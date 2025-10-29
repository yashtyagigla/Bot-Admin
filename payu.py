# payu.py
import hashlib
import random
import string
from config import PAYU_KEY, PAYU_SALT, PAYU_BASE_URL

def generate_txn_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))

def generate_payu_link(amount, productinfo, firstname, email, phone):
    txnid = generate_txn_id()
    # Fields required by PayU
    data = {
        "key": PAYU_KEY,
        "txnid": txnid,
        "amount": f"{amount:.2f}",
        "productinfo": productinfo,
        "firstname": firstname,
        "email": email,
        "phone": phone,
        "surl": "https://yourserver.com/payu/success",  # webhook after payment
        "furl": "https://yourserver.com/payu/failure",
        "service_provider": "payu_paisa"
    }
    # Generate hash as per PayU documentation
    hash_sequence = f"{data['key']}|{data['txnid']}|{data['amount']}|{data['productinfo']}|{data['firstname']}|{data['email']}|||||||||||{PAYU_SALT}"
    data["hash"] = hashlib.sha512(hash_sequence.encode('utf-8')).hexdigest().lower()
    # Construct payment URL
    payu_url = PAYU_BASE_URL + "?" + "&".join([f"{k}={v}" for k,v in data.items()])
    return payu_url
