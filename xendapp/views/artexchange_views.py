import os
import random
import string

import requests
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from .. import models, serializers, utils, permissions
from . import sterling_views

product_code = os.getenv('STERLING_PRODUCT_CODE')
accountt_officer_code = os.getenv('STERLING_ACCT_OFF_CODE')
asset_transfer_url = os.getenv('ASSET_TRANSFER_URL')
blockchain_domain = os.getenv('BLOCKCHAIN_DOMAIN')
blockchain_api_key = os.getenv('BLOCKCHAIN_API_KEY')


@swagger_auto_schema(method='post', request_body=serializers.RegistrationSerializer)
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

    headers = {
        'api-key': blockchain_api_key
    }

    resp_json, status = sterling_views.create_sterling_account(account_data)
    wallet_account_number = resp_json['Message']['AccountNumber']
    if resp_json.get('IsSuccessful'):
        user = models.ArtExchangeUser.objects.create(
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

        blockchain_url = f'{blockchain_domain}user/new-address/{user.id}'
        blockchain_resp = requests.get(blockchain_url, headers=headers)
        if blockchain_resp.ok:

            resp_json = blockchain_resp.json()
            password = resp_json.get('password')
            private_key = resp_json.get('privateKey')
            blockchain_address = resp_json.get('address')
            blockchain_id = resp_json.get('id')

            models.ArtExchangeUser.objects.filter(id=user.id).update(
                password=password,
                blockchain_id=blockchain_id,
                blockchain_address=blockchain_address,
                private_key=private_key
            )
        else:
            return Response({'detail': blockchain_resp.text}, status=500)

        return Response({'detail': 'Data Successfully processed', 'userId': user_id, 'wallet_account': wallet_account_number })
    else: # TODO consider using dummy account number and running cron jobs to create accounts later
        return Response({'detail': 'User registration not successful at this time.'}, status=500)


@swagger_auto_schema(method='post', request_body=serializers.BuyRequestSerializer)
@api_view(http_method_names=['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsArtexchange])
def asset_buy_request(request):
    '''Gets called when an investor places an asset buy request'''

    data = request.data
    serializer = serializers.BuyRequestSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    art_id = serializer.validated_data.get('art_id')
    buyer_id = serializer.validated_data.get('buyer_id')
    seller_id = serializer.validated_data.get('seller_id')
    issuer_id = serializer.validated_data.get('issuer_id')
    security = serializer.validated_data.get('security')
    number_of_tokens = serializer.validated_data.get('number_of_tokens')
    unit_price = serializer.validated_data.get('unit_price')
    nse_fee = serializer.validated_data.get('nse_fee')
    sms_fee = serializer.validated_data.get('sms_fee')
    market_type = serializer.validated_data.get('market_type')

    total_cost = (number_of_tokens * unit_price) + (nse_fee/2) + sms_fee + 200 # 200 for bank charges
    buyer = models.ArtExchangeUser.objects.get(user_id=buyer_id)
    seller = models.ArtExchangeUser.objects.get(user_id=seller_id)
    issuer = models.ArtExchangeUser.objects.get(user_id=issuer_id)
    buyer_account = models.BankAccount.objects.get(account_number=buyer.wallet_account_number)
    seller_account = models.BankAccount.objects.get(account_number=seller.wallet_account_number)
    utils.update_one_sterling_accounts(buyer.wallet_account_number)
    buyer_account.refresh_from_db()
    asset_transfer_url = f'{blockchain_domain}assets/buy'

    if buyer_account.balance >= total_cost:
        sterling_transfer_data = {
            'from_account_number': buyer_account.account_number,
            'to_account_number': seller_account.account_number,
            'narration': f'Payment for {number_of_tokens} units of {security} tokens',
            'amount': unit_price * number_of_tokens
        }

        sterling_resp, status = sterling_views.sterling_transfer(sterling_transfer_data)
        if not sterling_resp.get('IsSuccessFul'):
            return Response({'detail': 'Request not successful at this point.'}, status=500)

        blockchain_data = {
            'tokenId': art_id,
            'buyerId': buyer.id,
            'assetIssuerId': issuer.id,
            'sellerId': seller.id,
            'assetName': security,
            'quantity': number_of_tokens,
            'price': unit_price,
            'marketType': market_type
        }

        headers = {
            'api-key': blockchain_api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        resp = requests.post(f'{asset_transfer_url}', json=blockchain_data, headers=headers)

        if not resp.ok:
            models.PendingAssetTransfer.objects.create(
                buyer_id=blockchain_data.get('buyerId'),
                asset_issuer_id = blockchain_data.get('assetIssuerId'),
                seller_id=blockchain_data.get('sellerId'),
                asset_name=blockchain_data.get('assetName'),
                quantity=blockchain_data.get('quantity'),
                unit_price=blockchain_data.get('price'),
                market_type=blockchain_data.get('marketType')
            )

        return Response({'detail': f'Request successful', 'security': security, 'numberOfUnits': number_of_tokens})

    return Response({'detail': 'Insufficient fund in the account'}, status=400)


@swagger_auto_schema(method='post', request_body=serializers.ListRequestSerializer)
@api_view(http_method_names=['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsArtexchange])
def asset_listing(request):

    print('kkkkk', request.META.get('REMOTE_ADDR'), request.META.get('REMOTE_HOST'))
    # TODO update the permission_class to check for the request origin

    data = request.data
    serializer = serializers.ListRequestSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    art_id = serializer.validated_data.get('art_id')
    security = serializer.validated_data.get('security')
    issuer_id = serializer.validated_data.get('issuer_id')
    issuer = models.ArtExchangeUser.objects.get(user_id=issuer_id)
    number_of_tokens = serializer.validated_data.get('number_of_tokens')
    price = serializer.validated_data.get('unit_price')
    artwork_value = number_of_tokens * price

    data = {
        'tokenId': art_id,
        'symbol': security,
        'issuerId': issuer.id,
        'name': security,
        'totalQuantity': number_of_tokens,
        'description': f'Art {security} issued by {issuer.fullname}',
        'price': price,
        'listing_start_date': serializer.validated_data.get('listing_start_date'),
        'listing_end_date': serializer.validated_data.get('listing_end_date'),
        'decimal': 0
    }

    headers = {
        'api-key': blockchain_api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    asset_listing_url =  f'{blockchain_domain}assets/new'
    resp = requests.post(f'{asset_listing_url}', json=data, headers=headers)
    if resp.ok:
        qr_code = utils.generate_qrcode(serializer.validated_data.get('security'))
        models.ArtListing.objects.create(
            seller_id=issuer,
            security=security,
            number_of_tokens=number_of_tokens,
            artwork_value=artwork_value,
            blockchain_id=resp.json().get('id'),
            qr_code=qr_code
        )
        return Response({'detail': 'Asset listing successfully completed.', 'assetId': art_id, 'qr_code': qr_code})
    else:
        error = resp.json().get("error")
        if type(error) is list:
            error_input = error[0]
        else: error_input = error
        return Response({'detail': f'Request not successful: {error_input}'}, status=500)
