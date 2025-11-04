from django.db import models

from users.models import User


# Create your models here.
class TestCategory(models.Model):

    class Meta:
        verbose_name = "Категория теста"
        verbose_name_plural = "Категории тестов"

    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return f"Категория: {self.name}"


class StudyTest(models.Model):

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"

    title = models.CharField(max_length=255)
    category = models.ForeignKey(TestCategory, on_delete=models.CASCADE)
    description = models.TextField()
    attempt_limit = models.IntegerField(default=3)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Тест: {self.title} (автор: {self.author})"


class Question(models.Model):

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    test = models.ForeignKey(
        StudyTest, related_name="questions", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=255)
    multiple_answers = models.BooleanField(default=False)

    def __str__(self):
        suffix = " | множественный выбор" if self.multiple_answers else ""
        return f"Вопрос теста {self.test_id}: {self.text}{suffix}"


class Answer(models.Model):

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    question = models.ForeignKey(
        Question, related_name="answers", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        mark = "✔" if self.is_correct else "✘"
        return f"Ответ {self.id} к вопросу {self.question_id}: {self.text} {mark}"


class TestAttempt(models.Model):

    class Meta:
        verbose_name = "Попытка"
        verbose_name_plural = "Попытки"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(StudyTest, on_delete=models.CASCADE)
    attempt_number = models.IntegerField(default=1)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(null=True, blank=True)

    def get_correct_count(self):
        correct_count = 0
        for question_attempt in self.question_attempts.all():
            if question_attempt.selected_answers.count() == 0:
                continue
            if question_attempt.question.multiple_answers:
                if question_attempt.selected_answers.count() == question_attempt.question.answers.filter(is_correct=True).count():
                    correct_count += 1
                else:
                    correct_count += (
                    question_attempt.selected_answers.filter(is_correct=True).count()
                    / question_attempt.question.answers.count()
                )
            else:
                correct_count += (
                    1
                    if question_attempt.selected_answers.filter(
                        is_correct=True
                    ).exists()
                    else 0
                )

        return (
            correct_count if int(correct_count) != correct_count else int(correct_count)
        )

    def get_question_count(self):
        return self.test.questions.count()

    def __str__(self):
        return f"{self.user} - {self.test} - №{self.attempt_number}"


class QuestionAttempt(models.Model):

    class Meta:
        verbose_name = "Ответ на вопрос"
        verbose_name_plural = "Ответы на вопросы"

    attempt = models.ForeignKey(
        TestAttempt, on_delete=models.CASCADE, related_name="question_attempts"
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answers = models.ManyToManyField(Answer)

    def __str__(self):
        return f"{self.attempt} - {self.question} - {self.id}"
