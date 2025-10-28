from django.db import models

class GlobalVariables(models.Model):
    """
    Modèle qui contient toutes les variables globales de l'application.
    """

    group = models.CharField(max_length=50, verbose_name="Groupe")
    cle = models.CharField(max_length=50, verbose_name="Clé")
    valeur = models.TextField(max_length=1024, verbose_name="Valeur")
    description = models.TextField(max_length=1024, verbose_name="Description")

    class Meta:
        # Assure que la combinaison (group, cle) est unique
        unique_together = ('group', 'cle')
        indexes = [
            models.Index(fields=["group", "cle"]),
        ]
        ordering = ("group", "cle")
        verbose_name = "Variable globale"
        verbose_name_plural = "Variables globales"

    def __str__(self):
        return f"{{ '{self.cle}' : '{self.valeur}' }}"
