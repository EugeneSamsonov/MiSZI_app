import uuid

from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.http import FileResponse, Http404
from django.views import View
from django.utils import timezone

from .models import File, FileLink
from .forms import CreateFileForm, CreateLinkForm


# Create your views here.
class HomeView(CreateView):
    model = File
    template_name = "secure_share/home.html"
    form_class = CreateFileForm
    success_url = reverse_lazy("share:home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Secure Share"
        context["files"] = File.objects.filter(user=self.request.user)
        return context

    def form_valid(self, form):
        file_instance = form.save(commit=False)

        file_instance.user = self.request.user
        file_instance.orig_file_name = form.cleaned_data["file_obj"].name
        file_instance.size = form.cleaned_data["file_obj"].size

        file_instance.save()

        return super().form_valid(form)


class FileLinksView(CreateView):
    model = FileLink
    template_name = "secure_share/file_links.html"
    form_class = CreateLinkForm

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Secure Share"
        file_name = self.kwargs.get("file_name", None)
        context["orig_file_name"] = File.objects.values("orig_file_name").get(file_name=file_name).get("orig_file_name")
        context["links"] = FileLink.objects.filter(file__file_name=file_name)
        return context


    def form_valid(self, form):
        link = form.save(commit=False)

        link.file = File.objects.get(file_name=self.kwargs.get("file_name", None))
        link.blocking_date = form.cleaned_data.get("blocking_date")
        link.dowload_limit = form.cleaned_data.get("dowload_limit")
        link.token = uuid.uuid4()

        link.save()

        return super().form_valid(form)
    

class DownloadFileView(View):
    """Вьюха для скачивания файла по токену"""
    
    def get(self, request, token):
        try:
            file_link = FileLink.objects.get(token=token)
            
            if not file_link.is_active:
                raise Http404("Ссылка не активна")
            
            if file_link.file.is_deleted:
                raise Http404("Файл удален")
            
            if file_link.blocking_date and timezone.now() > file_link.blocking_date:
                file_link.is_active = False  # Деактивируем
                file_link.save()
                raise Http404("Срок действия ссылки истек")
            
            if file_link.dowload_limit and file_link.download_count >= file_link.dowload_limit:
                file_link.is_active = False  # Деактивируем
                file_link.save()
                raise Http404("Лимит скачиваний исчерпан")
            

            file_link.download_count += 1
            file_link.save()
            
            
            response = FileResponse(
                file_link.file.file_obj,
                as_attachment=True,  # Чтобы браузер скачивал, а не открывал
                filename=file_link.file.orig_file_name  # Оригинальное имя
            )
            
            return response
            
        except FileLink.DoesNotExist:
            raise Http404("Ссылка не найдена")
