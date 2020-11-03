import random
import string
import os
from datetime import datetime
from decimal import Decimal

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.debug import sensitive_variables
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from xendapp import models
from xendapp import serializers
from xendapp.utils import convert_dict_keys_to_camel_case


sterling_domain = os.getenv('STERLING_DOMAIN')
auth_key = os.getenv('STERLING_AUTH_KEY')
version = os.getenv('STERLING_API_VERSION')
product_code = os.getenv('STERLING_PRODUCT_CODE')
accountt_officer_code = os.getenv('STERLING_ACCT_OFF_CODE')
institution_code = os.getenv('STERLING_INST_CODE')

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


@sensitive_variables('auth_key')
def sterling_pnd_status(url, request):
    account_number = request.query_params.get('account_number')

    account = models.BankAccount.objects.get(account_number=account_number)

    data = {
        'AccountNo': account_number,
        'AuthenticationCode': auth_key
    }

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    resp = requests.post(url, json=data, headers=headers)

    return account, resp


@api_view()
@permission_classes([IsAuthenticated])
def sterling_activate_pnd(request):

    url = f'{sterling_domain}/ThirdPartyAPIService/APIService/Account/ActivatePND'

    account, resp = sterling_pnd_status(url, request)
    resp_json = resp.json()

    if resp.ok:
        account.restriction_type = 1
        account.save()

    return Response(convert_dict_keys_to_camel_case(resp_json), status=resp.status_code)


@api_view()
@permission_classes([IsAuthenticated])
def sterling_deactivate_pnd(request):


    url = f'{sterling_domain}/ThirdPartyAPIService/APIService/Account/DeActivatePND'

    account, resp = sterling_pnd_status(url, request)
    resp_json = resp.json()

    if resp.ok:
        account.restriction_type = '0'
        account.save()

    return Response(convert_dict_keys_to_camel_case(resp_json), status=resp.status_code)


@api_view()
@permission_classes([IsAuthenticated])
def sterling_check_pnd(request):

    url = f'{sterling_domain}/ThirdPartyAPIService/APIService/Account/CheckPNDStatus'

    account, resp = sterling_pnd_status(url, request)
    resp_json = resp.json()

    return Response(convert_dict_keys_to_camel_case(resp_json), status=resp.status_code)


@sensitive_variables('auth_key')
def sterling_transfer(request_data):

    url = f'{sterling_domain}/ThirdPartyAPIService/APIService/Transfer/LocalFundsTransfer'
    pnd_deact_url = f'{sterling_domain}/ThirdPartyAPIService/APIService/Account/DeActivatePND'


    from_account_number = request_data.get('from_account_number')
    to_account_number = request_data.get('to_account_number')
    narration = request_data.get('narration')
    amount = request_data.get('amount')

    if not models.BankAccount.objects.filter(account_number=from_account_number).exists():
        raise ObjectDoesNotExist(f'Debit account not found: {from_account_number}')

    data = {
        "AuthenticationKey": auth_key,
        "FromAccountNumber": from_account_number,
        "ToAccountNumber": to_account_number,
        "TransactionReference": ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10)),
        "Narration": narration,
        "Amount": amount

    }

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    resp = requests.post(url, json=data, headers=headers)
    resp_json = resp.json()

    if resp_json.get('IsSuccessFul'):
        account_transaction('debit', from_account_number, amount, narration)
        account_transaction('credit', to_account_number, amount, narration)
    status_code = 200 if resp_json.get('IsSuccessFul') else 400

    return resp_json, status_code

@api_view(http_method_names=['POST'])
@permission_classes([IsAuthenticated])

def sterling_local_transfer(request):

    resp, status_code = sterling_transfer(request.data)

    return Response(convert_dict_keys_to_camel_case(resp), status=status_code)


def create_sterling_account(data):
    url = f'{sterling_domain}/BankOneWebAPI/api/Account/CreateAccountQuick/{version}?authtoken={auth_key}'
    pnd_deact_url = f'{sterling_domain}/ThirdPartyAPIService/APIService/Account/DeActivatePND'

    bvn = data.get('BVN')
    lastname = data.get('LastName')
    othernames = data.get('OtherNames')

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    resp = requests.post(url, json=data, headers=headers)
    resp_json = resp.json()
    status = 201 if resp_json.get('IsSuccessful') else 400

    if resp_json.get('IsSuccessful'):

        models.BankAccount.objects.create(
            account_number=resp_json['Message']['AccountNumber'],
            fullname=resp_json['Message']['FullName'],
            account_type=data.get('account_type'),
            bvn=bvn,
            bank='sterling',
            restriction_type='0',
            account_reference=f'{bvn}_{othernames}_{lastname}'
        )

        deact_data = {
            'AccountNo': resp_json['Message']['AccountNumber'],
            'AuthenticationCode': auth_key
        }
        _ = requests.post(pnd_deact_url, json=deact_data, headers=headers)

    return resp_json, status

@sensitive_variables('auth_key')
@api_view(http_method_names=['POST'])
@permission_classes([IsAuthenticated])
def sterling_new_account(request):

    data = request.data
    serializer = serializers.NewAccountSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    lastname = serializer.validated_data.get('last_name')
    firstname = serializer.validated_data.get('first_name')
    middlename = serializer.validated_data.get('middle_name')
    bvn = serializer.validated_data.get('bvn')
    othernames = firstname + ' ' + middlename if middlename else firstname


    if models.BankAccount.objects.filter(bvn=bvn).exists():
        return Response({'detail': 'An account already exists for this bvn.'}, status=400)

    input_data = {
              'TransactionTrackingRef': ''.join(random.choices(string.ascii_uppercase + string.digits, k = 5)),
              'AccountOpeningTrackingRef': ''.join(random.choices(string.ascii_uppercase + string.digits, k = 6)),
              'ProductCode': product_code,
              'LastName': lastname,
              'OtherNames': othernames,
              'BVN': bvn,
              'AccountOfficerCode': accountt_officer_code,
              'NotificationPreference': 0,
              'TransactionPermission': 1
            }

    resp_json, status = create_sterling_account(input_data)

    return Response(convert_dict_keys_to_camel_case(resp_json), status=status)


@api_view()
@permission_classes([IsAuthenticated])
def sterling_account_balance(request):


    account_number = request.query_params.get('account_number')

    _ = models.BankAccount.objects.get(account_number=account_number)

    url = f'{sterling_domain}/BankOneWebAPI/api/Account/DoBalanceEnquiry/{version}?authtoken={auth_key}'

    data = {
          "InstitutionCode": institution_code,
          "AccountNumber": account_number
        }

    headers = {
        'Accept': 'application/json',
    }

    resp = requests.post(url, json=data, headers=headers)
    resp_json = resp.json()
    return Response(convert_dict_keys_to_camel_case(resp_json))
