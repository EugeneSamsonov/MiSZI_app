import os

from django import forms
from django.forms import ValidationError

from .models import File, FileLink


class CreateFileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = [
            "file_obj",
        ]
        labels = {
            "file_obj": "Файл",
        }

    # Ограничения
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 МБ
    ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt', '.png', '.jpg', '.jpeg', '.zip']
    
    def clean_file_obj(self):
        """Валидация файла"""
        uploaded_file = self.cleaned_data.get('file_obj')
        
        if not uploaded_file:
            raise ValidationError("Файл не выбран")
        
        # 1. Проверка размера
        if uploaded_file.size > self.MAX_FILE_SIZE:
            raise ValidationError(f"Файл слишком большой. Максимальный размер: {self.MAX_FILE_SIZE // (1024*1024)} МБ")
        
        # 2. Проверка расширения
        file_name = uploaded_file.name.lower()
        file_ext = os.path.splitext(file_name)[1]
        
        if file_ext not in self.ALLOWED_EXTENSIONS:
            raise ValidationError(
                f"Недопустимый тип файла. Разрешенные типы: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
        
        # 3. Проверка имени файла (базовая защита)
        if '..' in file_name or '/' in file_name or '\\' in file_name:
            raise ValidationError("Недопустимое имя файла")
        
        return uploaded_file



class CreateLinkForm(forms.ModelForm):
    blocking_date = forms.DateTimeField(
        label="Дата истечения",
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',  # Это даст нативную панель выбора!
            'placeholder': 'Выберите дату и время'
        }),
        required=False,  # Не обязательно
    )
    
    dowload_limit = forms.IntegerField(
        label="Лимит скачиваний",
        min_value=1,
        required=False
    )

    class Meta:
        model = FileLink
        fields = ["blocking_date", "dowload_limit"]
        labels = {
            "blocking_date": "Время активности",
            "dowload_limit": "Кол-во скачиваний",
        }
