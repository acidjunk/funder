import datetime
import urllib
import uuid

import decimal

from django.conf import settings
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route

from project import ProjectPage
from product import ProductPage

from cart.cart import Cart
from cart.models import Cart as CartModel
from sisow import _account_from_file
from sisow import SisowAPI
from sisow import Transaction
from sisow import WebshopURLs


class OrderIndexPage(RoutablePageMixin, Page):
    intro = RichTextField(blank=True)
    submit_info = RichTextField(blank=True)
    thanks_info = RichTextField(blank=True)

    @route(r'^$')
    def base(self, request):
        return TemplateResponse(
          request,
          self.get_template(request),
          self.get_context(request)
        )

    @route(r'^checkout/$')
    def checkout(self, request):
        api = SisowAPI(None, None)
        cart = Cart(request)

        total_without_vat = 0
        for item in cart:
            total_without_vat += item.total_price
        total_with_vat = float(total_without_vat* decimal.Decimal(1+settings.FUNDER_VAT_PERCENTAGE/100))

        return TemplateResponse(
            request,
            'fundraiser/checkout.html',
            {
                "banks": api.providers,
                "cart": cart,
                "total_without_vat": total_without_vat,
                "total_with_vat": total_with_vat,
                "show_vat": settings.FUNDER_SHOW_VAT,
                "vat_percentage": settings.FUNDER_VAT_PERCENTAGE,
             }
        )

    @route(r'^start-payment/$')
    def start_payment(self, request, *args, **kwargs):
        provider_id = request.POST.get('provider_id')
        if not provider_id:
            raise ValueError('No provider_id')
        cart = Cart(request)

        name = request.POST.get('name')
        organisation = request.POST.get('organisation')

        # Check if order already exist for this cart
        try:
            order = Order.objects.get(cart=cart.cart)
        except:
            order = Order(order_nr=uuid.uuid4(), cart=cart.cart, amount='2293', #todo
                          billing_name=name, billing_company=organisation, paid_date=datetime.datetime.now())
            order.save()

        (merchantid, merchantkey) = _account_from_file('account-sisow.secret')
        api = SisowAPI(merchantid, merchantkey, testmode=True)

        total_without_vat = 0
        for item in order.cart.item_set.all():
            total_without_vat += item.total_price
        total_with_vat = int(total_without_vat* decimal.Decimal(1.21))*100

        # Build transaction
        entrance = datetime.datetime.now().strftime("E%Y%m%dT%H%M")
        if settings.FUNDER_SHOW_VAT:
            t = Transaction(entrance, total_with_vat, '06', entrance, 'Funder donation')
        else:
            t = Transaction(entrance, total_without_vat, '06', entrance, 'Funder donation')
        # Send transaction
        # Todo: create something with a setting:
        urls = WebshopURLs('https://funder.formatics.nl/order/thanks/?order_nr={}'.format(order.order_nr))
        #urls = WebshopURLs('http://0.0.0.0:8000/order/thanks/?order_nr={}'.format(order.order_nr))
        response = api.start_transaction(t, urls)
        if not response.is_valid(merchantid, merchantkey):
            raise ValueError('Invalid SHA1')
        url_ideal = urllib.url2pathname(response.issuerurl)
        return TemplateResponse(
          request,
           'fundraiser/start_payment.html',
            {
                "order": order,
                "total_without_vat": total_without_vat,
                "total_with_vat": total_with_vat,
                "provider_id": provider_id,
                "url_ideal": url_ideal,
                "show_vat": settings.FUNDER_SHOW_VAT,
                "vat_percentage": settings.FUNDER_VAT_PERCENTAGE,
            }
        )

    @route(r'^thanks/$')
    def thanks(self, request, *args, **kwargs):
        status = request.GET.get('status')
        order_nr = request.GET.get('order_nr')

        # Todo add check so closed order will raise an Exception
        if status == "Success" and order_nr:  # todo add extra checks for trxid/ec/order_nr in session for reliable checkout
            print("Payment complete for order_nr {}".format(order_nr))
            order = Order.objects.get(order_nr=order_nr)
            order.paid_date=datetime.datetime.now()
            order.save()
            del request.session['CART-ID']
            # look for items in order and deal with product stock change + project amount
            for item in order.cart.item_set.all():
                wagtail_page = item.get_product()
                if wagtail_page.__class__.__name__ == "ProductPage":
                    wagtail_page.stock -= item.quantity
                    wagtail_page.save()
                elif wagtail_page.__class__.__name__ == "ProjectPage":
                    wagtail_page.amount_raised += item.total_price
                    wagtail_page.save()

        return TemplateResponse(
          request,
           'fundraiser/thanks.html',
           {
               "status": status,
               "trxid": request.GET.get('trxid'),
               "ec": request.GET.get('ec'),
               "order_nr": order_nr
           }
        )

    @route(r'^add-project/$')
    def add_project_to_cart(self, request, *args, **kwargs):
        project = ProjectPage.objects.get(id=request.POST.get('project_id'))
        cart = Cart(request)
        cart.add(project, request.POST.get('amount'), 1)
        request.session['funder_name']=request.POST.get('name')
        request.session['funder_organisation']=request.POST.get('organisation')
        return redirect('/order/checkout')

    @route(r'^remove-project/$')
    def remove_project_from_cart(self, request, *args, **kwargs):
        project = ProjectPage.objects.get(id=request.POST.get('project_id'))
        cart = Cart(request)
        cart.remove(project)
        return redirect('/order/checkout')

    @route(r'^add-product/$')
    def add_product_to_cart(self, request, *args, **kwargs):
        product = ProductPage.objects.get(id=request.POST.get('product_id'))
        cart = Cart(request)
        cart.add(product, product.prize, request.POST.get('quantity'))
        return redirect('/order/checkout')

    @route(r'^remove-product/$')
    def remove_product_from_cart(self, request, *args, **kwargs):
        product = ProductPage.objects.get(id=request.POST.get('product_id'))
        cart = Cart(request)
        cart.remove(product)
        return redirect('/order/checkout')


class Order(models.Model):
    order_nr = models.TextField()
    cart = models.OneToOneField(CartModel)
    billing_name = models.CharField(max_length=250, blank=True)
    billing_company = models.CharField(max_length=250, blank=True)
    billing_email = models.EmailField(blank=True)
    billing_date = models.DateField(auto_now_add=True)
    paid_date = models.DateField(editable=False, blank=True, null=True)
    paid_issuer = models.CharField(max_length=250, editable=False)
    paid_id = models.CharField(max_length=250, editable=False)
    anonymous = models.BooleanField(default=False)
    amount = models.IntegerField()

    @property
    def is_paid(self):
        if not self.paid_date:
            return False
        return True

class OrderLine(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    amount = models.PositiveIntegerField()
    prize = models.PositiveIntegerField()