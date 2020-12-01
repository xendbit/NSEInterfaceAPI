import base64
import hashlib
import os
from datetime import datetime

import requests
from drf_yasg.openapi import Parameter, IN_QUERY
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes, schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from xendapp import serializers, models
from xendapp.utils import account_transaction

providus_username = os.getenv('PROVIDUS_THIRD_PARTY_API_USERNAME')
providus_password = os.getenv('PROVIDUS_THIRD_PARTY_API_PASSWORD')
providus_api_url = os.getenv('PROVIDUS_THIRD_PARTY_API_URL')
providus_monnify_url = os.getenv('PROVIDUS_MONNIFY_URL')
providus_contract_code = os.getenv('PROVIDUS_CONTRACT_CODE')
providus_client_secret = os.getenv('PROVIDUS_SECRETKEY')


@swagger_auto_schema( method='get', manual_parameters=[Parameter('bvn', IN_QUERY, type='string')])
@api_view()
@permission_classes([IsAuthenticated])
@schema(None)
def providus_bvn_details(request):

    bvn = request.query_params.get('bvn')
    url = f'{providus_api_url}/GetBVNDetails'

    data = {
            "bvn": bvn,
            "userName": providus_username,
            "password": providus_password
        }

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    resp = requests.post(url, json=data, headers=headers)
    resp_json = resp.json()
    return Response(resp_json)


@swagger_auto_schema( method='get', manual_parameters=[Parameter('account_number', IN_QUERY, type='string'), Parameter('bank_code', IN_QUERY, type='string')])
@api_view()
@permission_classes([IsAuthenticated])
@schema(None)
def providus_account_number_details(request):

    account_number = request.query_params.get('account_number')
    bank_code = request.query_params.get('bank_code')
    url = f'{providus_api_url}/GetNIPAccount'

    data = {
            "accountNumber": account_number,
            "beneficiaryBank": bank_code,
            "userName": providus_username,
            "password": providus_password
        }

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    resp = requests.post(url, json=data, headers=headers)
    resp_json = resp.json()
    return Response(resp_json)


@swagger_auto_schema(method='post', request_body=serializers.ProvidusInterBankTransferSerializer)
@api_view(http_method_names=['POST'])
# @permission_classes([permissions.IsCustomerCareOrXendAdmin])
def providus_interbank_transfer(request):

    url = f'{providus_api_url}/NIPFundTransfer'
    serializer = serializers.ProvidusInterBankTransferSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    credit_account = serializer.validated_data.get('beneficiary_account_number')

    data = {
        "beneficiaryAccountName": serializer.validated_data.get('recipient_account_name'),
        "transactionAmount": serializer.validated_data.get('amount'),
        "currencyCode": "NGN",
        "narration": serializer.validated_data.get('narration'),
        "sourceAccountName": serializer.validated_data.get('source_account_name'),
        "beneficiaryAccountNumber": serializer.validated_data.get('recipient_account_number'),
        "beneficiaryBank": serializer.validated_data.get('recipient_bank'),
        "transactionReference": f'{credit_account}_{datetime.now()}'.replace(' ', '_'),
        "userName": providus_username,
        "password": providus_password
    }


    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    resp = requests.post(url, json=data, headers=headers)
    resp_json = resp.json()
    return Response(resp_json, status=resp_json.get('status'))


def providus_get_token():

    api_key = os.getenv('PROVIDUS_APIKEY')
    secret_key = os.getenv('PROVIDUS_SECRETKEY')

    auth_input = f'{api_key}:{secret_key}'
    auth_string = base64.b64encode(auth_input.encode('utf-8')).decode('utf-8')
    url = f'{providus_monnify_url}/auth/login'
    headers = {
        'Authorization': f'Basic {auth_string}'
    }

    resp = requests.post(url, headers=headers)
    resp_json = resp.json()
    if resp.ok:
        resp_body = resp_json['responseBody']
        token = resp_body.get('accessToken')
        return token
    raise Exception('An error occurred. Please try again latter')


def providus_reserve_account(payload):

    token = providus_get_token()
    url = f'{providus_monnify_url}/bank-transfer/reserved-accounts'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }


    resp = requests.post(url, json=payload, headers=headers)
    resp_json = resp.json()

    if resp_json.get('requestSuccessful'):
        status = 201
        return_resp = {
            'IsSuccessful': resp_json.get('requestSuccessful'),
            'CustomerIDInString': None,
            'Message':
                {'AccountNumber': resp_json['responseBody']['accountNumber'],
                 'CustomerID': None,
                 'FullName': resp_json['responseBody']['customerName'],
                 'CreationMessage': None
                 },
            'TransactionTrackingRef': None,
            'AccountReference': resp_json['responseBody']['accountReference'],
            'Page': None
        }
    else:
        status = 400
        return_resp = resp_json
    # status = 201 if resp_json.get('requestSuccessful') else 400
    bank = 'Providus'
    if return_resp.get('IsSuccessful'):

        models.BankAccount.objects.create(
            account_number=return_resp['Message']['AccountNumber'],
            fullname=return_resp['Message']['FullName'],
            bvn=payload.get('bvn'),
            bank='Providus',
            restriction_type='0',
            account_reference=return_resp.get('AccountReference')
        )

    return return_resp, status, bank


