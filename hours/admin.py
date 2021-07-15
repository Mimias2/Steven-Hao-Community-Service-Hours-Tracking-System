from django.contrib import admin
from .models import Category, Profile

# Allows admin to create and edit Category and Profile records
admin.site.register(Category)
admin.site.register(Profile)
