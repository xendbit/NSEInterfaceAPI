import hashlib
import io
import os
from datetime import datetime
from decimal import Decimal

from apscheduler.schedulers.background import BackgroundScheduler
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.response import Response
import cloudinary
import qrcode
import requests

from xendapp import models


blockchain_domain = os.getenv('BLOCKCHAIN_DOMAIN')
blockchain_api_key = os.getenv('BLOCKCHAIN_API_KEY')

def account_transaction(transaction_type, account_number, amount, narration, time=datetime.now(), reference=''):

    amount_dec = Decimal(amount)

    if transaction_type not in ['debit', 'credit']:
        raise ValueError('Transaction type must be debit or credit')

    account = models.BankAccount.objects.get(account_number=account_number)

    if transaction_type == 'debit':
        if amount_dec > account.balance:
            raise ValueError('Account has insufficient fund')
        account.balance -= amount_dec
        account.save()

    if transaction_type == 'credit':
        account.balance += amount_dec
        account.save()

    try:
        models.BankTransaction.objects.create(
            account_number=account_number,
            transaction_type=transaction_type,
            narration=narration,
            amount=amount_dec,
            time=time,
            transaction_reference=reference
        )
    except Exception as exc:
        return Response({'detail': str(exc)}, status=400)

    return Response({'detail': 'Transaction Successful', 'New balance': account.balance})


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

    if models.PendingAssetTransfer.objects.all().exists():
        for rcd in models.PendingAssetTransfer.objects.all():
            blockchain_data = {
                'buyerId': rcd.buyer_id,
                'assetIssuerId': rcd.asset_issuer_id,
                'sellerId': rcd.seller_id,
                'assetName': rcd.asset_name,
                'quantity': rcd.quantity,
                'price': rcd.unit_price,
                'marketType': rcd.market_type
            }

            headers = {
                'api-key': blockchain_api_key,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }

            asset_transfer_url = f'{blockchain_domain}assets/buy'
            resp = requests.post(f'{asset_transfer_url}', json=blockchain_data, headers=headers)
            if resp.ok:
                rcd.delete()


def start():
    scheduler = BackgroundScheduler(job_defaults={'misfire_grace_time': 15*60})
    scheduler.add_job(clear_pending_asset_transfer, 'interval', minutes=15)
    scheduler.start()


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


BANK_THREE_SIX_DIGIT_MAPPING = {
            '011': '000016',
            '014': '090171',
            '023': '000009',
            '070': '000007',
            '050': '000010',
            '030': '000020',
            '032': '000018',
            '033': '000004',
            '232': '000001',
            '035': '000017',
            '057': '000015',
            '311': '100003',
            '058': '000013',
            '214': '000003',
            '215': '000011',
            '315': '100009',
            '082': '000002',
            '084': '000019',
            '063': '000005',
            '044': '000014',
            '221': '000012',
            '068': '000021',
            '322': '100018',
            '323': '100013',
            '401': '090001',
            '301': '000006',
            '076': '000008',
            '101': '000023',
            '100': '000022',
            }


SIX_DIGIT_CODE_LIST = [
    "090270", "070010", "090260", "090197", "000014", "100013", "000005", "090134", "090160", "090268", "100028", "090133",
    "090259", "090131", "090169", "090116", "090143", "090282", "090001", "090172", "090264", "090127",	"090117", "090176",
    "090148", "070015",	"100005", "090154", "100015", "090141", "090144", "000009", "090130", "100032", "060001",  "070006",
    "090159", "090167", "100021", "090156", "000010", "100008", "100030", "090097",	"090273", "000019", "100006",	"090179",
    "100014", "090107", "060002", "100031", "100001", "090153", "000007", "100019", "090126", "090111", "000016", "000003",
    "070014", "070002", "100016", "400001", "090145", "090158", "070009", "090122", "090178", "090195", "100009", "000013",
    "090147", "070017", "090121", "000020", "090175", "090118", "090258", "100024", "090157", "070016", "100029", "100027",
    "090149", "000006", "090003", "000002", "100025", "100011", "070012", "090177", "090171", "090280", "090136", "090113",
    "100020", "090129",	"090151", "090128",	"090205", "090108", "090263", "999999", "090194", "060003", "070001", "090119",
    "090161", "090272",	"070007", "100026",	"100002", "070008",	"090004", "100003",	"110001", "100004", "090137",	"090196",
    "090135", "070013",	"000008", "090274",	"000023", "090261",	"000024", "070011",	"090125", "090198",	"090132", "090138",
    "090006",	"090140", "090112",	"100007", "000012",	"000021", "090262",	"000001", "100022",	"000022", "100023", "000026",
    "090115", "100010",	"090146", "090005",	"090276", "000018",	"000004", "000011",	"090251", "090123", "090110", "090150",
    "090139",	"100012", "000017",	"090120", "090124",	"090142", "000015",	"100018",
]
