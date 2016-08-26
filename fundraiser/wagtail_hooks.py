from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register)
from .models import (
    Order, ProductPage, ProductCategory, ProjectPage, ProjectCategory)


class ProductPageModelAdmin(ModelAdmin):
    model = ProductPage
    menu_icon = 'doc-full-inverse'  # change as required
    list_display = ('title', 'organisation', 'stock', 'prize', 'live')
    # list_filter = ('title', 'organisation', 'tags', 'live')
    search_fields = ('title',)


class ProjectPageModelAdmin(ModelAdmin):
    model = ProjectPage
    menu_icon = 'doc-full-inverse'  # change as required
    list_display = ('title', 'organisation', 'teaser', 'amount_needed', 'amount_raised', 'live')
    # list_filter = ('live', 'organisation', 'tags')
    search_fields = ('title',)


class OrderModelAdmin(ModelAdmin):
    model = Order
    menu_label = 'Orders'  # ditch this to use verbose_name_plural from model
    menu_icon = 'snippet'  # change as required
    list_display = ('order_nr', 'anonymous', 'billing_name', 'billing_company', 'billing_email', 'billing_date',
                    'paid_date', 'is_paid')
    list_filter = ('billing_name', 'billing_company', 'anonymous')
    search_fields = ('title',)


# class MySnippetModelAdmin(ModelAdmin):
#     model = MySnippetModel
#     menu_label = 'Snippet Model'  # ditch this to use verbose_name_plural from model
#     menu_icon = 'snippet'  # change as required
#     list_display = ('title', 'example_field2', 'example_field3')
#     list_filter = (example_field2', 'example_field3')
#     search_fields = ('title',)


class MyModelAdminGroup(ModelAdminGroup):
    menu_label = 'Fundraiser'
    menu_icon = 'folder-open-inverse'  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    items = (OrderModelAdmin, ProductPageModelAdmin, ProjectPageModelAdmin)

# When using a ModelAdminGroup class to group several ModelAdmin classes together,
# you only need to register the ModelAdminGroup class with Wagtail:
modeladmin_register(MyModelAdminGroup)
