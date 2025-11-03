from django.contrib import admin

from .models import Theory
# Register your models here.
class TheoryAdmin(admin.ModelAdmin):
    pass

admin.site.register(Theory, TheoryAdmin)