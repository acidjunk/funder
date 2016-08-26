import datetime
import urllib
import uuid

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

        return TemplateResponse(
            request,
            'fundraiser/checkout.html',
            {
                "banks": api.providers,
                "cart": Cart(request),
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

        # Build transaction
        entrance = datetime.datetime.now().strftime("E%Y%m%dT%H%M")
        t = Transaction(entrance, 100, '06', entrance, 'Funder donation')

        # Send transaction
        urls = WebshopURLs('https://funder.formatics.nl/order/thanks')
        response = api.start_transaction(t, urls)
        if not response.is_valid(merchantid, merchantkey):
            raise ValueError('Invalid SHA1')
        url_ideal = urllib.url2pathname(response.issuerurl)
        return TemplateResponse(
          request,
           'fundraiser/start_payment.html',
            {
                "order": order,
                "provider_id": provider_id,
                "url_ideal": url_ideal,
                "cart": Cart(request),
            }
        )

    @route(r'^thanks/$')
    def thanks(self, request, *args, **kwargs):
        return TemplateResponse(
          request,
           'fundraiser/thanks.html',
           {
               "status": request.GET.get('status'),
               "trxid": request.GET.get('trxid'),
               "ec": request.GET.get('ec')
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

    @route(r'^add-product/$')
    def add_product_to_cart(self, request, *args, **kwargs):
        product = ProductPage.objects.get(id=request.POST.get('product_id'))
        cart = Cart(request)
        cart.add(product, product.prize, request.POST.get('quantity'))
        return redirect('/order/checkout')


def add_project_to_cart(request, project_id, prize):
    project = ProjectPage.objects.get(id=project_id)
    cart = Cart(request)
    cart.add(project, prize, 1)

def remove_project_from_cart(request, project_id):
    project = ProjectPage.objects.get(id=project_id)
    cart = Cart(request)
    cart.remove(project)

def add_product_to_cart(request, product_id, prize):
    product = ProductPage.objects.get(id=product_id)
    cart = Cart(request)
    cart.add(product, prize, 1)

def remove_product_from_cart(request, product_id):
    project = ProductPage.objects.get(id=product_id)
    cart = Cart(request)
    cart.remove(project)

def get_cart(request):
    return dict(cart=Cart(request))


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