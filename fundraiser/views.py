"""
Funder: a Django/Wagtail based web application to facilitate online donations.
Copyright (C) 2016 R. Dohmen <acidjunk@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from django.contrib.syndication.views import Feed
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.utils.feedgenerator import Atom1Feed

from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils import timezone

from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Table
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from .models import ProductIndexPage, ProductPage, ProjectIndexPage, ProjectPage, ProjectCategory
from django.shortcuts import get_object_or_404, render
from django.conf import settings

# Todo use: generic Page to make search accross aa couple of tables
from wagtail.wagtailcore.models import Page

from wagtail.wagtailsearch.models import Query

def project_search(request):
    # Search
    search_query = request.GET.get('query', None)
    if search_query:
        search_results = ProjectPage.objects.live().search(search_query)
        print search_results

        # Log the query so Wagtail can suggest promoted results
        Query.get(search_query).add_hit()
    else:
        search_results = ProjectPage.objects.none()

    # Render template
    return render(request, 'fundraiser/search_results.html', {
        'title': 'Project search results',
        'search_query': search_query,
        'search_results': search_results,
    })

def product_search(request):
    # Search
    search_query = request.GET.get('query', None)
    if search_query:
        search_results = ProductPage.objects.live().search(search_query)
        print search_results

        # Log the query so Wagtail can suggest promoted results
        Query.get(search_query).add_hit()
    else:
        search_results = ProductPage.objects.none()

    # Render template
    return render(request, 'fundraiser/search_results.html', {
        'title': 'Product search results',
        'search_query': search_query,
        'search_results': search_results,
    })

def project_tag_view(request, tag):
    index = ProjectIndexPage.objects.first()
    return index.serve(request, tag=tag)

def product_tag_view(request, tag):
    index = ProductIndexPage.objects.first()
    return index.serve(request, tag=tag)

def project_category_view(request, category):
    index = ProjectIndexPage.objects.first()
    return index.serve(request, category=category)

def product_category_view(request, category):
    index = ProductIndexPage.objects.first()
    return index.serve(request, category=category)

def author_view(request, author):
    index = ProjectIndexPage.objects.first()
    return index.serve(request, author=author)


class ProjectLatestEntriesFeed(Feed):
    '''
    If a URL ends with "rss" try to find a matching ProjectIndexPage
    and return its items.
    '''

    def get_object(self, request, project_slug):
        return get_object_or_404(ProjectIndexPage, slug=project_slug)

    def title(self, project):
        if project.seo_title:
            return project.seo_title
        return project.title

    def link(self, project):
        return project.full_url

    def description(self, project):
        return project.search_description

    def items(self, project):
        num = getattr(settings, 'PROJECT_PAGINATION_PER_PAGE', 10)
        return project.get_descendants()[:num]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.specific.description

    def item_link(self, item):
        return item.full_url


class ProjectLatestEntriesFeedAtom(ProjectLatestEntriesFeed):
    feed_type = Atom1Feed


class ProductLatestEntriesFeed(Feed):
    '''
    If a URL ends with "rss" try to find a matching ProjectIndexPage
    and return its items.
    '''

    def get_object(self, request, product_slug):
        return get_object_or_404(ProductIndexPage, slug=product_slug)

    def title(self, product):
        if product.seo_title:
            return product.seo_title
        return product.title

    def link(self, product):
        return product.full_url

    def description(self, product):
        return product.search_description

    def items(self, product):
        num = getattr(settings, 'PRODUCT_PAGINATION_PER_PAGE', 10)
        return product.get_descendants()[:num]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.specific.description

    def item_link(self, item):
        return item.full_url


class ProductLatestEntriesFeedAtom(ProductLatestEntriesFeed):
    feed_type = Atom1Feed


class ProjectLatestCategoryFeed(Feed):
    description = "A project"

    def title(self, category):
        return "Project: " + category.name

    def link(self, category):
        return "/projects/category/" + category.slug

    def get_object(self, request, category):
        return get_object_or_404(ProjectCategory, slug=category)

    def items(self, obj):
        return ProjectPage.objects.filter(
            categories__category=obj).order_by('-date')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description


class ProductLatestCategoryFeed(Feed):
    description = "A product"

    def title(self, category):
        return "Product: " + category.name

    def link(self, category):
        return "/product/category/" + category.slug

    def get_object(self, request, category):
        return get_object_or_404(ProjectCategory, slug=category)

    def items(self, obj):
        return ProductPage.objects.filter(
            categories__category=obj).order_by('-date')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description


def pdf(request, order_nr):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="funder_invoice.pdf"'

    # Create the PDF object, using the response object as its "file."
    pdf = Canvas(response, pagesize=A4)

    """ Draws the invoice header """
    pdf.setStrokeColorRGB(0.9, 0.5, 0.2)
    pdf.setFillColorRGB(0.2, 0.2, 0.2)
    pdf.setFont('Helvetica', 16)
    pdf.drawString(18 * cm, 28 * cm, 'Factuur')
    # pdf.drawInlineImage(settings.INV_LOGO, 1 * cm, -1 * cm, 250, 16)
    pdf.setLineWidth(4)
    pdf.line(0, 27 * cm, 21.7 * cm, 27 * cm)

    """ Draws the business address """
    business_details = (
        u'COMPANY NAME LTD',
        u'STREET',
        u'TOWN',
        U'COUNTY',
        U'POSTCODE',
        U'COUNTRY',
        u'',
        u'',
        u'Phone: +00 (0) 000 000 000',
        u'Email: example@example.com',
        u'Website: www.example.com',
        u'Reg No: 00000000'
    )
    pdf.setFont('Helvetica', 9)
    textobject = pdf.beginText(1 * cm, 26 * cm)
    for line in business_details:
        textobject.textLine(line)
    pdf.drawText(textobject)

    """ Draws the client address """
    textobject = pdf.beginText(14 * cm, 26 * cm)
    textobject.textLine('Formatics')
    textobject.textLine('Contactpersoon: Freek de Groot')
    textobject.textLine('Big street 17')
    textobject.textLine('1234AB Barendburg')
    pdf.drawText(textobject)

    """ Draws the invoice info """
    pdf.setFont('Helvetica', 11)
    textobject = pdf.beginText(1.5 * cm, 19 * cm)
    textobject.textLine('Factuurnummer: 20170321-1, datum: {}'.format(timezone.now().strftime('%d %b %Y')))
    pdf.drawText(textobject)


    """ Draws the costs table """
    # table headers
    data = [[u'Quantity', u'Description', u'Amount', u'Total'], ]
    # fake some data for now
    data.append([5, 'Pony\'s', 12.00, 60.00])
    data.append([1, 'Mier', 15.00, 15.00])
    data.append([u'', u'', u'Total:', 75.00])

    # build the table
    table = Table(data, colWidths=[2 * cm, 11 * cm, 3 * cm, 3 * cm])
    table.setStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), (0.2, 0.2, 0.2)),
        ('GRID', (0, 0), (-1, -2), 1, (0.7, 0.7, 0.7)),
        ('GRID', (-2, -1), (-1, -1), 1, (0.7, 0.7, 0.7)),
        ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
        ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
    ])
    tw, th, = table.wrapOn(pdf, 15 * cm, 19 * cm)
    table.drawOn(pdf, 1 * cm, 18 * cm - th)

    """ Draws the invoice footer """
    note = (
        u'Funder iNvoice :: {}'.format(timezone.now()),
    )
    textobject = pdf.beginText(1 * cm, 0.5 * cm)
    for line in note:
        textobject.textLine(line)
    pdf.drawText(textobject)

    # Close the PDF object cleanly, and we're done.
    pdf.showPage()
    pdf.save()
    return response
