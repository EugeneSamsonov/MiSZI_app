from django.contrib import admin

# Register your models here.
from .models import File, FileLink
# Register your models here.
class FileAdmin(admin.ModelAdmin):
    pass


class FileLinkAdmin(admin.ModelAdmin):
    pass

admin.site.register(File, FileAdmin)
admin.site.register(FileLink, FileLinkAdmin)