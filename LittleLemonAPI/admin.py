from django.contrib import admin
from .models import Category, MenuItem


admin.site.register(MenuItem)
admin.site.register(Category)