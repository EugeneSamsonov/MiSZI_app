from django import forms
from .models import StudyTest, Question, Answer
from django.forms import formset_factory, inlineformset_factory, BaseInlineFormSet
from django.core.exceptions import ValidationError


class StudyTestForm(forms.ModelForm):
    class Meta:
        model = StudyTest
        fields = [
            "title",
            "description",
            "attempt_limit",
        ]
        labels = {
            "title": "Название",
            "description": "Описание",
            "attempt_limit": "Лимит попыток",
        }

    title = forms.CharField(required=True, label="Название")

    def clean_title(self):
        if self.cleaned_data["title"] == "":
            raise forms.ValidationError("Title can't be empty")
        title = self.cleaned_data["title"]
        return title


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            "text",
            # "multiple_answers",
        ]
        labels = {
            "text": "Вопрос",
            # "multiple_answers": "Множественные ответы",
        }

    text = forms.CharField(required=True, label="Вопрос")


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = [
            "text",
            "is_correct",
        ]
        labels = {
            "text": "Ответ",
            "is_correct": "Правильный?",
        }

    text = forms.CharField(required=True, label="Ответ")

    # def clean_text(self):
    #     if self.cleaned_data["text"] == "":
    #         raise forms.ValidationError("Question text can't be empty")
    #     text = self.cleaned_data["text"]
    #     return text


class AnswerFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        # Проверяем что хотя бы один ответ помечен как правильный
        has_correct_answer = False

        for form in self.forms:
            # Пропускаем удаленные формы
            if form.cleaned_data.get("DELETE", False):
                continue

            # Проверяем что форма не пустая и имеет данные
            if form.cleaned_data:
                if form.cleaned_data.get("is_correct", False):
                    has_correct_answer = True
                    break  # Достаточно одного правильного ответа

        # Если ни один ответ не правильный - ошибка
        if not has_correct_answer:
            raise ValidationError("Хотя бы один ответ должен быть правильным")


# Formset для вопросов
QuestionFormSet = formset_factory(
    QuestionForm, extra=2, max_num=2, min_num=2, can_delete=False
)

# Inline formset для ответов (привязан к вопросу)
AnswerFormSet = inlineformset_factory(
    Question,
    Answer,
    form=AnswerForm,
    formset=AnswerFormSet,
    max_num=2,
    min_num=2,
    can_delete=False,
)
