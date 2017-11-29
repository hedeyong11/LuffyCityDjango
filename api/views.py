import time

from django.shortcuts import HttpResponse
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from repository import models
from utils import common
from .utils.serialize import CourseSerialize, CourseDetailSerialize


class AuthView(APIView):
    parser_classes = [JSONParser, ]

    def post(self, request, *args, **kwargs):
        print(request.data)
        response = {"status": True, "msg": None, "code": 1000}
        username = request.data.get("username")
        password = request.data.get("password")
        # password = common.hash_str(username,password)
        user_obj = models.Account.objects.filter(username=username, password=password).first()
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
        response = {'code': 1000, 'msg': None, 'data': None}
        try:
            pk = kwargs.get('pk')
            if pk:
                course_detail_obj = models.CourseDetail.objects.filter(course_id=pk).first()
                ser = CourseDetailSerialize(instance=course_detail_obj, many=False)
            else:
                course_list = models.Course.objects.all()
                ser = CourseSerialize(instance=course_list, many=True, context={'request': request})
            # print(ser.data)
            response['data'] = ser.data
        except Exception as e:
            response['code'] = 1001
            response['msg'] = '课程详情获取失败,请检查日志'
            print(str(e))

        return Response(response)


class AddShoppingCartView(APIView):
    """加入购物车"""

    def post(self, request, *args, **kwargs):
        '自己实现'
        # response = {'code': 1000, 'msg': None, }
        # course_detail_pk = request.data.get('course_detail_pk')
        # policy_pk = request.data.get('policy_pk')
        # user_token = request.data.get('token')
        # user_obj = models.Token.objects.filter(tk=user_token).first().user
        #
        # print(course_detail_pk, policy_pk, user_token)
        #
        # course_detail_obj = models.CourseDetail.objects.filter(pk=course_detail_pk).first()
        # course_obj = course_detail_obj.course
        #
        # if course_obj.status != 0:
        #     response['msg'] = '课程不在线'
        #     response['code'] = 1001
        #     return Response(response)
        #
        # policy_obj = course_obj.price_policy.filter(pk=policy_pk).first()
        # if not policy_obj:
        #     response['msg'] = '当前价格策略与所选课程不匹配'
        #     response['code'] = 1002
        #     return Response(response)
        #
        # ser = CourseSerialize(instance=course_obj, many=False)
        # tmp = ser.data
        # tmp['selected_policy_id'] = policy_pk
        #
        # # 保存到cookie
        # if user_obj.uid not in request._request.session:
        #     info_dict = {'shopping_cart': None}
        #     goods_list = []
        #     goods_list.append(tmp)
        #     info_dict['shopping_cart'] = goods_list
        #     request._request.session[user_obj.uid] = info_dict
        # else:
        #     goods_list = request._request.session[user_obj.uid]['shopping_cart']
        #     goods_obj = check_if_goods_in_shopping_cart(goods_list, course_obj.pk)
        #     if goods_obj:
        #         #信息更新
        #         goods_obj['selected_policy_id']=policy_pk
        #     else:
        #         #新增商品
        #         request._request.session[user_obj.uid]['shopping_cart'].append(tmp)
        #
        # print(request._request.session[user_obj.uid]['shopping_cart'])
        return Response('xxx')


def check_if_goods_in_shopping_cart(goods_list, pk):
    """
    检查pk所对应的商品是否session中的购物车中
    :param goods_list: 
    :param pk: 
    :return: obj,已经存在,并将该对象返回,False,不存在
    """
    for goods in goods_list:
        if goods['pk'] == pk:
            return goods
    return False
