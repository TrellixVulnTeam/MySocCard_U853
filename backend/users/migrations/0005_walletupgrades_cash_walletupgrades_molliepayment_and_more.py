# Generated by Django 4.0 on 2022-11-18 18:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_molliepayments_identifier'),
    ]

    operations = [
        migrations.AddField(
            model_name='walletupgrades',
            name='cash',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='walletupgrades',
            name='molliePayment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='users.molliepayments'),
        ),
        migrations.AddField(
            model_name='walletupgrades',
            name='pin',
            field=models.BooleanField(default=False),
        ),
    ]