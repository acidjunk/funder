from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register)
from .models import (
    Order, ProductPage, ProjectPage)
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
class ProductPageModelAdmin(ModelAdmin):
    model = ProductPage
    menu_icon = 'doc-full-inverse'  # change as required
    list_display = ('title', 'organisation', 'stock', 'prize', 'live')
    search_fields = ('title',)


class ProjectPageModelAdmin(ModelAdmin):
    model = ProjectPage
    menu_icon = 'doc-full-inverse'  # change as required
    list_display = ('title', 'organisation', 'teaser', 'amount_needed', 'amount_raised', 'live')
    search_fields = ('title',)

class OrderModelAdmin(ModelAdmin):
    model = Order
    menu_label = 'Orders'  # ditch this to use verbose_name_plural from model
    menu_icon = 'snippet'  # change as required
    list_display = ('order_nr', 'anonymous', 'billing_name', 'billing_company', 'billing_email', 'billing_date',
                    'paid_date', 'is_paid')
    list_filter = ('billing_name', 'billing_company', 'anonymous')
    search_fields = ('title',)

class FundRaiserAdminGroup(ModelAdminGroup):
    menu_label = 'Fundraiser'
    menu_icon = 'folder-open-inverse'  # change as required
    menu_order = 201  # will put in 4rd place (000 being 1st, 100 2nd)
    items = (OrderModelAdmin, ProductPageModelAdmin, ProjectPageModelAdmin)

modeladmin_register(FundRaiserAdminGroup)
