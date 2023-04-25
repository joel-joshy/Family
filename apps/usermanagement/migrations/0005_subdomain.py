# Generated by Django 4.1.7 on 2023-03-15 06:32

import common.managers
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('usermanagement', '0004_familycontactdetails'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubDomain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Domain Name')),
                ('family', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='get_sub_domain', to='usermanagement.family', verbose_name='Family')),
                ('site', models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='sites.site', verbose_name='Site')),
            ],
            options={
                'verbose_name': 'SubDomain',
                'verbose_name_plural': 'SubDomains',
                'ordering': ('-created',),
            },
            managers=[
                ('objects', common.managers.CurrentSiteManager()),
            ],
        ),
    ]