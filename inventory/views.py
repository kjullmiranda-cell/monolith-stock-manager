import csv
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import admin_required
from .models import Category, Product, StockMovement


@login_required
def dashboard(request):
    user_profile = getattr(request.user, 'profile', None)
    company = user_profile.company if user_profile else None

    # Base de produtos por empresa
    products = Product.objects.filter(company=company) if company else Product.objects.all()

    # Captura o termo de pesquisa (se existir)
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(name__icontains=query) | products.filter(sku__icontains=query)

    total_products = products.count()
    low_stock_count = sum(1 for p in products if p.needs_reorder)
    total_inventory_value = sum(p.total_value for p in products)

    context = {
        'company': company,
        'products': products,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'total_inventory_value': total_inventory_value,
        'query': query, # Mantém o texto pesquisado no campo
    }
    return render(request, 'inventory/dashboard.html', context)


@login_required
def record_movement(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    user_profile = getattr(request.user, 'profile', None)
    if (
        user_profile
        and user_profile.company
        and product.company != user_profile.company
    ):
        messages.error(
            request, 'Não tem permissão para alterar este produto.'
        )
        return redirect('dashboard')

    if request.method == 'POST':
        movement_type = request.POST.get('movement_type')
        try:
            quantity = int(request.POST.get('quantity', 0))
        except ValueError:
            quantity = 0

        reason = request.POST.get('reason', '')

        if quantity <= 0:
            messages.error(
                request, 'A quantidade deve ser maior que zero.'
            )
            return redirect('dashboard')

        if movement_type == 'OUT' and product.quantity < quantity:
            messages.error(
                request,
                f'Stock insuficiente. Apenas {product.quantity} unidades disponíveis.',
            )
            return redirect('dashboard')

        if movement_type == 'IN':
            product.quantity += quantity
        elif movement_type == 'OUT':
            product.quantity -= quantity
        product.save()

        StockMovement.objects.create(
            product=product,
            user=request.user,
            movement_type=movement_type,
            quantity=quantity,
            reason=reason,
        )

        messages.success(
            request,
            f'Movimentação registada com sucesso para {product.name}!',
        )
        return redirect('dashboard')

    return redirect('dashboard')


@login_required
def movement_history(request):
    user_profile = getattr(request.user, 'profile', None)
    company = user_profile.company if user_profile else None

    if company:
        movements = StockMovement.objects.filter(
            product__company=company
        ).select_related('product', 'user')
    else:
        movements = StockMovement.objects.all().select_related('product', 'user')

    context = {
        'company': company,
        'movements': movements,
    }
    return render(request, 'inventory/movement_history.html', context)


@login_required
@admin_required
def product_create(request):
    user_profile = getattr(request.user, 'profile', None)
    company = user_profile.company if user_profile else None

    if request.method == 'POST':
        name = request.POST.get('name')
        sku = request.POST.get('sku')
        category_id = request.POST.get('category')
        unit = request.POST.get('unit', 'UNIT')
        try:
            quantity = int(request.POST.get('quantity', 0))
        except ValueError:
            quantity = 0

        try:
            min_stock = int(request.POST.get('min_stock', 5))
        except ValueError:
            min_stock = 5

        cost_price = request.POST.get('cost_price', '0.00')
        selling_price = request.POST.get('selling_price', '0.00')

        category = (
            Category.objects.filter(id=category_id, company=company).first()
            if category_id
            else None
        )

        Product.objects.create(
            company=company,
            name=name,
            sku=sku,
            category=category,
            unit=unit,
            quantity=quantity,
            min_stock=min_stock,
            cost_price=cost_price,
            selling_price=selling_price,
        )

        messages.success(request, f'Produto "{name}" criado com sucesso!')
        return redirect('dashboard')

    categories = (
        Category.objects.filter(company=company)
        if company
        else Category.objects.all()
    )
    return render(
        request, 'inventory/product_form.html', {'categories': categories}
    )


@login_required
@admin_required
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user_profile = getattr(request.user, 'profile', None)

    if (
        user_profile
        and user_profile.company
        and product.company != user_profile.company
    ):
        messages.error(request, 'Não tem permissão para editar este produto.')
        return redirect('dashboard')

    if request.method == 'POST':
        product.name = request.POST.get('name', product.name)
        product.sku = request.POST.get('sku', product.sku)
        category_id = request.POST.get('category')
        product.unit = request.POST.get('unit', product.unit)

        try:
            product.min_stock = int(
                request.POST.get('min_stock', product.min_stock)
            )
        except ValueError:
            pass

        product.cost_price = request.POST.get('cost_price', product.cost_price)
        product.selling_price = request.POST.get(
            'selling_price', product.selling_price
        )

        if category_id:
            product.category = Category.objects.filter(
                id=category_id
            ).first()
        else:
            product.category = None

        product.save()
        messages.success(
            request, f'Produto "{product.name}" atualizado com sucesso!'
        )
        return redirect('dashboard')

    categories = (
        Category.objects.filter(company=user_profile.company)
        if user_profile and user_profile.company
        else Category.objects.all()
    )
    return render(
        request,
        'inventory/product_form.html',
        {'product': product, 'categories': categories},
    )

@login_required
def export_products_csv(request):
    user_profile = getattr(request.user, 'profile', None)
    company = user_profile.company if user_profile else None

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="inventario_produtos.csv"'

    writer = csv.writer(response)
    # Cabeçalho do ficheiro CSV
    writer.writerow(['SKU', 'Produto', 'Categoria', 'Quantidade', 'Unidade', 'Custo Un. (MT)', 'Preço Venda (MT)', 'Valor Total (MT)', 'Estado'])

    products = Product.objects.filter(company=company) if company else Product.objects.all()

    for product in products:
        status = 'Repor Stock' if product.needs_reorder else 'Normal'
        category_name = product.category.name if product.category else 'Sem Categoria'
        writer.writerow([
            product.sku,
            product.name,
            category_name,
            product.quantity,
            product.get_unit_display(),
            product.cost_price,
            product.selling_price,
            product.total_value,
            status
        ])

    return response


@login_required
def export_movements_csv(request):
    user_profile = getattr(request.user, 'profile', None)
    company = user_profile.company if user_profile else None

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="historico_movimentacoes.csv"'

    writer = csv.writer(response)
    # Cabeçalho do ficheiro CSV
    writer.writerow(['Data e Hora', 'SKU', 'Produto', 'Tipo Movimento', 'Quantidade', 'Operador', 'Motivo'])

    movements = StockMovement.objects.filter(product__company=company).select_related('product', 'user') if company else StockMovement.objects.all().select_related('product', 'user')

    for movement in movements:
        movement_type = 'Entrada' if movement.movement_type == 'IN' else 'Saída'
        username = movement.user.username if movement.user else 'Sistema'
        writer.writerow([
            movement.created_at.strftime('%d/%m/%Y %H:%M'),
            movement.product.sku,
            movement.product.name,
            movement_type,
            movement.quantity,
            username,
            movement.reason or '-'
        ])

    return response

@login_required
@admin_required
def category_list(request):
    user_profile = getattr(request.user, 'profile', None)
    company = user_profile.company if user_profile else None

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            Category.objects.create(name=name, company=company)
            messages.success(request, f'Categoria "{name}" criada com sucesso!')
            return redirect('category_list')

    categories = (
        Category.objects.filter(company=company)
        if company
        else Category.objects.all()
    )
    return render(
        request, 'inventory/category_list.html', {'categories': categories}
    )

@login_required
def low_stock_alerts(request):
    user_profile = getattr(request.user, 'profile', None)
    company = user_profile.company if user_profile else None

    # Filtra apenas os produtos que precisam de reposição
    products = Product.objects.filter(company=company) if company else Product.objects.all()
    low_stock_products = [p for p in products if p.needs_reorder]

    context = {
        'company': company,
        'low_stock_products': low_stock_products,
        'count': len(low_stock_products),
    }
    return render(request, 'inventory/low_stock_alerts.html', context)