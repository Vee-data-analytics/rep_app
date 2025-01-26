from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView,FormView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import Product,Shop, Report,ShopStore, MainStore
from .forms import  ShopForm, ReportForm, ProductForm,MainStoreForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import logout 
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from PIL import Image as PILImage
import os
from django.http import HttpResponse
from datetime import datetime
from .forms import *
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_control
import os
from django.contrib.auth import authenticate, login
from django.contrib import messages
from users.forms import UserLoginForm
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import localtime
import json
from reportlab.lib.units import inch

from .models import Report, Shop, MainStore, Inventory, ShopStore, User
from django.core.serializers.json import DjangoJSONEncoder
from .models import Report
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from datetime import datetime, timedelta
from django.db.models import Count, Sum, Avg, F, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_protect,ensure_csrf_cookie
import logging

logger = logging.getLogger(__name__)



@ensure_csrf_cookie
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('reptrack_trace:home')  # Replace with the actual dashboard URL
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()

    return render(request, 'users/login.html', {'form': form})


login_required(login_url="reptrack_trace:login")
def logout_view(request):
    if request.method == "POST":
        # Perform logout
        logout(request)
        
        # Redirect to login page
        return redirect(reverse_lazy("reptrack_trace:login"))

    context = {"user": request.user}
    return render(request, "users/logout.html", context)



def main_report_window(request):
    return render(request,'reports/report_main.html')


def offline_view(request):
    return render(request, 'offline.html')


def settings_grid(request):
    return render(request, 'include/settings.html')

class ShopCreateView(CreateView):
    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse({
            'status': 'success',
            'id': self.object.id,
            'name': str(self.object),  
        })

    def form_invalid(self, form):
        return JsonResponse({
            'status': 'error',
            'errors': form.errors
        }, status=400)


