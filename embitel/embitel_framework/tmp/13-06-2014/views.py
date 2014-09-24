import os
import string
from random import choice
import re
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
from embitel_framework.models import P12Certificate, APNSDevices, GCMDevices, Messages, Groups, Channels
import commands

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, AnonymousUser

from forms import LoginForm, UploadP12Certificate, RegistrationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.cache import cache_control
from settings import PROFILE_PICS_PATH, MEDIA_PATH
from embitel_framework.mail import send_mail

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

@login_required
@csrf_exempt
def manage_teams(request):
    user = request.user
    team_name = ''
    print request.POST

    user = request.user
    data = request.POST.copy()
    if data.has_key('team_name') and data.has_key('edit_team_name') and data['team_name'] and data['edit_team_name']:
        try:
            group_members = Groups.objects.filter(group_name=data['team_name'])
            for member in group_members:
                member.group_name = data['edit_team_name']
                member.save()
        except Exception, e:
            print str(e)
            pass
        return HttpResponseRedirect('/embitel/manage_teams/')

    try:
        g = Groups.objects.exclude(group_name='Others').get(email=user.email)
        result = Groups.objects.all().order_by('group_name').values_list('group_name', flat='true').distinct()
    except:
        result = []
   
    try:
        data = request.POST.copy()
        if data.has_key('email') and data.has_key('username') and data['email'] and data['username']:
            try:
                g = Groups.objects.get(email=data["email"], group_name=data['team_name'])
            except:
                g = Groups.objects.create(email=data["email"], username=data["username"], group_name=data['team_name'])
                g.save()
         
    except Exception, e:
        print str(e)
        pass

 
    try:
        if request.POST.get('team_name'):
            team_name = request.POST['team_name'].strip()
            team_objects = Groups.objects.filter(group_name=team_name).order_by('username')
        else:
            team_objects = []
    except:
        team_objects = []


    response = render_to_response('teams.html', {'teams':result, 'team_objects': team_objects, 'selected_team':team_name})
    return response


@login_required
@csrf_exempt
def delete_user(request, encoded_key1=None):
    team_name = ''
    try:
        g = Groups.objects.get(id=encoded_key1)
        team_name = g.group_name
        g.delete()
        result = Groups.objects.all().order_by('group_name').values_list('group_name', flat='true').distinct()
        team_objects = Groups.objects.filter(group_name=team_name).order_by('username')
        #response = render_to_response('teams.html', {'teams':result, 'team_objects': team_objects, 'selected_team':team_name})
        #return response
    except:
        return HttpResponseRedirect('/embitel/manage_teams/')
    return HttpResponseRedirect('/embitel/manage_teams/')



def generate_rand(length=20,char=string.digits+ '!?$#*@%&' + string.letters):
    rand_num=""
    for i in range(length):
        rand_num = rand_num + choice(char)
    rand_num = 'EMB' + str(rand_num)
    return rand_num


def get_model(device_type=None, email=None):
    if email:
        try:
            APNSDevices.objects.get(email=email)
            return APNSDevices
        except:
            try:
                GCMDevices.objects.get(email=email)
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
def disable_on_alternate_os(email=None, device_type=None):
    #if the same mobile number is existing on both the tables delete the old entry in alternate os
    try:
        if device_type == 'android':
            APNSDevices.objects.get(email=email).delete()
        elif device_type == 'ios':
            GCMDevices.objects.get(email=email).delete()
    except Exception,e:
        print "This number is not registered in alternate OS"
        pass
    return


