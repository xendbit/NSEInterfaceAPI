# Generated by Django 3.1.2 on 2022-07-19 15:42

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.CharField(db_column='EMAIL', max_length=100, unique=True)),
                ('username', models.CharField(blank=True, db_column='USERNAME', max_length=100)),
                ('password', models.CharField(db_column='PASSWORD', max_length=100)),
                ('phone_number', models.CharField(db_column='PHONE_NUMBER', max_length=20)),
                ('full_name', models.CharField(blank=True, db_column='FULL_NAME', max_length=100, null=True)),
                ('is_staff', models.BooleanField(db_column='is_staff', default=False)),
                ('is_active', models.BooleanField(blank=True, db_column='IS_ACTIVE')),
                ('is_superuser', models.BooleanField(db_column='IS_SUPERUSER', default=False)),
                ('role', models.CharField(blank=True, choices=[('System Admin', 'System Admin'), ('Investor', 'Investor'), ('Issuer', 'Issuer')], db_column='ROLE', max_length=50, null=True)),
                ('bank_name', models.CharField(db_column='BANK_NAME', max_length=50)),
                ('bank_account_name', models.CharField(db_column='BANK_ACCOUNT_NAME', max_length=100)),
                ('bank_account_number', models.CharField(db_column='BANK_ACCOUNT_NUMBER', max_length=11)),
                ('wallet_account_number', models.CharField(db_column='WALLET_ACCOUNT_NUMBER', max_length=11, null=True)),
                ('bvn', models.CharField(db_column='BVN', max_length=12)),
                ('id_number', models.CharField(db_column='ID_NUMBER', max_length=20)),
                ('id_image_url', models.CharField(blank=True, db_column='ID_IMAGE_URL', default='', max_length=400)),
                ('image_url', models.CharField(blank=True, db_column='IMAGE_URL', default='', max_length=400)),
                ('is_deleted', models.BooleanField(db_column='IS_DELETED', default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='CREATED_AT')),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='UPDATED_AT')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'XB_USER',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ArtExchangeUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='CREATED_AT')),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='UPDATED_AT')),
                ('is_deleted', models.BooleanField(db_column='IS_DELETED', default=False)),
                ('user_id', models.CharField(db_column='USER_ID', max_length=20, unique=True)),
                ('email', models.CharField(db_column='EMAIL', max_length=100, unique=True)),
                ('phone_number', models.CharField(db_column='PHONE_NUMBER', max_length=20)),
                ('fullname', models.CharField(blank=True, db_column='FULLNAME', max_length=100, null=True)),
                ('user_type', models.CharField(blank=True, choices=[('Investor', 'Investor'), ('Issuer', 'Issuer')], db_column='USER_TYPE', max_length=50, null=True)),
                ('address', models.CharField(db_column='ADDRESS', max_length=255)),
                ('date_of_birth', models.DateField(db_column='DATE_OF_BIRTH')),
                ('bank_name', models.CharField(db_column='BANK_NAME', max_length=50, null=True)),
                ('bank_account_name', models.CharField(db_column='BANK_ACCOUNT_NAME', max_length=100, null=True)),
                ('bank_account_number', models.CharField(db_column='BANK_ACCOUNT_NUMBER', max_length=11, null=True)),
                ('wallet_account_number', models.CharField(db_column='WALLET_ACCOUNT_NUMBER', max_length=11)),
                ('bvn', models.CharField(db_column='BVN', max_length=12)),
                ('password', models.CharField(db_column='PASSWORD', max_length=300, null=True)),
                ('private_key', models.CharField(db_column='PRIVATE_KEY', max_length=300, null=True)),
                ('blockchain_address', models.CharField(db_column='BLOCKCHAIN_ADDRESS', max_length=200, null=True)),
                ('blockchain_id', models.IntegerField(db_column='BLOCKCHAIN_ID', null=True)),
            ],
            options={
                'db_table': 'XB_ART_EXCHANGE_USER',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='CREATED_AT')),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='UPDATED_AT')),
                ('is_deleted', models.BooleanField(db_column='IS_DELETED', default=False)),
                ('account_number', models.CharField(db_column='ACCOUNT_NUMBER', max_length=10, unique=True)),
                ('fullname', models.CharField(db_column='FULL_NAME', max_length=200, null=True)),
                ('account_reference', models.CharField(db_column='ACCOUNT_REFERENCE', max_length=200, null=True, unique=True)),
                ('balance', models.DecimalField(db_column='BALANCE', decimal_places=2, default=0.0, max_digits=10)),
                ('bvn', models.CharField(db_column='BVN', max_length=12, null=True, unique=True)),
                ('bank', models.CharField(blank=True, choices=[('011', 'First Bank Plc'), ('014', 'Mainstreet Bank Plc'), ('023', 'CitiBank'), ('070', 'Fidelity Bank Plc'), ('050', 'Ecobank Nigeria Plc'), ('030', 'Heritage Bank Plc'), ('032', 'Union Bank of Nigeria Plc'), ('033', 'United Bank For Africa Plc'), ('232', 'Sterling Bank Plc'), ('035', 'Wema Bank Plc'), ('057', 'Zenith Bank Plc'), ('311', 'Parkway'), ('058', 'GTBank Plc'), ('214', 'First City Monument Bank Plc'), ('215', 'UnityBank Plc'), ('315', 'GTB Mobile Money'), ('082', 'Keystone Bank Plc'), ('084', 'Enterprise Bank Ltd'), ('063', 'Diamond Bank Plc'), ('044', 'Access Bank Nigeria Plc'), ('221', 'StanbicIBTC Bank Plc'), ('068', 'Standard Chartered Bank Nigeria Ltd'), ('322', 'Zenith Mobile'), ('323', 'Access Mobile'), ('401', 'ASO Savings and Loans'), ('304', 'Stanbic Mobile'), ('305', 'PAYCOM'), ('307', 'Ecobank Mobile'), ('309', 'FBN Mobile'), ('301', 'Jaiz Bank'), ('076', 'Polaris Bank'), ('101', 'Providus Bank'), ('100', 'Suntrust Bank'), ('102', 'Titan Trust Bank')], db_column='BANK', max_length=45, null=True)),
                ('restriction_type', models.CharField(choices=[('0', 'No restriction'), ('1', 'Debit restriction'), ('2', 'Credit restriction'), ('3', 'Debit and Credit restrictions')], db_column='RESTRICTION_TYPE', default='1', max_length=1)),
            ],
            options={
                'db_table': 'XB_BANK_ACCOUNT',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BankTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='CREATED_AT')),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='UPDATED_AT')),
                ('is_deleted', models.BooleanField(db_column='IS_DELETED', default=False)),
                ('account_number', models.CharField(db_column='ACCOUNT_NUMBER', max_length=15)),
                ('transaction_type', models.CharField(db_column='TRANSACTION_TYPE', max_length=7)),
                ('narration', models.CharField(db_column='NARRATION', max_length=250)),
                ('time', models.DateTimeField(db_column='TIME', default=datetime.datetime.now)),
                ('amount', models.DecimalField(db_column='AMOUNT', decimal_places=2, max_digits=10)),
                ('transaction_reference', models.CharField(db_column='TRANSACTION_REFERENCE', max_length=50, null=True)),
            ],
            options={
                'db_table': 'XB_BANK_TRANSACTION',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='PendingAssetTransfer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='CREATED_AT')),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='UPDATED_AT')),
                ('is_deleted', models.BooleanField(db_column='IS_DELETED', default=False)),
                ('buyer_id', models.IntegerField(db_column='BUYER_ID', null=True)),
                ('asset_issuer_id', models.IntegerField(db_column='ASSET_ISSUER_ID', null=True)),
                ('seller_id', models.IntegerField(db_column='SELLER_ID')),
                ('asset_name', models.CharField(db_column='ASSET_NAME', max_length=20)),
                ('quantity', models.IntegerField(db_column='QUANTITY')),
                ('unit_price', models.FloatField(db_column='UNIT_PRICE')),
                ('market_type', models.CharField(db_column='MARKET_TYPE', max_length=20)),
            ],
            options={
                'db_table': 'XB_PENDING_ASSET_TRANSFER',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AssetTransfer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='CREATED_AT')),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='UPDATED_AT')),
                ('is_deleted', models.BooleanField(db_column='IS_DELETED', default=False)),
                ('asset_id', models.CharField(db_column='ASSET_ID', max_length=100)),
                ('asset_type', models.CharField(choices=[('Art', 'Art'), ('Estate', 'Estate')], db_column='ASSET_TYPE', max_length=50)),
                ('number_of_tokens', models.IntegerField(db_column='NUMBER_OF_TOKEN')),
                ('value', models.FloatField(db_column='VALUE')),
                ('buyer_id', models.ForeignKey(db_column='BUYER_ID', on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to='xendapp.artexchangeuser')),
                ('seller_id', models.ForeignKey(db_column='SELLER_ID', on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='xendapp.artexchangeuser')),
            ],
            options={
                'db_table': 'XB_ASSET_TRANSFER',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ArtListing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='CREATED_AT')),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='UPDATED_AT')),
                ('is_deleted', models.BooleanField(db_column='IS_DELETED', default=False)),
                ('token_id', models.IntegerField(db_column='TOKEN_ID', null=True)),
                ('asset_id', models.CharField(db_column='ASSET_ID', max_length=20)),
                ('description', models.CharField(db_column='DESCRIPTION', max_length=300)),
                ('asset_type', models.CharField(choices=[('art', 'art'), ('real estate', 'real estate')], db_column='ASSET_TYPE', max_length=15)),
                ('number_of_tokens', models.IntegerField(db_column='NUMBER_OF_TOKEN')),
                ('artwork_value', models.FloatField(db_column='ARTWORK_VALUE')),
                ('qr_code', models.CharField(db_column='QR_CODE', max_length=255, null=True)),
                ('blockchain_id', models.CharField(db_column='BLOCKCHAIN_ID', max_length=10, null=True)),
                ('seller_id', models.ForeignKey(db_column='SELLER_ID', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'XB_ART_LISTING',
                'managed': True,
            },
        ),
    ]
