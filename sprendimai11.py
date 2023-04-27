

# 1. Создать модель для хранения меню в БД, например, такую:

from django.db import models


class MenuItem(models.Model):
    title = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

# 2. Создать форму и админку для добавления / редактирования пунктов меню:

from django import forms
from django.contrib import admin
from .models import MenuItem


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = '__all__'


class MenuItemAdmin(admin.ModelAdmin):
    form = MenuItemForm


admin.site.register(MenuItem, MenuItemAdmin)


# 3. Создать custom template tag для отрисовки меню на странице:


from django import template
from django.urls import reverse
from .models import MenuItem

register = template.Library()


@register.simple_tag(takes_context=True)
def draw_menu(context, menu_name):
    request = context['request']
    current_url = request.path_info
    menu_items = MenuItem.objects.filter(title=menu_name).select_related('parent')

    def render_menu_item(item):
        active = False
        if current_url.startswith(item.url):
            active = True
        children = item.children.all()
        has_children = children.exists()
        html = '<li class="dropdown' + (' active' if active else '') + (' has-children' if has_children else '') + '">'
        html += '<a href="' + (reverse(item.url) if item.url.startswith('/') else item.url) + '">' + item.title + '</a>'
        if has_children:
            html += '<ul class="dropdown-menu">'
            for child in children:
                html += render_menu_item(child)
            html += '</ul>'
        html += '</li>'
        return html

    menu_html = ''
    for item in menu_items:
        if not item.parent:
            menu_html += render_menu_item(item)

    return menu_html




# 4. В шаблоне страницы можно отрисовать меню следующим образом:

#   <html>
#   {%load my_tags%}
#   <nav>
#     <ul class ="navbar-nav">
#     {%draw_menu 'main_menu'%}
#     </ul>
#   </nav>

# 5.Для отрисовки меню на каждой странице нужно использовать базовый шаблон, в
# котором будет подключаться код для отрисовки меню и передаваться название нужного
# меню в контексте.
