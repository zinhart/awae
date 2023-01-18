import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options





try:
    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options)
    url = "http://chips/"
    browser.get(url)
    #print(brower.page_source)
finally:
    try:
        browser.close()
        print("success")
    except:
        print("fail")
sys.exit(0)