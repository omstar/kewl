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

 
class Channels(models.Model):
    channel_id =  models.CharField(max_length=50, null=True, blank=True)
    channel_name =  models.CharField(max_length=50, null=True, blank=True)
    channel_pic =  models.CharField(max_length=200, null=True, blank=True)
    admin = models.EmailField('e-mail address', blank=True, null=True)
    channel_size = models.IntegerField('number of members', default=0)
    created_at = models.DateTimeField(auto_now = True,
                                           auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True,
                                           auto_now_add = True)

class APNSDevices(APNSDevice):
    #p12cer and
    unique_key = models.CharField("Unique key for app per device Eg: phone_num/email_id", max_length=50,
            blank = True, null=True) 
    unique_key_alias = models.CharField("Alias name for Unique key to display Eg: names", max_length=50,
            blank = True, null=True) 
    phone_number = models.CharField("phone number", max_length=50,
            blank = True, null=True) #For UrbanAirShip
    email = models.EmailField('e-mail address', blank=True, null=True)
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
    username = models.CharField(max_length=100, null=True, blank=True)
    pn_status = models.BooleanField("To set the settings for notifications (enable / disable)", default=True)
    #In any app, if unique key is opted then one has to verify their authentication and set the status
    auth_verified = models.BooleanField("This can be used if some one opt for unique key..", default=False)
    #channels = models.TextField(null=True, blank=True)
    friends = models.TextField('store friends emails', default="[]")
    pending_requests = models.TextField('store friends emails pending reqs', default="[]")
    status_message =  models.CharField(max_length=200, null=True, blank=True)
    dob = models.DateField("DOB", blank=True, null=True)
    channels = models.ManyToManyField(Channels)

    #TODO: p12_certificate and device id unique together?

class GCMDevices(GCMDevice):
    unique_key = models.CharField("Unique key for app per device Eg: phone_num/email_id", max_length=50,
            blank = True, null=True) 
    unique_key_alias = models.CharField("Alias name for Unique key to display Eg: names", max_length=50,
            blank = True, null=True) 
    phone_number = models.CharField("phone number", max_length=50,
            blank = True, null=True) #For UrbanAirShip
    email = models.EmailField('e-mail address', blank=True, null=True)

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
    username = models.CharField(max_length=100, null=True, blank=True)
    pn_status = models.BooleanField("To set the settings for notifications (enable / disable)", default=True)
    #In any app, if unique key is opted then one has to verify their authentication and set the status
    auth_verified = models.BooleanField("This can be used if some one opt for unique key..", default=False)
    #channels = models.TextField(null=True, blank=True)
    friends = models.TextField('store friends emails', default="[]")
    pending_requests = models.TextField('store friends emails pending reqs', default="[]")
    status_message =  models.CharField(max_length=200, default="Online")
    dob = models.DateField("DOB", blank=True, null=True)
    channels = models.ManyToManyField(Channels)
    #TODO: p12_certificate and device id unique together?


class Messages(models.Model):
    message = models.TextField(null=True, blank=True)
    message_id = models.CharField(max_length=100, null=True, blank=True)
    sent = models.BooleanField("To check message sent or not", default=False)
    delivered = models.BooleanField("To check message sent or not", default=False)
    from_phone_number = models.CharField(max_length=20, null=True, blank=True)
    from_email = models.EmailField('e-mail address', blank=True, null=True)

    apns_devices = models.ForeignKey(APNSDevices, null=True, blank=True)
    gcm_devices = models.ForeignKey(GCMDevices, null=True, blank=True)
    device_type = models.CharField(max_length=10, null=True, blank=True)
    message_type = models.CharField(max_length=20, default="message")
    start_time = models.DateTimeField("Event start time", null=True, blank=True)
    end_time = models.DateTimeField("Event end time", null=True, blank=True)
    subject = models.TextField("Event Subject line", null=True, blank=True)
    body = models.TextField("Content of the envent", null=True, blank=True)
    location = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now = True,
                                   auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True,
                                   auto_now_add = True)


class Groups(models.Model):
    phone_number = models.CharField("phone number", max_length=50,
            blank = True, null=True) 
    email = models.EmailField('e-mail address', blank=True, null=True)

    group_name =  models.CharField(max_length=50, null=True, blank=True)
    profile_pic =  models.CharField(max_length=200, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    installed = models.BooleanField("Installed or not", default=False)
    created_at = models.DateTimeField(auto_now = True,
                                           auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True,
                                           auto_now_add = True)
    dob = models.DateField("DOB", blank=True, null=True)
