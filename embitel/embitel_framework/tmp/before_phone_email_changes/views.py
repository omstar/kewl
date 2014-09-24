import os
import string
from random import choice
#from django.template.loader import get_template
#from django.template import Context
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import datetime

from django.template import  loader
#from django.shortcuts import render_to_response
#from registration.models import Registration
from django.template import RequestContext
from django.shortcuts import render_to_response

import json
from django.views.decorators.csrf import csrf_exempt

from push_notifications.models import APNSDevice, GCMDevice
from embitel_framework.models import P12Certificate, APNSDevices, GCMDevices, Messages
import commands

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, AnonymousUser

from forms import LoginForm, UploadP12Certificate, RegistrationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.cache import cache_control
from settings import PROFILE_PICS_PATH

TESTING = True
MESSAGE_EXPIRY = 50

class InputDataException (Exception):
    def __init__ (self, str=None):
        self.error = str
        return

def reg_login(request):
    return render_to_response('login.html')

@csrf_exempt
@cache_control(no_store=True, no_cache=True, must_revalidate=True,)
def login_proc(request):
    email = request.POST['email']
    password = request.POST['password']

    form_data = request.POST.copy()
    
    form = LoginForm(form_data)
    errors = form.errors
    if errors:
        return render_to_response('login.html', {'form': form})
    try:
        user = User.objects.get(email=email)
    except:
        return render_to_response('login.html', {'form': form})
    user = authenticate(username=email, password=password)
    login(request, user)
    response =  HttpResponseRedirect('/embitel/upload_certificate/')
    #response.set_cookie("generate_token", True)
    return response

from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/login/')
    # Redirect to a success page.

@csrf_exempt
@cache_control(no_store=True, no_cache=True, must_revalidate=True,)
def register(request):

    form_data = request.POST.copy()
    
    form = RegistrationForm(form_data)
    errors = form.errors
    print request.POST
    print form.errors
    if errors:
        return render_to_response('login.html', {'form': form})

    # logout the existing user
    if (isinstance (request.user, AnonymousUser)):
        u = None
    else:
        u = request.user
        logout(request)

    email = request.POST['register_email']
    password = request.POST['register_password']

    try:
        u = User(username=email)
        u.set_password(password)
        u.email = email
        u.save()
    except:
        return render_to_response('login.html', {'form': form})
    response = render_to_response('login.html', {'registration_status': "Registered successfully! Now you can login with your credentials!" })
    return response


@login_required
@cache_control(no_store=True, no_cache=True, must_revalidate=True,)
def upload_certificate(request):
    if request.method == 'POST':
        data = request.body
    #pass a cookie to the request and delete the cookie after generating token
    # This cookie avoids creating new tokens on refreshing the page
    response = render_to_response('generate_token.html')
    response.set_cookie("generate_token", True)
    return response


def generate_rand(length=20,char=string.digits+ '!?$#*@%&' + string.letters):
    rand_num=""
    for i in range(length):
        rand_num = rand_num + choice(char)
    rand_num = 'EMB' + str(rand_num)
    return rand_num


def get_model(device_type=None, phone_number=None):
    if phone_number:
        try:
            APNSDevices.objects.get(phone_number=phone_number)
            return APNSDevices
        except:
            try:
                GCMDevices.objects.get(phone_number=phone_number)
                return GCMDevices
            except:
                return None

    elif device_type == 'ios':
        return APNSDevices
    elif device_type == 'android':
        return GCMDevices

#unique key / tagging / enabling concept
#TODO: allow post method only
@csrf_exempt
def store_devices(request, *args, **kwargs):
    try:
        data = eval(str(request.body))
        emb_token = data['token']
        p12_certificate = P12Certificate.objects.get(emb_token=emb_token)
        device_key = data['device_key']
        device_type = data['device_type']
        try:
            device = APNSDevices.objects.get(registration_id=device_key, p12_certificate=p12_certificate,  device_type=device_type)
        except:
            device = APNSDevices.objects.create(registration_id=device_key, p12_certificate=p12_certificate, device_type=device_type)
    except:
        raise
    result = {'success': True}
    return HttpResponse(json.dumps(result), content_type='application/json')
               
@csrf_exempt
def disable_on_alternate_os(phone_number=None, device_type=None):
    #if the same mobile number is existing on both the tables delete the old entry in alternate os
    try:
        if device_type == 'android':
            APNSDevices.objects.get(phone_number=phone_number).delete()
        elif device_type == 'ios':
            GCMDevices.objects.get(phone_number=phone_number).delete()
    except Exception,e:
        print "This number is not registered in alternate OS"
        pass
    return


