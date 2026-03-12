from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from .models import Question


@login_required(login_url='login')
@role_required('admin', 'enseignant')
def question_liste(request):
    questions = Question.objects.select_related('module').all()
    return render(request, 'admin/questions/liste.html', {'questions': questions})