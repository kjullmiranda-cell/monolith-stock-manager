
from django.db import models
from django.utils.text import slugify


class Company(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Nome da empresa"
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True
    )
    nuit = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="NUIT"
    )
    email = models.EmailField(
        blank=True,
        verbose_name="E-mail"
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Telefone"
    )
    address = models.TextField(
        blank=True,
        verbose_name="Endereço"
    )
    logo = models.ImageField(
        upload_to="company_logos/",
        blank=True,
        null=True,
        verbose_name="Logótipo"
    )
    primary_color = models.CharField(
        max_length=7,
        default="#253F69",
        verbose_name="Cor principal"
    )
    secondary_color = models.CharField(
        max_length=7,
        default="#FFFFFF",
        verbose_name="Cor secundária"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de criação"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Empresa activa"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ["name"]
