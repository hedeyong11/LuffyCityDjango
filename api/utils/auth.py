# coding:utf-8
# Created by yang

from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from repository import models
import json
from rest_framework.views import APIView


# ################ 认证相关 ################
class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        tk = request.data.get('token')
        if not tk:
            tk = request.query_params.get('token')
        print('token:',tk)

        token_obj = models.Token.objects.filter(tk=tk).first()
        if token_obj:
            # (UserInfo对象,Token对象)
            return (token_obj.user,token_obj.tk)
        raise exceptions.AuthenticationFailed("认证失败")

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        # return 'Basic realm=api'
        pass