#For audio streaming
@csrf_exempt
def audio_streaming(request):
    try:
        data = request.GET
        print data
        email = data['email']
        from_email = str(data['from_email'])
        app_key = data['app_key']
        master_key = data['master_key']
        model = get_model(email=email)
        device = model.objects.get(email=email)
        channel_id = ''
        message_id= str(data['message_id'])
        message_type = 'message'

        COMMAND = ''
        result = {}
    except Exception, e:
        print "Error here>>@", str(e)
        raise

    try:
        data = request.body
        file_path =  MEDIA_PATH +  device.device_type + message_id + '.3gp'
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
        media_file = 'http://' + http_host + '/media/gallery/' + device.device_type + message_id + '.3gp'

        #For Android only.. Need to implement for ios

        try:
            pending_messages_check = Messages.objects.filter(gcm_devices=device, sent=False, delivered=False).order_by('id')
            if not pending_messages_check:
                Messages.objects.get(gcm_devices=device, delivered=False, sent=True, from_email=from_email)
            print "To be delivered messages are pending please wait"
            message_obj = Messages.objects.create(message=media_file, message_id=message_id, gcm_devices=device, device_type=device.device_type, from_email=from_email, message_type=message_type) ## sent false and delivered false
            message_obj.save()
        except Exception, e:
            print "No Pending messages Found", str(e)
            try:
                message_object = Messages.objects.create(message=media_file, message_id=message_id, gcm_devices=device, device_type=device.device_type, from_email=from_email, message_type=message_type, sent=True) ## sent false and delivered false

                print "Message sent and added into Messages queue with delivered=False"
                message_object.save()
            except Exception, e:
                print "NOT SAVEDDDDDDD", str(e)

            COMMAND = """curl -X POST -u "%s:%s"   -H "Content-type: application/json" -H "Accept: application/vnd.urbanairship+json; version=3;" --data '''{"audience":{"apid" : "%s"}, "notification":{"alert" : %s, "android":{"extra":%s, "time_to_live": 6000}},"device_types":["android"]}''' https://go.urbanairship.com/api/push/""" %(device.app_key, device.master_key, device.registration_id, repr(str(media_file)), {"email":str(device.email), "from_email":from_email, "message_id": message_id, "message_type": message_type, "channel_id": channel_id})
        if COMMAND:
            COMMAND = str(COMMAND.replace("\'","\"" ).replace("\"\"\"", '\'\'\''))
            print COMMAND
            result = commands.getoutput(COMMAND)
            print "result", result
            result={'result':'successfully sent Push notification!'}
    except Exception, e:
        print str(e)

    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def set_profile_pic(request):
    try:
        data = request.GET
        print "request.FILES", request.FILES
        email = data['email']
        app_key = data['app_key']
        master_key = data['master_key']
        model = get_model(email=email)
        device = model.objects.get(email=email)
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
        profile_pic = 'http://' + http_host + '/media/profile_pics/' + device.device_type + str(device.id) + '.jpg'
    except Exception, e:
        profile_pic = None
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
    return profile_pic#HttpResponse(json.dumps({}), content_type='application/json')

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
        email = data['email']
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
            #When userDinstalled the app in different device just update the device key
            device = model.objects.get(app_key=app_key, master_key=master_key, email=email, device_type=device_type)
            device.registration_id = device_key
        except ObjectDoesNotExist:
            try:
                device = model.objects.get(app_key=app_key, master_key=master_key, registration_id=data['device_key'], device_type=device_type)
                device.email = email
            except:
                device = model.objects.create(registration_id=device_key, app_key=app_key, master_key=master_key, email=email, device_type=device_type)
        if device_type == 'android':
            device.gcm_device_id = gcm_device_id
        device.save()

        result = [{'success': True, 'email':email}]

        disable_on_alternate_os(email, device_type) 
    except Exception, e:
        print str(e)
        result = [{'success': False,  'email': ''}]
    return HttpResponse(json.dumps(result), content_type='application/json')


def authenticate_user(email, otp):
    try:
        model = get_model(email=email)
        cc = []
        bcc = []
        try:
            device = model.objects.get(email=email)
            if email:
                #from django.core.mail import send_mail
                print "importingg"
                print "Imported"
                print "sending mail"
                if not TESTING:
                    #send_mail('Your verification number for ChatApplication', 'Hi,\n\nYour OTP is %s . Please use this OTP for the ChatApplication installed in your device.\n\nRegards,\nEmbitel Mobility Team' %otp, 'donotreply@embitel.com', ['%s'%email])
                    if email.endswith('embitel.com'): 
                        send_mail('donotreply@embitel.com', '%s'%email, 'Your verification number for ChatApplication', 'Hi,\n\nYour OTP is %s . Please use this OTP for the ChatApplication installed in your device.\n\nRegards,\nEmbitel Mobility Team' %otp, cc, bcc)
                else:
                    if email.endswith('embitel.com'): 
                        send_mail('donotreply@embitel.com', 'prakash.p@embitel.com', 'Your verification number for ChatApplication', 'Hi,\n\nYour OTP is %s . Please use this OTP for the ChatApplication installed in your device.\n\nRegards,\nEmbitel Mobility Team' %otp, cc, bcc)
                        send_mail('donotreply@embitel.com', 'mayank.j@embitel.com', 'Your verification number for ChatApplication', 'Hi,\n\nYour OTP is %s . Please use this OTP for the ChatApplication installed in your device.\n\nRegards,\nEmbitel Mobility Team' %otp, cc, bcc)
                print "sent mail"
            #try:
            #    import requests
            #    requests.post(url='http://site2sms.com/user/send_sms_next.asp', auth=('9886999801', '123'), data='txtMobileNo=%s&txtConfirmed=1&txtMessage=%s&txtGroup=0'%(otp, email))
            #except:
            #     pass
        except:
            raise
    except:
        raise
    result = {'success': True}
    return


