# utils/reference_generator.py
import re
from datetime import datetime
from django.db.models import Max


class ReferenceGenerator:
    """
    Générateur de numéros de référence pour Django
    Format: PREFIX-YYYYMM-XXXX
    """
    
    @staticmethod
    def generate_reference(model_class, field_name, prefix, nombre=4):
        """
        Génère un numéro de référence basé sur le dernier enregistrement
        
        Args:
            model_class: La classe du modèle Django (ex: Contribuable)
            field_name: Le nom du champ contenant le numéro (ex: 'matricule')
            prefix: Le préfixe (ex: 'CTB', 'PAR')
            nombre: Nombre de chiffres pour la séquence (par défaut: 4)
        
        Returns:
            Nouveau numéro de référence (ex: 'CTB-202511-0001')
        
        Raises:
            ValueError: Si le nombre est inférieur à 1
        """
        if nombre < 1:
            raise ValueError("Le nombre de chiffres doit être au moins 1")
        
        # Obtenir l'année et le mois actuel
        now = datetime.now()
        year_month = now.strftime('%Y%m')
        
        # Pattern pour extraire les références du mois en cours
        pattern = f"{prefix}-{year_month}-"
        
        # Récupérer le dernier objet avec ce préfixe et ce mois
        last_object = model_class.objects.filter(
            **{f"{field_name}__startswith": pattern}
        ).order_by(f"-{field_name}").first()
        
        new_number = 1  # Valeur par défaut
        
        if last_object:
            # Extraire le numéro de séquence du dernier objet
            last_reference = getattr(last_object, field_name)
            
            # Extraire l'année et mois de la dernière référence
            extr_year_month = ReferenceGenerator.extract_year_month(last_reference)
            
            # Vérifier si c'est le même mois
            if extr_year_month == year_month:
                # Extraire le numéro à la fin avec le nombre de chiffres spécifié
                match = re.search(rf'-(\d{{{nombre}}})$', last_reference)
                
                if match:
                    last_number = int(match.group(1))
                    new_number = last_number + 1
                else:
                    # Si le format ne correspond pas, commencer à 1
                    new_number = 1
            # Si le mois est différent, new_number reste à 1
        
        # Formater le nouveau numéro de référence
        reference = f"{prefix}-{year_month}-{new_number:0{nombre}d}"
        
        return reference
    
    @staticmethod
    def extract_year_month(reference):
        """
        Extrait l'année et le mois d'une référence
        
        Args:
            reference: String au format PREFIX-YYYYMM-XXXX (ex: 'CTB-202511-0001')
        
        Returns:
            str: Année et mois au format 'YYYYMM' (ex: '202511') ou None
        """
        if not reference:
            return None
        
        # Méthode avec regex
        match = re.search(r'-(\d{4})(\d{2})-', reference)
        if match:
            year = match.group(1)
            month = match.group(2)
            return f"{year}{month}"
        
        return None
    
    @staticmethod
    def extract_all_info(reference):
        """
        Extrait toutes les informations d'une référence
        
        Args:
            reference: String au format PREFIX-YYYYMM-XXXX
        
        Returns:
            dict: {'prefix': str, 'year': int, 'month': int, 'year_month': str, 'sequence': int}
                  ou None si le format est invalide
        """
        if not reference:
            return None
        
        parts = reference.split('-')
        if len(parts) != 3:
            return None
        
        try:
            prefix = parts[0]
            year_month = parts[1]
            sequence = parts[2]
            
            # Valider que year_month a 6 chiffres
            if len(year_month) != 6 or not year_month.isdigit():
                return None
            
            year = int(year_month[:4])
            month = int(year_month[4:6])
            
            # Valider que sequence est numérique
            if not sequence.isdigit():
                return None
            
            return {
                'prefix': prefix,
                'year': year,
                'month': month,
                'year_month': year_month,
                'sequence': int(sequence),
                'full_reference': reference
            }
        except (ValueError, IndexError):
            return None
    
    @staticmethod
    def validate_reference(reference, prefix=None):
        """
        Valide le format d'une référence
        
        Args:
            reference: String à valider
            prefix: Préfixe attendu (optionnel)
        
        Returns:
            bool: True si valide, False sinon
        """
        info = ReferenceGenerator.extract_all_info(reference)
        
        if not info:
            return False
        
        # Vérifier le préfixe si spécifié
        if prefix and info['prefix'] != prefix:
            return False
        
        # Vérifier que le mois est valide (1-12)
        if not (1 <= info['month'] <= 12):
            return False
        
        return True
    
    @staticmethod
    def get_month_name(reference, lang='fr'):
        """
        Retourne le nom du mois en français ou anglais
        
        Args:
            reference: String au format PREFIX-YYYYMM-XXXX
            lang: 'fr' ou 'en'
        
        Returns:
            str: Nom du mois ou None
        """
        months_fr = [
            'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
            'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
        ]
        
        months_en = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        
        info = ReferenceGenerator.extract_all_info(reference)
        if not info:
            return None
        
        month = info['month']
        if not (1 <= month <= 12):
            return None
        
        months = months_fr if lang == 'fr' else months_en
        return months[month - 1]
