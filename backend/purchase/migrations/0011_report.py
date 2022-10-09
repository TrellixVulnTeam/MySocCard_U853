# Generated by Django 4.0 on 2022-10-05 20:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_holder_image_ledenbase'),
        ('purchase', '0010_alter_category_products_alter_purchase_orders'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('action', models.CharField(choices=[('Open', 'Open'), ('Close', 'Close')], max_length=50, verbose_name='action')),
                ('total_cash', models.FloatField(verbose_name='total Cash')),
                ('flow_meter1', models.IntegerField(verbose_name='flow meter 1')),
                ('flow_meter2', models.IntegerField(verbose_name='flow meter 2')),
                ('comment', models.TextField(verbose_name='comment')),
                ('Personel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.personel', verbose_name='creator')),
            ],
        ),
    ]