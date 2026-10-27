from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path(
        'product/<int:product_id>/movement/',
        views.record_movement,
        name='record_movement',
    ),
    path('movements/', views.movement_history, name='movement_history'),
    path('product/add/', views.product_create, name='product_create'),
    path(
        'product/<int:product_id>/edit/',
        views.product_edit,
        name='product_edit',
    ),
    path(
        'export/products/',
        views.export_products_csv,
        name='export_products_csv',
    ),
    path(
        'export/movements/',
        views.export_movements_csv,
        name='export_movements_csv',
    ),
    path('categories/', views.category_list, name='category_list'),
    path('alerts/', views.low_stock_alerts, name='low_stock_alerts'),
]