import time

from django.shortcuts import HttpResponse
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from repository import models
from utils import common
from .utils.serialize import CourseSerialize


class AuthView(APIView):
    parser_classes = [JSONParser, ]

    def post(self, request, *args, **kwargs):
        print(request.data)
        response = {"status": True, "msg": None, "code": 1000}
        username = request.data.get("username")
        password = request.data.get("password")
        # password = common.hash_str(username,password)
        user_obj = models.User.objects.filter(username=username, password=password).first()
        if not user_obj:
            response['status'] = False
            response['msg'] = "用户名或密码错误"
            response['code'] = 1001
        else:
            tk = common.hash_str(username, time.time())
            models.Token.objects.update_or_create(user=user_obj, defaults={"tk": tk})
            response['token'] = tk
            response['username'] = username

        # response['Access-Control-Allow-Headers'] = "Content-Type,application/json"
        # import json
        # response = HttpResponse(json.dumps(response))
        # response['Access-Control-Allow-Origin'] = "*"
        return Response(response)

    def options(self, *args, **kwargs):
        # response = HttpResponse()
        # response['Access-Control-Allow-Origin']="*"
        # response['Access-Control-Allow-Headers']= "Content-Type,application/json"

        # response.('Access-Control-Allow-Origin', "http://www.xxx.com")
        # self.set_header('Access-Control-Allow-Headers', "k1,k2")
        # self.set_header('Access-Control-Allow-Methods', "PUT,DELETE")
        # self.set_header('Access-Control-Max-Age', 10)
        return HttpResponse()


def test(request):
    # models.UserInfo.objects.create(username="yang",password=make_password("123"))
    from django.shortcuts import HttpResponse
    # models.UserInfo.objects.create(username="yang",password=common.hash_str("yang","123"))

    return HttpResponse("xxx")


class CourseView(APIView):
    def get(self, request, *args, **kwargs):
        course_list = models.Course.objects.all()
        ser = CourseSerialize(instance=course_list, many=True, context={'request': request})
        # print(ser.data)
        return Response(ser.data)


class CourseDetailView(APIView):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        course_obj = models.Course.objects.filter(pk=pk).first()
        course_detail_obj = course_obj.coursedetail
        # print(course_detail_obj)
