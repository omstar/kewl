from lxml import html
import commands
import urllib
import time

url = 'http://10.99.99.117/embintra/index.php/Team'


def get_team_members():
	fi = open('team.csv', 'w')
	raw_data = urllib.urlopen(url).read()
	doc = html.fromstring(raw_data)
	employees = doc.xpath('//table[@border="1"]//tr')
	print employees
	for employee in employees:
	    details = employee.xpath('.//td//text()')
	    department =''.join(employee.xpath('./preceding-sibling::h2//span/b/text()')).replace("(", "").replace(")", "").strip()

	    if details:
		fi.write('%s,%s,%s,%s\n' %(details[1].strip(), details[2].strip(), details[4].strip(), department))
		print details[1].strip(), details[2].strip(), details[4].strip(), department
	fi.close()
	return True
