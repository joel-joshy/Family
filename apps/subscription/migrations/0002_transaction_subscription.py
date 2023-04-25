# Generated by Django 4.1.7 on 2023-04-24 11:11

import apps.usermanagement.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usermanagement', '0005_subdomain'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('subscription', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('transaction_id', models.CharField(blank=True, max_length=150, null=True, verbose_name='Transaction ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12, null=True, verbose_name='Amount')),
                ('coupon', models.CharField(blank=True, max_length=150, null=True, verbose_name='Coupon')),
                ('completed_date', models.DateTimeField(blank=True, null=True, verbose_name='Completed Date')),
                ('invoice_url', models.URLField(blank=True, null=True, verbose_name='Invoice URL')),
                ('customer_id', models.CharField(blank=True, max_length=150, null=True, verbose_name='Stripe Customer ID')),
                ('details', models.JSONField(blank=True, null=True, verbose_name='Transaction Details')),
                ('family', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='get_transactions', to='usermanagement.family', verbose_name='Family')),
                ('plan', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='get_transactions', to='subscription.plan', verbose_name='Plan')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='get_transactions', to=settings.AUTH_USER_MODEL, verbose_name='User Transaction')),
            ],
            options={
                'verbose_name': 'Transaction',
                'verbose_name_plural': 'Transactions',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('stripe_id', models.CharField(max_length=150, unique=True, verbose_name='Stripe Subscription')),
                ('start_date', models.DateTimeField(verbose_name='Start Date')),
                ('end_date', models.DateTimeField(verbose_name='End Date')),
                ('details', models.JSONField(blank=True, null=True, verbose_name='Subscription Details')),
                ('status', models.CharField(choices=[('active', 'Active'), ('canceled', 'Canceled'), ('incomplete', 'Incomplete'), ('unpaid', 'Unpaid'), ('past_due', 'Past Due'), ('incomplete_expired', 'Incomplete Expired')], default='active', max_length=50, verbose_name='Subscription Status')),
                ('is_trial_plan', models.BooleanField(default=apps.usermanagement.models.Family, verbose_name='Is Trial Plan')),
                ('family', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='get_subscriptions', to='usermanagement.family', verbose_name='Family')),
                ('plan', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='get_subscriptions', to='subscription.plan', verbose_name='Plan')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='get_subscriptions', to=settings.AUTH_USER_MODEL, verbose_name='User Subscription')),
            ],
            options={
                'verbose_name': 'Subscription',
                'verbose_name_plural': 'Subscriptions',
                'ordering': ('-created',),
            },
        ),
    ]
