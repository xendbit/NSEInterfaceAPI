# Generated by Django 3.1.2 on 2020-11-02 20:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('xendapp', '0002_auto_20201101_1621'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArtListing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='CREATED_AT')),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='UPDATED_AT')),
                ('is_deleted', models.BooleanField(db_column='IS_DELETED', default=False)),
                ('security', models.CharField(db_column='SECURITY', max_length=100, unique=True)),
                ('number_of_tokens', models.IntegerField(db_column='NUMBER_OF_TOKEN')),
                ('artwork_value', models.FloatField(db_column='ARTWORK_VALUE')),
                ('seller_id', models.ForeignKey(db_column='SELLER_ID', on_delete=django.db.models.deletion.CASCADE, to='xendapp.artexchangeuser')),
            ],
            options={
                'db_table': 'XB_ART_LISTING',
                'managed': True,
            },
        ),
    ]
