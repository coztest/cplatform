from django.conf.urls import patterns, include, url
from django.contrib import admin
from cp import views
urlpatterns = patterns('',
    # Examples:
     url(r'^$', views.index),
    # url(r'^blog/', include('blog.urls')),
     url(r'^login$', views.login),
#    url(r'^admin/', include(admin.site.urls)),
     url(r'^mainpage$', views.mainpage),
     url(r'^upload1/(\d+)$',views.upload1),
     url(r'^webterm1/(\d+)$',views.webterm1),
     url(r'^newproj$',views.newproj),

    url(r'^echo$',views.echo),

)
