import datetime
import urllib

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

    @route(r'^choose-bank/$')
    def choose_bank(self, request):
        api = SisowAPI(None, None)

        return TemplateResponse(
          request,
           'fundraiser/banks.html',
           { "banks" : api.providers,
             "project": "TODO: get dynamic project name",
             "cart": Cart(request)}
        )

    @route(r'^start-payment/(?P<provider_id>\d+)/$')
    def start_payment(self, request, *args, **kwargs):
        (merchantid, merchantkey) = _account_from_file('account-sisow.secret')
        api = SisowAPI(merchantid, merchantkey, testmode=True)

        # Build transaction
        entrance = datetime.datetime.now().strftime("E%Y%m%dT%H%M")
        t = Transaction(entrance, 100, '06', entrance, 'Funder donatie')

        # Send transaction
        urls = WebshopURLs('https://funder.formatics.nl/projects/project-1/thanks')
        response = api.start_transaction(t, urls)
        if not response.is_valid(merchantid, merchantkey):
            raise ValueError('Invalid SHA1')

        url_ideal = urllib.url2pathname(response.issuerurl)
        return TemplateResponse(
          request,
           'fundraiser/redirect_to_sisow.html',
           { "provider_id" : "provider_id",
             "project": "TODO: get dynamic project name",
             "url_ideal": url_ideal}
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
    @route(r'^add_project/$')
    def add_project_to_cart(self, request, *args, **kwargs):
        project = ProjectPage.objects.get(id=request.GET.get('project_id'))
        cart = Cart(request)
        cart.add(project, 300, 1)
        return TemplateResponse(
          request,
           'fundraiser/add.html',
           {
               "cart": Cart(request)
           }
        )


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
    billing_name = models.CharField(max_length=250, blank=True)
    billing_name = models.CharField(max_length=250, blank=True)
    billing_company = models.CharField(max_length=250, blank=True)
    billing_email = models.EmailField(blank=True)
    billing_date = models.DateField(auto_now_add=True)
    paid_date = models.DateField(editable=False)
    paid_issuer = models.CharField(max_length=250, editable=False)
    paid_id = models.CharField(max_length=250, editable=False)
    anonymous = models.BooleanField(default=False)
    amount = models.IntegerField()

class OrderLine(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    amount = models.PositiveIntegerField()
    prize = models.PositiveIntegerField()