from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'embitel_framework.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
     url(r'^embitel/urbanairship/$', 'embitel_framework.views.urbanairship', name='urbanairship'),
     url(r'^embitel/push_notification/$', 'embitel_framework.views.push_notification', name='push_notification'),
     url(r'^admin/', include(admin.site.urls)),
)
