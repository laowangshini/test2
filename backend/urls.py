from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.http import HttpResponse

def serve_media_index(request):
    """处理media根目录的访问"""
    return serve(request, '', document_root=settings.MEDIA_ROOT)

# 首先定义media相关的URL模式
media_patterns = [
    # 处理media根目录
    path('media/', serve_media_index),
    # 处理media文件
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
        'show_indexes': True
    }),
]

# 其他URL模式
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('myapp.urls')),
]

# 将media_patterns放在最前面
urlpatterns = media_patterns + urlpatterns

# 添加静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)