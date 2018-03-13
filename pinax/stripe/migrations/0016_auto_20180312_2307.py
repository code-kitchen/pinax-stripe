# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-03-12 23:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pinax_stripe', '0015_order_product_sku'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_id', models.CharField(max_length=191, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('metadata', jsonfield.fields.JSONField(blank=True, null=True)),
                ('object', models.CharField(choices=[('subscription_item', 'subscription_item'), ('plan', 'plan')], default='subscription_item', max_length=20)),
                ('quantity', models.IntegerField(blank=True, null=True)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscription_items', to='pinax_stripe.Plan')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='subscription',
            name='plan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pinax_stripe.Plan'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='quantity',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='subscriptionitem',
            name='subscription',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='pinax_stripe.Subscription'),
        ),
    ]