class RepresentativePerformanceView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'admin/representative_performance.html'
    
    def test_func(self):
        return self.request.user.role == User.ADMIN

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filters
        rep_id = self.request.GET.get('representative')
        start_date = self.request.GET.get('start_date', 
            (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = self.request.GET.get('end_date', 
            timezone.now().strftime('%Y-%m-%d'))

        # Base queryset
        reports = Report.objects.all()
        if rep_id:
            reports = reports.filter(representative_id=rep_id)
        if start_date and end_date:
            reports = reports.filter(created_at__range=[start_date, end_date])

        # Calculate performance metrics
        performance_metrics = {}
        for rep in User.objects.filter(role=User.REPRESENTATIVE):
            rep_reports = reports.filter(representative=rep)
            
            metrics = {
                'total_reports': rep_reports.count(),
                'submitted_reports': rep_reports.filter(status='submitted').count(),
                'shops_visited': rep_reports.values('shop').distinct().count(),
                'stores_visited': rep_reports.filter(store__isnull=False).values('store').distinct().count(),
                'avg_reports_per_day': rep_reports.annotate(
                    date=TruncDate('created_at')
                ).values('date').annotate(
                    count=Count('id')
                ).aggregate(avg=Avg('count'))['avg'] or 0,
                'topup_reports': rep_reports.filter(needs_topup=True).count(),
            }
            
            # Calculate completion rate
            if metrics['total_reports'] > 0:
                metrics['completion_rate'] = (metrics['submitted_reports'] / metrics['total_reports']) * 100
            else:
                metrics['completion_rate'] = 0

            performance_metrics[rep] = metrics

        # Daily activity for selected representative or all representatives
        daily_activity = reports.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            total=Count('id'),
            submitted=Count('id', filter=Q(status='submitted')),
            drafts=Count('id', filter=Q(status='draft'))
        ).order_by('date')

        context.update({
            'representatives': User.objects.filter(role=User.REPRESENTATIVE),
            'selected_rep': rep_id,
            'start_date': start_date,
            'end_date': end_date,
            'performance_metrics': performance_metrics,
            'daily_activity': daily_activity,
        })
        return context

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'admin/dashboard.html'
    
    def test_func(self):
        return self.request.user.role == User.ADMIN

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get today's date and 30 days ago
        today = timezone.now()
        thirty_days_ago = today - timedelta(days=30)

        # Basic statistics
        basic_stats = {
            'total_shops': Shop.objects.count(),
            'total_main_stores': MainStore.objects.count(),
            'total_representatives': User.objects.filter(role=User.REPRESENTATIVE).count(),
        }

        # Report statistics
        report_stats = {
            'total_reports': Report.objects.count(),
            'reports_today': Report.objects.filter(created_at__date=today.date()).count(),
            'reports_this_month': Report.objects.filter(created_at__gte=thirty_days_ago).count(),
            'pending_reports': Report.objects.filter(status='draft').count(),
        }

        # Recent activity
        recent_activity = Report.objects.select_related(
            'representative', 'shop', 'product'
        ).order_by('-created_at')[:10]

        # Get low stock alerts
        low_stock_alerts = Inventory.objects.annotate(
            alert_status=Case(
                When(quantity__lte=F('minimum_quantity'), then=Value('critical')),
                When(quantity__lte=F('minimum_quantity') * 2, then=Value('warning')),
                default=Value('normal'),
                output_field=CharField(),
            )
        ).filter(
            alert_status__in=['critical', 'warning']
        ).select_related('product', 'shop', 'main_store')[:10]

        # Representative performance summary
        rep_performance = []
        for rep in User.objects.filter(role=User.REPRESENTATIVE):
            rep_reports = Report.objects.filter(
                representative=rep,
                created_at__gte=thirty_days_ago
            )
            
            performance = {
                'representative': rep,
                'total_reports': rep_reports.count(),
                'submitted_reports': rep_reports.filter(status='submitted').count(),
                'shops_visited': rep_reports.values('shop').distinct().count(),
                'completion_rate': (
                    rep_reports.filter(status='submitted').count() / 
                    rep_reports.count() * 100 if rep_reports.count() > 0 else 0
                )
            }
            rep_performance.append(performance)

        context.update({
            'basic_stats': basic_stats,
            'report_stats': report_stats,
            'recent_activity': recent_activity,
            'low_stock_alerts': low_stock_alerts,
            'rep_performance': rep_performance,
            'chart_data': self.get_chart_data(thirty_days_ago),
        })
        return context

    def get_chart_data(self, start_date):
        # Daily reports data for charts
        daily_reports = Report.objects.filter(
            created_at__gte=start_date
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            total=Count('id'),
            submitted=Count('id', filter=Q(status='submitted')),
            drafts=Count('id', filter=Q(status='draft'))
        ).order_by('date')

        return {
            'labels': [entry['date'].strftime('%Y-%m-%d') for entry in daily_reports],
            'total': [entry['total'] for entry in daily_reports],
            'submitted': [entry['submitted'] for entry in daily_reports],
            'drafts': [entry['drafts'] for entry in daily_reports],
        }



class ShopStoreReportsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'admin/shop_store_report.html'
    
    def test_func(self):
        return self.request.user.role == User.ADMIN

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filters from request
        shop_id = self.request.GET.get('shop')
        store_id = self.request.GET.get('store')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        # Base querysets
        reports = Report.objects.filter(
            status='submitted',
            shop_store_manager_confirmed=True
        )
        shop_stores = ShopStore.objects.filter(is_active=True)

        # Apply filters
        if shop_id:
            reports = reports.filter(shop_id=shop_id)
            shop_stores = shop_stores.filter(shop_id=shop_id)

        if store_id:
            reports = reports.filter(store_id=store_id)
            shop_stores = shop_stores.filter(store_id=store_id)

        if start_date and end_date:
            reports = reports.filter(
                created_at__range=[start_date, end_date]
            )

        # Calculate stock movement summary
        stock_summary = []
        for shop_store in shop_stores:
            shop_reports = reports.filter(
                shop=shop_store.shop,
                store=shop_store.store
            )
            
            summary = {
                'shop': shop_store.shop,
                'store': shop_store.store,
                'initial_stock': shop_reports.earliest('created_at').shop_store_current_quantity if shop_reports.exists() else 0,
                'stock_taken': shop_reports.aggregate(
                    total=Sum('quantity_taken_from_shop_store')
                )['total'] or 0,
                'current_stock': shop_reports.latest('created_at').remaining_shop_store_quantity if shop_reports.exists() else 0,
            }
            
            # Calculate status based on current stock
            if summary['current_stock'] <= 10:
                summary['status'] = 'Critical'
            elif summary['current_stock'] <= 50:
                summary['status'] = 'Low'
            else:
                summary['status'] = 'Adequate'
            
            stock_summary.append(summary)

        context.update({
            'shops': Shop.objects.all(),
            
            'selected_shop': shop_id,
            'selected_store': store_id,
            'start_date': start_date,
            'end_date': end_date,
            'reports': reports.order_by('-created_at'),
            'stock_summary': stock_summary,
        })
        return context

class MainStoreReportsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'admin/main_store_reports.html'
    
    def test_func(self):
        return self.request.user.role == User.ADMIN

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filters from request
        store_id = self.request.GET.get('main_store')
        product_id = self.request.GET.get('product')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        # Base querysets
        reports = Report.objects.filter(
            status='submitted',
            main_store__isnull=False
        )
        inventory = Inventory.objects.filter(
            location_type='main_store'
        )

        # Apply filters
        if store_id:
            reports = reports.filter(main_store_id=store_id)
            inventory = inventory.filter(main_store_id=store_id)

        if product_id:
            reports = reports.filter(product_id=product_id)
            inventory = inventory.filter(product_id=product_id)

        if start_date and end_date:
            reports = reports.filter(
                created_at__range=[start_date, end_date]
            )

        # Calculate inventory statistics
        inventory_stats = []
        for item in inventory:
            store_reports = reports.filter(
                main_store=item.main_store,
                product=item.product
            )
            
            stats = {
                'store': item.main_store,
                'product': item.product,
                'current_quantity': item.quantity,
                'total_distributed': store_reports.aggregate(
                    total=Sum('quantity_taken_from_main_store')
                )['total'] or 0,
                'last_updated': item.last_updated,
            }
            
            # Calculate stock status
            if stats['current_quantity'] <= 20:
                stats['status'] = {'level': 'Critical', 'class': 'danger'}
            elif stats['current_quantity'] <= 100:
                stats['status'] = {'level': 'Low', 'class': 'warning'}
            else:
                stats['status'] = {'level': 'Adequate', 'class': 'success'}
            
            inventory_stats.append(stats)

        context.update({
            'main_stores': MainStore.objects.all(),
            'products': Product.objects.all(),
            'selected_store': store_id,
            'selected_product': product_id,
            'start_date': start_date,
            'end_date': end_date,
            'reports': reports.order_by('-created_at'),
            'inventory_stats': inventory_stats,
        })
        return context

class RepresentativeReportsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'admin/representative_reports.html'
    
    def test_func(self):
        return self.request.user.role == User.ADMIN

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filters from request
        rep_id = self.request.GET.get('representative')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        status = self.request.GET.get('status')

        # Base queryset
        reports = Report.objects.all()

        # Apply filters
        if rep_id:
            reports = reports.filter(representative_id=rep_id)

        if start_date and end_date:
            reports = reports.filter(
                created_at__range=[start_date, end_date]
            )

        if status:
            reports = reports.filter(status=status)

        # Calculate representative performance metrics
        performance_metrics = {}
        representatives = User.objects.filter(role=User.REPRESENTATIVE)
        
        for rep in representatives:
            rep_reports = reports.filter(representative=rep)
            
            metrics = {
                'total_reports': rep_reports.count(),
                'submitted_reports': rep_reports.filter(status='submitted').count(),
                'draft_reports': rep_reports.filter(status='draft').count(),
                'shops_visited': rep_reports.values('shop').distinct().count(),
                'stores_visited': rep_reports.filter(store__isnull=False).values('store').distinct().count(),
                'main_stores_visited': rep_reports.filter(main_store__isnull=False).values('main_store').distinct().count(),
                'topup_reports': rep_reports.filter(needs_topup=True).count(),
            }
            
            # Calculate completion rate
            metrics['completion_rate'] = (
                (metrics['submitted_reports'] / metrics['total_reports'] * 100)
                if metrics['total_reports'] > 0 else 0
            )
            
            # Calculate average reports per day
            if start_date and end_date:
                date_range = (datetime.strptime(end_date, '%Y-%m-%d') - 
                            datetime.strptime(start_date, '%Y-%m-%d')).days + 1
                metrics['avg_reports_per_day'] = metrics['total_reports'] / date_range
            else:
                metrics['avg_reports_per_day'] = 0

            performance_metrics[rep] = metrics

        # Get daily activity data for charts
        daily_activity = reports.values('created_at__date').annotate(
            total=Count('id'),
            submitted=Count('id', filter=Q(status='submitted')),
            drafts=Count('id', filter=Q(status='draft'))
        ).order_by('created_at__date')

        context.update({
            'representatives': representatives,
            'selected_rep': rep_id,
            'start_date': start_date,
            'end_date': end_date,
            'performance_metrics': performance_metrics,
            'reports': reports.order_by('-created_at'),
            'daily_activity': daily_activity,
            'total_reports': reports.count(),
            'submission_rate': (
                reports.filter(status='submitted').count() / reports.count() * 100
                if reports.count() > 0 else 0
            )
        })
        return context
    
class ShopReportsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'admin/shop_reports.html'
    
    def test_func(self):
        return self.request.user.role == User.ADMIN

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filters from request
        shop_id = self.request.GET.get('shop')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        # Base querysets
        reports = Report.objects.filter(status='submitted')
        inventory_items = Inventory.objects.filter(location_type='shop')

        # Apply filters
        if shop_id:
            reports = reports.filter(shop_id=shop_id)
            inventory_items = inventory_items.filter(shop_id=shop_id)

        if start_date and end_date:
            reports = reports.filter(
                created_at__range=[start_date, end_date]
            )

        # Get current inventory status
        current_inventory = []
        for item in inventory_items:
            current_inventory.append({
                'product': item.product,
                'quantity': item.quantity,
                'last_updated': item.last_updated,
                'needs_restock': item.quantity < item.minimum_quantity if hasattr(item, 'minimum_quantity') else False
            })

        context.update({
            'shops': Shop.objects.all(),
            'selected_shop': shop_id,
            'start_date': start_date,
            'end_date': end_date,
            'reports': reports.order_by('-created_at'),
            'current_inventory': current_inventory,
        })
        return context


class MainStoreReportsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'admin/main_store_reports.html'
    
    def test_func(self):
        return self.request.user.role == User.ADMIN

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filters from request
        store_id = self.request.GET.get('main_store')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        product_id = self.request.GET.get('product')

        # Base querysets
        reports = Report.objects.filter(
            status='submitted',
            main_store__isnull=False
        )
        
        inventory_items = Inventory.objects.filter(
            location_type='main_store'
        )

        # Apply filters
        if store_id:
            reports = reports.filter(main_store_id=store_id)
            inventory_items = inventory_items.filter(main_store_id=store_id)

        if product_id:
            reports = reports.filter(product_id=product_id)
            inventory_items = inventory_items.filter(product_id=product_id)

        if start_date and end_date:
            reports = reports.filter(
                created_at__range=[start_date, end_date]
            )

        # Calculate inventory statistics
        inventory_stats = []
        for item in inventory_items:
            total_supplied = reports.filter(
                main_store=item.main_store,
                product=item.product
            ).aggregate(
                total=models.Sum('quantity_taken_from_main_store')
            )['total'] or 0

            inventory_stats.append({
                'product': item.product,
                'current_quantity': item.quantity,
                'total_supplied': total_supplied,
                'last_updated': item.last_updated,
                'status': self.get_stock_status(item.quantity)
            })

        context.update({
            'main_stores': MainStore.objects.all(),
            'products': Product.objects.all(),
            'selected_store': store_id,
            'selected_product': product_id,
            'start_date': start_date,
            'end_date': end_date,
            'reports': reports.order_by('-created_at'),
            'inventory_stats': inventory_stats,
        })
        return context

    def get_stock_status(self, quantity):
        # You can customize these thresholds
        if quantity <= 10:
            return {'level': 'Critical', 'class': 'danger'}
        elif quantity <= 50:
            return {'level': 'Low', 'class': 'warning'}
        return {'level': 'Adequate', 'class': 'success'}

class ShopDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting a shop"""
    model = Shop
    template_name = 'track_n_trace/shop/delete_shop.html'
    success_url = reverse_lazy('shop-management')  # Redirect after successful deletion

    def test_func(self):
        """Restrict access to admin users only"""
        return self.request.user.role == User.ADMIN

class ShopUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating an existing shop"""
    model = Shop
    form_class = ShopForm
    template_name = 'admin/update_shop.html'
    success_url = reverse_lazy('reptrack_trace:admin-shop-management')  # Replace with the appropriate redirect URL

    def test_func(self):
        """Restrict access to only admin users"""
        return self.request.user.role == User.ADMIN

    def form_valid(self, form):
        """Optional: Custom logic before saving the updated instance"""
        # Add any additional logic here if required
        return super().form_valid(form)



class ShopCreateView(CreateView):
    model = Shop
    form_class = ShopForm
    template_name = 'reports/report_form.html'

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', '/')

    def form_valid(self, form):
        shop = form.save()
        messages.success(self.request, f'Shop "{shop.name}" created successfully')
        return super().form_valid(form)

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'reports/report_form.html'

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', '/')

    def form_valid(self, form):
        product = form.save()
        messages.success(self.request, f'Product "{product.name}" created successfully')
        return super().form_valid(form)


class ReportDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting a Drafted reports"""
    model = Report
    template_name = 'reports/report_delete.html'
    success_url = reverse_lazy('reptrack_trace:home')
    

class MainStoreCreateView(CreateView):
    model = MainStore
    form_class = MainStoreForm
    template_name = 'reports/report_form.html'

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', '/')

    def form_valid(self, form):
        main_store = form.save()
        messages.success(self.request, f'Main Store "{main_store.name}" created successfully')
        return super().form_valid(form)



    
    

class StoreUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating an existing shop"""
    model = Shop
    form_class = ShopForm
    template_name = 'admin/update_store.html'
    success_url = reverse_lazy('reptrack_trace:shop-management')  
    
    def test_func(self):
        """Restrict access to only admin users"""
        return self.request.user.role == User.ADMIN

    def form_valid(self, form):
        """Optional: Custom logic before saving the updated instance"""
        # Add any additional logic here if required
        return super().form_valid(form)



class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == User.ADMIN

# Shop Management
class AdminShopCreateView(AdminRequiredMixin, CreateView):
    model = Shop
    form_class = ShopForm
    template_name = 'admin/shopcreate.html'
    success_url = reverse_lazy('reptrack_trace:admin-shop-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Shop "{self.object.name}" created successfully')
        return response

class AdminShopUpdateView(AdminRequiredMixin, UpdateView):
    model = Shop
    form_class = ShopForm
    template_name = 'admin/update.html'
    success_url = reverse_lazy('reptrack_trace:admin-shop-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Shop "{self.object.name}" updated successfully')
        return response

class ShopAdminListView(AdminRequiredMixin, ListView):
    model = Shop
    template_name = 'admin/shoplist.html'
    context_object_name = 'shops'

class AdminShopDeleteView(AdminRequiredMixin, DeleteView):
    model = Shop
    template_name = 'admin/store_delete.html'
    success_url = reverse_lazy('reptrack_trace:admin-shop-list')

    def delete(self, request, *args, **kwargs):
        shop = self.get_object()
        messages.success(request, f'Shop "{shop.name}" deleted successfully')
        return super().delete(request, *args, **kwargs)




# Product Management
class AdminProductCreateView(AdminRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'admin/productcreate.html'
    success_url = reverse_lazy('reptrack_trace:admin-product-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Product "{self.object.name}" created successfully')
        return response

class AdminProductUpdateView(AdminRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'admin/productupdate.html'
    success_url = reverse_lazy('reptrack_trace:admin-product-list')

class AdminProductListView(AdminRequiredMixin, ListView):
    model = Product
    template_name = 'admin/productlist.html'
    context_object_name = 'products'

class AdminProductDeleteView(AdminRequiredMixin, DeleteView):
    model = Product
    template_name = 'admin/productdelete.html'
    success_url = reverse_lazy('reptrack_trace:admin-product-list')

# Main Store Management
class AdminMainStoreCreateView(AdminRequiredMixin, CreateView):
    model = MainStore
    form_class = MainStoreForm
    template_name = 'admin/mainstore_create.html'
    success_url = reverse_lazy('reptrack_trace:admin-main-store-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Main Store "{self.object.name}" created successfully')
        return response

class AdminMainStoreUpdateView(AdminRequiredMixin, UpdateView):
    model = MainStore
    form_class = MainStoreForm
    template_name = 'admin/main_storeupdate.html'
    success_url = reverse_lazy('reptrack_trace:admin-main-store-list')

class AdminMainStoreListView(AdminRequiredMixin, ListView):
    model = MainStore
    template_name = 'admin/mainstorelist.html'
    context_object_name = 'main_stores'

class AdminMainStoreDeleteView(AdminRequiredMixin, DeleteView):
    model = MainStore
    template_name = 'admin/main-store-delete.html'
    success_url = reverse_lazy('reptrack_trace:admin-main-store-list')


class ReportCreateView(FormView):
    template_name = 'reports/report_form.html'
    form_class = ReportForm
    success_url = reverse_lazy('reptrack_trace:home')
    
    
    def get_initial(self):
        initial = super().get_initial()
        # Retrieve unsaved data from session
        unsaved_data = self.request.session.get('unsaved_report_data', {})
        initial.update(unsaved_data)
           
        # Prepopulate with shop data if available
        
        main_store_id = self.request.GET.get('main_store') or self.request.POST.get('main_store')
        if main_store_id:
            try:
                main_store = MainStore.objects.get(id=main_store_id)
                initial.update({'main_store': main_store.id})
            except MainStore.DoesNotExist:
                pass
        
        shop_id = self.request.GET.get('shop') or self.request.POST.get('shop')
        if shop_id:
            try:
                shop = Shop.objects.get(id=shop_id)
                initial.update({'shop': shop.id})
            except Shop.DoesNotExist:
                pass
            
        product_id = self.request.GET.get('product') or self.request.POST.get('product')
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                initial.update({'product': product.id})
            except Product.DoesNotExist:
                pass
        return initial
       
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Fetch selected shop data
        context = super().get_context_data(**kwargs)
        
        # Fetch selected shop data
        selected_shop_id = self.request.GET.get('shop') or self.request.POST.get('shop')
        if selected_shop_id:
            try:
                selected_shop = Shop.objects.get(id=selected_shop_id)
                context['selected_shop'] = {
                    'name': selected_shop.name,
                    'address': selected_shop.address,
                    'manager_name': selected_shop.manager_name,
                    'manager_phone': selected_shop.manager_phone,
                    'stores_manager': selected_shop.store_manager_name,
                    'stores_manager_phone': selected_shop.store_manager_phone,
                }
            except Shop.DoesNotExist:
                context['selected_shop'] = None
        else:
            context['selected_shop'] = None

        # Fetch selected main store data
        selected_main_store_id = self.request.GET.get('main_store') or self.request.POST.get('main_store')
        if selected_main_store_id:
            try:
                selected_mainstore = MainStore.objects.get(id=selected_main_store_id)
                context['selected_mainstore'] = {
                    'location': selected_mainstore.address,
                    'manager_name': selected_mainstore.manager_name,
                    'manager_phone': selected_mainstore.manager_phone,
                    'manager_email': selected_mainstore.manager_email
                }
            except MainStore.DoesNotExist:
                context['selected_mainstore'] = None
        else:
            context['selected_mainstore'] = None

        # Fetch selected product data
        selected_product_id = self.request.GET.get('product') or self.request.POST.get('product')
        if selected_product_id:
            try:
                selected_product = Product.objects.get(id=selected_product_id)
                context['selected_product'] = {
                    'name': selected_product.name,
                }
            except Product.DoesNotExist:
                context['selected_product'] = None
        else:
            context['selected_product'] = None
    
        # Add dropdown options and forms
        context.update({
            'shops': Shop.objects.all(),
            'products': Product.objects.all(),
            'main_stores': MainStore.objects.all(),
            'shop_stores': ShopStore.objects.all(),
            'shop_form': ShopForm(),
            'product_form': ProductForm(),
            'main_store_form': MainStoreForm(),
            'shop_store_form': ShopStoreForm(),
        })
        
        return context

    def post(self, request, *args, **kwargs):
        
        # Handle AJAX modal form submissions
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form_key = request.POST.get('form_key')
            modal_forms = {
                'shop_form': ShopForm,
                'product_form': ProductForm,
                'store_form': StoreForm,
                'main_store_form': MainStoreForm,
                'shop_store_form': ShopStoreForm,
            }
    
            if form_key in modal_forms:
                form_class = modal_forms[form_key]
                form = form_class(request.POST, request.FILES)
                if form.is_valid():
                    instance = form.save()
                    return JsonResponse({
                        'success': True,
                        'dropdown_data': {
                            'dropdown_id': f'id_{form_key.split("_")[0]}',
                            'new_option': {
                                'value': instance.id,
                                'text': str(instance)
                            }
                        }
                    })
                else:
                    return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    
        # Handle main form submission
        form = self.get_form()
        if form.is_valid():
            report = form.save(commit=False)
            report.representative = request.user
    
            submission_type = request.POST.get('submission_type', 'draft')
            report.status = 'submitted' if submission_type == 'submit' else 'draft'
            report.submitted_at = timezone.now() if submission_type == 'submit' else None
    
            try:
                report.save()
                
                if 'unsaved_report_data' in self.request.session:
                    del self.request.session['unsaved_report_data']
    
                messages.success(request, 'Report saved successfully as {}'.format(
                    'final submission' if submission_type == 'submit' else 'draft'
                ))
                
                return redirect('reptrack_trace:home')
            except Exception as e:
                messages.error(request, f'Error saving report: {str(e)}')
                return self.form_invalid(form)
        else:
            return self.form_invalid(form) 
    

class ReportDetailView(DetailView):
    model = Report
    template_name = 'reports/report_detail.html'
    context_object_name = 'report'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report = self.object
        
        
       
        context['shop_details'] = {
            'shop': report.shop,
            'address': report.shop.address,
            'manager_name': report.shop.manager_name,
            'manager_phone': report.shop.manager_phone,
            'product': report.product,
            'current_quantity': report.shop_current_quantity,
            'desired_quantity': report.desired_quantity,
            'needs_topup': report.needs_topup,
            'topup_quantity': report.topup_quantity,
            'photo': report.shop_photo,
            'photo_taken_at': report.shop_photo_taken_at,
            'comments': report.shop_comments,
        }

        context['shop_store_details'] = {
            'name': report.shop,
            'manager_confirmed': report.shop_store_manager_confirmed,
            'current_quantity': report.shop_store_current_quantity,
            'has_sufficient_stock': report.shop_store_has_sufficient_stock,
            'quantity_taken': report.quantity_taken_from_shop_store,
            'remaining_quantity': report.remaining_shop_store_quantity,
            'updated': report.was_shop_updated,
            'final_shop_quantity': report.shop_update_quantity,
            'photo': report.shop_store_photo,
            'photo_taken_at': report.shop_store_photo_taken_at,
            'shop_update_photo': report.shop_photo_update,
            'shop_photo_update_taken_at':report.shop_photo_update_taken_at,
            'comments': report.shop_store_comments,
        }


        context['main_store_details'] = {
            'main_store': report.main_store,
            'address': report.main_store.address if report.main_store else None,
            'manager_name': report.main_store.manager_name if report.main_store else None,
            'manager_phone': report.main_store.manager_phone if report.main_store else None,
            'manager_email': report.main_store.manager_email if report.main_store else None,
            'current_quantity': report.main_store_quantity,
            'quantity_taken': report.quantity_taken_from_main_store,
            'remaining_quantity': report.remaining_main_store_quantity,
            'photo': report.main_store_photo,
            'photo_taken_at': report.main_store_photo_taken_at,
            'delivered_to_shop_stores': report.delivered_to_shop_stores,
            'was_shop_stores_updated': report.was_shop_stores_updated,
            'quantity_in_shopstores': report.quantity_in_shopstores,
            'current_shop_store_photo': report.current_shop_store_photo,
            'delivered_to_shop': report.delivered_to_shop,
            'was_shop_updated': report.was_shop_m_updated,
            'total_quantity_in_shop': report.total_quantity_in_shop,
            'current_shop_photo': report.current_shop_photo,
            'current_shop_photo_taken_at':report.current_shop_photo_taken_at,
            'current_shop_store_photo_taken_at':report.current_shop_store_photo_taken_at,
            'comments': report.main_store_comments,
        }

        context['general_info'] = {
            'status': report.status,
            'created_at': localtime(report.created_at),
            'submitted_at': localtime(report.submitted_at) if report.submitted_at else "Not Submitted",
            'final_shop_quantity': report.final_shop_quantity or 0,
            'final_store_quantity': report.final_store_quantity or 0,
        }

        return context





class UnfinishedReportsView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'reports/unfinished_reports.html'
    context_object_name = 'unfinished_reports'
    paginate_by = 10

    def get_date_range(self):
        """Helper method to get and validate date range"""
        today = timezone.now()
        default_start = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        default_end = today.strftime('%Y-%m-%d')

        start_date = self.request.GET.get('start_date', default_start)
        end_date = self.request.GET.get('end_date', default_end)

        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            
            if start > end:
                start = datetime.strptime(default_start, '%Y-%m-%d')
                end = datetime.strptime(default_end, '%Y-%m-%d') + timedelta(days=1)
                messages.warning(self.request, 'Invalid date range. Using default range.')
        except ValueError:
            start = datetime.strptime(default_start, '%Y-%m-%d')
            end = datetime.strptime(default_end, '%Y-%m-%d') + timedelta(days=1)
            messages.warning(self.request, 'Invalid date format. Using default range.')

        return start, end, start_date, end_date

    def get_queryset(self):
        """Return filtered unfinished reports"""
        queryset = Report.objects.filter(status='draft')
        
        if self.request.user.role == User.REPRESENTATIVE:
            queryset = queryset.filter(representative=self.request.user)

        # Get validated date range
        start, end, _, _ = self.get_date_range()
        
        # Apply date filter
        queryset = queryset.filter(
            created_at__gte=start,
            created_at__lt=end
        )

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current date range
        _, _, start_date, end_date = self.get_date_range()
        
        # Set context data
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'default_start_date': (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'default_end_date': timezone.now().strftime('%Y-%m-%d'),
            'total_drafts': self.get_queryset().count()
        })
        
        return context


class ReportUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Report
    form_class = ReportForm
    template_name = 'reports/report_form.html'
    success_url = reverse_lazy('reptrack_trace:unfinished_reports')

    def test_func(self):
        report = self.get_object()
        return self.request.user == report.representative

    def get_queryset(self):
        if self.request.user.role == User.REPRESENTATIVE:
            return Report.objects.filter(representative=self.request.user, status='draft')
        return Report.objects.filter(status='draft')

    def get_initial(self):
        initial = super().get_initial()
        # Retrieve unsaved data from session
        unsaved_data = self.request.session.get('unsaved_report_data', {})
        initial.update(unsaved_data)
    
        # Prepopulate with shop data if available
        shop_id = self.request.GET.get('shop') or self.request.POST.get('shop')
        if shop_id:
            try:
                shop = Shop.objects.get(id=shop_id)
                initial.update({'shop': shop.id})
            except Shop.DoesNotExist:
                pass
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the current report
        report = self.get_object()
        
        # If we have a shop in the report, use it
        if report.shop:
            context['selected_shop'] = {
                'name': report.shop.name,
                'address': report.shop.address,
                'manager_name': report.shop.manager_name,
                'manager_phone': report.shop.manager_phone,
                'stores_manager': report.shop.store_manager_name,
                'stores_manager_phone': report.shop.store_manager_phone,
            }
        
        # If we have a main store in the report, use it
        if report.main_store:
            context['selected_mainstore'] = {
                'address': report.main_store.address,
                'manager_name': report.main_store.manager_name,
                'manager_phone': report.main_store.manager_phone,
                'manager_email': report.main_store.manager_email,
            }
        
        # If we have a product in the report, use it
        if report.product:
            context['selected_product'] = {
                'name': report.product.name,
            }
        
        # Add your existing context
        context.update({
            'shops': Shop.objects.all(),
            'products': Product.objects.all(),
            'main_stores': MainStore.objects.all(),
            'shop_stores': ShopStore.objects.all(),
            'shop_form': ShopForm(),
            'product_form': ProductForm(),
            'main_store_form': MainStoreForm(),
            'shop_store_form': ShopStoreForm(),
        })
        

        return context



    def post(self, request, *args, **kwargs):
        """Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid."""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Handle modal form submissions (This part is correct)
            form_key = request.POST.get('form_key')
            modal_forms = {
                'shop_form': ShopForm,
                'product_form': ProductForm,
                'store_form': StoreForm,
                'main_store_form': MainStoreForm,
                'shop_store_form': ShopStoreForm,
            }
    
            if form_key in modal_forms:
                form_class = modal_forms[form_key]
                form = form_class(request.POST, request.FILES)
                if form.is_valid():
                    instance = form.save()
                    return JsonResponse({
                        'success': True,
                        'dropdown_data': {
                            'dropdown_id': f'id_{form_key.split("_")[0]}',
                            'new_option': {
                                'value': instance.id,
                                'text': str(instance)
                            }
                        }
                    })
                else:
                    return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    
        self.object = self.get_object()

        try:
            # Handle modal form submissions
            if 'product_form' in request.POST:
                return self.handle_modal_form(
                    form_class=ProductForm,
                    success_message='Product created successfully',
                    error_message='Error creating product'
                )
            
            elif 'store_form' in request.POST:
                return self.handle_modal_form(
                    form_class=StoreForm,
                    success_message='Store created successfully',
                    error_message='Error creating store'
                )
            
            elif 'main_store_form' in request.POST:
                return self.handle_modal_form(
                    form_class=MainStoreForm,
                    success_message='Main Store created successfully',
                    error_message='Error creating main store'
                )
            
            elif 'shop_store_form' in request.POST:
                return self.handle_modal_form(
                    form_class=ShopStoreForm,
                    success_message='Shop Store created successfully',
                    error_message='Error creating shop store'
                )

            # Handle main form submission
            return self.handle_main_form_submission()

        except Exception as e:
            logger.error(f"Error in ReportUpdateView POST: {str(e)}")
            messages.error(request, "An unexpected error occurred. Please try again.")
            return redirect(self.get_success_url())

    def handle_modal_form(self, form_class, success_message, error_message):
        """Helper method to handle modal form submissions"""
        form = form_class(self.request.POST, self.request.FILES)
        if form.is_valid():
            instance = form.save()
            messages.success(self.request, f'{success_message}: {instance.name}')
            return redirect(self.request.path)
        else:
            messages.error(self.request, f'{error_message}. Please check the form.')
            return self.form_invalid(form)

    def handle_main_form_submission(self):
        """Helper method to handle main report form submission"""
        form = self.get_form()
        if form.is_valid():
            report = form.save(commit=False)
            
            # Handle submission type
            submission_type = self.request.POST.get('submission_type', 'draft')
            if submission_type == 'submit':
                report.status = 'submitted'
                report.submitted_at = timezone.now()
                messages.success(self.request, 'Report submitted successfully')
            else:
                report.status = 'draft'
                messages.success(self.request, 'Draft updated successfully')
            
            report.save()
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Handle form validation errors"""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)

    def get_success_url(self):
        """Determine redirect URL based on submission type"""
        if self.object.status == 'submitted':
            return reverse_lazy('reptrack_trace:report-list')
        return reverse_lazy('reptrack_trace:unfinished_reports')


class FinishedReportsView(LoginRequiredMixin, ListView):
    """
    View for listing finished reports with advanced filtering capabilities
    """
    model = Report
    template_name = 'reports/report_list.html'
    context_object_name = 'finished_reports'
    paginate_by = 10

    def get_queryset(self):
        """
        Return filtered and sorted reports based on user role and date range
        """
        # Base queryset for closed reports
        queryset = Report.objects.filter(status='submitted')  
        # Filter by user role
        if self.request.user.role == User.REPRESENTATIVE:
            queryset = queryset.filter(representative=self.request.user)
        
        # Date range filtering
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if start_date and end_date:
            try:
                # Convert string dates to datetime objects
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                
                # Filter reports within the specified date range
                queryset = queryset.filter(
                    created_at__gte=start,
                    created_at__lt=end
                )
            except ValueError:
                # If date parsing fails, return original queryset
                pass
        
        # Order by most recent first
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        """
        Add additional context for date range and filtering
        """
        context = super().get_context_data(**kwargs)
        
        # Pass date range parameters
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        
        # Optional: Add total report count for the current filtered set
        context['total_reports'] = self.get_queryset().count()
        
        # Optional: Provide default date range (e.g., last 30 days)
        if not context['start_date'] or not context['end_date']:
            thirty_days_ago = timezone.now() - timedelta(days=30)
            context['default_start_date'] = thirty_days_ago.strftime('%Y-%m-%d')
            context['default_end_date'] = timezone.now().strftime('%Y-%m-%d')
        
        return context



class ShopReportsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'admin/shop_reports.html'
    
    def test_func(self):
        return self.request.user.role == User.ADMIN

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from request
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        shop_id = self.request.GET.get('shop')

        # Query reports based on filters
        reports = Report.objects.filter(status='submitted')
        
        if start_date and end_date:
            reports = reports.filter(
                created_at__range=[start_date, end_date]
            )
        
        if shop_id:
            reports = reports.filter(shop_id=shop_id)

        context.update({
            'reports': reports,
            'shops': Shop.objects.all(),
            'start_date': start_date,
            'end_date': end_date,
            'selected_shop': shop_id
        })
        return context


class RepresentativeReportsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'admin/representative_reports.html'
    
    def test_func(self):
        return self.request.user.role == User.ADMIN

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        rep_id = self.request.GET.get('representative')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        reports = Report.objects.all()
        
        if rep_id:
            reports = reports.filter(representative_id=rep_id)
        
        if start_date and end_date:
            reports = reports.filter(
                created_at__range=[start_date, end_date]
            )

        # Get statistics
        context.update({
            'representatives': User.objects.filter(role=User.REPRESENTATIVE),
            'reports': reports,
            'stats': {
                'total_reports': reports.count(),
                'submitted_reports': reports.filter(status='submitted').count(),
                'draft_reports': reports.filter(status='draft').count(),
                'shops_visited': reports.values('shop').distinct().count(),
                
            }
        })
        return context

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Admin dashboard view"""
    model = Report
    template_name = 'admin/dashboard.html'
    context_object_name = 'reports'

    def test_func(self):
        return self.request.user.role == User.ADMIN

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
        'total_shops': Shop.objects.count(),
        'total_main_stores': MainStore.objects.count(),
        'total_reports': Report.objects.filter(
        created_at__gte=datetime.now()-timedelta(days=7)).count(),
        'recent_reports': Report.objects.all().order_by('-created_at')[:5],
        'total_representatives': User.objects.filter(role=User.REPRESENTATIVE).count(),
        'recent_reports': Report.objects.filter(status='submitted').order_by('-created_at')[:5],
        'pending_reports': Report.objects.filter(status='draft').count(),
        #'inventory_alerts': self.get_inventory_alerts(),
        })
        return context



