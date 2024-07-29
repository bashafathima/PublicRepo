import psycopg2,os,time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import numpy as np

os.system('cls')
data = [
     ['https://www.redbus.in/online-booking/apsrtc/?utm_source=rtchometile','APSRTC'],
    ['https://www.redbus.in/online-booking/ksrtc-kerala/?utm_source=rtchometile','KSRTC'],
    ['https://www.redbus.in/online-booking/tsrtc/?utm_source=rtchometile','TSRTC'],
['https://www.redbus.in/online-booking/ktcl/?utm_source=rtchometile','KTCL']
,['https://www.redbus.in/online-booking/rsrtc/?utm_source=rtchometile','RSRTC'],
['https://www.redbus.in/online-booking/south-bengal-state-transport-corporation-sbstc/?utm_source=rtchometile','SBSTC'],
['https://www.redbus.in/online-booking/hrtc/?utm_source=rtchometile','HRTC'],
['https://www.redbus.in/online-booking/astc/?utm_source=rtchometile','ASTC'],
['https://www.redbus.in/online-booking/uttar-pradesh-state-road-transport-corporation-upsrtc/?utm_source=rtchometile','UPSRTC'],
['https://www.redbus.in/online-booking/wbtc-ctc/?utm_source=rtchometile','WBTC']
]

def Extract_Routes(lst):
    for div in lst:
            div_text = div.text.splitlines()
            div_text =div_text[0]
            anchor_tag = div.find_element(By.LINK_TEXT, div_text)
            href_value = anchor_tag.get_attribute('href')
            qry ='''INSERT INTO Routes  
                (state_name,Route_Name,Route_Link) VALUES('%s','%s','%s')'''% (state,div_text,href_value)
            print(qry)
            cursor.execute(qry)
            con.commit()

numpy_array = np.array(data)
list_from_numpy = numpy_array.tolist()
for i in list_from_numpy:
    url,state = i[0],i[1]
    service=Service(executable_path='./chromedriver_win32.exe')
    con = psycopg2.connect(database="Casestudy1",user="postgres",password="1234567",host="localhost",port="5432")
    cursor=con.cursor()
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Optional: run in headless mode without opening browser window
    options= webdriver.ChromeOptions()
    driver=webdriver.Chrome()
    driver.get(url)
    action=ActionChains(driver)
    page =[]
    wait=WebDriverWait(driver,20)
    try:
        WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.CLASS_NAME, 'DC_117_paginationTable')))
        
        # Find all pagination items (page numbers)
        pagination_items = driver.find_elements(By.CLASS_NAME, 'DC_117_paginationTable')
        
        js_add_class = """
        var element = document.querySelector(".DC_117_pageTabs");
        if (element) {
            element.classList.add(" DC_117_pageActive");
        }
        """
        for index, element in enumerate(pagination_items):
            result = element.text.split('\n')
        for i in range(len(result)):
            try:
                page_tab_text = result[i]
                if(page_tab_text=='1'):
                    div_elements = driver.find_elements(By.CLASS_NAME, 'route_link')
                    Extract_Routes(div_elements)
                else:
                    page= wait.until(EC.presence_of_element_located((By.XPATH,'//*[@class="DC_117_paginationTable"]')))
                    driver.execute_script("arguments[0].scrollIntoView();", page)
                    next=page.find_element(By.XPATH,f'//div[@class="DC_117_pageTabs " and text()={page_tab_text}]')
                    time.sleep(10)
                    next.click()
                    div_elements = driver.find_elements(By.CLASS_NAME, 'route_link')
                    Extract_Routes(div_elements)
                
               
            except Exception as e:
                print(f"No more pages or an error occurred: {e}")
                break
        
        
    finally:
        # Close the WebDriver session
        driver.quit()
        cursor.close()
        con.close()
