# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2021-04-22 11:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields
import orchestra.core.validators


class Migration(migrations.Migration):

    replaces = [('saas', '0001_initial'), ('saas', '0002_auto_20151001_0923'), ('saas', '0003_auto_20170528_2011'), ('saas', '0004_auto_20210422_1108')]

    initial = True

    dependencies = [
        ('databases', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SaaS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.CharField(choices=[('bscw', 'BSCW'), ('DokuWikiService', 'Dowkuwiki'), ('DrupalService', 'Drupal'), ('gitlab', 'GitLab'), ('MoodleService', 'Moodle'), ('seafile', 'SeaFile'), ('WordPressService', 'WordPress'), ('phplist', 'phpList')], max_length=32, verbose_name='service')),
                ('name', models.CharField(help_text='Required. 64 characters or fewer. Letters, digits and ./-/_ only.', max_length=64, validators=[orchestra.core.validators.validate_username], verbose_name='Name')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this service should be treated as active. ', verbose_name='active')),
                ('data', jsonfield.fields.JSONField(default={}, help_text='Extra information dependent of each service.', verbose_name='data')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saas', to=settings.AUTH_USER_MODEL, verbose_name='account')),
                ('database', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databases.Database')),
                ('custom_url', models.URLField(blank=True, help_text='Optional and alternative URL for accessing this service instance. A related website will be automatically configured if needed.', verbose_name='custom URL')),
            ],
            options={
                'verbose_name_plural': 'SaaS',
                'verbose_name': 'SaaS',
            },
        ),
        migrations.AlterUniqueTogether(
            name='saas',
            unique_together=set([('name', 'service')]),
        ),
        migrations.AlterField(
            model_name='saas',
            name='service',
            field=models.CharField(choices=[('bscw', 'BSCW'), ('dokuwiki', 'Dowkuwiki'), ('drupal', 'Drupal'), ('gitlab', 'GitLab'), ('moodle', 'Moodle'), ('seafile', 'SeaFile'), ('wordpress', 'WordPress'), ('phplist', 'phpList')], max_length=32, verbose_name='service'),
        ),
        migrations.AlterField(
            model_name='saas',
            name='custom_url',
            field=models.URLField(blank=True, help_text='Optional and alternative URL for accessing this service instance. i.e. <tt>https://wiki.mydomain/doku/</tt><br>A related website will be automatically configured if needed.', verbose_name='custom URL'),
        ),
        migrations.AlterField(
            model_name='saas',
            name='name',
            field=models.CharField(help_text='Required. 64 characters or fewer. Letters, digits and ./- only.', max_length=64, validators=[orchestra.core.validators.validate_hostname], verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='saas',
            name='service',
            field=models.CharField(choices=[('bscw', 'BSCW'), ('dokuwiki', 'Dowkuwiki'), ('drupal', 'Drupal'), ('gitlab', 'GitLab'), ('moodle', 'Moodle'), ('wordpress', 'WordPress'), ('nextcloud', 'nextCloud'), ('owncloud', 'ownCloud'), ('phplist', 'phpList')], max_length=32, verbose_name='service'),
        ),
        migrations.AlterField(
            model_name='saas',
            name='database',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='databases.Database'),
        ),
    ]
