import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_qcm.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Profil

# ── Admin principal ───────────────────────────────────────
admin = User.objects.create_superuser(
    username='OD67857',
    password='admin123',
    first_name='Salma',
    last_name='Ben Aouama',
    email='salma@gmail.com',
)
Profil.objects.create(user=admin, cin='OD67857', role='admin')
print("✅ Admin : Salma Ben Aouama — CIN: OD67857 — MDP: admin123")

# ── Enseignant ────────────────────────────────────────────
ens = User.objects.create_user(
    username='OD67853',
    password='ens123',
    first_name='Fatiha',
    last_name='Zouhri',
)
Profil.objects.create(user=ens, cin='OD67853', role='enseignant')
print("✅ Enseignant : Fatiha Zouhri — CIN: OD67853 — MDP: ens123")

# ── Candidats de test ─────────────────────────────────────
candidats = [
    {'prenom': 'Khadija', 'nom': 'Daji',   'cin': 'OD67855'},
    {'prenom': 'Mohamed', 'nom': 'Alami',  'cin': 'AB123456'},
    {'prenom': 'Fatima',  'nom': 'Benali', 'cin': 'CD789012'},
]

for c in candidats:
    u = User.objects.create_user(
        username=c['cin'], password=c['cin'],
        first_name=c['prenom'], last_name=c['nom'],
    )
    Profil.objects.create(user=u, cin=c['cin'], role='candidat')
    print(f"✅ Candidat : {c['prenom']} {c['nom']} — CIN: {c['cin']}")

print("\n🎉 Setup terminé !")