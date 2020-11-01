import os

import requests
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.response import Response

from xendapp import models


def custom_exception_handler(exc, context):

    msg = exc.detail if hasattr(exc, 'detail') else str(exc)
    status = 403 if type(exc) in [NotAuthenticated, PermissionDenied] else 400
    return Response({'detail': msg}, status=status)


def convert_dict_keys_to_camel_case(input_dict):
    for key in list(input_dict.keys()):
        new_key = key[0].lower() + key[1:]
        input_dict[new_key] = input_dict.pop(key)
    return input_dict


def update_blockchain(account_number, amount):
    data = {
        'account_number': account_number,
        'amount': amount
    }

    resp = requests.post('https://lb.xendbit.com/api/x/beneficiary/update-blockchain', json=data, headers={'Accept': 'application/json',
    'Content-Type': 'application/json'})

    if not resp.ok:
        raise Exception(f'Blockchain account update was not successful: {resp.text}') # TODO josonify resp and get the relevant message

def update_one_sterling_accounts(account_number):

    account = models.BankAccount.objects.get(account_number=account_number)
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
        update_blockchain(account_number, new_balance)


def update_all_sterling_accounts():

    account_qs = models.BankAccount.objects.filter(bank='sterling')
    for account in account_qs:
        update_one_sterling_accounts(account.account_number)


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