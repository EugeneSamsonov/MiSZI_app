from django.db import models
from study_tests.models import TestCategory
from users.models import User


# Create your models here.
class Theory(models.Model):
    class Meta:
        verbose_name = "Теория"
        verbose_name_plural = "Теории"

    title = models.CharField(max_length=255)
    description = models.TextField()
    text = models.TextField()
    category = models.ForeignKey(TestCategory, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
