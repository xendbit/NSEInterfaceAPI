# Generated by Django 3.1.2 on 2020-12-18 02:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xendapp', '0013_auto_20201217_2135'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='id_number',
            field=models.CharField(db_column='ID_NUMBER', default=0, max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='bank_account_name',
            field=models.CharField(db_column='BANK_ACCOUNT_NAME', max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='bank_account_number',
            field=models.CharField(db_column='BANK_ACCOUNT_NUMBER', max_length=11),
        ),
        migrations.AlterField(
            model_name='user',
            name='bank_name',
            field=models.CharField(db_column='BANK_NAME', max_length=50),
        ),
        migrations.AlterField(
            model_name='user',
            name='bvn',
            field=models.CharField(db_column='BVN', max_length=12),
        ),
        migrations.AlterField(
            model_name='user',
            name='wallet_account_number',
            field=models.CharField(db_column='WALLET_ACCOUNT_NUMBER', max_length=11),
        ),
    ]
