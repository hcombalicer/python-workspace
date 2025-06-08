"""
Testing Selenium
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# PATH = "/Users/haroldcombalicer/Documents/Chromedriver/chromedriver"
driver = webdriver.Chrome()

driver.get("https://www.investagrams.com/Stock/PSE:JFC")
time.sleep(5)

price = driver.find_element(By.CSS_SELECTOR, "h4.fs-24.invg-matte-black.fw-700.ng-binding")
print(price.text)
input("Press Enter to close the browser...")
driver.quit()
