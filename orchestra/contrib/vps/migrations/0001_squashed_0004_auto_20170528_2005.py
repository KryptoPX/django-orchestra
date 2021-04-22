# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2021-04-22 11:26
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import orchestra.core.validators


class Migration(migrations.Migration):

    replaces = [('vps', '0001_initial'), ('vps', '0002_auto_20150804_1524'), ('vps', '0003_vps_is_active'), ('vps', '0004_auto_20170528_2005')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='VPS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hostname', models.CharField(max_length=256, unique=True, validators=[orchestra.core.validators.validate_hostname], verbose_name='hostname')),
                ('type', models.CharField(choices=[('openvz', 'OpenVZ container'), ('lxc', 'LXC container')], default='lxc', max_length=64, verbose_name='type')),
                ('template', models.CharField(choices=[('debian7', 'Debian 7 - Wheezy'), ('placeholder', 'LXC placeholder')], default='placeholder', help_text='Initial template.', max_length=64, verbose_name='template')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vpss', to=settings.AUTH_USER_MODEL, verbose_name='Account')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
            ],
            options={
                'verbose_name': 'VPS',
                'verbose_name_plural': 'VPSs',
            },
        ),
    ]
