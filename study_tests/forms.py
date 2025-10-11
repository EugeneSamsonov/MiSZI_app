from django import forms
from .models import StudyTest, Question, Answer
from django.forms import formset_factory, inlineformset_factory


class StudyTestForm(forms.ModelForm):
    class Meta:
        model = StudyTest
        fields = [
            "title",
            "description",
            "attempt_limit",
        ]
    
    title = forms.CharField(required=True)

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            "text",
            "multiple_answers",
        ]
    
    text = forms.CharField(required=True)


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = [
            "text",
            "is_correct",
        ]

    
    text = forms.CharField(required=True)


# Formset для вопросов
QuestionFormSet = formset_factory(QuestionForm, extra=2, max_num=15)

# Inline formset для ответов (привязан к вопросу)
AnswerFormSet = inlineformset_factory(
    Question, Answer, form=AnswerForm, extra=2, max_num=4, can_delete=False
)
