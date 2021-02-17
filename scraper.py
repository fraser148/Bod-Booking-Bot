# Bodleian Booker Bot

import time
import json
import datetime
import threading
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

# Define preference dictionary
preference = {"UPPER BOD":["Upper Reading Room Desk Booking","10:00","13:00","16:30"],
"LOWER BOD":["Lower Reading Room Desk Booking","10:00","13:00","16:30"],
"LAW LIB":["Law Library Desk Booking","10:00","13:00","16:30"]}

# Check if the xpath exists on the webpage
def hasXpath(xpath,driver):
    try:
        driver.find_element_by_xpath(xpath)
        return True
    except:
        return False

# Highlight an element defined by the driver
def highlight(element):
    # Highlights a Selenium webdriver element
    driver = element._parent
    def apply_style(s):
        driver.execute_script("arguments[0].setAttribute('style', arguments[1])", element, s)
    orignal_style = element.get_attribute('style')
    apply_style("border: 4px solid red")
    if (element.get_attribute("style")!=None):
        time.sleep(5)
    apply_style(orignal_style)

# Click through the bookng process
def book(userdata, service, time_day):
    global preference

    # Login to SSO
    driver = webdriver.Remote(service.service_url)
    driver.get('https://spacefinder.bodleian.ox.ac.uk/')
    time.sleep(1)
    email = driver.find_element_by_id('i0116')
    email.send_keys(userdata[1]['username'])
    time.sleep(0.5)
    submit = driver.find_element_by_id("idSIButton9")
    submit.click()
    time.sleep(1)
    password = driver.find_element_by_id("i0118")
    password.send_keys(userdata[1]['password'])
    time.sleep(1)
    signin = driver.find_element_by_id("idSIButton9")
    signin.click()
    #time.sleep(6)
    # Click on calendar date until it the element loads
    # BUG: Wait until 10am and then refresh the page.
    okay = False
    while okay != True:
        try:
            calendar = driver.find_element_by_xpath("//span[@aria-label='" + day + "']")
            calendar.click()
            okay = True
        except:
            print("Calendar loading")
    # Clicking on slot until it loads
    okay = False
    if time_day == "morning":
        indexx = 1
    elif time_day == "afternoon":
        indexx = 2
    else:
        indexx = 3
    NO_SLOTS = 0
    while okay != True:
        try:
            # NOT PASSING PREFERENCES
            slot = driver.find_element_by_xpath("//div[contains(h5, '"+preference[userdata[2][time_day]][0]+"') and contains(p, '"+preference[userdata[2][time_day]][indexx]+"')]/parent::*/descendant::a")
            #highlight(slot)
            slot.click()
            okay = True
        except:
            xpather = "//h3[contains(text(), 'Sorry, no spaces found')]"
            xpather2 = "//div[contains(@class, 'tickets__submit')]"
            if hasXpath(xpather,driver):
                print("NO MORE SLOTS")
            elif hasXpath(xpather2,driver):
                print("NO MORE SLOTS FOR THIS SPECIFIC ONE")
                NO_SLOTS +=1
                if NO_SLOTS > 3:
                    return
            else:
                print("Slots are loading")
    okay = False
    while okay != True:
        try:
            confirm = driver.find_element_by_name("ctl00$ContentPlaceHolder$Cart$CheckoutButton")
            confirm.click()
            okay = True
        except:
            print("Loading!")
    okay = False
    while okay != True:
        try:
            for key in userdata[0]:
                element = driver.find_element_by_id(key)
                element.send_keys(userdata[0][key])
            confirm = driver.find_element_by_id("submitOrderButton")
            confirm.click()
            okay = True
        except:
            print("Loading Form!")
    time.sleep(20)
    

ids = ["FirstNameundefined","LastNameundefined","Phoneundefined","Street2undefined","Emailundefined","ConfirmEmailundefined"]

# Gets data from json file and returns a dictionary of lists for user data
userdata = {}
try:
    with open('data.json') as json_file:
        data = json.load(json_file)
        for p in data['users']:
            current_user = p
            temp = []
            userdata[current_user] = [data['users'][p][item] for item in data['users'][p]]
except:
    with open('userdata.json') as json_file:
        data = json.load(json_file)
        for p in data['users']:
            current_user = p
            temp = []
            userdata[current_user] = [data['users'][p][item] for item in data['users'][p]]

userkeys = []
index = 0
for user in userdata:
    userdata[user].insert(4,userdata[user][-4])
    userkeys.append([dict(zip(ids, userdata[user][0:6]))])
    userkeys[int(index)].append({"username":userdata[user][8]['username'],"password":userdata[user][8]['password']})
    userkeys[int(index)].append({"morning":userdata[user][7]['morning'],"afternoon":userdata[user][7]['afternoon'],"evening":userdata[user][7]['evening']})
    index += 1

# BUG Date has an extra 0 ie 08 but must be in form 8 instead ie February 8, 2021
NextDay_Date = datetime.datetime.today() + datetime.timedelta(days=2)
#day = NextDay_Date.strftime("%B %d, %Y").replace(" 0", " ")
day = NextDay_Date.strftime("%B %d, %Y")

service = Service('chromedriver.exe')
service.start()
threads = []
times = ["morning","afternoon","evening"]
for user in userkeys:
    for i in times:
        print("Thread Started")
        t = threading.Thread(target=book, args=(user,service,i))
        threads.append(t)
        t.start()