@csrf_exempt
def hrms_management(request):
    from embitel_framework.hrms import leave_management
    data = eval(str(request.body))
    email = data['email']
    app_key = data['app_key']
    user_id = data['user_id']
    password = data['password'] 
    result = leave_management(user_id, password)
    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def mailers(request, *args, **kwargs):
    print request.body
    data = eval(str(request.body))
    print data
    print "Eval Success"
    app_key = data['app_key']
    email = data['email']
    receiver = data['receiver']
    mail_type = data['mail_type']
    signature = data['signature'] #name
    if data.has_key('cc'):
        cc = data['cc']
    else:
        cc = []
    if data.has_key('bcc'):
        bcc = data['bcc']
    else:
        bcc = []

    if mail_type == 'sick_leave':
        subject = 'Request for sick leave!'
        body = "Hi,\n\nAs I\'m not feeling well, I\'m unable to come office today. Please kindly grant me sick leave for today.\n\nThanks & Regards\n%s" %signature 
    elif mail_type == 'casual_leave':
        subject = 'Request for casual leave!'
        body = "Hi,\n\nAs I'm having some personal work, I\'m unable to come office today. Please kindly grant me casual leave for today.\n\nThanks & Regards\n%s" %signature
    else:
        subject = data['subject']
        body = data['body']
    #if TESTING:
    #    send_mail(email, 'prakash.p@embitel.com', subject, body)
    #    send_mail(email, 'mayank.j@embitel.com', subject, body)
    #else:
    send_mail(email, receiver, subject, body, cc, bcc)
    result = {'success': True}
    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def register_urbanairship_devices_get(request, *args, **kwargs):
    print "Enter the dragon"
    try:
        try:
            data = request.GET
            print data
        except:
            pass
        print data

        email = data['email']

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

        model = get_model(device_type=device_type)

        try:
            device = model.objects.get(app_key=app_key, master_key=master_key, email=email)
        except:
            device = model.objects.create(app_key=app_key, master_key=master_key, email=email, device_type=device_type)
            device.save()

        if data.has_key('otp'):
            otp = data['otp']
        else:
            otp = ''
        if email and otp:
            print "EMAIL AND OTP ARE THERE",  email
            authenticate_user(email=email, otp=otp)
            result = {'success': True }
            return HttpResponse(json.dumps(result), content_type='application/json')


        if device_type == 'android':
            try:
                gcm_device_id = data['gcm_device_id']
            except:
                gcm_device_id = data['device_key']
   
        try:
            # there should be authentication for mobile number
            #When user installed the app in different device just update the device key
            device = model.objects.get(app_key=app_key, master_key=master_key, email=email, device_type=device_type)
            device.registration_id = device_key
        except ObjectDoesNotExist:
            try:
                device = model.objects.get(app_key=app_key, master_key=master_key, registration_id=data['device_key'], device_type=device_type)
                device.email = email
            except:
                device = model.objects.create(registration_id=device_key, app_key=app_key, master_key=master_key, email=email, device_type=device_type)
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

        disable_on_alternate_os(email, device_type) 
        #print "Multipart Files", request.FILES
        if request.body:
            print "YESSSSSSSSSSSSSS BODY CONTENT"
            device.profile_pic = set_profile_pic(request)
            device.save()
        else:
            print "No BODYYYYYYYYYYYYYYYYYY"
   

        if data.has_key('status_message'):
            status_message = data['status_message']
            device.status_message = status_message
            device.save()

        try:
            if data.has_key('dob'):
                dob = data['dob']
                print "DDDDDDDDDDDDD OOOOOOOOOOOOOOOOOOOOOOO BBBBBBBBBBBBBBBBBBBB", dob
                if dob:
                    device.dob = datetime.datetime.strptime(dob, '%d-%m-%Y').date()
                    device.save()
        except Exception, e:
            print "Error while saving dob",  str(e)

        result = [{'success': True, 'email':email, 'profile_pic': device.profile_pic, 'username':device.username, 'status_message':device.status_message}]
        try:
            print "saving INSTALLED flag and pic"
            g = Groups.objects.get(email=email)
            g.profile_pic = device.profile_pic
            g.installed = True
            g.save()
        except:
            print "Exception while saving INSTALLED flag and pic"
            g = Groups.objects.create(email=email, username=device.username, profile_pic=device.profile_pic, installed=True,  group_name='Others')
            g.save()
    except Exception, e:
        raise
        print str(e)
        result = [{'success': False,  'email': ''}]
    return HttpResponse(json.dumps(result), content_type='application/json')