@csrf_exempt
def set_profile_pic(request):
    try:
        data = request.GET
        print "request.FILES", request.FILES
        phone_number = data['phone_number']
        app_key = data['app_key']
        master_key = data['master_key']
        model = get_model(phone_number=phone_number)
        device = model.objects.get(phone_number=phone_number)
        print "Inside set profilepic ", device.username
    except Exception, e:
        print str(e)
        raise

    try:
        data = request.body
        file_path =  PROFILE_PICS_PATH +  device.device_type + str(device.id) + '.jpg'
        print file_path
        if os.path.isfile(file_path):
            commands.getoutput('rm -rf %s' %file_path)
        else:
            print "No such file"
        destination = open(file_path, 'w')
        destination.write(data)
        print "written data"
        destination.close()

        http_host = request.META['HTTP_HOST']
        device.profile_pic = 'http://' + http_host + '/media/profile_pics/' + device.device_type + str(device.id) + '.jpg'
        device.save()
    except Exception, e:
        print str(e)


    '''
    print data
    #for saving profile pic
    from settings import PROFILE_PICS_PATH
    try:
        print request.FILES
        for f in request.FILES.getlist('profile_pic'):
            print f, 11111
            file_path =  PROFILE_PICS_PATH +  device.device_type + str(device.id) + '_' + f.name
            if os.path.isfile(file_path):
                print "Yes file is there... Delete it!"
                commands.getoutput('rm -rf %s' %file_path)
                print "Deleted the file"
                if os.path.isfile(file_path):
                    print "STILL YESSS"
                else:
                    print "No such file exists"
            print file_path
            destination = open(file_path, 'wb+')
            for chunk in f.chunks():
                print "CHUNKS"
                destination.write(chunk)
                destination.close()
        device.profile_pic = '/media/profile_pics/' + device.device_type + str(device.id) + '_' + f.name
        print device.profile_pic
        device.save()
    except Exception, e:
        print str(e)
    '''
    return HttpResponse(json.dumps({}), content_type='application/json')

@csrf_exempt
def register_urbanairship_devices(request, *args, **kwargs):
    print 123
    try:
        try:
            print 1
            data = eval(str(request.body))
        except:
            data = request.POST
        print data
        phone_number = data['phone_number']
        device_type = data['device_type']
        device_key = data['device_key'] # to talk to APNS
        app_key = data['app_key'] # Provided by UrbanAirShip
        master_key = data['master_key'] # Provided by UrbanAirShip

        model = get_model(device_type=device_type)
        if device_type == 'android':
            try:
                gcm_device_id = data['gcm_device_id']
            except:
                gcm_device_id = data['device_key']
   
        try:
            # there should be authentication for mobile number
            #When user installed the app in different device just update the device key
            device = model.objects.get(app_key=app_key, master_key=master_key, phone_number=phone_number, device_type=device_type)
            device.registration_id = device_key
        except ObjectDoesNotExist:
            try:
                device = model.objects.get(app_key=app_key, master_key=master_key, registration_id=data['device_key'], device_type=device_type)
                device.phone_number = phone_number
            except:
                device = model.objects.create(registration_id=device_key, app_key=app_key, master_key=master_key, phone_number=phone_number, device_type=device_type)
        if device_type == 'android':
            device.gcm_device_id = gcm_device_id
        device.save()

        result = [{'success': True, 'phone_number':phone_number}]

        disable_on_alternate_os(phone_number, device_type) 
    except Exception, e:
        print str(e)
        result = [{'success': False,  'phone_number': ''}]
    return HttpResponse(json.dumps(result), content_type='application/json')


def authenticate_user(phone_number, email, otp):
    try:
        model = get_model(phone_number=phone_number)
        try:
            device = model.objects.get(phone_number=phone_number)
            if email:
                from django.core.mail import send_mail
                print "sending mail"
                if TESTING:
                    send_mail('Your verification number for ChatApplication', 'Hi,\n\nYour OTP is %s . Please use this OTP for the ChatApplication installed in your device.\n\nRegards,\nEmbitel Mobility Team' %otp, 'donotreply@embitel.com', 'mayank.j@embitel.com'])
                else:
                    send_mail('Your verification number for ChatApplication', 'Hi,\n\nYour OTP is %s . Please use this OTP for the ChatApplication installed in your device.\n\nRegards,\nEmbitel Mobility Team' %otp, 'donotreply@embitel.com', ['%s'%email])
                print "sent mail"
            #try:
            #    import requests
            #    requests.post(url='http://site2sms.com/user/send_sms_next.asp', auth=('9886999801', 'welcome@123'), data='txtMobileNo=%s&txtConfirmed=1&txtMessage=%s&txtGroup=0'%(otp, phone_number))
            #except:
            #     pass
        except:
            raise
    except:
        raise
    result = {'success': True}
    return

