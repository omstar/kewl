#from django.template.loader import get_template
#from django.template import Context
from django.http import HttpResponse
import datetime

#from django.template import  loader
#from django.shortcuts import render_to_response
#from registration.models import Registration
#from django.template import RequestContext
#from django.shortcuts import redirect

import json
from django.views.decorators.csrf import csrf_exempt

from push_notifications.models import APNSDevice, GCMDevice
import commands

@csrf_exempt
def push_notification(request):
    if request.method == 'POST':
        data = request.body
    '''
    device = GCMDevice.objects.get(registration_id=gcm_reg_id)
    device.send_message({"foo": "bar"}) # The message will be sent and received as json.
    '''
    #device = APNSDevice.objects.get(registration_id=apns_token)
    device = APNSDevice.objects.all().latest('id')
    device.send_message("Mr Uttam elected as CM candidate!") # The message may only be sent as text.

    result = {'result': 'successfully sent the push notification!'}
    return HttpResponse(json.dumps(result), content_type='application/json')
    #return HttpResponse(str({'a': 5}), content_type="text/plain")

@csrf_exempt
def urbanairship(request, *args, **kwargs):
    result = ''
    if request.body:
        data = eval(request.body)
        app_id = data['app_id']
        key = data['key']
        device_tokens = data['device_tokens']
        message = data['message']
    #output = commands.getoutput('''curl -X POST -u "3gutVRHDQ0O25Hlu2wc9lg:Vg5Y0DtOTPubQLAgZet5yQ"   -H "Content-Type: application/json"   --data '{"device_tokens": ["8C85A4ADD9947FF507158251A4A639084E9F8F6BF5260433D148257A625EBD85"], "aps": {"alert": "Hello!"}}'    https://go.urbanairship.com/api/push/''')
        COMMAND = """curl -X POST -u "%s:%s"   -H "Content-Type: application/json"   --data '''{"device_tokens": %s, "aps": {"alert": "%s"}}'''    https://go.urbanairship.com/api/push/""" %(app_id, key, str(device_tokens), message)
        COMMAND = COMMAND.replace("\'","\"" ).replace("\"\"\"", '\'\'\'')

        result = commands.getoutput(COMMAND)
    result = {'result': result} 
    return HttpResponse(json.dumps(result), content_type='application/json')
