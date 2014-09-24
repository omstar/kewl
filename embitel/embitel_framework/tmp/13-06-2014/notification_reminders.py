#!/home/embadmin/Documents/django_apps/django_experiments/bin/env python
import sys, os
sys.path.append(os.path.abspath('..'))
sys.path.append('/home/embadmin/Documents/django_apps/django_experiments/embitel')
sys.path.append('/home/embadmin/Documents/django_apps/django_experiments/embitel/embitel_framework')
import settings
import commands
import datetime

#from django.core.management import setup_environ
#setup_environ(settings)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "embitel_framework.settings")
from embitel_framework.models import Messages, APNSDevices, GCMDevices
from embitel_framework.views import get_model

today = datetime.datetime.today().date()


## messgate_type for Reminders is "reminder"

reminder_time = datetime.datetime.now().replace( second=0, microsecond=0)+datetime.timedelta(minutes=5)
messages = Messages.objects.filter(message_type='notification').filter(start_time=reminder_time)

print messages
for message_obj in messages:
    print message_obj.message
    if message_obj.apns_devices:
        device = message_obj.apns_devices
    else:
        device = message_obj.gcm_devices

    from_email = str(message_obj.from_email)
    email = str(device.email)
    message_id = str(message_obj.message_id)
    message_type = str(message_obj.message_type)
    
    if device.device_type == 'ios':
        COMMAND = """curl -X POST -u "%s:%s"   -H "Content-Type: application/json"   --data '''{"aps":{"alert":%s},"device_tokens": %s,"email":"%s", "from_email":"%s", "message_id":"%s"}'''    https://go.urbanairship.com/api/push/""" %(device.app_key, device.master_key, repr(message_obj.message), [str(device.registration_id)], email, from_email, message_id)

    else:
        COMMAND = """curl -X POST -u "%s:%s"   -H "Content-type: application/json" -H "Accept: application/vnd.urbanairship+json; version=3;" --data '''{"audience":{"apid" : "%s"}, "notification":{"alert" : %s, "android":{"extra":%s}},"device_types":["android"]}''' https://go.urbanairship.com/api/push/""" %(device.app_key, device.master_key, device.registration_id, repr(str(message_obj.message)), {"email":str(device.email), "from_email": str(message_obj.from_email), "message_id": str(message_obj.message_id), "message_type": "reminder", "start_time": str(message_obj.start_time), "end_time": str(message_obj.end_time), "subject": str(message_obj.message), "body": str(message_obj.body), "location": str(message_obj.location)})

    COMMAND = COMMAND.replace("\'","\"" ).replace("\"\"\"", '\'\'\'')
    print COMMAND
    result = commands.getoutput(COMMAND)
    print result