@csrf_exempt
def register_urbanairship_devices_get(request, *args, **kwargs):
    try:
        try:
            data = request.GET
            print data
        except:
            pass
        print data
        phone_number = data['phone_number']
        device_type = data['device_type']
        device_key = data['device_key'] # to talk to APNS
        app_key = data['app_key'] # Provided by UrbanAirShip
        master_key = data['master_key'] # Provided by UrbanAirShip
        if data.has_key('username'):
            username = data['username']
        else:
            username = ''

        if data.has_key('email'):
            email = data['email']
        else:
            email = ''

        if data.has_key('otp'):
            otp = data['otp']
        else:
            otp = ''

        model = get_model(device_type=device_type)
        if device_type == 'android':
            try:
                gcm_device_id = data['gcm_device_id']
            except:
                gcm_device_id = data['device_key']
   
        try:
            # there should be authentication for mobile number
            #When user installed the app in different device just update the device key
            device = model.objects.get(app_key=app_key, master_key=master_key, phone_number=phone_number, device_type=device_type)
            device.registration_id = device_key
        except ObjectDoesNotExist:
            try:
                device = model.objects.get(app_key=app_key, master_key=master_key, registration_id=data['device_key'], device_type=device_type)
                device.phone_number = phone_number
            except:
                device = model.objects.create(registration_id=device_key, app_key=app_key, master_key=master_key, phone_number=phone_number, device_type=device_type)
        if device_type == 'android':
            device.gcm_device_id = gcm_device_id
        if username:
            print "USERNAMEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEe", username
            device.username = username
            print "DEVICE>USERNAME", device.username
        print "device saved", device.username

        if email:
            device.email = email
        device.save()

        disable_on_alternate_os(phone_number, device_type) 
        #print "Multipart Files", request.FILES
        if request.body:
            print "YESSSSSSSSSSSSSS BODY CONTENT"
            set_profile_pic(request)
        else:
            print "No BODYYYYYYYYYYYYYYYYYY"
   
        if email and otp:
            print "EMAIL AND OTP ARE THERE",  email
            authenticate_user(phone_number=phone_number, email=email, otp=otp)

        result = [{'success': True, 'phone_number':phone_number, 'profile_pic': device.profile_pic, 'username':device.username}]
    except Exception, e:
        print str(e)
        result = [{'success': False,  'phone_number': ''}]
    return HttpResponse(json.dumps(result), content_type='application/json')



@csrf_exempt
def testing(request, *args, **kwargs):
    try:
        data = request.GET
        phone_number
    except:
        pass
 
    try:
        data = request.form
        print "Form", data
    except:
        pass

    try:
        data = request.POST
        print "POST data", data
    except Exception, e:
        print "POST DATA ERROR", str(e)
        pass
    try:
        print request.FILES
    except Exception, e:
        print "FILES ERROR", str(e)
    return HttpResponse(json.dumps({}), content_type='application/json')
 
#check for login
@csrf_exempt
def verify_user(request, *args, **kwargs):
    data = eval(str(request.body))
    app_key = data['app_key']
    phone_number = data['phone_number']
    try:
        model =  get_model(phone_number=phone_number) 
        device = model.objects.get(app_key=app_key, phone_number=phone_number)
        result = [{'success': True,  'phone_number': str(phone_number), 'profile_pic': device.profile_pic}]
    except:
        result = [{'success': False,  'phone_number': ''}]
        
    return HttpResponse(json.dumps(result), content_type='application/json')


#To check the App registered devices
@csrf_exempt
def verify_registered_users(request, *args, **kwargs):
    print request.body
    data = eval(str(request.body))
    app_key = data['app_key']
    print app_key
    phone_number = list(set(data['phone_number']))
    print phone_number
    try:
        import ast
        registered_ios_devices = APNSDevices.objects.filter(phone_number__in=phone_number).values('phone_number', 'profile_pic', 'username')#app_key=app_key in filter
        registered_android_devices = GCMDevices.objects.filter(phone_number__in=phone_number).values('phone_number', 'profile_pic', 'username')
        registered_devices = list(registered_ios_devices) + list(registered_android_devices)
        #registered_devices = list(set( list(registered_ios_devices) + list(registered_android_devices)))
        #registered_devices = u'%s' %(registered_devices)
        #devices = [ item.encode('ascii') for item in ast.literal_eval(registered_devices) ] 
        result = registered_devices
        print "result", result
    except Exception, e:
        print str(e)
        result = {'success': False}
    return HttpResponse(json.dumps(result), content_type='application/json')
      
 