@csrf_exempt
def testing(request, *args, **kwargs):
    try:
        data = request.GET
        email
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
    email = data['email']
    try:
        model =  get_model(email=email) 
        device = model.objects.get(app_key=app_key, email=email)
        result = [{'success': True,  'email': str(email), 'profile_pic': device.profile_pic}]
    except:
        result = [{'success': False,  'email': ''}]
        
    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def get_gropus_and_members(request, *args, **kwargs):
    print request.body
    data = eval(str(request.body))
    app_key = data['app_key']
    #email = list(set(data['email'])) # use this email to get the friends list
    result = {}
    try:
        groups = tuple(Groups.objects.exclude(group_name='Others').order_by('group_name').values_list('group_name', flat='true').distinct())
        if data.has_key('group_name'):
            group_name = data['group_name']
            result = tuple(Groups.objects.filter(group_name=group_name).order_by('username').values('email', 'username', 'installed', 'profile_pic'))
        else:
            result = groups
        '''
        for group in groups:
            result[str(group)] = tuple(Groups.objects.filter(group_name=group).order_by('username').values('email', 'username', 'installed', 'profile_pic'))
        result = ({'refresh':True}, result)
        print "result", result
        print type(result)
        '''
    except Exception, e:
        print str(e)
        result = ({'success': False})
    print result
    return HttpResponse(json.dumps(result), content_type='application/json')
 
@csrf_exempt
def get_group_members(request, *args, **kwargs):
    #This will send all the members in the particular group
    print request.body
    data = eval(str(request.body))
    app_key = data['app_key']
    group_name = data['group_name']
    #email = list(set(data['email'])) # use this email to get the friends list
    result = []
    try:
        result = list(Groups.objects.filter(group_name=group_name).values('email', 'username', 'installed', 'profile_pic'))
    except Exception, e:
        pass
    return HttpResponse(json.dumps(result), content_type='application/json')
 
@csrf_exempt
def manage_friends(request, *args, **kwargs):
    print request.body
    data = eval(str(request.body))
    app_key = data['app_key']
    email = data['email'] # email of the user who received the invitation
    friend_email = data['friend_email'] # email of the user who sent the invitation
    action = data['action'] # accepted / declined / pending
    print "Ok done"
    model = get_model(email=data['email'])
    device = model.objects.get(email=data['email'])
    if device:
        if friend_email == email:
            pass
        elif action == 'accepted':
            print "Friends>>>>>>>>>>>>>>>>>>>>", device.friends
            friends = eval(device.friends)
            print "friends... %s friends are %s(DB)" %(email, friends)
            if friend_email not in friends:
                print "before saving device.friends are", device.friends
                device.pending_requests = str(list(set(eval(device.pending_requests)) - set([friend_email])))
                device.friends = str(list(set(eval(device.friends) + [friend_email])))
                device.save()
                print "after saving device.friends are", device.friends
                try:
                    model = get_model(email=friend_email)
                    friend = model.objects.get(email=friend_email)
                    friend.friends = str(list(set(eval(friend.friends) + [data['email']])))
                    friend.save()
                except Exception, e:
                    print "Error >> Here", str(e)
                    pass
        elif action == 'pending':
            device.pending_requests = str(list(set(eval(device.pending_requests) + [friend_email])))
            device.save()
        else:
            #Rejected
            device.pending_requests = str(list(set(eval(device.pending_requests)) - set([friend_email])))
            device.save()

    response = {'result': "success"} 
    return HttpResponse(json.dumps(response), content_type='application/json')
 
@csrf_exempt
def pending_requests(request, *args, **kwargs):
    print request.body
    data = eval(str(request.body))
    app_key = data['app_key']
    email = data['email'] # email of the user who sent the invitation
    model = get_model(email=data['email'])
    device = model.objects.get(email=data['email'])
    pending_reqs = eval(device.pending_requests)
    ios_friends = APNSDevices.objects.filter(email__in = pending_reqs).values('email', 'profile_pic', 'username')
    android_friends = GCMDevices.objects.filter(email__in = pending_reqs).values('email', 'profile_pic', 'username')
    result = list(android_friends) + list(ios_friends)
    return HttpResponse(json.dumps(result), content_type='application/json')
 

