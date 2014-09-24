from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from lxml import html
import sys

from pyvirtualdisplay import Display


def leave_management(Id, pwd):
    #chromedriver = "/home/embadmin/Downloads/selenium/chromedriver"
    #browser = webdriver.Chrome(chromedriver)

    display = Display(visible=0, size=(800, 600))
    display.start()

    browser = webdriver.Firefox()
    browser.get('http://10.99.99.120/hrms/Login.aspx')

    python_link = browser.find_elements_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_Login_UserName']")[0]  
    python_link.send_keys(Id)

    python_link = browser.find_elements_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_Login_Password']")[0]  
    python_link.send_keys(pwd)

    python_link = browser.find_elements_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_Login_LoginButton']")[0]  
    python_link.click()

    try:
        python_link = browser.find_elements_by_xpath("//a[@id='ctl00_ctl00_ContentPlaceHolder1_LeaveManagement']")[0]  
        python_link.click()
    except:
        browser.close()
        display.stop()
        return {}

    import time
    time.sleep(2)

    source_code = browser.page_source
    source_code = source_code.encode('utf-8')
    browser.close()
    display.stop()

    doc = html.fromstring(source_code)
    table = doc.xpath('//table[@id[contains(string(), "MyLeaveSummaryTab_MyLeaveSummary_GridView1")]]')
    if table:
        table = table[0]
    else:
        result = {}
        return result
        sys.exit()


    trs = table.xpath('.//tr')

    result = {}
    for tr in trs:
        try:
            type_of_leave, entitled, taken, balance = tr.xpath('.//td//text()')
            result[type_of_leave] = {'entitled': int(entitled), 'taken': int(taken), 'balance': int(balance)}
        except Exception, e:
            continue

    print "\n\n\n\n\n"
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(result)
    print "\n\n\n\n\n"
    return result

#leave_management(1298, 1298)
