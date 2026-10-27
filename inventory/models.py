from companies.models import Company
from django.contrib.auth.models import User
from django.db import models

class Category(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='categories'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        unique_together = ('company', 'name')

    def __str__(self):
        return f'{self.name} ({self.company.name})'


class Product(models.Model):
    UNIT_CHOICES = [
        ('UN', 'Unidade'),
        ('KG', 'Quilograma'),
        ('CX', 'Caixa'),
        ('L', 'Litro'),
        ('M', 'Metro'),
        ('PCT', 'Pacote'),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='products'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
    )

    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, help_text='Código SKU / Barras')
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='UN')

    quantity = models.IntegerField(default=0)
    min_stock = models.IntegerField(default=5)

    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        unique_together = ('company', 'sku')

    def __str__(self):
        return f'[{self.sku}] {self.name}'

    @property
    def total_value(self):
        """Calcula o valor total em stock para este produto."""
        return self.quantity * self.cost_price

    @property
    def needs_reorder(self):
        """Indica se a quantidade está igual ou abaixo do limite mínimo de reposição."""
        return self.quantity <= self.min_stock

    from django.contrib.auth.models import User

class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('IN', 'Entrada (Aumento)'),
        ('OUT', 'Saída (Baixa)'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    reason = models.CharField(max_length=255, blank=True, null=True, help_text="Ex: Compra de fornecedor, Venda, Danificado, etc.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimentação de Stock'
        verbose_name_plural = 'Movimentações de Stock'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity})"