#To check the App registered devices
@csrf_exempt
def verify_registered_users(request, *args, **kwargs):
    print "Yes Im INNNN"
    #returns friends of the user
    print request.body
    data = eval(str(request.body))
    app_key = data['app_key']
    print app_key
    email = data['email']
    print email
    try:
        import ast
        model = get_model(email=email)
        device = model.objects.get(email=email)
        registered_friends = eval(device.friends)
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", registered_friends
        ios_friends = APNSDevices.objects.filter(email__in = registered_friends).values('email', 'profile_pic', 'username', 'status_message')
        android_friends = GCMDevices.objects.filter(email__in = registered_friends).values('email', 'profile_pic', 'username', 'status_message')
        result = list(android_friends) + list(ios_friends)
        
        print "result", result
    except Exception, e:
        print str(e)
        result = {'success': False}
    return HttpResponse(json.dumps(result), content_type='application/json')
      

@csrf_exempt
def verify_device_active(request, *args, **kwargs):
    print request.body
    data = eval(str(request.body))
    app_key = data['app_key']
    secret_key = data['secret_key']
    email = data['email']
    try:
        model = get_model(email=email)
        device = model.objects.get(email=email)
        registration_id = str(device.registration_id)
        COMMAND = '''curl -X GET -u "%s:%s"   -H "Content-type: application/json" -H "Accept: application/vnd.urbanairship+json; version=3;"  https://go.urbanairship.com/api/apids/%s/'''  %(app_key, secret_key, registration_id)
        result = commands.getoutput(COMMAND)
        result = eval(re.findall('(\{.*\})', result)[0].replace('true', 'True').replace('false', 'False'))
        active = result['active']
        response = {'active': active}
    except Exception, e:
        #Find an alternate when some error occurs
        response = {'active': False, 'error':str(e)}
    return HttpResponse(json.dumps(response), content_type='application/json')

 
