from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from study_tests.models import Answer, QuestionAttempt, StudyTest, TestAttempt

from .forms import StudyTestForm, QuestionFormSet, AnswerFormSet


@login_required()
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


@login_required()
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
            test.save()

            for question_form, answer_formset in questions_with_answers:
                question = question_form.save(commit=False)
                question.test = test

                correct_count = 0
                for answer_form in answer_formset:
                    if (
                        answer_form.cleaned_data
                        and answer_form.cleaned_data["is_correct"]
                    ):
                        correct_count += 1

                    question.multiple_answers = correct_count > 1

                    answer_formset.instance = question

                question.save()
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


@login_required()
def delete_test(request, test_id):
    test = StudyTest.objects.get(id=test_id)
    test.delete()
    return HttpResponseRedirect(reverse_lazy("tests:control-panel"))


@login_required()
def tests_list(request):
    tests = StudyTest.objects.all()
    return render(request, "study_tests/tests_list.html", {"tests": tests})


@login_required
def test(request, test_id):
    test = StudyTest.objects.get(id=test_id)
    questions = test.questions.all().prefetch_related("answers").order_by("id")
    user_attempts = TestAttempt.objects.filter(test=test, user=request.user).count()
    attempt_limit = test.attempt_limit - user_attempts
    correct_answers = {
        question.id: [str(answer.id) for answer in question.answers.filter(is_correct=True)]
        for question in questions
    }

    if request.method == "POST":
        score = 0

        if attempt_limit <= 0:
            return HttpResponseRedirect(reverse_lazy("tests:test", args=[test_id]))
        # Создаем попытку
        test_attempt = TestAttempt.objects.create(
            user=request.user,
            test=test,
            completed_at=timezone.now(),
            attempt_number=user_attempts + 1,
        )

        # Обрабатываем каждый вопрос
        for question in questions:
            field_name = f"question_{question.id}"

            if question.multiple_answers:
                # Чекбоксы - getlist() возвращает список
                selected_ids = request.POST.getlist(field_name)
                # ['5', '8', '12'] или [] если ничего не выбрано
            else:
                # Радио - get() возвращает строку или None
                selected_id = request.POST.get(field_name)
                # '7' или None если ничего не выбрано
                selected_ids = [selected_id] if selected_id else []

            # СОЗДАЕМ QuestionAttempt
            question_attempt = QuestionAttempt.objects.create(
                attempt=test_attempt, question=question
            )

            # ДОБАВЛЯЕМ выбранные ответы
            if selected_ids:
                # Конвертируем ID из строк в числа
                answer_ids = [int(id) for id in selected_ids]
                answers = Answer.objects.filter(id__in=answer_ids)
                question_attempt.selected_answers.set(answers)

                if selected_ids == correct_answers[question.id]:
                    score += 1
                else:
                    for id in selected_ids:
                        if id in correct_answers[question.id]:
                            score += 0.5 

        percent = score / len(questions)
        if percent >= 0.91:
            test_attempt.score = 5
        elif percent >= 0.76:
            test_attempt.score = 4
        elif percent >= 0.60:
            test_attempt.score = 3
        else:
            test_attempt.score = 2

        test_attempt.save()

        return HttpResponseRedirect(reverse_lazy("tests:list"))

    answers = [question.answers.all() for question in questions]
    questions_with_answers = zip(questions, answers)

    return render(
        request,
        "study_tests/test_attempt.html",
        {
            "test": test,
            "questions_with_answers": questions_with_answers,
            "attempt_limit": attempt_limit,
        },
    )
