from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register)
from .models import BlogPage
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
class BlogPageModelAdmin(ModelAdmin):
    menu_label = 'Blog'
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd), just after Explorer
    model = BlogPage
    menu_icon = 'doc-full-inverse'  # change as required
    list_display = ('title', 'teaser', 'live')
    search_fields = ('title',)

modeladmin_register(BlogPageModelAdmin)