class ShopListView(LoginRequiredMixin, ListView):
    """View for listing all shops."""
    model = Shop
    template_name = 'admin/shop_list.html'  # Replace with the path to your template
    context_object_name = 'shops'
    paginate_by = 10  # Number of shops per page

    def get_queryset(self):
        """
        Optionally, you can filter shops based on user role or other criteria.
        """
        return Shop.objects.all().order_by('name')  # Customize query if needed

    def get_context_data(self, **kwargs):
        """
        Add additional context to the template if needed.
        """
        context = super().get_context_data(**kwargs)
        context['total_shops'] = self.get_queryset().count()  # Example: Add total shop count
        return context


class AdminManagementView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'admin/management.html'
    
    def test_func(self):
        return self.request.user.role == 'admin'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'management'
        return context

@login_required
def shop_management(request):
    """View for managing shops"""
    if request.user.role != User.ADMIN:
        return redirect('home')

    shops = Shop.objects.all()
    return render(request, 'admin/shop_management.html', {'shops': shops})

@login_required
def store_management(request):
    """View for managing main stores"""
    if request.user.role != User.ADMIN:
        return redirect('home')

    stores = MainStore.objects.all()
    return render(request, 'admin/store_management.html', {'stores': stores})

# API Views for Dynamic Updates
@login_required
def get_shop_details(request):
    """API view to get shop details"""
    shop_id = request.GET.get('shop_id')
    shop = get_object_or_404(Shop, id=shop_id)

    data = {
        'address': shop.address,
        'manager_name': shop.manager_name,
        'manager_phone': shop.manager_phone,
        'store_manager_name': shop.store_manager_name,
        'store_manager_phone': shop.store_manager_phone
    }
    return JsonResponse(data)