#from mobile to mobile using urban airship
@csrf_exempt
def send_PN_to_device(request, *args, **kwargs):
    #{'phone_number':[]}
    pending_messages = ''
    COMMAND = ''
    print 1
    print "Here", request.body
    data = eval(str(request.body).replace('true', 'True').replace('false', 'False'))
    print data
    phone_number = data['phone_number']
    from_phone_number = data['from_phone_number']
    app_key = data['app_key']
    message = data['message']
    message_id = data['message_id']
    print 2
    model = get_model(phone_number=phone_number)        
    print model
    devices = list(model.objects.filter(phone_number=phone_number, pn_status=True)) #app_key in filter
    print devices
    for device in devices:
        #COMMAND = """curl -X POST -u "%s:%s"   -H "Content-Type: application/json"   --data '''{"device_tokens": %s, "aps": {"alert": "%s"}}'''    https://go.urbanairship.com/api/push/""" %(device.app_key, device.master_key, [str(device.registration_id)], message)
        if data.has_key('delivered') and device.device_type=='ios':
            print "Delivered key is present"
            try:
                
                from_device_model = get_model(phone_number=from_phone_number)
                from_device = from_device_model.objects.get(phone_number=from_phone_number, pn_status=True) #app_key
                
                if from_device.device_type == 'ios':
                    message_obj = Messages.objects.get(apns_devices=from_device, message_id=message_id, delivered=False, sent=True, from_phone_number=phone_number)
                else:
                    message_obj = Messages.objects.get(gcm_devices=from_device, message_id=message_id, delivered=False, sent=True, from_phone_number=phone_number)

                #message_obj.delivered=True
                #message_obj.save()
                message_obj.delete()
            except Exception, e:
                print "Should never come here", str(e)

            COMMAND = """curl -X POST -u "%s:%s"   -H "Content-Type: application/json"   --data '''{"aps":{"alert":"%s"},"device_tokens": %s,"phone_number":"%s", "from_phone_number":"%s", "delivered":"True", "message_id":"%s"}'''    https://go.urbanairship.com/api/push/""" %(device.app_key, device.master_key, message, [str(device.registration_id)], device.phone_number, from_phone_number, message_id)
            try:
                if from_device.device_type == 'ios':
                    pending_messages = Messages.objects.filter(apns_devices=from_device, sent=False, delivered=False).order_by('id')
                else:
                    pending_messages = Messages.objects.filter(gcm_devices=from_device, sent=False, delivered=False).order_by('id')
                #import time
                #time.sleep(5)

            except Exception, e:
                print str(e)
 
        elif device.device_type == 'ios':
            print "No delivered key in the dict.. Its a message!"
            try:
                pending_messages_check = Messages.objects.filter(apns_devices=device, sent=False, delivered=False).order_by('id')
                if not pending_messages_check:
                    Messages.objects.get(apns_devices=device, delivered=False, sent=True, from_phone_number=from_phone_number)
                print "To be delivered messages are pending please wait"
                message_obj = Messages.objects.create(message=message, message_id=message_id, apns_devices=device, device_type=device.device_type, from_phone_number=from_phone_number) ## sent false and delivered false
                message_obj.save()
                #pending_messages = Messages.objects.filter(apns_devices=device, sent=False, delivered=False).order_by('id')
                print "messages added to the queue"
                #result={'result':'Saved in queue! Will be sent shortly!'}
                #return HttpResponse(json.dumps(result), content_type='application/json')
            except Exception, e:
                print "No Pending messages Found", str(e)
                try:
                    message_object = Messages.objects.create(message=message, message_id=message_id, apns_devices=device, device_type=device.device_type, from_phone_number=from_phone_number, sent=True) ## sent false and delivered false
                    print "Message sent and added into Messages queue with delivered=False"
                    message_object.save()
                    #pending_messages = Messages.objects.filter(apns_devices=device, sent=False, delivered=False).order_by('id')
                    #if pending_messages:
                    #    message_object.sent=False
                except Exception, e:
                    print "NOT SAVEDDDDDDD", str(e)
           
                COMMAND = """curl -X POST -u "%s:%s"   -H "Content-Type: application/json"   --data '''{"aps":{"alert":"%s"}, "options":{"expiry":%s}, "device_tokens": %s,"phone_number":"%s", "from_phone_number":"%s", "message_id": "%s"}'''    https://go.urbanairship.com/api/push/""" %(device.app_key, device.master_key, message, MESSAGE_EXPIRY, [str(device.registration_id)], device.phone_number, from_phone_number, message_id)

        elif data.has_key('delivered') and device.device_type=='android':
            #import time
            #time.sleep(3)
            print "Inside android delivered"
            try:
                from_device_model = get_model(phone_number=from_phone_number)
                from_device = from_device_model.objects.get(phone_number=from_phone_number, pn_status=True) #app_key
                print "from_device.device_type", from_device.device_type
                if from_device.device_type == 'android':
                    message_obj = Messages.objects.get(gcm_devices=from_device, message_id=message_id, delivered=False, sent=True, from_phone_number=phone_number)
                else:
                    message_obj = Messages.objects.get(apns_devices=from_device, message_id=message_id, delivered=False, sent=True, from_phone_number=phone_number)
                print "Got the message with id %s and deliverd=True now" %message_id
                #message_obj.delivered=True
                #message_obj.save()
                message_obj.delete()
            except Exception, e:
                print "Should never come here", str(e)
            print "NEXTTTTTTTTTTTTTTT"
            COMMAND = """curl -X POST -u "%s:%s"   -H "Content-type: application/json" -H "Accept: application/vnd.urbanairship+json; version=3;" --data '''{"audience":{"apid" : "%s"}, "notification":{"alert" : "%s", "android":{"extra":%s}},"device_types":["android"]}''' https://go.urbanairship.com/api/push/""" %(device.app_key, device.master_key, device.registration_id, message, {"phone_number":phone_number, "from_phone_number":from_phone_number, "message_id": message_id, "delivered":"True"})
            try:
                if from_device.device_type == 'android':
                    pending_messages = Messages.objects.filter(gcm_devices=from_device, sent=False, delivered=False).order_by('id')
                else:
                    pending_messages = Messages.objects.filter(apns_devices=from_device, sent=False, delivered=False).order_by('id')
            except Exception, e:
                print str(e)
            print "11111111111111"
        elif device.device_type=='android':
            try:
                pending_messages_check = Messages.objects.filter(gcm_devices=device, sent=False, delivered=False).order_by('id')
                if not pending_messages_check:
                    Messages.objects.get(gcm_devices=device, delivered=False, sent=True, from_phone_number=from_phone_number)
                print "To be delivered messages are pending please wait"
                message_obj = Messages.objects.create(message=message, message_id=message_id, gcm_devices=device, device_type=device.device_type, from_phone_number=from_phone_number) ## sent false and delivered false
                message_obj.save()
                #pending_messages = Messages.objects.filter(apns_devices=device, sent=False, delivered=False).order_by('id')
                print "messages added to the queue"
                #result={'result':'Saved in queue! Will be sent shortly!'}
                #return HttpResponse(json.dumps(result), content_type='application/json')
            except Exception, e:
                print "No Pending messages Found", str(e)
                try:
                    message_object = Messages.objects.create(message=message, message_id=message_id, gcm_devices=device, device_type=device.device_type, from_phone_number=from_phone_number, sent=True) ## sent false and delivered false
                    print "Message sent and added into Messages queue with delivered=False"
                    message_object.save()
                    #pending_messages = Messages.objects.filter(apns_devices=device, sent=False, delivered=False).order_by('id')
                    #if pending_messages:
                    #    message_object.sent=False
                except Exception, e:
                    print "NOT SAVEDDDDDDD", str(e)

                COMMAND = """curl -X POST -u "%s:%s"   -H "Content-type: application/json" -H "Accept: application/vnd.urbanairship+json; version=3;" --data '''{"audience":{"apid" : "%s"}, "notification":{"alert" : "%s", "android":{"extra":%s, "time_to_live": 6000}},"device_types":["android"]}''' https://go.urbanairship.com/api/push/""" %(device.app_key, device.master_key, device.registration_id, message, {"phone_number":phone_number, "from_phone_number":from_phone_number, "message_id": message_id})
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>."
        print "COMMAND", COMMAND
        if COMMAND:
            COMMAND = COMMAND.replace("\'","\"" ).replace("\"\"\"", '\'\'\'')
            print COMMAND
            result = commands.getoutput(COMMAND)
        
        if pending_messages:
            #import time
            #time.sleep(1)
            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>", len(pending_messages)
            print "Since there are Pending messages. Triggering message"
            pending_message = pending_messages[0]
            print 1
            print 1
            if pending_message.device_type == 'ios':
                device = pending_message.apns_devices
            else:
                device = pending_message.gcm_devices
            print 2
            print device.device_type
            if device.device_type == 'ios':
                print 3 
                try:
                    COMMAND = """curl -X POST -u "%s:%s"   -H "Content-Type: application/json"   --data '''{"aps":{"alert":"%s"},"device_tokens": %s,"phone_number":"%s", "from_phone_number":"%s", "message_id": "%s"}'''    https://go.urbanairship.com/api/push/""" %(str(device.app_key), str(device.master_key), str(pending_message.message), [str(device.registration_id)], str(device.phone_number), str(pending_message.from_phone_number), str(pending_message.message_id))
                    COMMAND = COMMAND.replace("\'","\"" ).replace("\"\"\"", '\'\'\'')
                    result = commands.getoutput(COMMAND)
                    print "Androoud pending trigger result", result
                    print "Yes Triggered"
                    pending_message.sent = True
                    pending_message.save()
                except Exception, e:
                    print ">>>", str(e)
            else:
                #Android
                print 4
                try:
                    COMMAND = """curl -X POST -u "%s:%s"   -H "Content-type: application/json" -H "Accept: application/vnd.urbanairship+json; version=3;" --data '''{"audience":{"apid" : "%s"}, "notification":{"alert" : "%s", "android":{"extra":%s}},"device_types":["android"]}''' https://go.urbanairship.com/api/push/""" %(str(device.app_key), str(device.master_key), str(device.registration_id), str(pending_message.message), {"phone_number":str(device.phone_number), "from_phone_number": str(pending_message.from_phone_number), "message_id": str(pending_message.message_id)})
                    print 5
                    COMMAND = COMMAND.replace("\'","\"" ).replace("\"\"\"", '\'\'\'')
                    print COMMAND
                    print 6
                    result = commands.getoutput(COMMAND)
                    print "Androoud pending trigger result", result
                    print "YYes Triggered"
                    pending_message.sent = True
                    pending_message.save()
                except Exception, e:
                    print ">>>", str(e)

    result={'result':'successfully sent Push notification!'}
    return HttpResponse(json.dumps(result), content_type='application/json')

