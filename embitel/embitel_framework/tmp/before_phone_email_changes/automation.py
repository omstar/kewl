#!/home/embadmin/Documents/django_apps/django_experiments/bin/env python
import sys, os
sys.path.append(os.path.abspath('..'))
sys.path.append('/home/embadmin/Documents/django_apps/django_experiments/embitel')
sys.path.append('/home/embadmin/Documents/django_apps/django_experiments/embitel/embitel_framework')
import settings
import commands
#from django.core.management import setup_environ
#setup_environ(settings)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "embitel_framework.settings")
from embitel_framework.models import Messages, APNSDevices, GCMDevices

messages = Messages.objects.filter(sent=True, delivered=False)
import datetime
f = open('/tmp/abcom.txt', 'a')
f.write("%s\n" %(str(datetime.datetime.now())))
for message_obj in messages:
    print message_obj.message
    if message_obj.apns_devices:
        device = message_obj.apns_devices
    else:
        device = message_obj.gcm_devices

    from_phone_number = str(message_obj.from_phone_number)
    phone_number = str(device.phone_number)
    message_id = str(message_obj.message_id)

    if device.device_type == 'ios':
        COMMAND = """curl -X POST -u "%s:%s"   -H "Content-Type: application/json"   --data '''{"aps":{"alert":"%s"},"device_tokens": %s,"phone_number":"%s", "from_phone_number":"%s", "message_id":"%s"}'''    https://go.urbanairship.com/api/push/""" %(device.app_key, device.master_key, message_obj.message, [str(device.registration_id)], phone_number, from_phone_number, message_id)
    else:
        COMMAND = """curl -X POST -u "%s:%s"   -H "Content-type: application/json" -H "Accept: application/vnd.urbanairship+json; version=3;" --data '''{"audience":{"apid" : "%s"}, "notification":{"alert" : "%s", "android":{"extra":%s}},"device_types":["android"]}''' https://go.urbanairship.com/api/push/""" %(device.app_key, device.master_key, device.registration_id, message_obj.message, {"phone_number":"%s" %phone_number, "from_phone_number":from_phone_number, "message_id": message_id})
    COMMAND = COMMAND.replace("\'","\"" ).replace("\"\"\"", '\'\'\'')
    print COMMAND
    result = commands.getoutput(COMMAND)
    print result 
    print "\n"
print len(messages)       

f.write("%s\n\n" %(len(messages)))
f.close()
