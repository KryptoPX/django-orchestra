import calendar
import datetime
import decimal

from dateutil import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from orchestra.utils import plugins
from orchestra.utils.python import AttributeDict

from . import settings, helpers


class ServiceHandler(plugins.Plugin):
    """
    Separates all the logic of billing handling from the model allowing to better
    customize its behaviout
    """
    
    model = None
    
    __metaclass__ = plugins.PluginMount
    
    def __init__(self, service):
        self.service = service
    
    def __getattr__(self, attr):
        return getattr(self.service, attr)
    
    @classmethod
    def get_plugin_choices(cls):
        choices = super(ServiceHandler, cls).get_plugin_choices()
        return [('', _("Default"))] + choices
    
    def get_content_type(self):
        if not self.model:
            return self.content_type
        app_label, model = self.model.split('.')
        return ContentType.objects.get_by_natural_key(app_label, model.lower())
    
    def matches(self, instance):
        safe_locals = {
            instance._meta.model_name: instance
        }
        return eval(self.match, safe_locals)
    
    def get_metric(self, instance):
        if self.metric:
            safe_locals = {
                instance._meta.model_name: instance
            }
            return eval(self.metric, safe_locals)
    
    def get_billing_point(self, order, bp=None, **options):
        not_cachable = self.billing_point == self.FIXED_DATE and options.get('fixed_point')
        if not_cachable or bp is None:
            bp = options.get('billing_point', timezone.now().date())
            if not options.get('fixed_point'):
                msg = ("Support for '%s' period and '%s' point is not implemented"
                    % (self.get_billing_period_display(), self.get_billing_point_display()))
                if self.billing_period == self.MONTHLY:
                    date = bp
                    if self.payment_style == self.PREPAY:
                        date += relativedelta.relativedelta(months=1)
                    else:
                        date = timezone.now().date()
                    if self.billing_point == self.ON_REGISTER:
                        day = order.registered_on.day
                    elif self.billing_point == self.FIXED_DATE:
                        day = 1
                    else:
                        raise NotImplementedError(msg)
                    bp = datetime.datetime(year=date.year, month=date.month, day=day,
                        tzinfo=timezone.get_current_timezone()).date()
                elif self.billing_period == self.ANUAL:
                    if self.billing_point == self.ON_REGISTER:
                        month = order.registered_on.month
                        day = order.registered_on.day
                    elif self.billing_point == self.FIXED_DATE:
                        month = settings.SERVICES_SERVICE_ANUAL_BILLING_MONTH
                        day = 1
                    else:
                        raise NotImplementedError(msg)
                    year = bp.year
                    if self.payment_style == self.POSTPAY:
                        year = bp.year - relativedelta.relativedelta(years=1)
                    if bp.month >= month:
                        year = bp.year + 1
                    bp = datetime.datetime(year=year, month=month, day=day,
                        tzinfo=timezone.get_current_timezone()).date()
                elif self.billing_period == self.NEVER:
                    bp = order.registered_on
                else:
                    raise NotImplementedError(msg)
        if self.on_cancel != self.NOTHING and order.cancelled_on and order.cancelled_on < bp:
            return order.cancelled_on
        return bp
    
    def get_price_size(self, ini, end):
        rdelta = relativedelta.relativedelta(end, ini)
        if self.billing_period == self.MONTHLY:
            size = rdelta.years * 12
            size += rdelta.months
            days = calendar.monthrange(end.year, end.month)[1]
            size += decimal.Decimal(rdelta.days)/days
        elif self.billing_period == self.ANUAL:
            size = rdelta.years
            size += decimal.Decimal(rdelta.months)/12
            days = 366 if calendar.isleap(end.year) else 365
            size += decimal.Decimal(rdelta.days)/days
        elif self.billing_period == self.NEVER:
            size = 1
        else:
            raise NotImplementedError
        return decimal.Decimal(size)
    
    def get_pricing_slots(self, ini, end):
        day = 1
        month = settings.SERVICES_SERVICE_ANUAL_BILLING_MONTH
        if self.billing_point == self.ON_REGISTER:
            day = ini.day
            month = ini.month
        period = self.get_pricing_period()
        rdelta = self.get_pricing_rdelta()
        if period == self.MONTHLY:
            ini = datetime.datetime(year=ini.year, month=ini.month, day=day,
                                    tzinfo=timezone.get_current_timezone()).date()
        elif period == self.ANUAL:
            ini = datetime.datetime(year=ini.year, month=month, day=day,
                                    tzinfo=timezone.get_current_timezone()).date()
        elif period == self.NEVER:
            yield ini, end
            raise StopIteration
        else:
            raise NotImplementedError
        while True:
            next = ini + rdelta
            yield ini, next
            if next >= end:
                break
            ini = next
    
    def get_pricing_rdelta(self):
        period = self.get_pricing_period()
        if period == self.MONTHLY:
            return relativedelta.relativedelta(months=1)
        elif period == self.ANUAL:
            return relativedelta.relativedelta(years=1)
        elif period == self.NEVER:
            return None
    
    def generate_discount(self, line, dtype, price):
        line.discounts.append(AttributeDict(**{
            'type': dtype,
            'total': price,
        }))
    
    def generate_line(self, order, price, *dates, **kwargs):
        if len(dates) == 2:
            ini, end = dates
        elif len(dates) == 1:
            ini, end = dates[0], dates[0]
        else:
            raise AttributeError
        metric = kwargs.pop('metric', 1)
        discounts = kwargs.pop('discounts', ())
        computed = kwargs.pop('computed', False)
        if kwargs:
            raise AttributeError
        
        size = self.get_price_size(ini, end)
        if not computed:
            price = price * size
        subtotal = self.nominal_price * size * metric
        line = AttributeDict(**{
            'order': order,
            'subtotal': subtotal,
            'ini': ini,
            'end': end,
            'size': size,
            'metric': metric,
            'discounts': [],
        })
        discounted = 0
        for dtype, dprice in discounts:
            self.generate_discount(line, dtype, dprice)
            discounted += dprice
        subtotal += discounted
        if subtotal > price:
            self.generate_discount(line, 'volume', price-subtotal)
        return line
    
    def assign_compensations(self, givers, receivers, **options):
        compensations = []
        for order in givers:
            if order.billed_until and order.cancelled_on and order.cancelled_on < order.billed_until:
                interval = helpers.Interval(order.cancelled_on, order.billed_until, order)
                compensations.append(interval)
        for order in receivers:
            if not order.billed_until or order.billed_until < order.new_billed_until:
                # receiver
                ini = order.billed_until or order.registered_on
                end = order.cancelled_on or datetime.date.max
                interval = helpers.Interval(ini, end)
                compensations, used_compensations = helpers.compensate(interval, compensations)
                order._compensations = used_compensations
                for comp in used_compensations:
                    # TODO get min right
                    comp.order.new_billed_until = min(comp.order.billed_until, comp.ini,
                            getattr(comp.order, 'new_billed_until', datetime.date.max))
        if options.get('commit', True):
            for order in givers:
                if hasattr(order, 'new_billed_until'):
                    order.billed_until = order.new_billed_until
                    order.save()
    
    def apply_compensations(self, order, only_beyond=False):
        dsize = 0
        discounts = ()
        ini = order.billed_until or order.registered_on
        end = order.new_billed_until
        beyond = end
        cend = None
        for comp in getattr(order, '_compensations', []):
            intersect = comp.intersect(helpers.Interval(ini=ini, end=end))
            if intersect:
                cini, cend = intersect.ini, intersect.end
                if comp.end > beyond:
                    cend = comp.end
                    if only_beyond:
                        cini = beyond
                elif not only_beyond:
                    continue
                dsize += self.get_price_size(cini, cend)
            # Extend billing point a little bit to benefit from a substantial discount
            elif comp.end > beyond and (comp.end-comp.ini).days > 3*(comp.ini-beyond).days:
                cend = comp.end
                dsize += self.get_price_size(comp.ini, cend)
        return dsize, cend
    
    def get_register_or_renew_events(self, porders, ini, end):
        counter = 0
        for order in porders:
            bu = getattr(order, 'new_billed_until', order.billed_until)
            if bu:
                if order.registered_on > ini and order.registered_on <= end:
                    counter += 1
                if order.registered_on != bu and bu > ini and bu <= end:
                    counter += 1
                if order.billed_until and order.billed_until != bu:
                    if order.registered_on != order.billed_until and order.billed_until > ini and order.billed_until <= end:
                        counter += 1
        return counter
    
    def bill_concurrent_orders(self, account, porders, rates, ini, end):
        # Concurrent
        # Get pricing orders
        priced = {}
        for ini, end, orders in helpers.get_chunks(porders, ini, end):
            size = self.get_price_size(ini, end)
            metric = len(orders)
            interval = helpers.Interval(ini=ini, end=end)
            for position, order in enumerate(orders, start=1):
                csize = 0
                compensations = getattr(order, '_compensations', [])
                # Compensations < new_billed_until
                for comp in compensations:
                    intersect = comp.intersect(interval)
                    if intersect:
                        csize += self.get_price_size(intersect.ini, intersect.end)
                price = self.get_price(account, metric, position=position, rates=rates)
                price = price * size
                cprice = price * csize
                if order in priced:
                    priced[order][0] += price
                    priced[order][1] += cprice
                else:
                    priced[order] = (price, cprice)
        lines = []
        for order, prices in priced.iteritems():
            discounts = ()
            # Generate lines and discounts from order.nominal_price
            price, cprice = prices
            # Compensations > new_billed_until
            dsize, new_end = self.apply_compensations(order, only_beyond=True)
            cprice += dsize*price
            if cprice:
                discounts = (
                    ('compensation', -cprice),
                )
                if new_end:
                    size = self.get_price_size(order.new_billed_until, new_end)
                    price += price*size
                    order.new_billed_until = new_end
            line = self.generate_line(order, price, ini, new_end or end, discounts=discounts, computed=True)
            lines.append(line)
        return lines
    
    def bill_registered_or_renew_events(self, account, porders, rates):
        # Before registration
        lines = []
        rdelta = self.get_pricing_rdelta()
        if not rdelta:
            raise NotImplementedError
        for position, order in enumerate(porders, start=1):
            if hasattr(order, 'new_billed_until'):
                pend = order.billed_until or order.registered_on
                pini = pend - rdelta
                metric = self.get_register_or_renew_events(porders, pini, pend)
                price = self.get_price(account, metric, position=position, rates=rates)
                ini = order.billed_until or order.registered_on
                end = order.new_billed_until
                discounts = ()
                dsize, new_end = self.apply_compensations(order)
                if dsize:
                    discounts=(('compensation', -dsize*price),)
                    if new_end:
                        order.new_billed_until = new_end
                        end = new_end
                size = self.get_price_size(ini, end)
                line = self.generate_line(order, price, ini, end, discounts=discounts)
                lines.append(line)
        return lines
    
    def bill_with_orders(self, orders, account, **options):
        # For the "boundary conditions" just think that:
        #   date(2011, 1, 1) is equivalent to datetime(2011, 1, 1, 0, 0, 0)
        #   In most cases:
        #       ini >= registered_date, end < registered_date
        # boundary lookup and exclude cancelled and billed
        orders_ = []
        bp = None
        ini = datetime.date.max
        end = datetime.date.min
        for order in orders:
            cini = order.registered_on
            if order.billed_until:
                # exclude cancelled and billed
                if self.on_cancel != self.REFOUND:
                    if order.cancelled_on and order.billed_until > order.cancelled_on:
                        continue
                cini = order.billed_until
            bp = self.get_billing_point(order, bp=bp, **options)
            order.new_billed_until = bp
            ini = min(ini, cini)
            end = max(end, bp)
            orders_.append(order)
        orders = orders_
        
        # Compensation
        related_orders = account.orders.filter(service=self.service)
        if self.on_cancel == self.COMPENSATE:
            # Get orders pending for compensation
            givers = list(related_orders.givers(ini, end))
            givers.sort(cmp=helpers.cmp_billed_until_or_registered_on)
            orders.sort(cmp=helpers.cmp_billed_until_or_registered_on)
            self.assign_compensations(givers, orders, **options)
        
        rates = self.get_rates(account)
        has_billing_period = self.billing_period != self.NEVER
        has_pricing_period = self.get_pricing_period() != self.NEVER
        if rates and (has_billing_period or has_pricing_period):
            concurrent = has_billing_period and not has_pricing_period
            if not concurrent:
                rdelta = self.get_pricing_rdelta()
                ini -= rdelta
            porders = related_orders.pricing_orders(ini, end)
            porders = list(set(orders).union(set(porders)))
            porders.sort(cmp=helpers.cmp_billed_until_or_registered_on)
            if concurrent:
                # Periodic billing with no pricing period
                lines = self.bill_concurrent_orders(account, porders, rates, ini, end)
            else:
                # TODO compensation in this case?
                # Periodic and one-time billing with pricing period
                lines = self.bill_registered_or_renew_events(account, porders, rates)
        else:
            # No rates optimization or one-time billing without pricing period
            lines = []
            price = self.nominal_price
            # Calculate nominal price
            for order in orders:
                ini = order.billed_until or order.registered_on
                end = order.new_billed_until
                discounts = ()
                dsize, new_end = self.apply_compensations(order)
                if dsize:
                    discounts=(
                        ('compensation', -dsize*price),
                    )
                    if new_end:
                        order.new_billed_until = new_end
                        end = new_end
                line = self.generate_line(order, price, ini, end, discounts=discounts)
                lines.append(line)
        return lines
    
    def bill_with_metric(self, orders, account, **options):
        lines = []
        bp = None
        for order in orders:
            if order.billed_until and order.cancelled_on and order.cancelled_on >= order.billed_until:
                continue
            if self.billing_period != self.NEVER:
                bp = self.get_billing_point(order, bp=bp, **options)
                ini = order.billed_until or order.registered_on
                # Periodic billing
                if bp <= ini:
                    continue
                order.new_billed_until = bp
                if self.get_pricing_period() == self.NEVER:
                    # Changes (Mailbox disk-like)
                    for ini, end, metric in order.get_metric(ini, bp, changes=True):
                        price = self.get_price(order, metric)
                        lines.append(self.generate_line(order, price, ini, end, metric=metric))
                else:
                    # pricing_slots (Traffic-like)
                    for ini, end in self.get_pricing_slots(ini, bp):
                        metric = order.get_metric(ini, end)
                        price = self.get_price(order, metric)
                        lines.append(self.generate_line(order, price, ini, end, metric=metric))
            else:
                # One-time billing
                if order.billed_until:
                    continue
                date = order.registered_on
                order.new_billed_until = date
                if self.get_pricing_period() == self.NEVER:
                    # get metric (Job-like)
                    metric = order.get_metric(date)
                    price = self.get_price(order, metric)
                    lines.append(self.generate_line(order, price, date, metric=metric))
                else:
                    raise NotImplementedError
        return lines
    
    def generate_bill_lines(self, orders, account, **options):
        if options.get('proforma', False):
            options['commit'] = False
        if not self.metric:
            lines = self.bill_with_orders(orders, account, **options)
        else:
            lines = self.bill_with_metric(orders, account, **options)
        if options.get('commit', True):
            for line in lines:
                line.order.billed_until = line.order.new_billed_until
                line.order.save()
        return lines