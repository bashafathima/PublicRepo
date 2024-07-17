import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import numpy as np

data = [
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

    try:
        div_elements = driver.find_elements(By.CLASS_NAME, 'route_link')
        # Loop through each div element
        Extract_Routes(div_elements)
    finally:
        # Close the WebDriver session
        driver.quit()
        cursor.close()
        con.close()