@login_required
def get_inventory_status(request):
    """API view to get current inventory status"""
    product_id = request.GET.get('product_id')
    location_id = request.GET.get('location_id')
    location_type = request.GET.get('location_type')

    # Build the filter arguments dynamically based on location_type
    filters = {
        'product_id': product_id,
    }

    if location_type == 'shop':
        filters['shop_id'] = location_id
    else:
        filters['main_store_id'] = location_id

    # Get the inventory object with the appropriate filters
    inventory = get_object_or_404(Inventory, **filters)

    return JsonResponse({'quantity': inventory.quantity})

def get_image_for_pdf(image_field, max_width=6*inch, max_height=4*inch):
    """Helper function to process and resize images for PDF"""
    if not image_field:
        return None
        
    try:
        # Open the image using PIL
        img = PILImage.open(image_field)
        
        # Convert to RGB if necessary (for PNG with transparency)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
            
        # Calculate aspect ratio and new dimensions
        aspect = img.width / img.height
        if aspect > (max_width / max_height):
            new_width = max_width
            new_height = max_width / aspect
        else:
            new_height = max_height
            new_width = max_height * aspect
            
        # Save the processed image to a temporary BytesIO buffer
        temp_buffer = BytesIO()
        img.save(temp_buffer, format='JPEG', quality=85)
        temp_buffer.seek(0)
        
        # Create ReportLab Image object
        return Image(temp_buffer, width=new_width, height=new_height)
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None

