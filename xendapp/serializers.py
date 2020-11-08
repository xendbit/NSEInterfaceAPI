from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User, ArtExchangeUser, BankAccount, BankTransaction
from .utils import SIX_DIGIT_CODE_LIST


class AdminCreateUserSerializer(serializers.ModelSerializer):
    """UserSerializer class"""
    confirm_password = serializers.CharField(max_length=200, write_only=True)
    role = serializers.ReadOnlyField(source='get_role_display')

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError("passwords do not match")
        return data

    class Meta:
        model = User
        exclude = ['is_superuser', 'last_login']
        write_only_fields = ('password', 'confirm_password')
        read_only_fields = ['id', 'created_at', 'role', 'username', 'is_active', 'is_staff', 'image_url', 'groups', 'user_permissions', 'is_deleted']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=200)




class RegistrationSerializer(serializers.ModelSerializer):
    '''Serializer for validating request body for user registration'''

    class Meta:
        model = ArtExchangeUser
        fields = '__all__'
        read_only_fields = ['is_deleted', 'createdAt', 'updatedAt', 'wallet_account_number']


class BuyRequestSerializer(serializers.Serializer):
    art_id = serializers.IntegerField()
    buyer_id = serializers.CharField()
    seller_id = serializers.CharField()
    issuer_id = serializers.CharField()
    security = serializers.CharField()
    number_of_tokens = serializers.IntegerField()
    unit_price = serializers.FloatField()
    nse_fee = serializers.FloatField()
    sms_fee = serializers.FloatField()
    market_type = serializers.CharField()


class ListRequestSerializer(serializers.Serializer):
    issuer_id = serializers.CharField()
    art_id = serializers.IntegerField()
    security = serializers.CharField()
    number_of_tokens = serializers.IntegerField()
    artwork_value = serializers.FloatField()
    unit_price = serializers.FloatField()
    listing_start_date = serializers.CharField()
    listing_end_date = serializers.CharField()


class FundTransferSerializer(serializers.Serializer):

    from_account_number = serializers.CharField()
    to_account_number = serializers.CharField()
    narration = serializers.CharField()
    amount = serializers.CharField()


class NewAccountSerializer(serializers.Serializer):
    last_name = serializers.CharField()
    first_name = serializers.CharField()
    middle_name = serializers.CharField(required=False)
    bvn = serializers.CharField()
    email = serializers.CharField()


class PasswordChangeSerializer(serializers.Serializer):
    """
    Used by the password-change endpoint.
    """
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

class ProvidusInterBankTransferSerializer(serializers.Serializer):
    recipient_account_name = serializers.CharField()
    amount = serializers.CharField()
    narration = serializers.CharField()
    source_account_name = serializers.CharField()
    recipient_account_number = serializers.CharField()
    recipient_bank = serializers.CharField()

    def validate(self, data):
        if not data.get('recipient_bank') in SIX_DIGIT_CODE_LIST:
            raise serializers.ValidationError(
                f'Invalid bank code provided selected. Bank code must be one of roles. Must be one of {SIX_DIGIT_CODE_LIST}')
        return data

class BankTransactionsSerializer(serializers.ModelSerializer):
    bank = serializers.ReadOnlyField(source='get_bank')

    class Meta:
        model = BankTransaction
        fields = ['bank', 'account_number', 'transaction_type', 'narration', 'time', 'amount']
