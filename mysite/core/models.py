from django.db import models

from django.contrib.auth.models import User
from django.utils import timezone

class Utilisateur(models.Model):
    TYPE_CHOICES = [
        ('etudiant', 'Étudiant'),
        ('enseignant', 'Enseignant'),  # Correction de l'orthographe
        ('admin', 'Administrateur'),
    ]
    
    SPECIALITE_CHOICES = [
        ('info', 'Informatique'),
        ('med', 'Médecine'),
        ('ing', 'Ingénierie'),
    ]
    cours_inscrits = models.ManyToManyField('Cours', related_name='etudiants_inscrits', blank=True)
    idu = models.CharField(max_length=100, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    motdepasse = models.CharField(max_length=100)
    dateinscrit = models.DateField(auto_now_add=True)
    specialisation = models.TextField(blank=True, null=True)
    cv = models.FileField(upload_to='cvs/', blank=True, null=True)
    niveau = models.CharField(max_length=100, blank=True, null=True)
    specialite = models.CharField(max_length=50, choices=SPECIALITE_CHOICES, null=True, blank=True)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    
    def __str__(self):
        return f"{self.nom} - {self.email}"

class Cours(models.Model):
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('en_attente', 'En attente'),
    ]
    
    idc = models.CharField(max_length=100, primary_key=True)
    titre = models.CharField(max_length=200)
    description = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='actif')
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='cours')
    
    def __str__(self):
        return f"{self.titre} - {self.statut}"

class Section(models.Model):
    idsec = models.CharField(max_length=100, primary_key=True)
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    fichier = models.FileField(upload_to='section_fichiers/', blank=True, null=True)  # Nouveau champ
    cache = models.BooleanField(default=False)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='sections')
    
    def __str__(self):
        return self.titre
    
    def delete(self, *args, **kwargs):
        if self.fichier:
            self.fichier.delete()
        super().delete(*args, **kwargs)
        

class Travail(models.Model):
    TYPE_CHOICES = [
        ('tp', 'Travail Pratique'),
        ('td', 'Travail Dirigé'),
        ('projet', 'Projet'),
        ('devoir', 'Devoir'),
    ]
    
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('archive', 'Archivé'),
    ]
    
    idT = models.CharField(max_length=100, primary_key=True)
    titre = models.CharField(max_length=200)
    description = models.TextField()
    typeT = models.CharField(max_length=50, choices=TYPE_CHOICES)
    fichier = models.FileField(upload_to='travaux/', null=True, blank=True)
    date_creation = models.DateTimeField(default=timezone.now)
    date_limite = models.DateTimeField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='actif')
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='travaux')
    enseignant = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.get_typeT_display()} - {self.titre}"

class Soumission(models.Model):
    ETAT_CHOICES = [
        ('soumis', 'Soumis'),
        ('en_retard', 'En retard'),
        ('corrige', 'Corrigé'),
        ('note', 'Noté'),
    ]
    
    ids = models.CharField(max_length=100, primary_key=True)
    fichier = models.FileField(upload_to='soumissions/')
    date_soumission = models.DateTimeField(default=timezone.now)
    date_modification = models.DateTimeField(auto_now=True)
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='soumis')
    note = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    commentaire = models.TextField(blank=True)
    travail = models.ForeignKey(Travail, on_delete=models.CASCADE, related_name='soumissions')
    etudiant = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='soumissions')

    def __str__(self):
        return f"Soumission {self.ids} - {self.etat}"

    def save(self, *args, **kwargs):
        # Vérifier si la date limite est dépassée
        if self.date_soumission > self.travail.date_limite:
            self.etat = 'en_retard'
        super().save(*args, **kwargs)



class Paiement(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('paye', 'Payé'),
        ('annule', 'Annulé'),
    ]
    
    METHODE_CHOICES = [
        ('cb', 'Carte Bancaire'),
        ('esp', 'Espèces'),
        ('virm', 'Virement'),
    ]
    
    idp = models.CharField(max_length=100, primary_key=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    methode = models.CharField(max_length=50, choices=METHODE_CHOICES)
    statutP = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='paiements')
    date_paiement = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Paiement {self.idp} - {self.montant}"
    
