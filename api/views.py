import time
import json
import math

from django.shortcuts import HttpResponse
from django.conf import settings
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from repository import models
from utils import common
from utils.redis import redis
from .utils.serialize import CourseSerialize, CourseDetailSerialize
from .utils.auth import CustomAuthentication


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

            # 初始化用户的购物车,本应该在注册的时候就初始化
            res = redis.hset(settings.LUFFY_CART, user_obj.uid, "{}")

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
    authentication_classes = [CustomAuthentication, ]  # 增加认证

    def post(self, request, *args, **kwargs):
        '自己实现'
        response = {'code': 1000, 'msg': None, }
        course_detail_pk = request.data.get('course_detail_pk')
        policy_pk = request.data.get('policy_pk')
        user_obj = request.user

        print(course_detail_pk, policy_pk, user_obj.username)

        course_detail_obj = models.CourseDetail.objects.filter(pk=course_detail_pk).first()
        course_obj = course_detail_obj.course

        if course_obj.status != 0:
            response['msg'] = '课程不在线'
            response['code'] = 1001
            return Response(response)

        policy_obj = course_obj.price_policy.filter(pk=policy_pk).first()
        if not policy_obj:
            response['msg'] = '当前价格策略与所选课程不匹配'
            response['code'] = 1002
            return Response(response)

        ser = CourseSerialize(instance=course_obj, many=False)
        tmp = ser.data
        tmp['selected_policy_id'] = policy_pk
        tmp['selected_policy_price'] = policy_obj.price

        # 更新或添加商品到购物车
        update_or_add_shopping_cart(user_obj, tmp)

        cart_info = redis.hget(settings.LUFFY_CART, user_obj.uid)
        cart_info = json.loads(cart_info.decode('utf-8'))
        response['data'] = cart_info

        return Response(response)

    def get(self, request, *args, **kwargs):
        """获取购物车信息"""
        response = {'code': 1000, 'msg': None, }
        try:
            cart_info = redis.hget(settings.LUFFY_CART, request.user.uid)
            res = json.loads(cart_info.decode('utf-8'))
            print(res)
            response['data'] = res
        except Exception as e:
            response['msg'] = '获取购物车信息失败,请检查日志'
            response['code'] = 1001
        return Response(response)

    def delete(self, request, *args, **kwargs):
        """删除购物车中的商品"""
        response = {'code': 1000, 'msg': None, }
        try:
            cart_info = redis.hget(settings.LUFFY_CART, request.user.uid)
            cart_info = json.loads(cart_info.decode('utf-8'))
            course_id = request.data.get('course_id')
            cart_info.pop(course_id)

            # print(cart_info)

            # 重新写回redis
            redis.hset(settings.LUFFY_CART, request.user.uid, json.dumps(cart_info, ensure_ascii=False))
        except Exception as e:
            print(str(e))
            response['msg'] = '删除商品失败,请检查日志'
            response['code'] = 1001

        return Response(response)

    def options(self, request, *args, **kwargs):
        return Response()


def update_or_add_shopping_cart(user_obj, goods_dict):
    """
    更新或添加商品到购物车
    :param user_obj: 
    :param goods_dict: 
    :return: 
    """
    goods_pk = goods_dict.get('pk')
    cart_info = redis.hget(settings.LUFFY_CART, user_obj.uid)
    cart_info = json.loads(cart_info.decode('utf-8'))
    if not isinstance(cart_info, dict):
        cart_info = {}

    if goods_pk in cart_info:
        # 策略更换下
        cart_info.get(goods_pk)['selected_policy_id'] = goods_dict['selected_policy_id']
    else:
        # 新增商品
        cart_info[goods_pk] = goods_dict

    redis.hset(settings.LUFFY_CART, user_obj.uid, json.dumps(cart_info, ensure_ascii=False))