@csrf_exempt
def set_PN_status(request):
    data = eval(str(request.body).replace('true', "True").replace('false', 'False'))
    print "Inside set_PN_Status", data
    phone_number = data['phone_number']
    app_key = data['app_key']
    status = data['status']
    try:
        model = get_model(phone_number=phone_number)
        device = model.objects.get(app_key=app_key, phone_number=phone_number)
        device.pn_status = status
        device.save()
        print "Status set to ", device.pn_status 
    except Exception, e:
        print str(e)
        pass
    result={'result':'success'}
    return HttpResponse(json.dumps(result), content_type='application/json')

@csrf_exempt
def set_channels(request):
    data = eval(str(request.body).replace('true', "True").replace('false', 'False'))
    devices = data['device']
    emb_token = data['token']
    channel = data['channel']
    try:
        p12_certificate = P12Certificate.objects.get(emb_token=emb_token)
        devices = APNSDevices.objects.filter(p12_certificate=p12_certificate, registration_id__in=devices)
        for device in devices:
            if eval(str(device.channels)):
                channels = device.channels + channel + '##'
            else:
                device.channels = channel + '##'
            device.save()
    except Exception, e:
        print str(e)
        pass
    result={'result':'success'}
    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def set_channels(request):
    data = eval(str(request.body))
    devices = data['device']
    emb_token = data['token']
    channel = data['channel']
    operation = data['operation'] # add/delete/edit
    if operation == 'edit':
        new_channel = data['new_channel']
    try:
        p12_certificate = P12Certificate.objects.get(emb_token=emb_token)
        devices = APNSDevices.objects.filter(p12_certificate=p12_certificate, registration_id__in=devices)
        for device in devices:
            if device.channels:
                if operation == 'add':
                    channels = device.channels + channel + '##'
                elif operation == 'delete':
                    channels = device.channels.replace(channel+ '##', '')
                elif operation == 'edit':
                    channels = device.channels.replace(channel+ '##', new_channel + '##')
                device.channels = channels
            else:
                if operation == 'add':
                    device.channels = channel + '##'
            device.save()

    except Exception, e:
        print str(e)
        pass
    result={'result':'success'}
    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def urbanairship_set_channels(request):
    # {'channel': 'EMBMobility', 'device': ['8c85a4add9947ff507158251a4a639084e9f8f6bf5260433d148257a625ebd85'], 'app_key': '3gutVRHDQ0O25Hlu2wc9lg', 'operation': "delete",}
    data = eval(str(request.body))
    devices = data['device']
    app_key = data['app_key']
    channel = data['channel']
    operation = data['operation'] # add/delete/edit
    if operation == 'edit':
        new_channel = data['new_channel']
    try:
        devices = APNSDevices.objects.filter(app_key=app_key, registration_id__in=devices)
        for device in devices:
            if device.channels:
                if operation == 'add':
                    channels = device.channels + channel + '##'
                elif operation == 'delete':
                    channels = device.channels.replace(channel+ '##', '')
                elif operation == 'edit':
                    channels = device.channels.replace(channel+ '##', new_channel + '##')
                device.channels = channels
            else:
                if operation == 'add':
                    device.channels = channel + '##'
            device.save()
    except Exception, e:
        print str(e)
        pass
    result={'result':'success'}
    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
