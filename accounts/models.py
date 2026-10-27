from django.contrib.auth.models import User
from django.db import models
from companies.models import Company


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrador da Empresa'),
        ('OPERATOR', 'Operador de Armazém'),
        ('VIEWER', 'Apenas Visualização'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile'
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True,
        help_text='Empresa à qual este utilizador pertence',
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='OPERATOR')

    def __str__(self):
        company_name = self.company.name if self.company else 'Sem Empresa (Superadmin)'
        return f'{self.user.username} - {company_name}'