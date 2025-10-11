from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import test

from .forms import StudyTestForm, QuestionFormSet, AnswerFormSet


def control_panel(request):
    return render(request, "study_tests/control_panel.html")


def validate_all_forms(test_form, question_formset, answer_formsets):
    errors = []

    if not test_form.is_valid():
        errors.append("Ошибки в форме теста")

    if not question_formset.is_valid():
        errors.append("Ошибки в вопросах")

    for i, answer_formset in enumerate(answer_formsets):
        if not answer_formset.is_valid():
            errors.append(f"Ошибки в ответах для вопроса {i+1}")

    return len(errors) == 0, errors


@login_required
def create_test(request):
    if request.method == "POST":
        test_form = StudyTestForm(request.POST)
        question_formset = QuestionFormSet(request.POST, prefix="questions")

        answer_formsets = [
            AnswerFormSet(request.POST, prefix=f"answers-{i}") for i in range(2)
        ]
        questions_with_answers = zip(question_formset, answer_formsets)

        is_valid, errors = validate_all_forms(test_form, question_formset, answer_formsets)
        if is_valid:
            test = test_form.save(commit=False)
            test.author = request.user
            test.save()

            for question_form, answer_formset in questions_with_answers:
                # Проверяем, что вопрос не пустой
                if question_form.cleaned_data and not question_form.cleaned_data.get('DELETE', False):
                    question = question_form.save(commit=False)
                    question.test = test
                    question.save()

                    answer_formset.instance = question  
                    answer_formset.save()

            return HttpResponseRedirect(reverse_lazy("tests:control-panel"))
        else:
            
            return render(
                request,
                "study_tests/create_test.html",
                {
                    "test_form": test_form,
                    "question_formset": question_formset,
                    "questions_with_answers": questions_with_answers,
                    "answer_formsets": answer_formsets,
                },
            )

    test_form = StudyTestForm()
    question_formset = QuestionFormSet(prefix="questions")
    answer_formsets = [AnswerFormSet(prefix=f"answers-{i}") for i in range(2)]  # Исправьте на 10 если нужно

    questions_with_answers = zip(question_formset, answer_formsets)

    return render(
        request,
        "study_tests/create_test.html",
        {
            "test_form": test_form,
            "questions_with_answers": questions_with_answers,
            "question_formset": question_formset,  # Добавьте это для management_form
        },
    )
