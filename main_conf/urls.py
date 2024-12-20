from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib import admin
from django.urls import path,include,reverse_lazy
from users.models import User
from django.http import HttpResponseRedirect

user = User

def main_view(request):
    if not request.user.is_authenticated: 
        return HttpResponseRedirect(reverse_lazy('reptrack_trace:login'))
    else:
        return HttpResponseRedirect(reverse_lazy('reptrack_trace:home'))



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_view, name='authe'),
    path("track-n-trace/", include('reptrack_trace.urls', namespace='rep-track-trace/')),
    #path("reports/", include('reports.urls', namespace='report')),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)