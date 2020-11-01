from rest_framework import serializers

from .models import User, ArtExchangeUser, BankAccount, BankTransaction


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
        read_only_fields = ['id', 'created_at', 'role', 'username', 'is_active', 'is_staff']
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
        read_only_fields = ['isDeleted', 'createdAt', 'updatedAt', 'wallet_account_number']


class BuyRequestSerializer(serializers.Serializer):
    buyer_id = serializers.CharField()
    seller_id = serializers.CharField()
    security = serializers.CharField()
    number_of_tokens = serializers.IntegerField()
    unit_price = serializers.FloatField()
    nse_fee = serializers.FloatField()
    sms_fee = serializers.FloatField()
    market_type = serializers.CharField()


class ListRequestSerializer(serializers.Serializer):
    investor_id = serializers.CharField()
    security = serializers.CharField()
    number_of_tokens = serializers.IntegerField()
    artwork_value = serializers.FloatField()
    unit_price = serializers.FloatField()
    listing_start_date = serializers.DateField()
    listing_end_date = serializers.DateField()


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