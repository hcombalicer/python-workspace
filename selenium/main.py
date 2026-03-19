"""
Testing Selenium
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# PATH = "/Users/haroldcombalicer/Documents/Chromedriver/chromedriver"
driver = webdriver.Chrome()

stock_codes = ["JFC", "MER", "SCC"]
all_stocks_data = {}
for stock_code in stock_codes:
    driver.get("https://www.investagrams.com/Stock/PSE:" + stock_code)
    time.sleep(5)
    current_stock_data = {
        "price": "N/A",
        "percent_change": "N/A",
        "value_change": "N/A",
        "dividend_yield": "N/A",
        "pe_ratio": "N/A",
    }
    price_element = driver.find_element(By.CSS_SELECTOR,
                                "h4[data-ng-class='ViewStockPage.Data.Stock.LatestStockHistory.LastClass']")
    current_stock_data["price"] = price_element.text.strip()
    percent_change_element = driver.find_element(By.CSS_SELECTOR,
                                        "div.data-badge-color[data-ng-show*='ViewStockPage.Data.Stock.LatestStockHistory.ChangePercentage']:not(.ng-hide)")
    current_stock_data["percent_change"] =percent_change_element.text.strip()
    value_change_element = driver.find_element(By.CSS_SELECTOR,
                                    "span.fs-14.fw-700.ng-binding")
    current_stock_data["value_change"] = value_change_element.text.strip()
    dividend_yield_element = driver.find_element(By.CSS_SELECTOR,
                                    "td[data-ng-class*='IsConsistentCashDiv']")
    current_stock_data["dividend_yield"] = dividend_yield_element.text.strip()
    pe_ratio_element = driver.find_element(By.CSS_SELECTOR,
                            "td[data-ng-class*='PriceEarningsRatio']")
    current_stock_data["pe_ratio"] = pe_ratio_element.text.strip()
    all_stocks_data[stock_code] = current_stock_data

print(json.dumps(all_stocks_data, indent=4))

input("Press Enter to close the browser...")
driver.quit()
