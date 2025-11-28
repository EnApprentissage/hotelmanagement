from django import forms
from django.utils import timezone
from .models import Reservation
from clients.models import Client
from chambres.models import Chambre


class ReservationCreateForm(forms.ModelForm):
    # Champs pour créer un nouveau client si nécessaire
    nouveau_client = forms.BooleanField(
        required=False, 
        label="Créer un nouveau client",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Champs client
    client_nom = forms.CharField(
        max_length=100, 
        required=False, 
        label="Nom",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    client_prenom = forms.CharField(
        max_length=100, 
        required=False, 
        label="Prénom",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    client_email = forms.EmailField(
        required=False, 
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    client_telephone = forms.CharField(
        max_length=20, 
        required=False, 
        label="Téléphone",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    client_date_naissance = forms.DateField(
        required=False, 
        label="Date de naissance",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    client_adresse = forms.CharField(
        required=False,
        label="Adresse",
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'})
    )
    client_piece_identite = forms.CharField(
        max_length=50, 
        required=False,
        label="Pièce d'identité",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Reservation
        fields = [
            'client', 'chambre', 'date_arrivee', 'date_depart',
            'nombre_adultes', 'nombre_enfants', 'type_reservation',
            'prix_par_nuit', 'acompte', 'demandes_speciales', 'notes'
        ]
        widgets = {
            'date_arrivee': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_depart': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'demandes_speciales': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'chambre': forms.Select(attrs={'class': 'form-control'}),
            'nombre_adultes': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'nombre_enfants': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'type_reservation': forms.Select(attrs={'class': 'form-control'}),
            'prix_par_nuit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'acompte': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Rendre le champ client optionnel
        self.fields['client'].required = False
        
        # Filtrer uniquement les chambres disponibles pour création
        # Pour modification, afficher toutes les chambres
        if not self.instance.pk:
            self.fields['chambre'].queryset = Chambre.objects.filter(
                statut__in=['disponible', 'propre']
            )
        
        # Labels
        self.fields['client'].label = "Client existant"
        self.fields['chambre'].label = "Chambre"
        self.fields['date_arrivee'].label = "Date d'arrivée"
        self.fields['date_depart'].label = "Date de départ"
        self.fields['nombre_adultes'].label = "Nombre d'adultes"
        self.fields['nombre_enfants'].label = "Nombre d'enfants"
        self.fields['type_reservation'].label = "Type de réservation"
        self.fields['prix_par_nuit'].label = "Prix par nuit (FBU)"
        self.fields['acompte'].label = "Acompte (FBU)"
        self.fields['demandes_speciales'].label = "Demandes spéciales"
        self.fields['notes'].label = "Notes internes"
    
    def clean(self):
        cleaned_data = super().clean()
        nouveau_client = cleaned_data.get('nouveau_client')
        client = cleaned_data.get('client')
        
        # Validation : soit client existant, soit nouveau client
        if not nouveau_client and not client:
            raise forms.ValidationError(
                "Veuillez sélectionner un client existant ou cocher 'Créer un nouveau client'."
            )
        
        # Si nouveau client, vérifier les champs obligatoires
        if nouveau_client:
            required_fields = {
                'client_nom': 'Le nom du client est obligatoire',
                'client_prenom': 'Le prénom du client est obligatoire',
                'client_telephone': 'Le téléphone du client est obligatoire',
                'client_email': 'L\'email du client est obligatoire'
            }
            
            for field, error_msg in required_fields.items():
                if not cleaned_data.get(field):
                    self.add_error(field, error_msg)
        
        # Validation des dates
        date_arrivee = cleaned_data.get('date_arrivee')
        date_depart = cleaned_data.get('date_depart')
        
        if date_arrivee and date_depart:
            if date_depart <= date_arrivee:
                raise forms.ValidationError(
                    "La date de départ doit être après la date d'arrivée."
                )
            
            # Pour nouvelle réservation, vérifier que la date n'est pas dans le passé
            if not self.instance.pk and date_arrivee < timezone.now().date():
                raise forms.ValidationError(
                    "La date d'arrivée ne peut pas être dans le passé."
                )
        
        # Validation de la disponibilité de la chambre
        chambre = cleaned_data.get('chambre')
        if chambre and date_arrivee and date_depart:
            # Vérifier si la chambre est disponible pour ces dates
            reservations_conflits = Reservation.objects.filter(
                chambre=chambre,
                statut__in=['confirmee', 'en_cours', 'en_attente']
            ).filter(
                date_arrivee__lt=date_depart,
                date_depart__gt=date_arrivee
            )
            
            # Exclure la réservation actuelle si c'est une modification
            if self.instance.pk:
                reservations_conflits = reservations_conflits.exclude(pk=self.instance.pk)
            
            if reservations_conflits.exists():
                raise forms.ValidationError(
                    f"La chambre {chambre.numero} n'est pas disponible pour ces dates. "
                    f"Il existe déjà {reservations_conflits.count()} réservation(s) en conflit."
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        reservation = super().save(commit=False)
        
        # Créer un nouveau client si nécessaire
        if self.cleaned_data.get('nouveau_client'):
            client = Client.objects.create(
                nom=self.cleaned_data['client_nom'],
                prenom=self.cleaned_data['client_prenom'],
                email=self.cleaned_data['client_email'],
                telephone=self.cleaned_data['client_telephone'],
                date_naissance=self.cleaned_data.get('client_date_naissance'),
                adresse=self.cleaned_data.get('client_adresse', ''),
                piece_identite=self.cleaned_data.get('client_piece_identite', ''),
            )
            reservation.client = client
        
        # Calculer le total si pas déjà défini
        if not reservation.total or reservation.total == 0:
            if reservation.date_arrivee and reservation.date_depart and reservation.prix_par_nuit:
                nombre_nuits = (reservation.date_depart - reservation.date_arrivee).days
                reservation.total = reservation.prix_par_nuit * nombre_nuits
        
        # Statut par défaut
        if not reservation.statut:
            reservation.statut = 'en_attente'
        
        if commit:
            reservation.save()
        
        return reservation