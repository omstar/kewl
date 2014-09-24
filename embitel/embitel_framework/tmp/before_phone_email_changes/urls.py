from django.conf.urls import patterns, include, url

from django.contrib import admin
from settings import STATIC_ROOT
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'embitel_framework.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    # url(r'^login/', include('django.contrib.auth.urls')),
     url(r'^login/$', 'embitel_framework.views.reg_login', name='login'),
     url(r'^register/$', 'embitel_framework.views.register', name='registration'),
     url(r'^login/proc/$', 'embitel_framework.views.login_proc', name='login_proc'),
     url(r'^logout/$', 'embitel_framework.views.logout_view', name='logout'),
     url(r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root':STATIC_ROOT}),
     url(r'^embitel/upload_certificate/$', 'embitel_framework.views.upload_certificate', name='upload_certificate'),
     url(r'^embitel/generate_token/$', 'embitel_framework.views.generate_token', name='generate_token'),
     url(r'^embitel/vault/$', 'embitel_framework.views.vault', name='user vault'),
     url(r'^embitel/set_channels/$', 'embitel_framework.views.set_channels', name='Set channels/groups'),
     url(r'^embitel/urbanairship/set_channels/$', 'embitel_framework.views.urbanairship_set_channels', name='Set channels/groups'),
     url(r'^embitel/urbanairship/$', 'embitel_framework.views.urbanairship', name='urbanairship'),
     url(r'^embitel/urbanairship/register_device.*', 'embitel_framework.views.register_urbanairship_devices_get', name='register_urbanairship_devices'),
     url(r'^embitel/urbanairship/verify_user/$', 'embitel_framework.views.verify_user', name='verify_user'),
     url(r'^embitel/urbanairship/send_message/$', 'embitel_framework.views.send_PN_to_device', name='send PN to device'),
     url(r'^embitel/urbanairship/registered_users/$', 'embitel_framework.views.verify_registered_users', name='registered users for an app'),
     url(r'^embitel/urbanairship/set_status/$', 'embitel_framework.views.set_PN_status', name='set enabled/disabled PN status'),
     url(r'^embitel/store_devices/$', 'embitel_framework.views.store_devices', name='store_devices'),
     url(r'^embitel/push_notification/$', 'embitel_framework.views.push_notification', name='push_notification'),
     url(r'^embitel/configure_PN/(?P<encoded_key1>[\w=-]+)/', 'embitel_framework.views.configure_PN', name="Configure PN"),
     url(r'^embitel/PN/(?P<encoded_key1>[\w=-]+)/status/', 'embitel_framework.views.send_bulk_PN', name="send bulk PN"),
     url(r'^embitel/send_PN/', 'embitel_framework.views.send_bulk_PN', name="send bulk PN"),
     url(r'^embitel/set_profile_pic.*', 'embitel_framework.views.set_profile_pic', name="send bulk PN"),
     url(r'^testing.*', 'embitel_framework.views.testing', name="testing"),
     url(r'^admin/', include(admin.site.urls)),
)
