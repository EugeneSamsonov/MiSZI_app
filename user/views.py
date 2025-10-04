from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

# Create your views here.
from user.models import User


def user_update(request):
    if request.method == 'POST':
        user = User.objects.get(id=request.POST.get('user_id'))

        user.is_blocked = not user.is_blocked
        user.save()

    return HttpResponseRedirect(reverse_lazy("home"))