from .models import Product


def low_stock_context(request):
    if not request.user.is_authenticated:
        return {'low_stock_count': 0}

    user_profile = getattr(request.user, 'profile', None)
    company = user_profile.company if user_profile else None

    if company:
        products = Product.objects.filter(company=company)
    else:
        products = Product.objects.all()

    # Conta produtos que precisam de reposição
    count = sum(1 for p in products if p.needs_reorder)

    return {'low_stock_count': count}