# Generated by Django 4.0 on 2022-10-01 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0009_alter_category_products'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='products',
            field=models.ManyToManyField(blank=True, related_name='cat_products', to='purchase.Product'),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='orders',
            field=models.ManyToManyField(related_name='ordered', to='purchase.Order'),
        ),
    ]
