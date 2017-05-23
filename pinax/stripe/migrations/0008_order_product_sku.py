# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-05-23 21:48
from __future__ import unicode_literals

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pinax_stripe', '0007_auto_20170108_1202'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_id', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True)),
                ('amount_returned', models.DecimalField(blank=True, decimal_places=2, default=Decimal('0'), max_digits=9, null=True)),
                ('currency', models.CharField(default='usd', max_length=10)),
                ('livemode', models.BooleanField(default=False)),
                ('metadata', jsonfield.fields.JSONField(null=True)),
                ('selected_shipping_method', models.TextField(blank=True)),
                ('shipping', jsonfield.fields.JSONField(null=True)),
                ('shipping_methods', jsonfield.fields.JSONField(null=True)),
                ('status', models.CharField(max_length=25)),
                ('status_transitions', jsonfield.fields.JSONField(null=True)),
                ('items', jsonfield.fields.JSONField(null=True)),
                ('returns', jsonfield.fields.JSONField(null=True)),
                ('charge', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='pinax_stripe.Charge')),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pinax_stripe.Customer')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_id', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('active', models.BooleanField(default=False)),
                ('attributes', jsonfield.fields.JSONField(blank=True, null=True)),
                ('caption', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('images', jsonfield.fields.JSONField(blank=True, null=True)),
                ('livemode', models.BooleanField(default=False)),
                ('metadata', jsonfield.fields.JSONField(blank=True, null=True)),
                ('name', models.TextField(blank=True)),
                ('package_dimensions', jsonfield.fields.JSONField(blank=True, null=True)),
                ('shippable', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Sku',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_id', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('price', models.DecimalField(decimal_places=2, max_digits=9, null=True)),
                ('currency', models.CharField(default='usd', max_length=10)),
                ('attributes', jsonfield.fields.JSONField(blank=True, null=True)),
                ('image', models.TextField(blank=True, null=True)),
                ('inventory', jsonfield.fields.JSONField(null=True)),
                ('livemode', models.BooleanField(default=False)),
                ('metadata', jsonfield.fields.JSONField(blank=True, null=True)),
                ('package_dimensions', jsonfield.fields.JSONField(blank=True, null=True)),
                ('active', models.BooleanField(default=False)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='skus', to='pinax_stripe.Product')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