@swagger_auto_schema(method='post', request_body=serializers.NewAccountSerializer)
@api_view(http_method_names=['POST'])
def providus_new_account(request):
    '''Creates a Providus bank account for an agent or beneficiary'''

    request_data = request.data
    serializer = serializers.NewAccountSerializer(data=request_data)
    serializer.is_valid(raise_exception=True)

    lastname = serializer.validated_data.get('last_name')
    firstname = serializer.validated_data.get('first_name')
    middlename = serializer.validated_data.get('middle_name')
    bvn = serializer.validated_data.get('bvn')
    email = serializer.validated_data.get('email')
    othernames = firstname + ' ' + middlename if middlename else firstname

    data = {
        'accountReference': f'{bvn}_{firstname}',
        'accountName': f'{firstname} {lastname}',
        'currencyCode': "NGN",
        'contractCode': providus_contract_code,
        'customerEmail': email,
        'customerName': f'{othernames} {lastname}'
    }

    resp_json, status, bank = providus_reserve_account(data)

    return Response(resp_json, status=status)

def virtual_account_transfer(data):

    from_account_number = data.get('from_account_number')
    to_account_number = data.get('to_account_number')
    narration = data.get('narration')
    amount = data.get('amount')
    try:
        account_transaction('debit', from_account_number, amount, narration)
        account_transaction('credit', to_account_number, amount, narration)
    except Exception as exc:
        raise Exception(f'Operation not successful: {str(exc)}')


@api_view(http_method_names=['POST'])
@schema(None)
def providus_account_webhook(request):
    '''Handles the notification sent by Providus when there is a credit on a reserved account'''

    request_data = request.data

    transaction_reference = request_data.get('transaction_reference')
    payment_reference = request_data.get('payment_reference')
    amount_paid = request_data.get('amount_paid')
    paid_on = request_data.get('paid_on')
    transaction_hash = request_data.get('transaction_hash')
    narration = request_data.get('payment_description')
    transaction_time = datetime.strptime(paid_on, "%d/%m/%Y %I:%M:%S %p")
    product = request_data.get('product')
    account_reference = product.get('reference')

    try:
        account = models.BankAccount.objects.get(account_reference=account_reference)
    except (models.BankAccount.DoesNotExist, models.BankAccount.MultipleObjectsReturned):
        return Response({'detail': 'Account_reference mismatch'})

    account_number = account.account_number

    if models.BankTransaction.objects.filter(transaction_reference=transaction_reference).exists():
        return Response({'detail': 'Transaction Duplicate'}, status=400)

    hash_input = f'{providus_client_secret}|{payment_reference}|{amount_paid}|{paid_on}|{transaction_reference}'
    hash = hashlib.sha512(hash_input.encode('utf-8')).hexdigest()

    if hash != transaction_hash:
        return Response({'detail': 'Hash mismatch'}, status=400)

    try:
        account_transaction('credit', account_number, amount_paid, narration, transaction_time, transaction_reference)
    except Exception as exc:
        return Response({'detail': str(exc)}, 400)

    blkchn_url = f'https://xendfilb.xendbit.net/api/x/user/fund-account/{account_number}/{amount_paid}'

    blkchn_resp = requests.get(blkchn_url)

    return Response({'detail': 'Notification successfully processed'})


@swagger_auto_schema( method='get', manual_parameters=[
    Parameter('account_number', IN_QUERY, type='string'),
    Parameter('page', IN_QUERY, type='string'),
    Parameter('page_size', IN_QUERY, type='string')
])
@api_view()
def providus_account_transactions(request):
    '''Returns all transactions on a virtual account'''

    account_number = request.query_params.get('account_number')
    page = request.query_params.get('page', 0)
    page_size = request.query_params.get('page_size', 10)
    token = providus_get_token()

    account = models.BankAccount.objects.get(account_number=account_number)
    account_reference = account.account_reference

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    url = f'{providus_monnify_url}/bank-transfer/reserved-accounts/transactions?accountReference={account_reference}&page={page}&size={page_size}'

    resp = requests.get(url, headers=headers)
    resp_json = resp.json()
    return Response(resp_json)


@swagger_auto_schema( method='get', manual_parameters=[Parameter('account_number', IN_QUERY, type='string')])
@api_view()
@schema(None)
def providus_deallocate_account(request):
    '''Deallocate a reserved account'''

    account_number = request.query_params.get('account_number')
    token = providus_get_token()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    url = f'{providus_monnify_url}/bank-transfer/reserved-accounts/transactions?accountNumber={account_number}'

    resp = requests.delete(url, headers=headers)
    resp_json = resp.json()
    return Response(resp_json)



@swagger_auto_schema(method='post', request_body=serializers.BankTransactionsSerializer)
@api_view(http_method_names=['POST'])
@permission_classes([IsAuthenticated])
def providus_account_transaction(request):

    request_data = request.data
    serializer = serializers.BankTransactionsSerializer(data=request_data)
    serializer.is_valid(raise_exception=True)

    account_number = serializer.validated_data.get('account_number')
    transaction_type = serializer.validated_data.get('transaction_type')
    narration = serializer.validated_data.get('narration')
    amount = serializer.validated_data.get('amount')

    account = models.BankAccount.objects.get(account_number=account_number)

    if account.bank.lower() != 'providus':
        return Response({'detail': 'Operation not allowed on this account'}, status=400)

    return account_transaction(transaction_type, account_number, amount, narration)
