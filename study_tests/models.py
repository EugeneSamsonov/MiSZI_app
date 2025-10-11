from django.db import models

from users.models import User


# Create your models here.
class StudyTest(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    attempt_limit = models.IntegerField(default=3)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Question(models.Model):
    test = models.ForeignKey(
        StudyTest, related_name="questions", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=255)
    multiple_answers = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(
        Question, related_name="answers", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class TestAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(StudyTest, on_delete=models.CASCADE)
    attempt_number = models.IntegerField(default=1)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.test} - №{self.attempt_number}"


class QuestionAttempt(models.Model):
    attempt = models.ForeignKey(
        TestAttempt, on_delete=models.CASCADE, related_name="question_attempts"
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answers = models.ManyToManyField(Answer)

    def __str__(self):
        return f"{self.attempt} - {self.question}"
