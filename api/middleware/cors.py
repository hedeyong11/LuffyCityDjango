# coding:utf-8
# Created by yang
from django.shortcuts import HttpResponse
class MiddlewareMixin(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super(MiddlewareMixin, self).__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response

class CorsMiddleware(MiddlewareMixin):
    """用来给响应设置响应头,支持使其支持跨域"""
    def process_response(self,request,response):
        response['Access-Control-Allow-Origin'] = "*"
        response['Access-Control-Allow-Headers'] = "Content-Type,application/json"
        return response

    def process_request(self,request):
        """option方式直接返回,因为option方法不带来token,会导致认证失败"""
        if request.method=="OPTIONS":
            return HttpResponse()