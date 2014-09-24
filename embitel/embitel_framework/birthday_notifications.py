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

start_date = ''#datetime.datetime(today.year, today.month, today.day, 23, 59)

def send_bday_PN(device, bday_user):
    if device.device_type == 'android':
        COMMAND = """curl -X POST -u "%s:%s"   -H "Content-type: application/json" -H "Accept: application/vnd.urbanairship+json; version=3;" --data '''{"audience":{"apid" : "%s"}, "notification":{"alert" : "%s", "android":{"extra":%s}},"device_types":["android"]}''' https://go.urbanairship.com/api/push/""" %(device.app_key, device.master_key, device.registration_id, "Birthday Reminder!!!", {"email":str(device.email), "from_email": '', "message_id": '', "message_type": "notification", "start_time":str(start_date),  "end_time": str(start_date), "subject": "Birthday Reminder!", "body": str("Todays Birthday: %0A%0A" + bday_user.username + "%0A%0AWish your friend a very Happy Birthday!"), "location": ""})
        COMMAND = COMMAND.replace("\'","\"" ).replace("\"\"\"", '\'\'\'')
        print COMMAND
        result = commands.getoutput(COMMAND)
        print result 


android_users = GCMDevices.objects.filter(dob__month=today.month, dob__day=today.day)
for android_user in android_users:
    friends = eval(android_user.friends)
    for friend_email in friends:
        model = get_model(email=friend_email)
        device = model.objects.get(email=friend_email)
        send_bday_PN(device, android_user)

    if android_user.device_type == 'android':
        device = android_user
        COMMAND = """curl -X POST -u "%s:%s"   -H "Content-type: application/json" -H "Accept: application/vnd.urbanairship+json; version=3;" --data '''{"audience":{"apid" : "%s"}, "notification":{"alert" : "%s", "android":{"extra":%s}},"device_types":["android"]}''' https://go.urbanairship.com/api/push/""" %(device.app_key, device.master_key, device.registration_id, "Happy Birthday %s!"%str(android_user.username), {"email":str(device.email), "from_email": '', "message_id": '', "message_type": "notification", "start_time":str(start_date),  "end_time": str(start_date), "subject": "Happy Birthday %s!"%str(android_user.username), "body": str("Embitel Wishing you Many more Happy returns of the day :) Have a blast!"), "location": ""})

        COMMAND = COMMAND.replace("\'","\"" ).replace("\"\"\"", '\'\'\'')
        print COMMAND
        result = commands.getoutput(COMMAND)
        print result

