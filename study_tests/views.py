from django.utils import timezone
from datetime import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Window
from django.db.models import Subquery, OuterRef, Q
from django.db.models.functions import RowNumber

from study_tests.models import (
    Answer,
    QuestionAttempt,
    StudyTest,
    TestAttempt,
    TestCategory,
)

from .forms import StudyTestForm, QuestionFormSet, AnswerFormSet


@login_required
def control_panel(request, category):
    if not request.user.is_admin:
        return HttpResponseRedirect(reverse_lazy("user:home"))

    tests = StudyTest.objects.filter(author=request.user, category__name=category)
    return render(
        request,
        "study_tests/control_panel.html",
        {"tests": tests, "category": category},
    )

    # tests = StudyTest.objects.filter(author=request.user)
    # return render(request, "study_tests/control_panel.html", {"tests": tests})


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


@login_required
def create_test(request, category):
    if not request.user.is_admin:
        return HttpResponseRedirect(reverse_lazy("user:home"))

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
            test.category = TestCategory.objects.get(name=category)
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

            return HttpResponseRedirect(
                request.META.get(
                    "HTTP_REFERER",
                    reverse_lazy("tests:control-panel", kwargs={"category": category}),
                )
            )
            # return HttpResponseRedirect(reverse_lazy("tests:control-panel", kwargs={'category': category}))
        else:
            return render(
                request,
                "study_tests/create_test.html",
                {
                    "test_form": test_form,
                    "question_formset": question_formset,
                    "questions_with_answers": questions_with_answers,
                    "answer_formsets": answer_formsets,
                    "category": category,
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
            "category": category,  # Добавьте это для management_form
        },
    )


@login_required
def delete_test(request, test_id):
    if not request.user.is_admin:
        return HttpResponseRedirect(reverse_lazy("user:home"))

    test = StudyTest.objects.get(id=test_id)
    test.delete()
    return HttpResponseRedirect(
        request.META.get(
            "HTTP_REFERER",
            reverse_lazy("tests:control-panel"),
        )
    )


@login_required
def tests_list(request, category=None):
    if category is None:
        tests_categories = TestCategory.objects.all()
        link_name = "tests:list"
        return render(
            request,
            "study_tests/tests_category_list.html",
            {"tests_categories": tests_categories, "link_name": link_name},
        )

    tests = StudyTest.objects.filter(category__name=category)
    return render(request, "study_tests/tests_list.html", {"tests": tests})


@login_required
def test(request, test_id):
    test = StudyTest.objects.get(id=test_id)
    questions = test.questions.all().prefetch_related("answers").order_by("id")
    user_attempts = TestAttempt.objects.filter(test=test, user=request.user).count()
    attempt_limit = test.attempt_limit - user_attempts

    if request.method == "POST":
        if attempt_limit <= 0:
            return HttpResponseRedirect(reverse_lazy("tests:test", args=[test_id]))
        test_attempt = TestAttempt.objects.create(
            user=request.user,
            test=test,
            started_at=datetime.strptime(request.POST.get("started_at"), "%Y-%m-%d %H:%M"),
            completed_at=timezone.now(),
            attempt_number=user_attempts + 1,
        )

        for question in questions:
            field_name = f"question_{question.id}"

            if question.multiple_answers:
                selected_ids = request.POST.getlist(field_name)
            else:
                selected_id = request.POST.get(field_name)
                selected_ids = [selected_id] if selected_id else []

            question_attempt = QuestionAttempt.objects.create(
                attempt=test_attempt, question=question
            )

            if selected_ids:
                answer_ids = [int(id) for id in selected_ids]
                answers = Answer.objects.filter(id__in=answer_ids)
                question_attempt.selected_answers.set(answers)

        percent = test_attempt.get_correct_count() / test_attempt.get_question_count()
        if percent >= 0.86:
            test_attempt.score = 5
        elif percent >= 0.66:
            test_attempt.score = 4
        elif percent >= 0.56:
            test_attempt.score = 3
        else:
            test_attempt.score = 2

        test_attempt.save()

        return HttpResponseRedirect(reverse_lazy("tests:home"))

    answers = [question.answers.all() for question in questions]
    questions_with_answers = zip(questions, answers)
    started_at = timezone.localtime(timezone.now())

    return render(
        request,
        "study_tests/test_attempt.html",
        {
            "test": test,
            "questions_with_answers": questions_with_answers,
            "attempt_limit": attempt_limit,
            "started_at": started_at.strftime("%Y-%m-%d %H:%M"),
        },
    )


@login_required
def home(request, category=None):
    if request.user.is_admin:
        if category is None:
            tests_categories = TestCategory.objects.all()
            link_name = "tests:control-panel"
            return render(
                request,
                "study_tests/tests_category_list.html",
                {
                    "tests_categories": tests_categories,
                    "link_name": link_name,
                },
            )
        return render(request, "study_tests/home_admin.html")
    # Самая лучшая попытка для каждого теста
    best_attempts = (
        TestAttempt.objects.filter(user=request.user, test_id=OuterRef("test_id"))
        .order_by("-score", "-started_at")
        .values("id")[:1]
    )

    # Самая последняя попытка для каждого теста
    latest_attempts = (
        TestAttempt.objects.filter(user=request.user, test_id=OuterRef("test_id"))
        .order_by("-started_at")
        .values("id")[:1]
    )

    # Объединяем оба условия через Q
    attempts = (
        TestAttempt.objects.filter(user=request.user)
        .filter(Q(id__in=Subquery(best_attempts)) | Q(id__in=Subquery(latest_attempts)))
        .order_by("test_id", "-score")
    )

    return render(
        request,
        "study_tests/home.html",
        {
            "attempts": attempts,
        },
    )


@login_required
def attempt_result(request, test_id):
    attempt = TestAttempt.objects.get(id=test_id)
    questions = attempt.test.questions.all().prefetch_related("answers").order_by("id")
    selected_answers_ids = [
        answer.id
        for question in attempt.question_attempts.all()
        for answer in question.selected_answers.all()
    ]
    questions_with_answers = zip(
        questions, [question.answers.all() for question in questions]
    )
    return render(
        request,
        "study_tests/attempt_result.html",
        {
            "attempt": attempt,
            "questions_with_answers": questions_with_answers,
            "selected_answers_ids": selected_answers_ids,
        },
    )


@login_required
def list_passed_users(request, category, test_id=None):
    if not request.user.is_admin:
        return HttpResponseRedirect(reverse_lazy("user:home"))

    if test_id is None:
        tests = StudyTest.objects.filter(category__name=category)
        return render(
            request,
            "study_tests/tests_list_passed_users.html",
            {"tests": tests, "category": category},
        )

    attempts = (
        TestAttempt.objects.filter(test_id=test_id, test__category__name=category)
        .annotate(
            row_number=Window(
                expression=RowNumber(),
                partition_by=["user_id"],
                order_by=[
                    "-score",
                    "-id",
                ],  # -id чтобы брать последнюю при одинаковых оценках
            )
        )
        .filter(row_number=1)
        .order_by("-score")
    )
    test_title = StudyTest.objects.get(id=test_id).title
    return render(
        request,
        "study_tests/list_passed_users.html",
        {"attempts": attempts, "test_title": test_title},
    )
