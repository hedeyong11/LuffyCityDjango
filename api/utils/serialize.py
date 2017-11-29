# coding:utf-8
# Created by yang

##序列化
from rest_framework import serializers
from repository import models


class CourseSerialize(serializers.ModelSerializer):
    """课程序列化"""
    level = serializers.CharField(source='get_level_display')
    price_policies = serializers.SerializerMethodField()

    class Meta:
        model = models.Course
        fields = ['pk', 'name', 'brief', 'level', 'course_img','price_policies']

    def get_price_policies(self, obj):
        policies = obj.price_policy.all()
        ret = []
        for i in policies:
            d = {}
            d['pk'] = i.pk
            d['valid_period'] = i.get_valid_period_display()
            d['price'] = i.price
            ret.append(d)
        return ret


class CourseDetailSerialize(serializers.ModelSerializer):
    """课程详情序列化"""
    name = serializers.CharField(source='course.name')
    level = serializers.CharField(source='course.get_level_display')
    recommend_courses = serializers.SerializerMethodField()
    teachers = serializers.SerializerMethodField()
    outlines = serializers.SerializerMethodField()
    questions = serializers.SerializerMethodField()
    price_policies = serializers.SerializerMethodField()  # 价格策略
    chapters = serializers.SerializerMethodField()  # 章节

    class Meta:
        model = models.CourseDetail
        fields = ['pk','name', 'course_slogan', 'level', 'hours',
                  'video_brief_link', 'summary', 'why_study',
                  'what_to_study_brief', 'career_improvement',
                  'prerequisite', 'recommend_courses', 'teachers',
                  'outlines', 'questions', 'price_policies','chapters',
                  ]

    def get_recommend_courses(self, obj):
        ret = []
        courses = obj.recommend_courses.all()
        for i in courses:
            d = {}
            d['pk'] = i.pk
            d['name'] = i.name
            ret.append(d)
        return ret

    def get_teachers(self, obj):
        ret = []
        teachers = obj.teachers.all()
        for i in teachers:
            d = {}
            d['pk'] = i.pk
            d['name'] = i.name
            d['title'] = i.title
            d['image'] = i.image
            d['brief'] = i.brief
            ret.append(d)
        return ret

    def get_outlines(self, obj):
        ret = []
        outlines = obj.courseoutline_set.all()
        for i in outlines:
            d = {}
            d['pk'] = i.pk
            d['title'] = i.title
            d['order'] = i.order
            d['content'] = i.content
            ret.append(d)
        return ret

    def get_questions(self, obj):
        questions = obj.course.questions.all()
        ret = []
        for i in questions:
            d = {}
            d['pk'] = i.pk
            d['question'] = i.question
            d['answer'] = i.answer
            ret.append(d)
        return ret

    def get_price_policies(self, obj):
        policies = obj.course.price_policy.all()
        ret = []
        for i in policies:
            d = {}
            d['pk'] = i.pk
            d['valid_period'] = i.get_valid_period_display()
            d['price'] = i.price
            ret.append(d)
        return ret

    def get_chapters(self, obj):
        chapters = obj.course.coursechapters.all()
        ret = []
        for chapter in chapters:
            d = {}
            d['pk'] = chapter.pk
            d["order"] = chapter.chapter
            d["name"] = chapter.name
            d["summary"] = chapter.summary
            d["pub_date"] = chapter.pub_date
            sections = chapter.coursesections.all()#章节目录
            sections_list=[]
            for section in sections:
                section_dict={}
                section_dict['pk']=section.pk
                section_dict['name']=section.name
                section_dict['order']=section.order
                section_dict['section_type']=section.get_section_type_display()
                section_dict['section_link']=section.section_link
                section_dict['video_time']=section.video_time
                section_dict['pub_date']=section.pub_date
                section_dict['free_trail']=section.free_trail
                sections_list.append(section_dict)
            d["sections"] = sections_list
            ret.append(d)
        return ret



