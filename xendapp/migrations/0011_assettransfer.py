# Generated by Django 3.1.2 on 2020-11-19 15:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('xendapp', '0010_remove_bankaccount_account_type'),
    ]

    operations = [
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
    ]
