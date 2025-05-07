from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('register/', views.register, name='register'),
    path('enseignant_dashboard/', views.enseignant_dashboard, name='enseignant_dashboard'),
    path('login/', views.login_view, name='login'),
    path('profil_enseignant/', views.profil_enseignant, name='profil_enseignant'),
    path('mes_cours/', views.mes_cours, name='mes_cours'),
    path('creer_cours/', views.creer_cours, name='creer_cours'),
path('cours/<str:cours_id>/', views.detail_cours, name='detail_cours'),
    path('cours/<str:cours_id>/creer-section/', views.creer_section, name='creer_section'),
    path('cours/<str:cours_id>/modifier/', views.modifier_cours, name='modifier_cours'),
    path('sections/<str:section_id>/modifier/', views.modifier_section, name='modifier_section'),
   # Dans urls.py
path('selectionner-cours-travail/', views.selectionner_cours_pour_travail, name='selectionner_cours_pour_travail'),
path('creer-travail/<str:cours_id>/', views.creer_travail, name='creer_travail'),
  path('sections/<str:section_id>/supprimer/', views.supprimer_section, name='supprimer_section'),
  path('travaux/<str:travail_id>/supprimer/', views.supprimer_travail, name='supprimer_travail'),
path('travail/modifier/<str:travail_id>/', views.modifier_travail, name='modifier_travail'),
path('cours/<str:cours_id>/supprimer/', views.supprimer_cours, name='supprimer_cours'),

    # URLs Étudiant

    path('etudiant_dashboard/', views.etudiant_dashboard, name='etudiant_dashboard'),
 path('etudiant/profil/', views.profil_etudiant, name='profil_etudiant'),
path('etudiant/cours-disponibles/', views.cours_disponibles, name='cours_disponibles')
,    path('etudiant/acceder-cours/<str:cours_id>/', views.acceder_cours, name='acceder_cours'),
   
]