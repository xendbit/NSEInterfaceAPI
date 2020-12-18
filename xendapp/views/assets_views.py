import os

from rest_framework import generics
import requests
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from .. import models, serializers, utils, permissions, filters
from . import sterling_views, providus_views

product_code = os.getenv('STERLING_PRODUCT_CODE')
accountt_officer_code = os.getenv('STERLING_ACCT_OFF_CODE')
asset_transfer_url = os.getenv('ASSET_TRANSFER_URL')
blockchain_domain = os.getenv('BLOCKCHAIN_DOMAIN')
blockchain_api_key = os.getenv('BLOCKCHAIN_API_KEY')
providus_contract_code = os.getenv('PROVIDUS_CONTRACT_CODE')


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

    '''
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

    resp_json, status, bank = sterling_views.create_sterling_account(account_data)
'''

    headers = {
        'api-key': blockchain_api_key
    }

    providus_request_data = {
        'accountReference': f'{bvn}_{fullname}',
        'accountName': fullname,
        'currencyCode': 'NGN',
        'contractCode': providus_contract_code,
        'customerEmail': email,
        'customerName': fullname,
        'bvn': bvn
    }

    resp_json, status, bank = providus_views.providus_reserve_account(providus_request_data)

    if resp_json.get('IsSuccessful'):
        wallet_account_number = resp_json['Message']['AccountNumber']
        user = models.ArtExchangeUser.objects.create(
            user_id=user_id,
            email=email,
            phone_number=phone_number,
            fullname=fullname,
            user_type=user_type,
            address=address,
            date_of_birth=date_of_birth,
            bank_name=bank_name,
            bank_account_name=bank_account_name,
            bank_account_number=bank_account_number,
            wallet_account_number=wallet_account_number,
            bvn=bvn
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

        return Response(
            {'detail': 'Data Successfully processed', 'userId': user_id, 'wallet_account': wallet_account_number,
             'bank': bank})
    else:  # TODO consider using dummy account number and running cron jobs to create accounts later
        return Response(
            {'detail': f'User registration not successful at this time: {resp_json.get("responseMessage")}'},
            status=400)


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

    total_cost = (number_of_tokens * unit_price) + (nse_fee / 2) + sms_fee + 200  # 200 for bank charges
    buyer = models.ArtExchangeUser.objects.get(user_id=buyer_id)
    seller = models.ArtExchangeUser.objects.get(user_id=seller_id)
    issuer = models.ArtExchangeUser.objects.get(user_id=issuer_id)
    buyer_account = models.BankAccount.objects.get(account_number=buyer.wallet_account_number)
    seller_account = models.BankAccount.objects.get(account_number=seller.wallet_account_number)
    asset_transfer_url = f'{blockchain_domain}assets/buy'

    transfer_data = {
        'from_account_number': buyer_account.account_number,
        'to_account_number': seller_account.account_number,
        'narration': f'Payment for {number_of_tokens} units of {security} tokens',
        'amount': unit_price * number_of_tokens
    }

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

    '''
    utils.update_one_sterling_accounts(buyer.wallet_account_number)
    buyer_account.refresh_from_db()

    if buyer_account.balance >= total_cost:

        sterling_resp, status = sterling_views.sterling_transfer(transfer_data)
        if not sterling_resp.get('IsSuccessFul'):
            return Response({'detail': 'Request not successful at this point.'}, status=500)


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
    '''

    if buyer_account.balance < total_cost:
        return Response({'detail': 'Insufficient fund in the account'}, status=400)

    providus_views.virtual_account_transfer(transfer_data)
    blockchain_resp = requests.post(f'{asset_transfer_url}', json=blockchain_data, headers=headers)

    models.AssetTransfer.objects.create(
        seller_id=seller,
        buyer_id=buyer,
        asset_id=art_id,
        asset_type='Art',
        number_of_tokens=number_of_tokens,
        value=number_of_tokens * unit_price
    )

    if not blockchain_resp.ok:
        models.PendingAssetTransfer.objects.create(
            buyer_id=blockchain_data.get('buyerId'),
            asset_issuer_id=blockchain_data.get('assetIssuerId'),
            seller_id=blockchain_data.get('sellerId'),
            asset_name=blockchain_data.get('assetName'),
            quantity=blockchain_data.get('quantity'),
            unit_price=blockchain_data.get('price'),
            market_type=blockchain_data.get('marketType')
        )

    return Response({'detail': f'Request successful', 'security': security, 'numberOfUnits': number_of_tokens})


@swagger_auto_schema(method='post', request_body=serializers.ListRequestSerializer)
@api_view(http_method_names=['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsArtexchange])
def asset_listing(request):
    # TODO update the permission_class to check for the request origin, in Production

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

    asset_listing_url = f'{blockchain_domain}assets/new'
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
        else:
            error_input = error
        return Response({'detail': f'Request not successful: {error_input}'}, status=500)


class AssetUserListView(generics.ListAPIView):
    '''All Asset Users'''

    serializer_class = serializers.RegistrationSerializer
    filterset_class = filters.AssetsUserFilter

    def get_queryset(self):
        return models.ArtExchangeUser.objects.filter(is_deleted=False)


class AssetTransferListView(generics.ListAPIView):
    '''All Asset Transfers'''

    serializer_class = serializers.AssetTransferSerializer
    filterset_class = filters.AssetTransferFilter

    def get_queryset(self):
        return models.AssetTransfer.objects.filter(is_deleted=False).order_by('-created_at')


class AssetListingListView(generics.ListAPIView):
    '''All Asset Listings'''

    serializer_class = serializers.AssetListingSerializer
    # filterset_class = filters.AssetTransferFilter

    def get_queryset(self):
        return models.ArtListing.objects.filter(is_deleted=False).order_by('-created_at')



