from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.http import FileResponse, Http404
from django.conf import settings
import os
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny

from .models import Survey, MediaItem, UserProfile
from .serializers import SurveySerializer, MediaItemSerializer, UserProfileSerializer

class SurveyViewSet(viewsets.ModelViewSet):
    """调查记录的视图集"""
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        """添加request到序列化器上下文"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        """获取查询集，支持过滤"""
        queryset = Survey.objects.all()
        
        # 获取查询参数
        category = self.request.query_params.get('category', None)
        view_type = self.request.query_params.get('view_type', None)
        
        # 根据category过滤
        if category:
            queryset = queryset.filter(category=category)
            
        # 如果是请求"我的项目"，则只返回当前用户的项目
        if view_type == 'my' and self.request.user.is_authenticated:
            queryset = queryset.filter(investigator=self.request.user)
            
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """创建时自动设置调查人"""
        serializer.save(investigator=self.request.user)
    
    @action(detail=True, methods=['post'])
    def upload_media(self, request, pk=None):
        """上传媒体文件到特定调查"""
        try:
            survey = self.get_object()
            file_obj = request.FILES.get('file')
            if not file_obj:
                return Response({'error': '没有文件被上传'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取或生成文件标题
            title = request.data.get('title') or os.path.splitext(file_obj.name)[0]
            
            media_data = {
                'survey_name': survey.name,
                'title': title,
                'description': request.data.get('description', ''),
                'media_type': request.data.get('media_type'),
                'category': request.data.get('category'),
                'file_path': file_obj
            }
            
            serializer = MediaItemSerializer(data=media_data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        print("接收到的数据:", request.data)  # 调试日志
        return super().create(request, *args, **kwargs)

class MediaItemViewSet(viewsets.ModelViewSet):
    """媒体资料的视图集"""
    queryset = MediaItem.objects.all()
    serializer_class = MediaItemSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def get_serializer_context(self):
        """添加request到序列化器上下文"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        queryset = MediaItem.objects.all()
        survey_name = self.request.query_params.get('survey_name', None)
        if survey_name is not None:
            queryset = queryset.filter(survey__name=survey_name)
        return queryset

    def perform_create(self, serializer):
        """创建媒体项"""
        serializer.save()

class UserProfileViewSet(viewsets.ModelViewSet):
    """用户配置的视图集"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """获取当前用户信息"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': '请提供用户名和密码'}, status=400)
    
    user = authenticate(username=username, password=password)
    
    if not user:
        return Response({'error': '用户名或密码错误'}, status=401)
    
    token, _ = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user': UserProfileSerializer(user).data
    })

@api_view(['POST'])
def logout(request):
    if request.user.is_authenticated:
        Token.objects.filter(user=request.user).delete()
    return Response({'message': '已登出'})

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def register(request):
    """用户注册视图"""
    username = request.data.get('username')
    password = request.data.get('password')
    display_name = request.data.get('display_name')
    
    if not username or not password or not display_name:
        return Response({'error': '请提供所有必填字段'}, status=400)
    
    # 检查用户名是否已存在
    if UserProfile.objects.filter(username=username).exists():
        return Response({'error': '用户名已存在'}, status=400)
    
    try:
        # 创建新用户
        user = UserProfile.objects.create_user(
            username=username,
            display_name=display_name,
            password=password
        )
        
        # 创建token
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': UserProfileSerializer(user).data
        }, status=201)
        
    except Exception as e:
        return Response({'error': str(e)}, status=400)