#from mobile to mobile using urban airship
@csrf_exempt
def send_PN_to_device(request, *args, **kwargs):
    #{'email':[]}
    pending_messages = ''
    COMMAND = ''
    print 1
    print "Here", request.body
    data = eval(str(request.body).replace('true', 'True').replace('false', 'False'))
    print data
    email = data['email']
    if isinstance(email, (str, unicode)):
        email = [email]
       
    from_email = data['from_email']

    if data.has_key('channel_id'):
        channel_id = data["channel_id"]
        ios_members = list(APNSDevices.objects.filter(channels__channel_id = data['channel_id']).exclude(email=from_email).values_list('email', flat='true'))
        android_members = list(GCMDevices.objects.filter(channels__channel_id = data['channel_id']).exclude(email=from_email).values_list('email', flat='true'))
        email = ios_members + android_members 

    else:
        channel_id = ''

    app_key = data['app_key']
    message = str(data['message'])
    message_id = data['message_id']
    if data.has_key('message_type'):
        message_type = data["message_type"]
    else:
        message_type = 'message'

    if message_type == 'notification':
        if data.has_key('start_time') and data['start_time']:
            start_time = data['start_time']
            start_time = datetime.datetime.strptime(start_time, '%d-%m-%Y %I:%M %p')
        else:
            start_time = ''
        if data.has_key('end_time') and data['end_time']:
            end_time = data['end_time']
            end_time = datetime.datetime.strptime(end_time, '%d-%m-%Y %I:%M %p')
        else:
            end_time = ''
        #subject = data["subject"]

        if data.has_key('location') and data['location']:
            location = data['location']
        else:
            location = ''

        if data.has_key('body'):
            body = data["body"]
       
        #email = email + [from_email] #TODO: decide.. do we need to send it to user(self) as well??

    print 2
    #model = get_model(email=email)        
    #print model
    devices = list(APNSDevices.objects.filter(email__in=email, pn_status=True)) #app_key in filter
    devices = devices + list(GCMDevices.objects.filter(email__in=email, pn_status=True)) #app_key in filter
    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", devices
    for device in devices:
        #COMMAND = """curl -X POST -u "%s:%s"   -H "Content-Type: application/json"   --data '''{"device_tokens": %s, "aps": {"alert": "%s"}}'''    https://go.urbanairship.com/api/push/""" %(device.app_key, device.master_key, [str(device.registration_id)], message)
        if data.has_key('delivered') and device.device_type=='ios':
            print "Delivered key is present"
            try:
                
                from_device_model = get_model(email=from_email)
                from_device = from_device_model.objects.get(email=from_email, pn_status=True) #app_key
                
                if from_device.device_type == 'ios':
                    message_obj = Messages.objects.get(apns_devices=from_device, message_id=message_id, delivered=False, sent=True, from_email=device.email)
                else:
                    message_obj = Messages.objects.get(gcm_devices=from_device, message_id=message_id, delivered=False, sent=True, from_email=device.email)

                #message_obj.delivered=True
                #message_obj.save()
                if not message_obj.message_type == 'notification':
                    message_obj.delete()
                else:
                    message_obj.delivered = True
                    message_obj.save()
            except Exception, e:
                print "Should never come here", str(e)

            COMMAND = """curl -X POST -u "%s:%s"   -H "Content-Type: application/json"   --data '''{"aps":{"alert": %s },"device_tokens": %s,"email":"%s", "from_email":"%s", "delivered":"True", "message_id":"%s", "message_type":"%s", "channel_id":"%s"}'''    https://go.urbanairship.com/api/push/""" %(device.app_key, device.master_key, repr(message), [str(device.registration_id)], str(device.email), from_email, message_id, message_type, channel_id)
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
                    Messages.objects.get(apns_devices=device, delivered=False, sent=True, from_email=from_email)
                print "To be delivered messages are pending please wait"
                message_obj = Messages.objects.create(message=message, message_id=message_id, apns_devices=device, device_type=device.device_type, from_email=from_email, message_type=message_type) ## sent false and delivered false
                if message_type == 'notification':
                    message_obj.start_time = start_time#datetime.datetime.now() + datetime.timedelta(minutes=10)#start_time
                    message_obj.end_time = end_time#datetime.datetime.now() + datetime.timedelta(minutes=30)
                    message_obj.location = location
                    message_obj.subject = message#subject
                    message_obj.body = body 
                message_obj.save()
                #pending_messages = Messages.objects.filter(apns_devices=device, sent=False, delivered=False).order_by('id')
                print "messages added to the queue"
                #result={'result':'Saved in queue! Will be sent shortly!'}
                #return HttpResponse(json.dumps(result), content_type='application/json')
            except Exception, e:
                print "No Pending messages Found", str(e)
                try:
                    message_object = Messages.objects.create(message=message, message_id=message_id, apns_devices=device, device_type=device.device_type, from_email=from_email, message_type=message_type, sent=True) ## sent false and delivered false
                    if message_type == 'notification':
                        message_object.start_time = start_time#datetime.datetime.now() + datetime.timedelta(minutes=10)#start_time
                        message_object.end_time = end_time#datetime.datetime.now() + datetime.timedelta(minutes=30)#end_time
                        message_object.subject = message#subject
                        message_object.body = body 
                        message_object.location = location
                    print "Message sent and added into Messages queue with delivered=False"
                    message_object.save()
                    #pending_messages = Messages.objects.filter(apns_devices=device, sent=False, delivered=False).order_by('id')
                    #if pending_messages:
                    #    message_object.sent=False
                except Exception, e:
                    print "NOT SAVEDDDDDDD", str(e)
                COMMAND = """curl -X POST -u "%s:%s"   -H "Content-Type: application/json"   --data '''{"aps":{"alert":%s}, "options":{"expiry":%s}, "device_tokens": %s,"email":"%s", "from_email":"%s", "message_id": "%s", "message_type":"%s", "channel_id": "%s"}'''    https://go.urbanairship.com/api/push/""" %(device.app_key, device.master_key, repr(message), MESSAGE_EXPIRY, [str(device.registration_id)], str(device.email), from_email, message_id, message_type, channel_id)
                if message_type == 'notification':
                    COMMAND = """curl -X POST -u "%s:%s"   -H "Content-Type: application/json"   --data '''{"aps":{"alert":%s}, "options":{"expiry":%s}, "device_tokens": %s,"email":"%s", "from_email":"%s", "message_id": "%s", "message_type":"%s", "channel_id":"%s", "start_time":"%s", "end_time": "%s", "subject": %s, "body": %s, "location": "%s"}'''    https://go.urbanairship.com/api/push/""" %(device.app_key, device.master_key, repr(message), MESSAGE_EXPIRY, [str(device.registration_id)], str(device.email), from_email, message_id, message_type, channel_id, str(start_time), str(end_time), repr(message), repr(body), location)
                

        elif data.has_key('delivered') and device.device_type=='android':
            #import time
            #time.sleep(3)
            print "Inside android delivered"
            try:
                from_device_model = get_model(email=from_email)
                from_device = from_device_model.objects.get(email=from_email, pn_status=True) #app_key
                print "from_device.device_type", from_device.device_type
                if from_device.device_type == 'android':
                    message_obj = Messages.objects.get(gcm_devices=from_device, message_id=message_id, delivered=False, sent=True, from_email=device.email)
                else:
                    message_obj = Messages.objects.get(apns_devices=from_device, message_id=message_id, delivered=False, sent=True, from_email=device.email)
                print "Got the message with id %s and deliverd=True now" %message_id
                #message_obj.delivered=True
                #message_obj.save()
                if message_obj.message_type == 'message':  
                    message_obj.delete()
                else:
                    message_obj.delivered = True
                    message_obj.save()
            except Exception, e:
                print "Should never come here", str(e)
            print "NEXTTTTTTTTTTTTTTT"
            COMMAND = """curl -X POST -u "%s:%s"   -H "Content-type: application/json" -H "Accept: application/vnd.urbanairship+json; version=3;" --data '''{"audience":{"apid" : "%s"}, "notification":{"alert" : %s, "android":{"extra":%s}},"device_types":["android"]}''' https://go.urbanairship.com/api/push/""" %(device.app_key, device.master_key, device.registration_id, repr(message), {"email": str(device.email), "from_email":from_email, "message_id": message_id, "delivered":"True", "message_type": message_type, "channel_id": channel_id})
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
                    Messages.objects.get(gcm_devices=device, delivered=False, sent=True, from_email=from_email)
                print "To be delivered messages are pending please wait"
                message_obj = Messages.objects.create(message=message, message_id=message_id, gcm_devices=device, device_type=device.device_type, from_email=from_email, message_type=message_type) ## sent false and delivered false
                if message_type == 'notification':
                    message_obj.start_time = start_time#datetime.datetime.now() + datetime.timedelta(minutes=10) #start_time
                    message_obj.end_time = end_time#datetime.datetime.now() + datetime.timedelta(minutes=30) #end_time
                    message_obj.subject = message#subject
                    message_obj.location = location
                    message_obj.body = body 

                message_obj.save()
                #pending_messages = Messages.objects.filter(apns_devices=device, sent=False, delivered=False).order_by('id')
                print "messages added to the queue"
                #result={'result':'Saved in queue! Will be sent shortly!'}
                #return HttpResponse(json.dumps(result), content_type='application/json')
            except Exception, e:
                print "No Pending messages Found", str(e)
                try:
                    message_object = Messages.objects.create(message=message, message_id=message_id, gcm_devices=device, device_type=device.device_type, from_email=from_email, message_type=message_type, sent=True) ## sent false and delivered false
                    if message_type == 'notification':
                        message_object.start_time = start_time
                        message_object.end_time = end_time
                        message_object.subject = message#subject
                        message_object.body = body 
                        message_object.location = location

                    print "Message sent and added into Messages queue with delivered=False"
                    message_object.save()
                    #pending_messages = Messages.objects.filter(apns_devices=device, sent=False, delivered=False).order_by('id')
                    #if pending_messages:
                    #    message_object.sent=False
                except Exception, e:
                    print "NOT SAVEDDDDDDD", str(e)

                COMMAND = """curl -X POST -u "%s:%s"   -H "Content-type: application/json" -H "Accept: application/vnd.urbanairship+json; version=3;" --data '''{"audience":{"apid" : "%s"}, "notification":{"alert" : %s, "android":{"extra":%s, "time_to_live": 6000}},"device_types":["android"]}''' https://go.urbanairship.com/api/push/""" %(device.app_key, device.master_key, device.registration_id, repr(message), {"email":str(device.email), "from_email":from_email, "message_id": message_id, "message_type": message_type, "channel_id": channel_id})


                if message_type == 'notification':
                    COMMAND = """curl -X POST -u "%s:%s"   -H "Content-type: application/json" -H "Accept: application/vnd.urbanairship+json; version=3;" --data '''{"audience":{"apid" : "%s"}, "notification":{"alert" : %s, "android":{"extra":%s, "time_to_live": 6000}},"device_types":["android"]}''' https://go.urbanairship.com/api/push/""" %(device.app_key, device.master_key, device.registration_id, repr(message), {"email":str(device.email), "from_email":from_email, "message_id": message_id, "message_type": message_type, "channel_id": channel_id, "start_time": str(start_time), "end_time": str(end_time), "subject": str(message), "body": str(body), "location": location})

        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>."
        #print "COMMAND", COMMAND
        if COMMAND:
            COMMAND = str(COMMAND.replace("\'","\"" ).replace("\"\"\"", '\'\'\''))
            print COMMAND
            result = commands.getoutput(COMMAND)
            print "result", result
        
        if not data.has_key('delivered') and message_type == 'invitation':
            device.pending_requests = str(list(set(eval(device.pending_requests) + [from_email])))
            device.save()

        if pending_messages:
            #import time
            #time.sleep(1)
            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>", len(pending_messages)
            print "Since there are Pending messages. Triggering message"
            pending_message = pending_messages[0]
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
                    COMMAND = """curl -X POST -u "%s:%s"   -H "Content-Type: application/json"   --data '''{"aps":{"alert":%s},"device_tokens": %s,"email":"%s", "from_email":"%s", "message_id": "%s", "message_type":"%s", "channel_id": "%s"}'''    https://go.urbanairship.com/api/push/""" %(str(device.app_key), str(device.master_key), repr(str(pending_message.message)), [str(device.registration_id)], str(device.email), str(pending_message.from_email), str(pending_message.message_id), message_type, channel_id)
                    #if pending_message.message_type == 'notification':
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
                    COMMAND = """curl -X POST -u "%s:%s"   -H "Content-type: application/json" -H "Accept: application/vnd.urbanairship+json; version=3;" --data '''{"audience":{"apid" : "%s"}, "notification":{"alert" : %s, "android":{"extra":%s}},"device_types":["android"]}''' https://go.urbanairship.com/api/push/""" %(str(device.app_key), str(device.master_key), str(device.registration_id), repr(str(pending_message.message)), {"email":str(device.email), "from_email": str(pending_message.from_email), "message_id": str(pending_message.message_id), "message_type": message_type, "channel_id": channel_id})
                    if pending_message.message_type=='notification':
                        COMMAND = """curl -X POST -u "%s:%s"   -H "Content-type: application/json" -H "Accept: application/vnd.urbanairship+json; version=3;" --data '''{"audience":{"apid" : "%s"}, "notification":{"alert" : %s, "android":{"extra":%s, "time_to_live": 6000}},"device_types":["android"]}''' https://go.urbanairship.com/api/push/""" %(device.app_key, device.master_key, device.registration_id, repr(pending_message.message), {"email":str(device.email), "from_email": str(pending_message.from_email), "message_id": str(pending_message.message_id), "message_type": str(pending_message.message_type), "start_time": str(pending_message.start_time), "end_time": str(pending_message.end_time), "subject": str(pending_message.message), "body": str(pending_message.body), "location": str(pending_message.location)})
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
    email = data['email']
    app_key = data['app_key']
    status = data['status']
    try:
        model = get_model(email=email)
        device = model.objects.get(app_key=app_key, email=email)
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

