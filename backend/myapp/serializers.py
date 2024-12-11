from rest_framework import serializers
from .models import Survey, MediaItem, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'display_name', 'user_type', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class MediaItemSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    survey_name = serializers.CharField(write_only=True)

    class Meta:
        model = MediaItem
        fields = ['id', 'title', 'description', 'media_type', 'category', 'file_path', 'file_url', 'created_at', 'survey_name']
        read_only_fields = ['created_at']

    def get_file_url(self, obj):
        if not obj.file_path:
            return None
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(obj.file_path.url)
        return obj.file_path.url

    def create(self, validated_data):
        survey_name = validated_data.pop('survey_name')
        
        try:
            survey = Survey.objects.get(name=survey_name)
        except Survey.DoesNotExist:
            raise serializers.ValidationError({'survey_name': '找不到对应的项目'})
        
        media_item = MediaItem.objects.create(
            survey=survey,
            **validated_data
        )
        return media_item

class SurveySerializer(serializers.ModelSerializer):
    media_items = MediaItemSerializer(many=True, read_only=True)
    investigator = UserProfileSerializer(read_only=True)

    class Meta:
        model = Survey
        fields = [
            'id', 'name', 'longitude', 'latitude', 
            'start_date', 'end_date', 'investigator', 
            'created_at', 'updated_at', 'media_items'
        ]
        read_only_fields = ['investigator', 'created_at', 'updated_at', 'media_items']