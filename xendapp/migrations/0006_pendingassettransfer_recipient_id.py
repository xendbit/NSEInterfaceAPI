# Generated by Django 3.1.2 on 2020-11-04 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xendapp', '0005_auto_20201104_0917'),
    ]

    operations = [
        migrations.AddField(
            model_name='pendingassettransfer',
            name='recipient_id',
            field=models.IntegerField(db_column='RECIPIENT_ID', null=True),
        ),
    ]