@login_required
#@cache_control(no_store=True, no_cache=True, must_revalidate=True,)
def generate_token(request):
    #TODO: Before saving p12 certificate try to generate pem file if success then only accept it, else redirect to upload page saying incorrect upload
    form_data = request.POST.copy()
    form = UploadP12Certificate(form_data, request.FILES)
    form.user_id = request.user.id
    if form.errors:
        response = render_to_response('generate_token.html', {'form': form})
        response.set_cookie("generate_token", True)
        return response
    
    if not request.FILES.getlist('p12_certificate'):
        result = {'result': "No Uploads found..! Please Upload the file!"}
        return HttpResponse(json.dumps(result), content_type='application/json')
    
    try:
        if request.COOKIES.has_key('generate_token'):
            data = request.POST
	    for f in request.FILES.getlist('p12_certificate'):
	        p12_certificates_dir = "/home/embadmin/Documents/django_apps/django_experiments/embitel/embitel_framework/p12_certificates"
	        p12_dir = os.path.join(p12_certificates_dir, datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
	        try:
	    	    COMMAND = 'mkdir -p %s' %p12_dir
		    result = commands.getoutput(COMMAND)
		except Exception,e:
		    raise

		file_path =  p12_dir + '/' + f.name
		destination = open(file_path, 'wb+')
		for chunk in f.chunks():
	    	    destination.write(chunk)
		    destination.close()


            result = False
            while result is False:
                try:
	            emb_token = generate_rand()
                    try:
                        P12Certificate.objects.get(emb_token=emb_token)
                    except:
                        result = True
                except:
                    pass			

            try:
	        #TODO: try with out password
	        pem_file_name = f.name.rsplit('.')[0]
	        pem_file_path = p12_dir + '/' + pem_file_name + '.pem'
	        COMMAND = "openssl pkcs12 -in %s  -password pass:%s -out %s -nodes" %(file_path, data['password'], pem_file_path)
	        result = commands.getoutput(COMMAND)
                if 'mac verified ok' in result.lower():
	            try:
    	                p12_certificate = P12Certificate.objects.create(path=file_path, emb_token=emb_token, p12_password=data['password'], pem_file=pem_file_path, app_name=data['app_name'], user=request.user)
	                p12_certificate.save()
	                result = {"emb_token": emb_token}
	            except:
	                result = {'result': "Unable to create P12Certificate object!!"}
                else:
                    form._errors["p12_certificate"] = form.error_class(["Incorrect upload/password!"])
                    response = render_to_response('generate_token.html', {'form': form})
                    response.set_cookie("generate_token", True)
                    return response
            except:
                raise
        else:
            emb_token = P12Certificate.objects.filter(user=request.user).latest('id').emb_token
    except Exception,e:
        result = {'result': "Corrupted file. Please Upload the correct file!"}

    if not request.COOKIES.has_key('generate_token'):
        return HttpResponseRedirect('/embitel/upload_certificate/')
        
    user = request.user
    response = render_to_response('token.html', {'token': emb_token})
    response.delete_cookie('generate_token')
    return response
    #return HttpResponse(json.dumps(result), content_type='application/json')

def vault(request):
    user = request.user
    response = render_to_response('vault.html', {'objects': P12Certificate.objects.filter(user=request.user).order_by('-created_at')})
    return response

@csrf_exempt
def push_notification(request):
    #You may or may not get the device ids. Make sure this parameter is optional
    #send to all who has registered for that app
    # Try different ios applications and store device ids and try to send PNs
    if request.method != 'POST':
        result = {'result': 'This is not the correct method use POST method instead GET method!'}
        return HttpResponse(json.dumps(result), content_type='application/json')
    data = eval(str(request.body))
    if not data.has_key('device_key') or not data.has_key('token') or not data.has_key('message'):
        result = {'result': 'Please pass the token provied by us along with the Device Keys and message!'}
        return HttpResponse(json.dumps(result), content_type='application/json')
    try:
        pem_certificate = P12Certificate.objects.get(emb_token=data['token'])
    except:
        result = {'result': 'Please check your token number!'}
        return HttpResponse(json.dumps(result), content_type='application/json')
    '''
    device = GCMDevice.objects.get(registration_id=gcm_reg_id)
    device.send_message({"foo": "bar"}) # The message will be sent and received as json.
    '''
    #device = APNSDevice.objects.get(registration_id=apns_token)
    device_keys = data['device_key']
    for device_key in device_keys:
        try:
            device = APNSDevice.objects.get(registration_id=device_key)
        except:
            device = APNSDevice.objects.create(registration_id=device_key)
        device.save()
        device.send_message(data['message'],  certificate=pem_certificate.pem_file) # The message may only be sent as text.

    result = {'result': 'successfully sent the push notification!'}
    return HttpResponse(json.dumps(result), content_type='application/json')
    #return HttpResponse(str({'a': 5}), content_type="text/plain")

@csrf_exempt
def configure_PN(request, encoded_key1=None): 
    try:
        p12_obj = P12Certificate.objects.get(id=encoded_key1)
    except:
        return HttpResponseRedirect('/embitel/vault/')
    users = APNSDevices.objects.filter(p12_certificate=p12_obj).values_list('phone_number', flat='true')
    users = list(set(users) -set([None, '']))
    response = render_to_response('configure_PN.html', {'encoded_key1':encoded_key1, 'users': users})
    return response

#TODO: check for multiple devices, single devices, ALL from WEB and from POST DATA
@csrf_exempt
def send_bulk_PN(request, encoded_key1=None):
    print request.POST
    web = False  
    result= {}
    from push_notifications.apns import apns_send_bulk_message
    try:
        #This will work only for web based hits
        data = request.POST
        print data
        PN_message = data['PN_message']
        p12_certificate = P12Certificate.objects.get(id=encoded_key1)
        if data['send_bulk_PN'] == 'Send to ALL':
            device_ids = 'ALL'
        elif data.has_key('users') and data['users']:
            users = data.getlist('users')
            device_ids = list(APNSDevices.objects.filter(p12_certificate=p12_certificate, phone_number__in=users).extra(where=['CHAR_LENGTH(registration_id) = 64']).values_list('registration_id', flat='true'))
        elif data.has_key('limit') and data['limit']:
            limit = int(data.get('limit'))
            device_ids = list(APNSDevices.objects.filter(p12_certificate=p12_certificate).extra(where=['CHAR_LENGTH(registration_id) = 64']).order_by('-id').values_list('registration_id', flat='true'))[:limit]
            print "device_ids" , device_ids
        web = True
    except Exception, e:
        print "Error here 1", str(e)
        p12_certificate = ''

    try:
        if not web:
            #This try block will work when a person sends request by passing token number and message with individual registration ids
            data = eval(str(request.body))
            p12_certificate = P12Certificate.objects.get(emb_token=data['token'])
            PN_message = data['message']
            device_ids = data['device_id']
    except Exception, e:
        print "error here 2", str(e)
        p12_certificate = ''
        if not p12_certificate:
            result = {}
    if not p12_certificate:
        #return error to form or display message on status page
        return HttpResponseRedirect('/embitel/vault/')
    #Use Asynchronous method to send PN
        
    if device_ids == "ALL":
        devices = list(APNSDevices.objects.filter(p12_certificate=p12_certificate).extra(where=['CHAR_LENGTH(registration_id) = 64']).values_list('registration_id', flat='true'))
    elif device_ids:
        devices = list(APNSDevices.objects.filter(p12_certificate=p12_certificate, registration_id__in=device_ids).extra(where=['CHAR_LENGTH(registration_id) = 64']).values_list('registration_id', flat='true'))

    else:
        #This will not hit any time.. should replace with phone number or user name and replace device keys with usernames
        devices = data['device_id']
        if web:
            devices = list(APNSDevices.objects.filter(p12_certificate=p12_certificate, registration_id__in=devices).values_list('registration_id', flat='true'))
        else:
            for device in devices:
                try:
                    #Handle length of registration key
                    #store some source name in the model
                    dev = APNSDevices.objects.get(registration_id=device)
                except:
                    dev = APNSDevices.objects.create(registration_id=device)
                    dev.save()
    if devices:
        try:
            apns_send_bulk_message(registration_ids=devices, data=PN_message)
            response = render_to_response('bulk_PN_status.html', {'status': "Successfully sent Push Notifications to all the registered users!" })
        except:
            raise
            response = render_to_response('bulk_PN_status.html', {'status': "Something went wrong and unable to send the push notifications!" })
    else:
        response = render_to_response('bulk_PN_status.html', {'status': "No registered users for the application you've opted!" })
    if not web:
        result = {'status': "Successfully sent Push Notifications to all the registered users!" } 
        return HttpResponse(json.dumps(result), content_type='application/json')
    return response


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