class SettlementView(APIView):
    """结算,需对用户提交的数据进行验证,验证通过后,返回立即跳转到支付页面"""
    authentication_classes = [CustomAuthentication, ]  # 增加认证

    def post(self, request, *args, **kwargs):
        response = {'code': 1000, 'msg': None, }

        if not self.validate():
            response['msg'] = self.error_msg
            response['code'] = self.error_code
        final_price = self.calc_price()
        print("原始价格",self.original_price)
        # print("锁定贝里",self.locked_bely)
        print("最终价格",final_price)

        # print(request.data)
        return Response(response)

    def calc_price(self):
        """计算价格"""
        self.original_price = self.policy_obj.price

        self.course_coupon_translate(self.original_price)

        if not self.course_coupon_record_id and not self.global_coupon_record_id:
            # 不使用优惠券
            if not self.use_bely:
                # 不使用贝里
                print('不使用优惠券 不使用贝里')
                return self.original_price
            else:
                print("不使用优惠券 使用贝里")
                return self.bely_translate(self.original_price)
        else:
            #使用优惠券
            if not self.course_coupon_record_id:
                print("使用全局优惠券")
                return self.global_coupon_translate(self.original_price)

    def course_coupon_translate(self,price):
        """
        开始课程优惠券计算
        :param price: 
        :return: 
        """
        if not self.course_coupon_record_id:
            print("开始课程优惠券计算:无课程优惠券")
            return price

        coupon_record_obj = models.CouponRecord.objects.filter(id=self.course_coupon_record_id).first()
        coupon_obj = coupon_record_obj.coupon
        self.locked_course_coupon = coupon_obj


        return self.coupon_translate(price, coupon_obj)

    def global_coupon_translate(self,price):
        """
        开始全局优惠券计算
        :param price: 交易前的价格
        :return: 
        """
        if not self.global_coupon_record_id:
            print("开始全局优惠券计算:无全局优惠券")
            return price
        coupon_record_obj = models.CouponRecord.objects.filter(id=self.global_coupon_record_id).first()
        coupon_obj = coupon_record_obj.coupon
        self.locked_globel_coupon = coupon_obj

        return self.coupon_translate(price, coupon_obj)


    def coupon_translate(self,price,coupon_obj):
        """
        开始优惠券计算
        :param price: 计算前价格
        :param coupon_record_id: 优惠券记录id
        :return: 
        """
        type_and_func={0:self.all_coupon_exec,1:self.full_cut_coupon_exec,2:self.discount_coupon_exec}

        price_after_coupon = type_and_func.get(coupon_obj.coupon_type)(coupon_obj,price) #优惠券之后的价格

        return price_after_coupon


    def all_coupon_exec(self,coupon_obj,price):
        """进入通用优惠券计算"""
        if coupon_obj.money_equivalent_value>price:
            print('通用优惠券计算:优惠券面值%s,全部使用优惠券结算'%coupon_obj.money_equivalent_value)
            return 0
        else:
            print('通用优惠券计算:优惠券面值%s,使用优惠券抵扣该金额' % coupon_obj.money_equivalent_value)
            return price-coupon_obj.money_equivalent_value


    def full_cut_coupon_exec(self,coupon_obj,price):
        """进入满优惠券计算"""
        if price<coupon_obj.minimum_consume:
            print('进入满减优惠券计算:价格未达到满减需求,优惠券解除锁定')
            self.locked_coupon=None
            return price
        else:
            if coupon_obj.money_equivalent_value > price:#针对满300减400这种变态优惠券
                print('进入满减优惠券计算:优惠券面值%s,全部使用优惠券结算' % coupon_obj.money_equivalent_value)
                return 0
            else:
                print('进入满减优惠券计算:优惠券面值%s,使用优惠券抵扣该金额' % coupon_obj.money_equivalent_value)
                return price - coupon_obj.money_equivalent_value

    def discount_coupon_exec(self,coupon_obj,price):
        """进入折扣惠券计算"""
        print('进入折扣惠券计算:优惠券折扣%s折' % (coupon_obj.off_percent/10))
        return price*coupon_obj.off_percent/100

    def bely_translate(self, price):
        """
        使用贝里交易,需注意,该交易默认会使用全部的贝里,
        :param price: 使用贝里交易前的价格
        :return: 
        """
        # 获取用户贝里账号余额
        bely_account = self.request.user.transactionrecord_set.order_by("date").reverse().first()
        if bely_account:
            if bely_account.balance / 10 > price:
                print('全部使用贝里支付')
                self.locked_bely = math.ceil(price * 10)#用于将类似于33.45元转换为334.5贝里进一到335贝里
                return 0
            else:
                self.locked_bely=bely_account.balance
                print("使用贝里支付%s" % (bely_account.balance / 10))
                return price - bely_account.balance / 10
        else:
            self.locked_bely = 0
            print("无贝里")
            return price

    def validate(self):
        """开始验证,检查用户提交的数据是否有效,防止爬虫或非法提交"""
        if not self.get_info_from_request():
            return False
        # request = self.request
        # course_id = request.data.get('course_id')
        # selected_policy_id = request.data.get('selected_policy_id')
        # course_coupon_record_id = request.data.get('course_coupon_record_id')
        # global_coupon_record_id = request.data.get('global_coupon_record_id')
        # self.course_id = course_id
        # print("course_id", course_id)
        # print("selected_policy_id", selected_policy_id)
        # print("course_coupon_record_id", course_coupon_record_id)
        # print("global_coupon_record_id", global_coupon_record_id)

        # 课程状态检查
        self.course_obj = models.Course.objects.filter(id=self.course_id).first()
        if self.course_obj.status != 0:
            self.error_msg = '课程未上线'
            self.error_code = 1001
            return False

        # 课程所选价格策略检查
        self.policy_obj = self.course_obj.price_policy.filter(id=self.selected_policy_id).first()
        if not self.policy_obj:
            self.error_msg = '课程所选价格策略错误'
            self.error_code = 1002
            return False

        # 优惠券检查(含课程优惠券和全局优惠券)
        if self.validate_coupon(self.course_coupon_record_id):  # 优惠券1验证通过后再验证优惠券2
            return self.validate_coupon(self.global_coupon_record_id)

    def get_info_from_request(self):
        """从request中获取并验证数据"""
        request = self.request
        course_id = request.data.get('course_id')
        if not isinstance(course_id, int):
            self.error_msg = '课程id非int型错误'
            self.error_code = 1007
            return False

        selected_policy_id = request.data.get('selected_policy_id')
        if not isinstance(selected_policy_id, int):
            self.error_msg = '价格策略id非int型错误'
            self.error_code = 1008
            return False

        course_coupon_record_id = request.data.get('course_coupon_record_id')
        if course_coupon_record_id and not isinstance(course_coupon_record_id, int):
            self.error_msg = '课程优惠券记录id非int型错误'
            self.error_code = 1009
            return False

        global_coupon_record_id = request.data.get('global_coupon_record_id')
        if global_coupon_record_id and not isinstance(global_coupon_record_id, int):
            self.error_msg = '全局优惠券记录id非int型错误'
            self.error_code = 1010
            return False

        use_bely = request.data.get('use_bely')
        if not isinstance(use_bely, bool):
            self.error_msg = '是否使用贝里非bool型错误'
            self.error_code = 1010
            return False

        self.course_id, self.selected_policy_id, self.course_coupon_record_id, self.global_coupon_record_id, self.use_bely = course_id, selected_policy_id, course_coupon_record_id, global_coupon_record_id, use_bely
        return True

    def validate_coupon(self, coupon_record_id):
        """
        验证优惠券是否合法
        :param coupon_record_id: 优惠券发放记录id
        :return: 
        """
        if not coupon_record_id:  # 说明无此类型的优惠券
            return True
        coupon_record_obj = models.CouponRecord.objects.filter(id=coupon_record_id).first()
        if not coupon_record_obj:
            self.error_msg = '所选优惠券记录并不存在,或许并未领取'
            self.error_code = 1003
            return False

        if coupon_record_obj.status != 0:
            self.error_msg = '优惠券无法使用,已过期或已经使用'
            self.error_code = 1004
            return False

        if coupon_record_obj.account.id != self.request.user.id:
            self.error_msg = '用户无此优惠券'
            self.error_code = 1005
            return False

        if coupon_record_obj.coupon.content_object:  # 优惠券,绑定了课程,否则是全局优惠券
            if coupon_record_obj.coupon.content_object.id != self.course_id:
                self.error_msg = '优惠券与所选课程不匹配'
                self.error_code = 1006
                return False

        return True  # 该优惠券信息正常

    def xxx(self):
        pass
