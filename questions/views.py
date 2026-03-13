from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from .models import Question, Choix


# Dashboard enseignant
@login_required(login_url='login')
@role_required('enseignant')
def dashboard_enseignant(request):
    questions = Question.objects.filter(cree_par=request.user)

    context = {
        "total_questions": questions.count(),
        "questions": questions[:5]
    }

    return render(request, "enseignant/dashboard_enseignant.html", context)


@login_required(login_url='login')
@role_required('admin', 'enseignant')
def question_liste(request):
    questions = Question.objects.filter(cree_par=request.user).prefetch_related('choix_set').order_by('-date_creation')
    return render(request, 'enseignant/questions/liste.html', {'questions': questions})


@login_required(login_url='login')
@role_required('enseignant')
def question_ajouter(request):
    if request.method == 'POST':
        texte = request.POST.get('texte', '').strip()
        bonne_reponse = request.POST.get('bonne_reponse', '')

        if not texte:
            messages.error(request, 'Le texte de la question est obligatoire.')
        elif bonne_reponse == '':
            messages.error(request, 'Veuillez sélectionner la bonne réponse.')
        else:
            question = Question.objects.create(texte=texte, cree_par=request.user)

            for i in range(4):
                texte_choix = request.POST.get(f'choix_{i}', '').strip()
                if texte_choix:
                    Choix.objects.create(
                        question=question,
                        texte=texte_choix,
                        est_correct=(str(i) == str(bonne_reponse))
                    )

            messages.success(request, 'Question ajoutée avec succès.')
            return redirect('question_liste')

    return render(request, 'enseignant/questions/form.html', {
        'titre': 'Ajouter une question',
        'action': 'Ajouter',
    })


@login_required(login_url='login')
@role_required('enseignant')
def question_modifier(request, pk):
    question = get_object_or_404(Question, pk=pk, cree_par=request.user)
    choix_list = list(question.choix_set.all())

    if request.method == 'POST':
        texte = request.POST.get('texte', '').strip()
        bonne_reponse = request.POST.get('bonne_reponse', '')

        if not texte:
            messages.error(request, 'Le texte de la question est obligatoire.')
        elif bonne_reponse == '':
            messages.error(request, 'Veuillez sélectionner la bonne réponse.')
        else:
            question.texte = texte
            question.save()

            question.choix_set.all().delete()

            for i in range(4):
                texte_choix = request.POST.get(f'choix_{i}', '').strip()
                if texte_choix:
                    Choix.objects.create(
                        question=question,
                        texte=texte_choix,
                        est_correct=(str(i) == str(bonne_reponse))
                    )

            messages.success(request, 'Question modifiée avec succès.')
            return redirect('question_liste')

    return render(request, 'enseignant/questions/form.html', {
        'titre': 'Modifier la question',
        'action': 'Enregistrer',
        'question': question,
        'choix_list': choix_list,
    })


@login_required(login_url='login')
@role_required('enseignant')
def question_supprimer(request, pk):
    question = get_object_or_404(Question, pk=pk, cree_par=request.user)
    question.delete()
    messages.success(request, 'Question supprimée.')
    return redirect('question_liste')