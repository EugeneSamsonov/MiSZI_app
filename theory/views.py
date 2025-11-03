from django.shortcuts import render

from study_tests.models import TestCategory
from theory.models import Theory


# Create your views here.
def theory_list(request, category=None):
    if category is None:
        tests_categories = TestCategory.objects.all()
        link_name = "theory:list"
        return render(
            request,
            "study_tests/tests_category_list.html",
            {
                "tests_categories": tests_categories,
                "link_name": link_name,
            },
        )
    
    theory_list = Theory.objects.filter(category__name=category)
    return render(request, "theory/theory_list.html", {"theory_list": theory_list})


def theory_detail(request, theory_id):
    theory = Theory.objects.get(id=theory_id)
    return render(request, "theory/theory_detail.html", {"theory": theory})