'''
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
'''

@csrf_exempt
def urbanairship_set_channels(request):
    '''
	{
	'channel_id': '123456',
	'app_key': 'abc123',
	'channel_name': 'AlphaTeam',
	'email': 'prakash.p@embitel.com',
	'group_members': ['mayank.j@embitel.com', 'jeevan.v@embitel.com']
	}
    '''
    #operation = data['operation'] # add/delete/edit
    data = eval(str(request.body))
    channel_id = data['channel_id']
    app_key = data['app_key']
    channel_name = data['channel_name']
    email = data['email']
    if data.has_key('group_members'):
        group_members = data['group_members'] + [email]
    else:
        group_members = []
    try:
        channel_obj = Channels.objects.get(channel_id=data['channel_id'])
        channel_obj.channel_name = channel_name
        channel_obj.save()
    except:
        channel_obj = Channels.objects.create(channel_id=channel_id, channel_name=channel_name, admin=email)
        channel_obj.save()

    if group_members:
        for group_member in group_members:
            device_model = get_model(email=group_member)
            device = device_model.objects.get(email=group_member) #app_key
            device.channels.add(channel_obj)
            device.save()

    ios_members = APNSDevices.objects.filter(channels__channel_id = channel_id).extra(select={'admin': "email = '%s'"%channel_obj.admin}).values('email', 'admin')
    android_members = GCMDevices.objects.filter(channels__channel_id = channel_id).extra(select={'admin': "email = '%s'"%channel_obj.admin}).values('email', 'admin')
    result = list(android_members) + list(ios_members)
    return HttpResponse(json.dumps(result), content_type='application/json')

@csrf_exempt
def urbanairship_delete_from_channels(request):
    '''
	    {
		'channel_id': '123456',
		'app_key': 'abc123',
		'channel_name': 'AlphaTeam',
		'email': 'mayank.j@embitel.com',
	     }	
    '''
    data = eval(str(request.body))
    channel_id = data['channel_id']
    app_key = data['app_key']
    channel_name = data['channel_name']
    email = data['email']
    try:
        channel_obj = Channels.objects.get(channel_id=data['channel_id'])
    except:
        channel_obj = ''

    if channel_obj:
        device_model = get_model(email=email)
        device = device_model.objects.get(email=email) #app_key
        device.channels.remove(channel_obj)
        device.save()

    result = {}
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
    users = APNSDevices.objects.filter(p12_certificate=p12_obj).values_list('email', flat='true')
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
            device_ids = list(APNSDevices.objects.filter(p12_certificate=p12_certificate, email__in=users).extra(where=['CHAR_LENGTH(registration_id) = 64']).values_list('registration_id', flat='true'))
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
