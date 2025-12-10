import uuid

from django.utils import timezone

from django.db import models
from users.models import User


# Create your models here.
class File(models.Model):

    def user_directory_path(instance, filename):
        # Будет сохранять в: secure_share/username/filename
        ext = filename.split('.')[-1]
        # Меняем имя файла на UUID
        return f"secure_share/{instance.user.username}/{instance.file_name}.{ext}"

    class Meta:
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    orig_file_name = models.CharField(max_length=255)  # изначальное имя файла
    file_name = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True
    )  # фактическое имя файла на сервере (UUID)
    file_obj = models.FileField(upload_to=user_directory_path, max_length=100)
    upload_date = models.DateTimeField(auto_now_add=True)
    size = models.PositiveIntegerField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Файл: {self.id} | {self.orig_file_name}"


class FileLink(models.Model):

    class Meta:
        verbose_name = "Ссылка на файл"
        verbose_name_plural = "Ссылки на файлы"

    file = models.ForeignKey("File", on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now=False, auto_now_add=True)
    blocking_date = models.DateTimeField(auto_now=False, blank=True, null=True)
    dowload_limit = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    download_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Ссылка: {self.id} {f" | активна до {self.blocking_date}" if self.blocking_date else 'бессрочно'} | осталось {f"{self.download_count}/{self.dowload_limit}" if self.dowload_limit else '∞'} скачаваний {f" | неактивна " if not self.is_active else ""}"
