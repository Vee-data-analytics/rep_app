from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from users.views import(
    UserCreateView,
    UserListView,
    UserUpdateView,
    UserDeleteView, 
    
    )

from .modal_views import (
    create_shop, create_product, create_store, create_main_store, create_shop_store,
)

app_name = 'reptrack_trace'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Representative URLs
    path('', views.main_report_window, name='home'),
    path('settings/', views.settings_grid, name='settings'),
    path('reports/new/', views.ReportCreateView.as_view(), name='report-create'),
    path('report-details/reports/<uuid:pk>/', views.ReportDetailView.as_view(), name='report-detail'),
    path('reports/', views.FinishedReportsView.as_view(), name='report-list'),
    path('reports/unfinished/', views.UnfinishedReportsView.as_view(), name='unfinished_reports'),
    path('shops/create/', views.ShopCreateView.as_view(), name='shop-create'),
    path('stores/create/',  views.StoreCreateView.as_view(), name='store-create'),
    path('products/create/', views.ProductCreateView.as_view(), name='product-create'),
    
    path('create-shop/', create_shop, name='create_shop'),
    path('create-product/', create_product, name='create_product'),
    path('create-store/', create_store, name='create_store'),
    path('create-main-store/', create_main_store, name='create_main_store'),
    path('create-shop-store/', create_shop_store, name='create_shop_store'),

    
    
    path('main-stores/create/', views.MainStoreCreateView.as_view(), name='main-store-create'),
    path('reports/<uuid:pk>/', views.ReportUpdateView.as_view(), name='report-update'),
    path('reports/<uuid:pk>/pdf/', views.generate_pdf_report, name='download_report'),

    # Admin URLs
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    path('admin/shops/', views.shop_management, name='shop-management'),
    path('admin/stores/', views.store_management, name='store-management'),
    path('admin/management/', views.AdminManagementView.as_view(), name='admin-management'),
    path('admin/shop-list/', views.ShopAdminListView.as_view(), name='admin-shop-list'),
    path('admin/analytics/', views.AnalyticsView.as_view(), name='analytics'),
    
    path('admin/reports/shops/', views.ShopReportsView.as_view(), name='shop-reports'),
    path('admin/reports/shop-stores/', views.ShopStoreReportsView.as_view(), name='shop-store-reports'),
    path('admin/reports/main-stores/', views.MainStoreReportsView.as_view(), name='main-store-reports'),
    path('admin/reports/representatives/', views.RepresentativeReportsView.as_view(), name='rep-reports'),
    path('admin/shops/create/', views.AdminShopCreateView.as_view(), name='admin-shop-create'),
    path('admin/shops/<int:pk>/update/', views.AdminShopUpdateView.as_view(), name='admin-shop-update'),
    path('admin/shops/<int:pk>/delete/', views.AdminShopDeleteView.as_view(), name='admin-shop-delete'),
    
    path('admin/storage-list',views.AdminStoreListView.as_view(), name='admin-store-list'),
    path('admin/stores/create/', views.AdminStoreCreateView.as_view(), name='admin-store-create'),
    path('admin/stores/<int:pk>/update/', views.AdminStoreUpdateView.as_view(), name='admin-store-update'),
    path('admin/stores/<int:pk>/delete/', views.AdminStoreDeleteView.as_view(), name='admin-store-delete'),

    path('admin/products/', views.AdminProductListView.as_view(), name='admin-product-list'),
    path('admin/products/create/', views.AdminProductCreateView.as_view(), name='admin-product-create'),
    path('admin/products/<int:pk>/update/', views.AdminProductUpdateView.as_view(), name='admin-product-update'),
    path('admin/products/<int:pk>/delete/', views.AdminProductDeleteView.as_view(), name='admin-product-delete'),

    path('admin/main-stores/', views.AdminMainStoreListView.as_view(), name='admin-main-store-list'),
    path('admin/main-stores/create/', views.AdminMainStoreCreateView.as_view(), name='admin-main-store-create'),
    path('admin/main-stores/<int:pk>/update/', views.AdminMainStoreUpdateView.as_view(), name='admin-main-store-update'),
    path('admin/main-stores/<int:pk>/delete/', views.AdminMainStoreDeleteView.as_view(), name='admin-main-store-delete'),

    # API URLs
    path('api/get-shop-details/', views.get_shop_details, name='get-shop-details'),
    #path('api/inventory-status/', views.get_inventory_status, name='api-inventory-status'),
    
    # Shop Management URLs
    path('admin/shops/add/',views.ShopCreateView.as_view(), name='shop-create'),
    path('shops/', views.ShopListView.as_view(), name='shop-list'),
    path('admin/shops/<int:pk>/edit/', views.ShopUpdateView.as_view(), name='shop-update'),
    path('admin/shops/<int:pk>/delete/', views.ShopDeleteView.as_view(), name='shop-delete'),
    
    # Store Management URLs
    path('admin/stores/add/', views.StoreCreateView.as_view(), name='store-create'),
    path('admin/stores/<int:pk>/delete/', views.StoreDeleteView.as_view(), name='store-delete'),
    
    # User Management URLs
    path('admin/users/', UserListView.as_view(), name='user-list'),
    path('admin/users/add/', UserCreateView.as_view(), name='user-create'),
    path('admin/users/<int:pk>/edit/', UserUpdateView.as_view(), name='user-update'),
    path('admin/users/<int:pk>/delete/',UserDeleteView.as_view(), name='user-delete'),
    
    # PWA URLs
    path('manifest.json', views.manifest, name='manifest'),
    path('service-worker.js', views.ServiceWorkerView.as_view(), name='service_worker'),
    path('api/reports/sync/', views.sync_reports, name='sync_reports'),
]