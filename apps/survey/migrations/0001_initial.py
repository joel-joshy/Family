# Generated by Django 4.1.7 on 2023-03-30 10:26

import common.managers
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('usermanagement', '0005_subdomain'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=250, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('demographic_questions', models.JSONField(blank=True, help_text='Demographic Questions and choices in JSON format', null=True, verbose_name='Demographic Questions')),
                ('general_questions', models.JSONField(blank=True, help_text='General Questions and choices in JSON format', null=True, verbose_name='General Questions')),
                ('expiry_date', models.DateField(blank=True, null=True, verbose_name='Expiry Date')),
                ('is_private', models.BooleanField(default=False, verbose_name='Is Private')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('is_published', models.BooleanField(default=False, verbose_name='Is Published')),
                ('link', models.URLField(blank=True, null=True, verbose_name='Link')),
                ('survey_uuid', models.CharField(default=uuid.uuid4, max_length=100, unique=True, verbose_name='Survey UUID')),
                ('qr_code', models.ImageField(blank=True, upload_to='qr_codes', verbose_name='QR Code')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='get_surveys', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('family', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='get_surveys', to='usermanagement.family', verbose_name='Family')),
                ('site', models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='sites.site', verbose_name='Site')),
            ],
            options={
                'verbose_name': 'survey',
                'verbose_name_plural': 'Surveys',
                'ordering': ('-created',),
            },
            managers=[
                ('objects', common.managers.CurrentSiteManager()),
            ],
        ),
    ]
