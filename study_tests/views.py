from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from study_tests.models import StudyTest

from .forms import StudyTestForm, QuestionFormSet, AnswerFormSet


@login_required(login_url=reverse_lazy("user:login"))
def control_panel(request):
    tests = StudyTest.objects.filter(author=request.user)
    return render(request, "study_tests/control_panel.html", {"tests": tests})


def validate_all_forms(test_form, question_formset, answer_formsets):
    errors = 0

    if not test_form.is_valid():
        errors += 1

    if not question_formset.is_valid():
        errors += 1

    for answer_formset in answer_formsets:
        if not answer_formset.is_valid():
            errors += 1

    return errors == 0


@login_required(login_url=reverse_lazy("user:login"))
def create_test(request):
    if request.method == "POST":
        test_form = StudyTestForm(request.POST)
        question_formset = QuestionFormSet(request.POST, prefix="questions")

        answer_formsets = [
            AnswerFormSet(request.POST, prefix=f"answers-{i}")
            for i in range(question_formset.max_num)
        ]
        questions_with_answers = zip(question_formset, answer_formsets)

        is_valid = validate_all_forms(test_form, question_formset, answer_formsets)
        if is_valid:
            test = test_form.save(commit=False)
            test.author = request.user

            is_breaked = False
            for question_form, answer_formset in questions_with_answers:
                # Проверяем, что вопрос не пустой
                if question_form.cleaned_data and not question_form.cleaned_data.get(
                    "DELETE", False
                ):
                    question = question_form.save(commit=False)
                    question.test = test

                    correct_count = 0
                    for answer_form in answer_formset:
                        if (
                            answer_form.cleaned_data
                            and answer_form.cleaned_data["is_correct"]
                        ):
                            correct_count += 1

                    if correct_count == 0:
                        question_form.add_error(
                            "text", "At least one answer must be correct"
                        )
                        is_breaked = True
                        break
                    else:
                        question.multiple_answers = correct_count > 1

                        answer_formset.instance = question

                        test.save()
                        question.save()
                        answer_formset.save()
                        return HttpResponseRedirect(reverse_lazy("tests:control-panel"))

            if is_breaked:
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
    else:
        test_form = StudyTestForm()
        question_formset = QuestionFormSet(prefix="questions")
        answer_formsets = [
            AnswerFormSet(prefix=f"answers-{i}")
            for i in range(question_formset.max_num)
        ]  # Исправьте на 10 если нужно

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


@login_required(login_url=reverse_lazy("user:login"))
def delete_test(request, test_id):
    test = StudyTest.objects.get(id=test_id)
    test.delete()
    return HttpResponseRedirect(reverse_lazy("tests:control-panel"))
