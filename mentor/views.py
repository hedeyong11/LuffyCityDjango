from django.shortcuts import render, redirect, HttpResponse
from repository import models as repository_models
from rbac.service.rbac import initial_permission

def login(request):
    if request.method == "GET":
        return render(request, "login.html")
    elif request.method == "POST":
        username = request.POST.get("username")
        pwd = request.POST.get("pwd")
        # print("___cookie",request.COOKIES)
        obj = repository_models.Account.objects.filter(username=username, password=pwd).first()
        if obj:
            # 初始化权限
            request.session["user_info"] = {"nid": obj.id}
            print(request.session["user_info"])
            initial_permission(request, obj)

            return redirect('/admin/index/')
        else:
            return render(request, "login.html")


def logout(request):
    request.session["user_info"] = None
    return redirect("/admin/login/")

def index(request):
    return render(request, "index.html")
