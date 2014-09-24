#!/home/embadmin/Documents/django_apps/django_experiments/bin/env python
import sys, os
sys.path.append(os.path.abspath('..'))
sys.path.append('/home/embadmin/Documents/django_apps/django_experiments/embitel')
sys.path.append('/home/embadmin/Documents/django_apps/django_experiments/embitel/embitel_framework')
import settings
#from django.core.management import setup_environ
#setup_environ(settings)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "embitel_framework.settings")


from embitel_framework.models import Groups
import datetime

def teams():
	fi = open('team.csv', 'r')
	lines = fi.readlines()
	fi.close()
	for line in lines:
	    line = line.strip()
	    name, email, dob, group = line.split(',')
	    dob = dob.replace('st', '').replace('nd', '').replace('rd', '').replace('th', '').title().replace('Augu', 'August').strip()
            if dob:
                try:
     	            dob = datetime.datetime.strptime(dob, '%d %B').date()
                except Exception, e:
                    dob = datetime.datetime.strptime(dob, '%d %b').date()
	    try:
		g = Groups.objects.get(email=email)
		g.username = name
                if dob:
		    g.dob = dob
		g.group_name = group
		g.save()
	    except Exception, e:
		g = Groups.objects.create(email=email, username=name, group_name=group)
                if dob:
                    g.dob = dob
		g.save()
	    
	return True

