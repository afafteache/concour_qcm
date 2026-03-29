from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from accounts.decorators import role_required
from .models import Concours, Module, SessionConcours


# ═══════════════════════════════════════════════════════════
#  MODULES
# ═══════════════════════════════════════════════════════════

@login_required(login_url='login')
@role_required('admin', 'enseignant')
def module_liste(request):
    modules = Module.objects.all().order_by('nom')
    return render(request, 'admin/modules/liste.html', {'modules': modules})


@login_required(login_url='login')
@role_required('admin', 'enseignant')
def module_creer(request):
    if request.method == 'POST':
        nom         = request.POST.get('nom', '').strip()
        description = request.POST.get('description', '').strip()
        if not nom:
            messages.error(request, 'Le nom du module est obligatoire.')
        else:
            Module.objects.create(nom=nom, description=description)
            messages.success(request, f'Module "{nom}" créé avec succès.')
            return redirect('module_liste')
    return render(request, 'admin/modules/form.html', {'action': 'Créer'})


@login_required(login_url='login')
@role_required('admin', 'enseignant')
def module_modifier(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if request.method == 'POST':
        module.nom         = request.POST.get('nom', '').strip()
        module.description = request.POST.get('description', '').strip()
        if not module.nom:
            messages.error(request, 'Le nom du module est obligatoire.')
        else:
            module.save()
            messages.success(request, 'Module modifié avec succès.')
            return redirect('module_liste')
    return render(request, 'admin/modules/form.html', {'action': 'Modifier', 'module': module})


@login_required(login_url='login')
@role_required('admin')
def module_supprimer(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if request.method == 'POST':
        module.delete()
        messages.success(request, 'Module supprimé.')
        return redirect('module_liste')
    return render(request, 'admin/modules/confirmer_suppression.html', {'objet': module, 'type': 'module'})


# ═══════════════════════════════════════════════════════════
#  CONCOURS
# ═══════════════════════════════════════════════════════════

@login_required(login_url='login')
@role_required('admin', 'enseignant')
def concours_liste(request):
    concours = Concours.objects.select_related('module').all()
    return render(request, 'admin/concours/liste.html', {'concours': concours})


@login_required(login_url='login')
@role_required('admin', 'enseignant')
def concours_creer(request):
    modules = Module.objects.all()
    if request.method == 'POST':
        titre            = request.POST.get('titre', '').strip()
        module_id        = request.POST.get('module')
        nombre_questions = request.POST.get('nombre_questions', 20)
        duree_minutes    = request.POST.get('duree_minutes', 60)

        if not titre:
            messages.error(request, 'Le titre est obligatoire.')
            return render(request, 'admin/concours/form.html', {
                'modules': modules,
                'action': 'Créer',
                'concours': None,
                'post_data': request.POST,
            })
        else:
            from django.utils import timezone
            Concours.objects.create(
                titre=titre,
                date=timezone.now().date(),
                module_id=module_id if module_id else None,
                nombre_questions=nombre_questions,
                duree_minutes=duree_minutes,
                cree_par=request.user,
            )
            messages.success(request, f'Concours "{titre}" créé.')
            return redirect('concours_liste')

    return render(request, 'admin/concours/form.html', {
        'modules': modules,
        'action': 'Créer',
        'concours': None,
        'post_data': None,
    })


@login_required(login_url='login')
@role_required('admin', 'enseignant')
def concours_modifier(request, pk):
    concours = get_object_or_404(Concours, pk=pk)
    modules  = Module.objects.all()
    if request.method == 'POST':
        concours.titre            = request.POST.get('titre', '').strip()
        concours.date             = request.POST.get('date', '')
        module_id                 = request.POST.get('module')
        concours.module_id        = module_id if module_id else None
        concours.nombre_questions = request.POST.get('nombre_questions', 20)
        concours.duree_minutes    = request.POST.get('duree_minutes', 60)
        if not concours.titre:
            messages.error(request, 'Le titre est obligatoire.')
        else:
            concours.save()
            messages.success(request, 'Concours modifié.')
            return redirect('concours_liste')
    return render(request, 'admin/concours/form.html', {
        'modules': modules,
        'concours': concours,
        'action': 'Modifier',
        'post_data': None,
    })


@login_required(login_url='login')
@role_required('admin')
def concours_supprimer(request, pk):
    concours = get_object_or_404(Concours, pk=pk)
    if request.method == 'POST':
        concours.delete()
        messages.success(request, 'Concours supprimé.')
        return redirect('concours_liste')
    return render(request, 'admin/concours/confirmer_suppression.html', {'objet': concours, 'type': 'concours'})


# ═══════════════════════════════════════════════════════════
#  SESSIONS
# ═══════════════════════════════════════════════════════════

@login_required(login_url='login')
@role_required('admin', 'enseignant')
def session_liste(request):
    sessions = SessionConcours.objects.select_related('concours', 'concours__module').all()
    now      = timezone.now()
    return render(request, 'admin/sessions/liste.html', {'sessions': sessions, 'now': now})


@login_required(login_url='login')
@role_required('admin', 'enseignant')
def session_creer(request):
    concours_list = Concours.objects.all()
    if request.method == 'POST':
        nom_session   = request.POST.get('nom_session', '').strip()
        concours_id   = request.POST.get('concours')
        date_debut    = request.POST.get('date_heure_debut', '')
        date_fin      = request.POST.get('date_heure_fin', '')
        duree_minutes = request.POST.get('duree_minutes', 60)

        if not nom_session or not concours_id or not date_debut:
            messages.error(request, 'Tous les champs obligatoires doivent être remplis.')
        else:
            SessionConcours.objects.create(
                nom_session=nom_session,
                concours_id=concours_id,
                date_heure_debut=date_debut,
                date_heure_fin=date_fin,
                duree_minutes=duree_minutes,
            )
            messages.success(request, f'Session "{nom_session}" créée.')
            return redirect('session_liste')
    return render(request, 'admin/sessions/form.html', {'concours_list': concours_list, 'action': 'Créer'})


@login_required(login_url='login')
@role_required('admin', 'enseignant')
def session_modifier(request, pk):
    session       = get_object_or_404(SessionConcours, pk=pk)
    concours_list = Concours.objects.all()
    if request.method == 'POST':
        session.nom_session      = request.POST.get('nom_session', '').strip()
        session.concours_id      = request.POST.get('concours')
        session.date_heure_debut = request.POST.get('date_heure_debut', '')
        session.date_heure_fin   = request.POST.get('date_heure_fin', '')
        session.duree_minutes    = request.POST.get('duree_minutes', 60)
        session.etat             = request.POST.get('etat', 'planifiee')
        session.save()
        messages.success(request, 'Session modifiée.')
        return redirect('session_liste')
    return render(request, 'admin/sessions/form.html', {
        'concours_list': concours_list, 'session': session, 'action': 'Modifier'
    })


@login_required(login_url='login')
@role_required('admin')
def session_supprimer(request, pk):
    session = get_object_or_404(SessionConcours, pk=pk)
    if request.method == 'POST':
        session.delete()
        messages.success(request, 'Session supprimée.')
        return redirect('session_liste')
    return render(request, 'admin/sessions/confirmer_suppression.html', {'objet': session, 'type': 'session'})


@login_required(login_url='login')
@role_required('admin')
def session_lancer(request, pk):
    session = get_object_or_404(SessionConcours, pk=pk)
    now     = timezone.now()

    if session.examen_lance:
        messages.warning(request, 'Cet examen a déjà été lancé.')
    elif now < session.date_heure_debut:
        messages.error(request, "L'heure de début n'est pas encore atteinte.")
    else:
        from datetime import timedelta
        session.examen_lance   = True
        session.etat           = 'en_cours'
        session.date_lancement = now
        session.lance_par      = request.user
        # Recalcule la fin à partir du moment du lancement
        session.date_heure_fin = now + timedelta(minutes=session.duree_minutes)
        session.save()
        messages.success(request, "Examen lancé ! Les candidats peuvent maintenant accéder à l'examen.")

    return redirect('dashboard_admin')