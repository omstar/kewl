from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from push_notifications.models import APNSDevice, GCMDevice
#from embitel_framework.models import P12Certificate

class P12Certificate(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    path = models.CharField(max_length=200, unique=True)
    app_name = models.CharField(max_length=100, null=True, blank=True)
    p12_password = models.CharField(max_length=100, null=True, blank=True)
    pem_file = models.CharField(max_length=200, null=True, blank=True)
    emb_token =  models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now = True,
                                   auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True,
                                   auto_now_add = True)
    spare_1 =  models.CharField(max_length=50, null=True, blank=True)
    spare_2 =  models.CharField(max_length=50,   null=True, blank=True)
    class Meta:
        unique_together = (('user', 'app_name'),)

class GCMApiKey(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    app_name = models.CharField(max_length=100, null=True, blank=True)
    api_key = models.CharField(max_length=100, null=True, blank=True)
    emb_token =  models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now = True,
                                   auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True,
                                   auto_now_add = True)
    spare_1 =  models.CharField(max_length=50, null=True, blank=True)
    spare_2 =  models.CharField(max_length=50,   null=True, blank=True)
    class Meta:
        unique_together = (('user', 'app_name'),)


class APNSDevices(APNSDevice):
    #p12cer and
    unique_key = models.CharField("Unique key for app per device Eg: phone_num/email_id", max_length=50,
            blank = True, null=True) 
    unique_key_alias = models.CharField("Alias name for Unique key to display Eg: names", max_length=50,
            blank = True, null=True) 
    phone_number = models.CharField("phone number", max_length=50,
            blank = True, null=True) #For UrbanAirShip
    device_type =  models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now = True,
                                           auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True,
                                           auto_now_add = True)
    p12_certificate = models.ForeignKey(P12Certificate, null=True, blank=True)
    # app_key and master_key are created only for urban airship purpose
    app_key =  models.CharField(max_length=200, null=True, blank=True)
    master_key =  models.CharField(max_length=200, null=True, blank=True)
    profile_pic =  models.CharField(max_length=200, null=True, blank=True)
    pn_status = models.BooleanField("To set the settings for notifications (enable / disable)", default=True)
    #In any app, if unique key is opted then one has to verify their authentication and set the status
    auth_verified = models.BooleanField("This can be used if some one opt for unique key..", default=False)
    channels = models.TextField(null=True, blank=True)
    #TODO: p12_certificate and device id unique together?

class GCMDevices(GCMDevice):
    unique_key = models.CharField("Unique key for app per device Eg: phone_num/email_id", max_length=50,
            blank = True, null=True) 
    unique_key_alias = models.CharField("Alias name for Unique key to display Eg: names", max_length=50,
            blank = True, null=True) 
    phone_number = models.CharField("phone number", max_length=50,
            blank = True, null=True) #For UrbanAirShip
    device_type =  models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now = True,
                                           auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True,
                                           auto_now_add = True)
    api_key = models.ForeignKey(GCMApiKey, null=True, blank=True)
    gcm_device_id = models.CharField("device id given by gcm only for android", max_length=200, null=True, blank=True)
    # app_key and master_key are created only for urban airship purpose
    app_key =  models.CharField(max_length=200, null=True, blank=True)
    master_key =  models.CharField(max_length=200, null=True, blank=True)
    profile_pic =  models.CharField(max_length=200, null=True, blank=True)
    pn_status = models.BooleanField("To set the settings for notifications (enable / disable)", default=True)
    #In any app, if unique key is opted then one has to verify their authentication and set the status
    auth_verified = models.BooleanField("This can be used if some one opt for unique key..", default=False)
    channels = models.TextField(null=True, blank=True)
    #TODO: p12_certificate and device id unique together?

