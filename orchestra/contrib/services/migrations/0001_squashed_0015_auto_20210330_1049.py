# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2021-04-22 11:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('services', '0001_initial'), ('services', '0002_auto_20150509_1501'), ('services', '0003_auto_20150917_0942'), ('services', '0004_auto_20160405_1133'), ('services', '0005_auto_20160427_1531'), ('services', '0006_auto_20170528_2005'), ('services', '0007_auto_20170528_2011'), ('services', '0008_auto_20170625_1813'), ('services', '0009_auto_20170625_1840'), ('services', '0010_auto_20170625_1840'), ('services', '0011_auto_20170625_1840'), ('services', '0012_auto_20170625_1841'), ('services', '0013_auto_20190805_1134'), ('services', '0014_auto_20200204_1218'), ('services', '0015_auto_20210330_1049')]

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=256, unique=True, verbose_name='description')),
                ('match', models.CharField(blank=True, help_text="Python <a href='https://docs.python.org/2/library/functions.html#eval'>expression</a> that designates wheter a <tt>content_type</tt> object is related to this service or not, always evaluates <tt>True</tt> when left blank. Related instance can be instantiated with <tt>instance</tt> keyword or <tt>content_type.model_name</tt>.</br><tt>&nbsp;databaseuser.type == 'MYSQL'</tt><br><tt>&nbsp;miscellaneous.active and str(miscellaneous.identifier).endswith(('.org', '.net', '.com'))</tt><br><tt>&nbsp;contractedplan.plan.name == 'association_fee''</tt><br><tt>&nbsp;instance.active</tt>", max_length=256, verbose_name='match')),
                ('handler_type', models.CharField(blank=True, choices=[('', 'Default')], help_text='Handler used for processing this Service. A handler enables customized behaviour far beyond what options here allow to.', max_length=256, verbose_name='handler')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('ignore_superusers', models.BooleanField(default=True, help_text='Designates whether superuser, staff and friend orders are marked as ignored by default or not.', verbose_name='ignore superuser, staff and friend')),
                ('billing_period', models.CharField(blank=True, choices=[('', 'One time service'), ('MONTHLY', 'Monthly billing'), ('ANUAL', 'Anual billing')], default='ANUAL', help_text='Renewal period for recurring invoicing.', max_length=16, verbose_name='billing period')),
                ('billing_point', models.CharField(choices=[('ON_REGISTER', 'Registration date'), ('ON_FIXED_DATE', 'Every January')], default='ON_FIXED_DATE', help_text='Reference point for calculating the renewal date on recurring invoices', max_length=16, verbose_name='billing point')),
                ('is_fee', models.BooleanField(default=False, help_text='Designates whether this service should be billed as membership fee or not', verbose_name='fee')),
                ('order_description', models.CharField(blank=True, help_text="Python <a href='https://docs.python.org/2/library/functions.html#eval'>expression</a> used for generating the description for the bill lines of this services.<br>Defaults to <tt>'%s: %s' % (ugettext(handler.description), instance)</tt>", max_length=256, verbose_name='Order description')),
                ('ignore_period', models.CharField(blank=True, choices=[('', 'Never'), ('ONE_DAY', 'One day'), ('TWO_DAYS', 'Two days'), ('TEN_DAYS', 'Ten days'), ('ONE_MONTH', 'One month')], default='TEN_DAYS', help_text='Period in which orders will be ignored if cancelled. Useful for designating <i>trial periods</i>', max_length=16, verbose_name='ignore period')),
                ('metric', models.CharField(blank=True, help_text="Python <a href='https://docs.python.org/2/library/functions.html#eval'>expression</a> used for obtinging the <i>metric value</i> for the pricing rate computation. Number of orders is used when left blank. Related instance can be instantiated with <tt>instance</tt> keyword or <tt>content_type.model_name</tt>.<br><tt>&nbsp;max((mailbox.resources.disk.allocated or 0) -1, 0)</tt><br><tt>&nbsp;miscellaneous.amount</tt><br><tt>&nbsp;max((account.resources.traffic.used or 0) - getattr(account.miscellaneous.filter(is_active=True, service__name='traffic-prepay').last(), 'amount', 0), 0)</tt>", max_length=256, verbose_name='metric')),
                ('nominal_price', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='nominal price')),
                ('tax', models.PositiveIntegerField(choices=[(0, 'Duty free'), (21, '21%')], default=0, verbose_name='tax')),
                ('pricing_period', models.CharField(blank=True, choices=[('', 'Current value'), ('BILLING_PERIOD', 'Same as billing period'), ('MONTHLY', 'Monthly data'), ('ANUAL', 'Anual data')], default='BILLING_PERIOD', help_text='Time period that is used for computing the rate metric.', max_length=16, verbose_name='pricing period')),
                ('rate_algorithm', models.CharField(choices=[('orchestra.contrib.plans.ratings.step_price', 'Step price'), ('orchestra.contrib.plans.ratings.match_price', 'Match price'), ('orchestra.contrib.plans.ratings.best_price', 'Best price')], default='orchestra.contrib.plans.ratings.step_price', help_text='Algorithm used to interprete the rating table.<br>&nbsp;&nbsp;Step price: All rates with a quantity lower or equal than the metric are applied. Nominal price will be used when initial block is missing.<br>&nbsp;&nbsp;Match price: Only <b>the rate</b> with a) inmediate inferior metric and b) lower price is applied. Nominal price will be used when initial block is missing.<br>&nbsp;&nbsp;Best price: Produces the best possible price given all active rating lines (those with quantity lower or equal to the metric).', max_length=64, verbose_name='rate algorithm')),
                ('on_cancel', models.CharField(choices=[('NOTHING', 'Nothing'), ('DISCOUNT', 'Discount'), ('COMPENSATE', 'Compensat'), ('REFUND', 'Refund')], default='DISCOUNT', help_text='Defines the cancellation behaviour of this service.', max_length=16, verbose_name='on cancel')),
                ('payment_style', models.CharField(choices=[('PREPAY', 'Prepay'), ('POSTPAY', 'Postpay (on demand)')], default='PREPAY', help_text='Designates whether this service should be paid after consumtion (postpay/on demand) or prepaid.', max_length=16, verbose_name='payment style')),
                ('content_type', models.ForeignKey(help_text='Content type of the related service objects.', on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType', verbose_name='content type')),
                ('periodic_update', models.BooleanField(default=False, help_text='Whether a periodic update of this service orders should be performed or not. Needed for <tt>match</tt> definitions that depend on complex model interactions, where <tt>content type</tt> model save and delete operations are not enought.', verbose_name='periodic update')),
            ],
        ),
    ]
