from django.contrib import admin

from .models import StudyTest, Question, Answer, TestAttempt, QuestionAttempt, TestCategory
# Register your models here.
class TestCategoryAdmin(admin.ModelAdmin):
    pass

class StudyTestAdmin(admin.ModelAdmin):
    pass

class QuestionAdmin(admin.ModelAdmin):
    pass

class AnswerAdmin(admin.ModelAdmin):
    pass

class TestAttemptAdmin(admin.ModelAdmin):
    pass

class QuestionAttemptAdmin(admin.ModelAdmin):
    pass


admin.site.register(TestCategory, TestCategoryAdmin)
admin.site.register(StudyTest, StudyTestAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(TestAttempt, TestAttemptAdmin)
admin.site.register(QuestionAttempt, QuestionAttemptAdmin)