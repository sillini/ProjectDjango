from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import Utilisateur
import uuid
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, TravailForm
from .models import Utilisateur, Cours, Section, Travail, Soumission
from django.utils import timezone


# Create your views here.
def accueil(request):
    context = {
        'title': 'Bienvenue ', 
    }
    return render(request, 'core/accueil.html', context)

from django.contrib.auth.models import User, Group
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.contrib import messages
import uuid
from .models import Utilisateur

def register(request):
    if request.method == 'POST':
        try:
            # Validation des champs obligatoires
            required_fields = ['nom', 'email', 'motdepasse', 'type']
            for field in required_fields:
                if not request.POST.get(field):
                    messages.error(request, f"Le champ {field} est obligatoire")
                    return redirect('register')

            # Vérification de l'email unique
            if Utilisateur.objects.filter(email=request.POST.get('email')).exists() or \
               User.objects.filter(email=request.POST.get('email')).exists():
                messages.error(request, "Cet email est déjà utilisé")
                return redirect('register')

            # Vérification de la correspondance des mots de passe
            if request.POST.get('motdepasse') != request.POST.get('confirm_mdp'):
                messages.error(request, "Les mots de passe ne correspondent pas")
                return redirect('register')

            # Génération d'un ID unique
            idu = str(uuid.uuid4())[:8]
            
            # Récupération du type d'utilisateur avec correction orthographique
            user_type = request.POST.get('type')
            if user_type == 'enseignant':  # S'assurer que c'est bien 'enseignant' et non 'enseigant'
                user_type_db = 'enseignant'
            else:
                user_type_db = user_type
            
            # Création de l'utilisateur Django (User)
            django_user = User.objects.create_user(
                username=request.POST.get('email'),
                email=request.POST.get('email'),
                password=request.POST.get('motdepasse'),
                first_name=request.POST.get('nom').split(' ')[0],
                last_name=' '.join(request.POST.get('nom').split(' ')[1:]) if ' ' in request.POST.get('nom') else ''
            )
            
            # Ajout de l'utilisateur au groupe approprié
            group = Group.objects.get(name=user_type)  # Le groupe doit correspondre exactement
            django_user.groups.add(group)
            django_user.save()

            # Création du profil Utilisateur
            utilisateur = Utilisateur(
                idu=idu,
                user=django_user,
                nom=request.POST.get('nom'),
                email=request.POST.get('email'),
                motdepasse=make_password(request.POST.get('motdepasse')),
                specialite=request.POST.get('specialite'),
                type=user_type_db,  # Utilisation de la version corrigée
            )
            
            # Champs spécifiques aux enseignants
            if user_type == 'enseignant':
                cv_file = request.FILES.get('cv')
                if not cv_file:
                    messages.error(request, "Le CV est obligatoire pour les enseignants")
                    django_user.delete()
                    return redirect('register')
                
                fs = FileSystemStorage(location='media/cvs/')
                filename = fs.save(cv_file.name, cv_file)
                utilisateur.cv = f'cvs/{filename}'
                utilisateur.specialisation = request.POST.get('specialisation', '')
            
            # Champs spécifiques aux étudiants
            elif user_type == 'etudiant':
                utilisateur.niveau = request.POST.get('niveau', '')
            
            utilisateur.save()
            
            messages.success(request, 'Votre compte a été créé avec succès!')
            return redirect('accueil')
            
        except Group.DoesNotExist:
            messages.error(request, "Le groupe spécifié n'existe pas")
            if 'django_user' in locals():
                django_user.delete()
            return redirect('register')
        except Exception as e:
            messages.error(request, f"Une erreur est survenue: {str(e)}")
            if 'django_user' in locals():
                django_user.delete()
            return redirect('register')
    
    return render(request, 'core/register.html')

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Utilisateur

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, Group

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Utilisateur

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            # 1. Trouver l'utilisateur par email
            user = User.objects.get(email=email)
            
            # 2. Authentifier avec le username
            auth_user = authenticate(request, username=user.username, password=password)
            
            if auth_user is not None:
                login(request, auth_user)
                
                # 3. Récupérer le profil utilisateur personnalisé
                try:
                    utilisateur = Utilisateur.objects.get(user=auth_user)
                    
                    # 4. Redirection selon le type
                    if utilisateur.type == 'admin':
                        return redirect('admin_dashboard')
                    elif utilisateur.type == 'enseignant':
                        return redirect('enseignant_dashboard')
                    elif utilisateur.type == 'etudiant':
                        return redirect('etudiant_dashboard')
                    else:
                        messages.error(request, "Votre compte n'a pas de rôle attribué")
                        return redirect('accueil')
                        
                except Utilisateur.DoesNotExist:
                    messages.error(request, "Profil utilisateur introuvable")
                    return redirect('accueil')
            else:
                messages.error(request, "Mot de passe incorrect")
                return redirect('accueil')
                
        except User.DoesNotExist:
            messages.error(request, "Aucun compte avec cet email")
            return redirect('accueil')
    
    return render(request, 'core/accueil.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Utilisateur, Cours, Travail, Soumission
from django.utils import timezone

@login_required
def enseignant_dashboard(request):
    return render(request, 'core/enseignant_dashboard.html')

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from .models import Utilisateur

@login_required
def profil_enseignant(request):
    try:
        utilisateur = Utilisateur.objects.get(user=request.user)
    except Utilisateur.DoesNotExist:
        messages.error(request, "Profil utilisateur non trouvé.")
        return redirect('enseignant_dashboard')

    if request.method == 'POST':
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        motdepasse = request.POST.get('motdepasse')
        confirm_motdepasse = request.POST.get('confirm_motdepasse')
        specialisation = request.POST.get('specialisation')

        # Vérifier unicité de l'email
        if Utilisateur.objects.exclude(pk=utilisateur.pk).filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
        else:
            # Vérification du mot de passe
            if motdepasse:
                if len(motdepasse) < 8:
                    messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
                elif motdepasse != confirm_motdepasse:
                    messages.error(request, "Les mots de passe ne correspondent pas.")
                else:
                    # Seul le User standard de Django a set_password()
                    request.user.set_password(motdepasse)
                    update_session_auth_hash(request, request.user)
                    messages.success(request, "Mot de passe mis à jour avec succès.")

            # Mise à jour des autres champs
            utilisateur.nom = nom
            utilisateur.email = email
            utilisateur.specialisation = specialisation
            
            # Sauvegarde
            utilisateur.save()
            request.user.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('profil_enseignant')

    return render(request, 'core/profil_enseignant.html', {'utilisateur': utilisateur})
@login_required
def mes_cours(request):
    try:
        utilisateur = Utilisateur.objects.get(user=request.user)
        cours = Cours.objects.filter(utilisateur=utilisateur).order_by('-idc')
    except Utilisateur.DoesNotExist:
        messages.error(request, "Profil utilisateur non trouvé.")
        return redirect('enseignant_dashboard')
    
    context = {
        'cours_list': cours,
        'utilisateur': utilisateur
    }
    return render(request, 'core/mes_cours.html', context)


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Cours, Utilisateur, Section
from .forms import CoursForm, SectionFormSet
import time

@login_required
def creer_cours(request):
    try:
        enseignant = Utilisateur.objects.get(user=request.user, type='enseignant')
    except Utilisateur.DoesNotExist:
        messages.error(request, "Seuls les enseignants peuvent créer des cours")
        return redirect('enseignant_dashboard')

    if request.method == 'POST':
        form = CoursForm(request.POST)
        formset = SectionFormSet(request.POST, request.FILES)  # Ajout de request.FILES
        
        if form.is_valid() and formset.is_valid():
            # Création du cours
            cours = form.save(commit=False)
            cours.utilisateur = enseignant
            cours.idc = f"CRS-{int(time.time())}-{enseignant.idu[:4]}"
            cours.save()
            
            # Création des sections
            for section_form in formset:
                if section_form.cleaned_data.get('titre'):
                    section = section_form.save(commit=False)
                    section.cours = cours
                    section.idsec = f"SEC-{int(time.time())}-{section_form.cleaned_data['titre'][:3].upper()}"
                    section.save()
            
            messages.success(request, "Cours créé avec succès!")
            return redirect('mes_cours')
    else:
        form = CoursForm()
        formset = SectionFormSet(queryset=Section.objects.none())

    return render(request, 'core/creer_cours.html', {
        'form': form,
        'formset': formset,
        'enseignant': enseignant
    })

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cours, Utilisateur

@login_required
def detail_cours(request, cours_id):
    cours = get_object_or_404(Cours, idc=cours_id)
    sections = cours.sections.all().order_by('idsec')
    travaux = cours.travaux.all().order_by('-date_creation')  # Récupère tous les travaux du cours
    
    try:
        utilisateur = Utilisateur.objects.get(user=request.user)
        if utilisateur != cours.utilisateur and utilisateur.type != 'admin':
            messages.error(request, "Vous n'avez pas accès à ce cours")
            return redirect('mes_cours')
    except Utilisateur.DoesNotExist:
        messages.error(request, "Utilisateur non trouvé")
        return redirect('accueil')

    return render(request, 'core/detail_cours.html', {
        'cours': cours,
        'sections': sections,
        'travaux': travaux,  # Ajout des travaux au contexte
        'is_enseignant': utilisateur.type == 'enseignant'
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Cours, Section, Utilisateur
from .forms import SectionForm
import uuid
from datetime import datetime

@login_required
def creer_section(request, cours_id):
    cours = get_object_or_404(Cours, idc=cours_id)
    
    # Vérification des permissions
    try:
        utilisateur = Utilisateur.objects.get(user=request.user)
        if utilisateur != cours.utilisateur and utilisateur.type != 'admin':
            messages.error(request, "Vous n'avez pas la permission d'ajouter des sections à ce cours")
            return redirect('detail_cours', cours_id=cours.idc)
    except Utilisateur.DoesNotExist:
        messages.error(request, "Utilisateur non trouvé")
        return redirect('accueil')

    if request.method == 'POST':
        form = SectionForm(request.POST, request.FILES)
        if form.is_valid():
            section = form.save(commit=False)
            section.cours = cours
            section.idsec = f"SEC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
            
            # Gestion du fichier uploadé
            if 'fichier' in request.FILES:
                section.fichier = request.FILES['fichier']
            
            section.save()
            messages.success(request, "Section créée avec succès!")
            return redirect('detail_cours', cours_id=cours.idc)
    else:
        form = SectionForm(initial={'cache': False})

    return render(request, 'core/creer_section.html', {
        'form': form,
        'cours': cours,
        'is_enseignant': utilisateur.type == 'enseignant'
    })
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Cours, Utilisateur
from .forms import CoursForm

@login_required
def modifier_cours(request, cours_id):
    cours = get_object_or_404(Cours, idc=cours_id)
    
    # Vérification des permissions
    try:
        utilisateur = Utilisateur.objects.get(user=request.user)
        if utilisateur != cours.utilisateur and utilisateur.type != 'admin':
            messages.error(request, "Vous n'avez pas la permission de modifier ce cours")
            return redirect('detail_cours', cours_id=cours.idc)
    except Utilisateur.DoesNotExist:
        messages.error(request, "Utilisateur non trouvé")
        return redirect('accueil')

    if request.method == 'POST':
        form = CoursForm(request.POST, instance=cours)
        if form.is_valid():
            form.save()
            messages.success(request, "Cours mis à jour avec succès!")
            return redirect('detail_cours', cours_id=cours.idc)
    else:
        form = CoursForm(instance=cours)

    return render(request, 'core/modifier_cours.html', {
        'form': form,
        'cours': cours,
        'is_enseignant': utilisateur.type == 'enseignant'
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Section, Cours, Utilisateur
from .forms import SectionForm
from django.core.files.base import ContentFile
import os

@login_required
def modifier_section(request, section_id):
    section = get_object_or_404(Section, idsec=section_id)
    cours = section.cours

    # Vérification des permissions
    try:
        utilisateur = Utilisateur.objects.get(user=request.user)
        if utilisateur != cours.utilisateur and utilisateur.type != 'admin':
            messages.error(request, "Vous n'avez pas la permission de modifier cette section")
            return redirect('detail_cours', cours_id=cours.idc)
    except Utilisateur.DoesNotExist:
        messages.error(request, "Utilisateur non trouvé")
        return redirect('accueil')

    if request.method == 'POST':
        form = SectionForm(request.POST, request.FILES, instance=section)
        if form.is_valid():
            # Créer une copie du fichier avant la sauvegarde
            new_file = request.FILES.get('fichier', None)
            if new_file:
                # Sauvegarder le contenu du fichier en mémoire
                file_content = new_file.read()
                section.fichier.save(
                    new_file.name,
                    ContentFile(file_content),
                    save=False
                )
            
            # Gestion de la suppression du fichier
            if 'fichier-clear' in request.POST and section.fichier:
                section.fichier.delete()
                section.fichier = None
            
            # Sauvegarder les autres modifications
            form.save()
            
            messages.success(request, "Section modifiée avec succès!")
            return redirect('detail_cours', cours_id=cours.idc)
    else:
        form = SectionForm(instance=section)

    return render(request, 'core/modifier_section.html', {
        'form': form,
        'section': section,
        'cours': cours,
        'has_file': bool(section.fichier)
    })

# Dans views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Cours, Travail

def selectionner_cours_pour_travail(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'utilisateur'):
        return redirect('login')
    
    # Récupérer seulement les cours de l'enseignant connecté
    cours_list = Cours.objects.filter(utilisateur=request.user.utilisateur)
    
    return render(request, 'core/selectionner_cours_travail.html', {
        'cours_list': cours_list
    })

def creer_travail(request, cours_id):
    if not request.user.is_authenticated or not hasattr(request.user, 'utilisateur'):
        return redirect('login')
    
    cours = get_object_or_404(Cours, idc=cours_id, utilisateur=request.user.utilisateur)
    
    if request.method == 'POST':
        # Traitement du formulaire de création de travail
        titre = request.POST.get('titre')
        description = request.POST.get('description')
        typeT = request.POST.get('typeT')
        fichier = request.FILES.get('fichier')
        date_limite = request.POST.get('date_limite')
        
        travail = Travail(
            idT=f"T{timezone.now().strftime('%Y%m%d%H%M%S')}",
            titre=titre,
            description=description,
            typeT=typeT,
            fichier=fichier,
            date_limite=date_limite,
            cours=cours,
            enseignant=request.user.utilisateur
        )
        travail.save()
        return redirect('detail_cours', cours_id=cours.idc)
    
    return render(request, 'core/creer_travail.html', {
        'cours': cours,
        'type_choices': Travail.TYPE_CHOICES
    })


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

def supprimer_section(request, section_id):
    section = get_object_or_404(Section, idsec=section_id)
    cours_id = section.cours.idc
    
    # Vérifier que l'utilisateur est l'enseignant du cours
    if request.user.utilisateur == section.cours.utilisateur:
        section.delete()
        messages.success(request, "La section a été supprimée avec succès.")
    else:
        messages.error(request, "Vous n'avez pas la permission de supprimer cette section.")
    
    return redirect('detail_cours', cours_id=cours_id)

def modifier_travail(request, travail_id):
    travail = get_object_or_404(Travail, idT=travail_id)
    
    # Vérifier que l'utilisateur est l'enseignant du cours
    if request.user.utilisateur != travail.enseignant:
        messages.error(request, "Vous n'avez pas la permission de modifier ce travail.")
        return redirect('detail_cours', cours_id=travail.cours.idc)
    
    if request.method == 'POST':
        form = TravailForm(request.POST, request.FILES, instance=travail)
        if form.is_valid():
            form.save()
            messages.success(request, "Le travail a été modifié avec succès.")
            return redirect('detail_cours', cours_id=travail.cours.idc)
    else:
        form = TravailForm(instance=travail)
    
    return render(request, 'core/modifier_travail.html', {
        'form': form,
        'travail': travail,
        'cours': travail.cours
    })
def supprimer_travail(request, travail_id):
    travail = get_object_or_404(Travail, idT=travail_id)
    cours_id = travail.cours.idc
    
    # Vérifier que l'utilisateur est l'enseignant du cours
    if request.user.utilisateur == travail.enseignant:
        travail.delete()
        messages.success(request, "Le travail a été supprimé avec succès.")
    else:
        messages.error(request, "Vous n'avez pas la permission de supprimer ce travail.")
    
    return redirect('detail_cours', cours_id=cours_id)

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Cours

def supprimer_cours(request, cours_id):
    cours = get_object_or_404(Cours, idc=cours_id)
    
    # Vérifier que l'utilisateur est bien le propriétaire du cours
    if request.user.utilisateur != cours.utilisateur:
        messages.error(request, "Vous n'avez pas la permission de supprimer ce cours.")
        return redirect('mes_cours')
    
    titre_cours = cours.titre
    cours.delete()
    
    messages.success(request, f"Le cours '{titre_cours}' a été supprimé avec succès.")
    return redirect('mes_cours')






@login_required
def etudiant_dashboard(request):
    return render(request, 'core/etudiant_dashboard.html')
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .models import Utilisateur

@login_required
def profil_etudiant(request):
    try:
        utilisateur = Utilisateur.objects.get(user=request.user)
    except Utilisateur.DoesNotExist:
        messages.error(request, "Profil utilisateur non trouvé.")
        return redirect('etudiant_dashboard')

    if request.method == 'POST':
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        motdepasse = request.POST.get('motdepasse')
        confirm_motdepasse = request.POST.get('confirm_motdepasse')
        specialite = request.POST.get('specialite')
        niveau = request.POST.get('niveau')

        # Vérifier unicité de l'email
        if Utilisateur.objects.exclude(pk=utilisateur.pk).filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé par un autre compte.")
        else:
            # Vérification du mot de passe
            if motdepasse:
                if len(motdepasse) < 8:
                    messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
                elif motdepasse != confirm_motdepasse:
                    messages.error(request, "Les mots de passe ne correspondent pas.")
                else:
                    request.user.set_password(motdepasse)
                    update_session_auth_hash(request, request.user)
                    messages.success(request, "Mot de passe mis à jour avec succès.")

            # Mise à jour des champs
            utilisateur.nom = nom
            utilisateur.email = email
            utilisateur.specialite = specialite
            utilisateur.niveau = niveau
            
            # Sauvegarde
            utilisateur.save()
            request.user.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('profil_etudiant')

    context = {
        'utilisateur': utilisateur,
    }
    return render(request, 'core/profil_etudiant.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cours, Utilisateur

@login_required
def cours_disponibles(request):
    try:
        etudiant = Utilisateur.objects.get(user=request.user, type='etudiant')
    except Utilisateur.DoesNotExist:
        messages.error(request, "Accès réservé aux étudiants.")
        return redirect('accueil')

    # Tous les cours actifs
    tous_les_cours = Cours.objects.filter(statut='actif').select_related('utilisateur')
    
    # Cours où l'étudiant n'est pas inscrit
    cours_non_inscrits = tous_les_cours.exclude(etudiants_inscrits=etudiant)
    
    context = {
        'cours_list': cours_non_inscrits,
        'specialites': dict(Utilisateur.SPECIALITE_CHOICES)
    }
    return render(request, 'core/cours_disponibles.html', context)

@login_required
def acceder_cours(request, cours_id):
    if request.method == 'POST':
        cle_admin = request.POST.get('cle_admin', '')
        
        if cle_admin != "admin":
            messages.error(request, "Clé d'accès incorrecte")
            return redirect('cours_disponibles')
        
        try:
            etudiant = Utilisateur.objects.get(user=request.user, type='etudiant')
            cours = get_object_or_404(Cours, idc=cours_id)
            
            # Ajouter l'étudiant au cours (simule l'inscription)
            etudiant.cours_inscrits.add(cours)
            
            # Rediriger vers la page du cours
            return redirect('etudiant_dashboard', cours_id=cours.idc)
            
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    return redirect('cours_disponibles')



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Cours, Section, Travail, Soumission, Utilisateur, SectionVue
from .forms import SoumissionForm
@login_required
def detail_cours_etudiant(request, cours_id):
    try:
        etudiant = Utilisateur.objects.get(user=request.user, type='etudiant')
        cours = get_object_or_404(Cours, idc=cours_id)
        
        if not etudiant.cours_inscrits.filter(idc=cours_id).exists():
            messages.error(request, "Accès refusé : Vous n'êtes pas inscrit à ce cours")
            return redirect('mes_cours')
        
        sections = cours.sections.filter(cache=False).order_by('idsec')
        travaux = cours.travaux.filter(statut='actif').order_by('-date_creation')
        
        # Récupérer les soumissions existantes
        soumissions = Soumission.objects.filter(
            etudiant=etudiant,
            travail__in=travaux
        ).select_related('travail')
        
        # Créer un dictionnaire pour un accès facile
        soumissions_dict = {s.travail.idT: s for s in soumissions}
        
        context = {
            'cours': cours,
            'sections': sections,
            'travaux': travaux,
            'soumissions': soumissions_dict,
            'now': timezone.now()
        }
        return render(request, 'core/detail_cours_etudiant.html', context)
        
    except Utilisateur.DoesNotExist:
        messages.error(request, "Accès réservé aux étudiants")
        return redirect('accueil')
import os
from django.db import transaction
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Soumission, Travail, Utilisateur
from .forms import SoumissionForm
@login_required
def soumettre_travail(request, travail_id):
    """
    Vue pour soumettre un travail étudiant avec validation et gestion des fichiers
    """
    try:
        # Récupération de l'étudiant et vérification des permissions
        etudiant = Utilisateur.objects.get(user=request.user, type='etudiant')
        travail = get_object_or_404(Travail, idT=travail_id, statut='actif')
        
        # Vérification que l'étudiant est inscrit au cours
        if not etudiant.cours_inscrits.filter(idc=travail.cours.idc).exists():
            messages.error(request, "Vous n'êtes pas autorisé à soumettre ce travail")
            return redirect('mes_cours')
            
        # Vérification de la date limite
        if travail.date_limite < timezone.now():
            messages.error(request, "La date limite de soumission est dépassée")
            return redirect('detail_cours_etudiant', cours_id=travail.cours.idc)
        
        # Récupération de la soumission existante si elle existe
        soumission_existante = Soumission.objects.filter(
            travail=travail,
            etudiant=etudiant
        ).first()

        if request.method == 'POST':
            form = SoumissionForm(request.POST, request.FILES)
            
            if form.is_valid():
                # Validation de la case à cocher
                if not form.cleaned_data.get('valider'):
                    messages.error(request, "Vous devez confirmer la validation de votre travail")
                else:
                    try:
                        # Création ou mise à jour de la soumission
                        with transaction.atomic():
                            if soumission_existante:
                                soumission = soumission_existante
                                ancien_fichier = soumission.fichier.path if soumission.fichier else None
                            else:
                                soumission = Soumission(travail=travail, etudiant=etudiant)
                            
                            soumission.fichier = form.cleaned_data['fichier']
                            soumission.valide = True
                            soumission.save()
                            
                            # Suppression de l'ancien fichier après sauvegarde réussie
                            if soumission_existante and ancien_fichier:
                                try:
                                    os.remove(ancien_fichier)
                                except OSError:
                                    pass
                            
                            # Message de succès
                            messages.success(
                                request,
                                mark_safe(
                                    f"<i class='fas fa-check-circle me-2'></i>"
                                    f"<strong>Soumission réussie !</strong><br>"
                                    f"Votre travail <strong>{travail.titre}</strong> a été envoyé.<br>"
                                    f"<small class='text-muted'>Soumis le {timezone.now().strftime('%d/%m/%Y à %H:%M')}</small>"
                                )
                            )
                            return redirect('detail_cours_etudiant', cours_id=travail.cours.idc)
                            
                    except Exception as e:
                        messages.error(request, f"Une erreur est survenue lors de l'enregistrement: {str(e)}")
            else:
                # Gestion des erreurs de formulaire
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")
        else:
            form = SoumissionForm()
        
        context = {
            'travail': travail,
            'form': form,
            'soumission_existante': soumission_existante,
            'now': timezone.now()
        }
        return render(request, 'core/soumettre_travail.html', context)
        
    except Utilisateur.DoesNotExist:
        messages.error(request, "Accès réservé aux étudiants")
        return redirect('accueil')
    except Exception as e:
        messages.error(request, f"Une erreur inattendue est survenue: {str(e)}")
        return redirect('mes_cours')
    
@login_required
def mes_coursEtudiant(request):
    try:
        etudiant = Utilisateur.objects.get(user=request.user, type='etudiant')
        cours_inscrits = etudiant.cours_inscrits.all().select_related('utilisateur')
        
        for cours in cours_inscrits:
            cours.progression_etudiant = cours.progression(etudiant)

        context = {
            'cours_inscrits': cours_inscrits,
            'now': timezone.now()
        }
        return render(request, 'core/mes_coursEtudiant.html', context)

    except Utilisateur.DoesNotExist:
        messages.error(request, "Accès réservé aux étudiants.")
        return redirect('accueil')
