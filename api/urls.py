
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^(?P<version>\w+)/auth/$', views.AuthView.as_view()),
    url(r'^(?P<version>\w+)/course/$', views.CourseView.as_view()),
    url(r'^(?P<version>\w+)/course/(?P<pk>\d+)/$', views.CourseView.as_view()),
    url(r'^(?P<version>\w+)/add_shopping_cart/$', views.AddShoppingCartView.as_view()),
    url(r'^(?P<version>\w+)/settlement/$', views.SettlementView.as_view()),#结算
]
