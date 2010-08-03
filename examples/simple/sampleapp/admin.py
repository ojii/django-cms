from django.contrib import admin
from models import Picture, Category

class PictureInline(admin.StackedInline):
    model = Picture

class CategoryAdmin(admin.ModelAdmin):
    inlines = [PictureInline]

admin.site.register(Category, CategoryAdmin)