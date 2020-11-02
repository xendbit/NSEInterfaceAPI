from datetime import datetime

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import PermissionsMixin

from xendapp.utils import BANK_CODES_CHOICES


class UserManager(BaseUserManager):
    """
    users can only be created when all required fields are provided.
    """

    def create_user(
            self,
            email=None,
            password=None,
            **extra_fields
    ):
        """
        Create and return a `User` with an email and password.
        """

        if not email:
            raise TypeError('Users must have an email address.')

        if not password:
            raise TypeError('Users must have a password.')

        user = self.model(
            email=self.normalize_email(email),
            username=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, first_name=None, last_name=None, email=None, password=None):
        """Create a `User` who is also a superuser"""

        if not email:
            raise TypeError('Superusers must have an email address.')

        if not password:
            raise TypeError('Superusers must have a password.')

        user = self.model(email=self.normalize_email(email))
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

class BaseAbstractModel(models.Model):
    """
    This model defines base models that implements common fields like:
    created_at
    updated_at
    is_deleted
    """

    created_at = models.DateTimeField(db_column='CREATED_AT', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='UPDATED_AT', auto_now=True)
    is_deleted = models.BooleanField(db_column='IS_DELETED', default=False)

    def soft_delete(self):
        """Soft delete a model instance"""
        self.is_deleted = True
        self.save()

    class Meta:
        abstract = True
        ordering = ['-created_at']


def validate_foreign_key(value):
    '''Checks that a record is not created that links to a deleted parent in FK relationship'''
    if value.is_deleted:
        raise ValidationError(
            f'The provided {type(value).__name__.lower()} record is deleted: {value}',
            params={'value': value},
        )


class User(PermissionsMixin, AbstractBaseUser):
    ROLE_CHOICES = [
        ('System Admin', 'System Admin'),
    ]

    email = models.CharField(db_column='EMAIL', unique=True, max_length=100)
    username = models.CharField(max_length=100, db_column='USERNAME', blank=True)
    password = models.CharField(db_column='PASSWORD', max_length=100)
    phone_number = models.CharField(db_column='PHONE_NUMBER', max_length=20)
    full_name = models.CharField(db_column='FULL_NAME', max_length=100, blank=True, null=True)
    is_staff = models.BooleanField(db_column='is_staff', default=False)
    is_active = models.BooleanField(db_column='IS_ACTIVE', blank=True)
    is_superuser = models.BooleanField(db_column='IS_SUPERUSER', default=False)
    role = models.CharField(max_length=50, db_column='ROLE', null=True, blank=True, choices=ROLE_CHOICES)
    image_url = models.CharField(max_length=400, db_column='IMAGE_URL', blank=True, default='')
    is_deleted = models.BooleanField(db_column='IS_DELETED', default=False)
    created_at = models.DateTimeField(db_column='CREATED_AT', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='UPDATED_AT', auto_now=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    class Meta:
        managed = True
        db_table = 'XB_USER'


class ArtExchangeUser(BaseAbstractModel):
    ROLE_CHOICES = [
        ('Investor', 'Investor'),
        ('Issuer', 'Issuer')
    ]

    user_id = models.CharField(db_column='USER_ID', max_length=20, unique=True)
    email = models.CharField(db_column='EMAIL', unique=True, max_length=100)
    phone_number = models.CharField(db_column='PHONE_NUMBER', max_length=20)
    fullname = models.CharField(db_column='FULLNAME', max_length=100, blank=True, null=True)
    user_type = models.CharField(max_length=50, db_column='USER_TYPE', null=True, blank=True, choices=ROLE_CHOICES)
    address = models.CharField(db_column='ADDRESS', max_length=255)
    date_of_birth = models.DateField(db_column='DATE_OF_BIRTH')
    bank_name = models.CharField(db_column='BANK_NAME', max_length=50, null=True)
    bank_account_name = models.CharField(max_length=100, db_column='BANK_ACCOUNT_NAME', null=True)
    bank_account_number = models.CharField(max_length=11, db_column='BANK_ACCOUNT_NUMBER', null=True)
    wallet_account_number = models.CharField(max_length=11, db_column='WALLET_ACCOUNT_NUMBER')
    bvn = models.CharField(max_length=12, db_column='BVN')

    class Meta:
        managed = True
        db_table = 'XB_ART_EXCHANGE_USER'


class ArtListing(BaseAbstractModel):

    seller_id = models.ForeignKey(ArtExchangeUser, on_delete=models.CASCADE, db_column='SELLER_ID')
    security = models.CharField(db_column='SECURITY', unique=True, max_length=100)
    number_of_tokens = models.IntegerField(db_column='NUMBER_OF_TOKEN')
    artwork_value = models.FloatField(db_column='ARTWORK_VALUE')

    class Meta:
        managed = True
        db_table = 'XB_ART_LISTING'


class BankAccount(BaseAbstractModel):
    account_number = models.CharField(max_length=10, db_column='ACCOUNT_NUMBER', unique=True)
    fullname = models.CharField(max_length=200, db_column='FULL_NAME', null=True)
    account_reference = models.CharField(max_length=200, db_column='ACCOUNT_REFERENCE', unique=True, null=True)
    account_type = models.CharField(max_length=20, db_column='ACCOUNT_TYPE', null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, db_column='BALANCE')
    bvn = models.CharField(max_length=12, db_column='BVN', unique=True, null=True)
    bank = models.CharField(db_column='BANK', max_length=45, choices=BANK_CODES_CHOICES, blank=True, null=True)
    restriction_type = models.CharField(db_column='RESTRICTION_TYPE', default='1', max_length=1,
                                        choices=[
                                            ('0', 'No restriction'),
                                            ('1', 'Debit restriction'),
                                            ('2', 'Credit restriction'),
                                            ('3', 'Debit and Credit restrictions')
                                        ])

    class Meta:
        managed = True
        db_table = 'XB_BANK_ACCOUNT'

    def date_created(self):
        return self.created_at.date()


class BankTransaction(BaseAbstractModel):
    account_number = models.CharField(max_length=15, db_column='ACCOUNT_NUMBER')
    transaction_type = models.CharField(max_length=7, db_column='TRANSACTION_TYPE')
    narration = models.CharField(max_length=250, db_column='NARRATION')
    time = models.DateTimeField(db_column='TIME', default=datetime.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2, db_column='AMOUNT')
    transaction_reference = models.CharField(max_length=50, db_column='TRANSACTION_REFERENCE', null=True)

    def get_bank(self):
        account = BankAccount.objects.get(account_number=self.account_number)
        return account.bank

    class Meta:
        managed = True
        db_table = 'XB_BANK_TRANSACTION'

