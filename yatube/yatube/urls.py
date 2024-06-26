from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from django.urls import include, path

handler404 = 'core.views.page_not_found'
handler403 = 'core.views.csrf_failure'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/', include('about.urls', namespace='about')),
    path('auth/', include('users.urls', namespace='users')),
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('posts.urls', namespace='posts')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
