
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^(?P<version>\w+)/auth/$', views.AuthView.as_view()),
    url(r'^(?P<version>\w+)/course/$', views.CourseView.as_view()),
    url(r'^(?P<version>\w+)/course_detail/(?P<pk>\d+)$', views.CourseDetailView.as_view()),
]
