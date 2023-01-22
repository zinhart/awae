import argparse
import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options




parser = argparse.ArgumentParser()
parser.add_argument('--token', help='rdp token', type=str, required=True)
args = parser.parse_args()

try:
    token = args.token
    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options)
    url = "http://chips/rdp?token="+token+"&width=1762&height=167"
    browser.get(url)
    #print(brower.page_source)
finally:
    try:
        browser.close()
        print("success")
    except:
        print("fail")
sys.exit(0)