def generate_pdf_report(report, pk=None):
    """Generate PDF for the report"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title Section
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20
    )
    elements.append(Paragraph(f"Inventory Report #{report.pk}", title_style))
    elements.append(Spacer(1, 20))

    # Report metadata
    metadata_style = ParagraphStyle(
        'MetadataStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=6
    )
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", metadata_style))
    elements.append(Paragraph(f"Shop: {report.shop}", metadata_style))
    elements.append(Paragraph(f"Product: {report.product}", metadata_style))
    elements.append(Spacer(1, 20))

    # Shop Section
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10
    )
    elements.append(Paragraph("Shop Details", section_style))
    shop_data = [
        ["Current Quantity", str(report.shop_current_quantity)],
        ["Needs Top-up", "Yes" if report.needs_topup else "No"],
        ["Desired Quantity", str(report.desired_quantity)],
        ["Top-up Quantity", str(report.topup_quantity)],
        ["Comments", report.shop_comments or "N/A"]
    ]
    shop_table = Table(shop_data, colWidths=[200, 300])
    shop_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(shop_table)
    
    # Add shop photo if exists
    shop_image = get_image_for_pdf(report.shop_photo)
    if shop_image:
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("Shop Photo:", metadata_style))
        elements.append(shop_image)
    elements.append(Spacer(1, 20))

    # Shop Store Section
    elements.append(Paragraph("Shop Store Details", section_style))
    shop_store_data = [
        ["Manager Confirmed", "Yes" if report.shop_store_manager_confirmed else "No"],
        ["Current Quantity", str(report.shop_store_current_quantity)],
        ["Quantity Taken", str(report.quantity_taken_from_shop_store)],
        ["Remaining Quantity", str(report.remaining_shop_store_quantity)],
        ["Comments", report.shop_store_comments or "N/A"]
    ]
    shop_store_table = Table(shop_store_data, colWidths=[200, 300])
    shop_store_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(shop_store_table)
    
    # Add shop store photo if exists
    shop_store_image = get_image_for_pdf(report.shop_store_photo)
    if shop_store_image:
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("Shop Store Photo:", metadata_style))
        elements.append(shop_store_image)
    elements.append(Spacer(1, 20))

    # Store Section
    elements.append(Paragraph("Store Details", section_style))
    store_data = [
        ["Store", str(report.store)],
        ["Current Quantity", str(report.store_current_quantity)],
        ["Quantity Taken", str(report.quantity_taken_from_store)],
        ["Remaining Quantity", str(report.remaining_store_quantity)],
        ["Comments", report.store_comments or "N/A"]
    ]
    store_table = Table(store_data, colWidths=[200, 300])
    store_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(store_table)
    
    # Add store photo if exists
    store_image = get_image_for_pdf(report.store_photo)
    if store_image:
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("Store Photo:", metadata_style))
        elements.append(store_image)
    elements.append(Spacer(1, 20))

    # Main Store Section
    elements.append(Paragraph("Main Store Details", section_style))
    main_store_data = [
        ["Main Store", str(report.main_store)],
        ["Current Quantity", str(report.main_store_quantity)],
        ["Quantity Taken", str(report.quantity_taken_from_main_store)],
        ["Remaining Quantity", str(report.remaining_main_store_quantity)],
        ["Comments", report.main_store_comments or "N/A"]
    ]
    main_store_table = Table(main_store_data, colWidths=[200, 300])
    main_store_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(main_store_table)
    
    # Add main store photo if exists
    main_store_image = get_image_for_pdf(report.main_store_photo)
    if main_store_image:
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("Main Store Photo:", metadata_style))
        elements.append(main_store_image)

    # Build PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def download_report_pdf(request, pk):
    """View to download the report as PDF"""
    report = get_object_or_404(Report, pk=pk)
    
    # Generate PDF
    pdf = generate_pdf_report(report, pk)
    
    # Create response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{pk}.pdf"'
    response.write(pdf)
    
    return response

# Analytics Views
class AnalyticsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """View for displaying analytics"""
    model = Report
    template_name = 'admin/analytics.html'

    def test_func(self):
        return self.request.user.role == User.ADMIN

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'report_stats': self.get_report_statistics(),
            'inventory_trends': self.get_inventory_trends(),
            'representative_performance': self.get_representative_performance(),
        })
        return context


def manifest(request):
    """
    Return the manifest.json file for PWA
    """
    return JsonResponse({
        'name': 'Reps Track and Trace',
        'short_name': 'RepTrack',
        'start_url': '/',
        'display': 'standalone',
        'background_color': '#ffffff',
        'theme_color': '#000000',
        'scope': '/',
        'icons': [
            {
                'src': '/static/images/logo.png',
                'sizes': '192x192',
                'type': 'image/png'
            },
            {
                'src': '/static/images/logo.png',
                'sizes': '512x512',
                'type': 'image/png'
            }
        ]
    })

@cache_control(max_age=86400)
def service_worker(request):
    """
    Return the service worker JavaScript file
    """
    return render(request, 'service-worker.js',
                 content_type='application/javascript')

def offline(request):
    """
    Return the offline page
    """
    return render(request, 'offline.html')

class ServiceWorkerView(TemplateView):
    """
    Serve the service worker template
    """
    template_name = 'service-worker.js'
    content_type = 'application/javascript'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

@csrf_exempt
def sync_reports(request):
    """
    Handle syncing of reports from IndexedDB to server
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Process the report data here
            # Save to your Django models
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'},
                       status=405)
