from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import AccessMixin
from .models import File, FileLink


class OwnerRequiredMixin(AccessMixin):
    """Базовый миксин для проверки владельца"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class FileOwnerRequiredMixin(OwnerRequiredMixin):
    """Проверяет что пользователь - владелец файла"""

    def dispatch(self, request, *args, **kwargs):
        # Сначала вызываем родительскую проверку авторизации
        response = super().dispatch(request, *args, **kwargs)

        # Получаем file_name из URL
        file_name = self.kwargs.get("file_name")
        if file_name:
            # Проверяем владельца файла
            file = get_object_or_404(File, file_name=file_name)
            if file.user != request.user:
                raise PermissionDenied("Вы не владелец этого файла")

        return response


class LinkOwnerRequiredMixin(OwnerRequiredMixin):
    """Проверяет что пользователь - владелец ссылки (через файл)"""

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        # Для DeleteFileLinkView - получаем token из POST данных
        token = request.POST.get("token") or self.kwargs.get("token")

        if token:
            # Проверяем владельца через файл
            link = get_object_or_404(FileLink, token=token)
            if link.file.user != request.user:
                raise PermissionDenied("Вы не владелец этой ссылки")

        return response
