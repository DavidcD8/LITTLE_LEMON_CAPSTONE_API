from django.contrib import admin
from .models import Category, MenuItem, Cart


admin.site.register(MenuItem)
admin.site.register(Category)
admin.site.register(Cart)