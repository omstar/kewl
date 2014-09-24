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
fi = open('team.csv', 'r')
lines = fi.readlines()
fi.close()
for line in lines:
    line = line.strip()
    print line
    name, email, dob, group = line.split(',')
    dob = dob.replace('st', '').replace('nd', '').replace('rd', '').replace('th', '').replace('Augu', 'August')
    dob = datetime.datetime.strptime(dob, '%d %B').date()
    try:
        g = Groups.objects.get(email=email)
        g.username = name
        g.dob = dob
        g.group_name = group
        g.save()
    except:
        g = Groups.objects.create(email=email, username=name, dob=dob, group_name=group)
        g.save()
    

