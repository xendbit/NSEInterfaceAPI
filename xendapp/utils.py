import hashlib
import io
import os

from PIL import Image
import cloudinary
import qrcode
import requests
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.response import Response

from xendapp import models


blockchain_domain = os.getenv('BLOCKCHAIN_DOMAIN')
blockchain_api_key = os.getenv('BLOCKCHAIN_API_KEY')

def custom_exception_handler(exc, context):

    msg = exc.detail if hasattr(exc, 'detail') else str(exc)
    status = 403 if type(exc) in [NotAuthenticated, PermissionDenied] else 400
    return Response({'detail': msg}, status=status)


def convert_dict_keys_to_camel_case(input_dict):
    for key in list(input_dict.keys()):
        new_key = key[0].lower() + key[1:]
        input_dict[new_key] = input_dict.pop(key)
    return input_dict


def update_blockchain(amount, user_id):
    data = {
        'user_id': user_id,
        'amount': amount
    }

    headers = {
        'api-key': blockchain_api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    resp = requests.post(f'{blockchain_domain}/user/set-balance', json=data, headers=headers)

    if not resp.ok:
        raise Exception(f'Blockchain account update was not successful: {resp.json().get("error")[0]}')

def update_one_sterling_accounts(account_number):

    account = models.BankAccount.objects.get(account_number=account_number)
    user = models.ArtExchangeUser.objects.get(wallet_account_number=account_number)
    old_balance = account.balance
    auth_token = os.getenv('STERLING_AUTH_KEY')
    version = os.getenv('STERLING_API_VERSION')
    institution_code = os.getenv('STERLING_INST_CODE')
    domain = os.getenv('STERLING_DOMAIN')
    url = f'{domain}/BankOneWebAPI/api/Account/DoBalanceEnquiry/{version}?authtoken={auth_token}'

    headers = {
        'Accept': 'application/json',
    }

    data = {
        "InstitutionCode": institution_code,
        "AccountNumber": account_number
    }
    resp = requests.post(url, json=data, headers=headers)
    resp_json = resp.json()
    new_balance = (resp_json.get("WithdrawableAmount"))/100
    if old_balance != new_balance:
        account.balance = new_balance
        account.save()
        update_blockchain(new_balance, user.id)


def update_all_sterling_accounts():

    account_qs = models.BankAccount.objects.filter(bank='sterling')
    for account in account_qs:
        update_one_sterling_accounts(account.account_number)


def upload_image(image):
    cloudinary.config(
        cloud_name=os.getenv('CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET')
    )
    bytes_object = io.BytesIO()
    image.save(bytes_object, 'jpeg')
    im_bytes = bytes_object.getvalue()
    response = cloudinary.uploader.upload(im_bytes)
    return response['url']

def generate_qrcode(input_string):
    '''Generates a QR code'''

    hash_input = input_string
    hash = hashlib.sha512(hash_input.encode('utf-8')).hexdigest()

    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(hash)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    return upload_image(img)


def clear_pending_asset_transfer(): # TODO Set up a cron job to run this periodically
    for rcd in models.PendingAssetTransfer.objects.all():
        blockchain_data = {
            'recipientId': rcd.recipient_id,
            'asset_issuer_id': rcd.asset_issuer_id,
            'senderId': rcd.sender_id,
            'assetName': rcd.asset_name,
            'quantity': rcd.quantity,
            'unitPrice': rcd.unit_price,
            'marketType': rcd.market_type
        }

        asset_transfer_url = f'{blockchain_domain}assets/transfer'
        resp = requests.post(f'{asset_transfer_url}', json=blockchain_data,
                             headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
        if resp.ok:
            rcd.delete()


BANK_CODES_CHOICES = [
('011', 'First Bank Plc'),
('014', 'Mainstreet Bank Plc'),
('023', 'CitiBank'),
('070', 'Fidelity Bank Plc'),
('050', 'Ecobank Nigeria Plc'),
('030', 'Heritage Bank Plc'),
('032', 'Union Bank of Nigeria Plc'),
('033', 'United Bank For Africa Plc'),
('232', 'Sterling Bank Plc'),
('035', 'Wema Bank Plc'),
('057', 'Zenith Bank Plc'),
('311', 'Parkway'),
('058', 'GTBank Plc'),
('214', 'First City Monument Bank Plc'),
('215', 'UnityBank Plc'),
('315', 'GTB Mobile Money'),
('082', 'Keystone Bank Plc'),
('084', 'Enterprise Bank Ltd'),
('063', 'Diamond Bank Plc'),
('044', 'Access Bank Nigeria Plc'),
('221', 'StanbicIBTC Bank Plc'),
('068', 'Standard Chartered Bank Nigeria Ltd'),
('322', 'Zenith Mobile'),
('323', 'Access Mobile'),
('401', 'ASO Savings and Loans'),
('304', 'Stanbic Mobile'),
('305', 'PAYCOM'),
('307', 'Ecobank Mobile'),
('309', 'FBN Mobile'),
('301', 'Jaiz Bank'),
('076', 'Polaris Bank'),
('101', 'Providus Bank'),
('100', 'Suntrust Bank'),
('102', 'Titan Trust Bank')
]