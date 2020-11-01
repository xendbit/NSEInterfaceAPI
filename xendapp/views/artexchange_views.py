import json
import os
import random
import string

import requests
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from .. import models, serializers, utils, permissions
from . import sterling_views

product_code = os.getenv('STERLING_PRODUCT_CODE')
accountt_officer_code = os.getenv('STERLING_ACCT_OFF_CODE')
asset_transfer_url = os.getenv('ASSET_TRANSFER_URL')


@api_view(http_method_names=['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsArtexchange])
def user_registration(request):
    '''Called when a user is registered on ArtExchange platform'''
    data = request.data
    serializer = serializers.RegistrationSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    user_id = serializer.validated_data.get('user_id')
    email = serializer.validated_data.get('email')
    phone_number = serializer.validated_data.get('phone_number')
    fullname = serializer.validated_data.get('fullname')
    user_type = serializer.validated_data.get('user_type')
    address = serializer.validated_data.get('address')
    date_of_birth = serializer.validated_data.get('date_of_birth')
    bank_name = serializer.validated_data.get('bank_name')
    bank_account_name = serializer.validated_data.get('bank_account_name')
    bank_account_number = serializer.validated_data.get('bank_account_number')
    bvn = serializer.validated_data.get('bvn')

    account_data = {
        'TransactionTrackingRef': ''.join(random.choices(string.ascii_uppercase + string.digits, k=5)),
        'AccountOpeningTrackingRef': ''.join(random.choices(string.ascii_uppercase + string.digits, k=6)),
        'ProductCode': product_code,
        'LastName': fullname,
        'OtherNames': '',
        'BVN': bvn,
        'AccountOfficerCode': accountt_officer_code,
        'NotificationPreference': 0,
        'TransactionPermission': 1
    }

    resp_json, status = sterling_views.create_sterling_account(account_data)
    wallet_account_number = resp_json['Message']['AccountNumber']
    if resp_json.get('IsSuccessful'):
        models.ArtExchangeUser.objects.create(
        user_id=user_id,
        email = email,
        phone_number = phone_number,
        fullname = fullname,
        user_type = user_type,
        address = address,
        date_of_birth = date_of_birth,
        bank_name = bank_name,
        bank_account_name = bank_account_name,
        bank_account_number = bank_account_number,
        wallet_account_number = wallet_account_number,
        bvn = bvn
        )

        return Response({'detail': 'Data Successfully processed', 'userId': user_id, 'wallet_account': wallet_account_number })
    else:
        return Response(resp_json['Message'].get('CreationMessage'), status=status)


@api_view(http_method_names=['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsArtexchange])
def asset_buy_request(request):
    '''Gets called when an investor places an asset buy request'''

    data = request.data
    serializer = serializers.BuyRequestSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    buyer_id = serializer.validated_data.get('buyer_id')
    seller_id = serializer.validated_data.get('seller_id')
    security = serializer.validated_data.get('security')
    number_of_tokens = serializer.validated_data.get('number_of_tokens')
    unit_price = serializer.validated_data.get('unit_price')
    nse_fee = serializer.validated_data.get('nse_fee')
    sms_fee = serializer.validated_data.get('sms_fee')
    market_type = serializer.validated_data.get('market_type')

    total_cost = (number_of_tokens * unit_price) + (nse_fee/2) + sms_fee + 200 # 200 for bank charges
    buyer = models.ArtExchangeUser.objects.get(user_id=buyer_id)
    buyer_account = models.BankAccount.objects.get(account_number=buyer.wallet_account_number)
    utils.update_one_sterling_accounts(buyer.wallet_account_number)

    if buyer_account.balance >= total_cost:
        blockchain_data = {
            'buyer_id': buyer_id,
            'seller_id': seller_id,
            'security': security,
            'number_of_tokens': number_of_tokens,
            'unit_price': unit_price,
            'market_type': market_type
        }

        resp = requests.post(f'{asset_transfer_url}', json=blockchain_data, headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
        if resp.ok:
            return Response({'detail': 'Request successfully completed.'})
        else:
            return Response({'detail': f'Request not successful: {resp.text}'}) #TODO josonify respose and pick the relevant message

    return Response({'detail': 'Insufficient fund in the account'}, status=400)


@api_view(http_method_names=['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsArtexchange])
def asset_listing(request):

    data = request.data
    serializer = serializers.ListRequestSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    data = {
        'investor_id': serializer.validated_data.get('investor_id'),
        'security': serializer.validated_data.get('security'),
        'number_of_tokens': serializer.validated_data.get('number_of_tokens'),
        'artwork_value': serializer.validated_data.get('artwork_value'),
        'unit_price': serializer.validated_data.get('unit_price'),
        'listing_start_date': serializer.validated_data.get('listing_start_date'),
        'listing_end_date': serializer.validated_data.get('listing_end_date')
    }

    resp = requests.post(f'{asset_transfer_url}', json=data,  headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
    if resp.ok:
        return Response({'detail': 'Request successfully completed.'}) # TODO: Use the right blockchain url
    else:
        return Response(
            {'detail': f'Request not successful: {resp.text}'})  # TODO josonify respose and pick the relevant message