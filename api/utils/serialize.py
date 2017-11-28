# coding:utf-8
# Created by yang

##序列化
from rest_framework import serializers
from repository import models


class CourseSerialize(serializers.ModelSerializer):
    """课程序列化"""
    level=serializers.CharField(source='get_level_display')
    class Meta:
        model = models.Course
        fields = ['pk','name', 'brief','level','course_img']

class CourseDetailSerialize(serializers.ModelSerializer):
    """课程详情序列化"""
    class Meta:
        model=models.CourseDetail
        fields=['']