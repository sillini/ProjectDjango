from django.contrib import admin
from .models import Utilisateur, Cours, Section, Travail, Soumission, Paiement
admin.site.register(Utilisateur)
admin.site.register(Cours)
admin.site.register(Section)
admin.site.register(Travail)
admin.site.register(Soumission)
admin.site.register(Paiement)
# Register your models here