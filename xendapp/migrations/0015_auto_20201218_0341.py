# Generated by Django 3.1.2 on 2020-12-18 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xendapp', '0014_auto_20201218_0328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='wallet_account_number',
            field=models.CharField(db_column='WALLET_ACCOUNT_NUMBER', max_length=11, null=True),
        ),
    ]