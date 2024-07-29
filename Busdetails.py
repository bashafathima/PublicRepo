from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import psycopg2 as pg
import time ,os,re
import pandas as pd
from numpy import nan
from datetime import datetime, timedelta


options= webdriver.ChromeOptions()
chrome_options = Options()
service=Service(executable_path='./chromedriver_win32.exe')
chrome_options.add_argument("--headless")  # Ensure GUI is off
chrome_options.add_argument("--disable-gpu")  # Disable GPU usage for stability
chrome_options.add_experimental_option('excludeSwitch',['enable-logging']) 
chrome_options.add_argument('--log-level=3') 
os.system('cls')
replacements = {'h': '', 'm': ''}
con = pg.connect(database="Casestudy1",user="postgres",password="1234567",host="localhost",port="5432")
cursor=con.cursor()

# cursor.execute("SELECT * from bus_routes")

# # Fetch all rows from database
# record = cursor.fetchall()

# print("Data from Database:- ", record)

def scroll_down_all(driver, pause_sec=1):
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Pause
        time.sleep(pause_sec)
        # After scroll down, get current height.
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
# Set up Chrome options
def custom_todatetime(s):
    """
    split date/time string formatted as 'DD/MM/YYYY hh:mm:ss' into date and time parts.
    parse date part to datetime and add time part as timedelta.
    """
    parts = s.split(' ')
    seconds = sum(int(x) * 60 ** i for i, x in enumerate(reversed(parts[1].split(':'))))
    return datetime.strptime(parts[0], "%d/%m/%Y") + timedelta(seconds=seconds)


def fetch_data(query, conn,param=""):
    try:
        if param == "":
            df = pd.read_sql(query, conn)
        else:
            df = pd.read_sql(query, conn,params=param)
        return df
    except pg.Error as e:
        print(f"Error executing query: {e}")

def Exract_dus_details(lst):
    for bus in lst:
        bus_name = bus.find_element(By.CLASS_NAME,'travels').text
        bus_name = re.sub("'", '', bus_name)  
        bus_type = bus.find_element(By.CLASS_NAME,'bus-type').text
        dep_time= bus.find_element(By.CLASS_NAME,'dp-time').text
        # departure_time_obj = datetime.strptime(dep_time, '%H:%M')
        dep_time="08-Jul-2024 "+dep_time
        start_time=bus.find_element(By.CLASS_NAME,'bp-time').text
        seat_availability_element = bus.find_element(By.CSS_SELECTOR, "div.seat-left")
        seat_availability ="".join(char for char in seat_availability_element.text.strip() if char.isnumeric()) 
        rating_element = driver.find_element(By.CSS_SELECTOR, "div.rating")
        rating = rating_element.text.strip()
        dur= bus.find_element(By.CLASS_NAME,'dur').text
        dur = ''.join([replacements.get(char, char) for char in dur])
        prices= bus.find_element(By.CLASS_NAME,'fare').text
        prices_rnumbers = "".join([char for char in prices if char.isnumeric()])
        
        departure_time_obj = datetime.strptime(dep_time, '%d-%b-%Y %H:%M')
        if(int(str(dur)[:2])<= 24):
            duration_obj = datetime.strptime(dur , '%H %M')
        else:
            duration_obj = datetime.strptime(custom_todatetime(dur) , '%H %M')
        arrival_time = departure_time_obj + timedelta(hours=duration_obj.hour, minutes=duration_obj.minute, seconds=duration_obj.second)
        qry ='''INSERT INTO bus_routes  
            (route_name,busname, bustype, departing_time, duration, price,star_rating,reaching_time,seats_available) 
        VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s')'''% (tile,bus_name,bus_type,dep_time,start_time,prices_rnumbers,rating,arrival_time,seat_availability)
        # print(qry)
        cursor.execute(qry)
        con.commit()
    cnt=cursor.rowcount
    return cnt,"Record inserted successfully into bus_routes table"

# url = "https://www.redbus.in/bus-tickets/thanjavur-to-chennai?fromCityName=Thanjavur&fromCityId=66007&srcCountry=IND&toCityName=Chennai&toCityId=123&destCountry=IND&onward=08-Jul-2024&opId=0&busType=Any"

try:
    
    qry="select Route_Link,Route_Name from Routes where isdone is null "
    cursor.execute(qry)
    con.commit()
    lst = cursor.fetchall()
    for Route_Link,Route_Name in lst:
        
        driver=webdriver.Chrome()
        # driver.implicitly_wait(100)  # Implicit wait to handle synchronization
        print(Route_Link)
        url= Route_Link
        # Open the URL in headless mode
        driver.get(url)
        scroll_down_all(driver, pause_sec=1) 
        time.sleep(5);
        tile=Route_Name
        try:
            Govt_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'group-data') and contains(@class, 'clearfix')]")
            if Govt_elements:
                print(f"Found {len(Govt_elements)} Govt Buses.")
            # Iterate over the elements and perform actions
                for element in Govt_elements:
                    print(element.text)  # Print the text content of each element
                view_buses_button = WebDriverWait(driver, 50).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'button') and contains(text(), 'View Buses')]"))
                )
                for button in view_buses_button:
                    driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    driver.execute_script("arguments[0].click();", button)
                    
                time.sleep(5)
            else:
                print("Govt buses not found.")
        except TimeoutException:
            print("Govt elements not found within the timeout period.")
        try:
            scroll_down_all(driver, pause_sec=1) 
            WebDriverWait(driver, 100).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "bus-items"))
                )
          
            bus_services = driver.find_elements(By.CLASS_NAME, "bus-item")
            Exract_dus_details(bus_services)
            driver.quit()
        except TimeoutException:
            print("Private Bus not found within the timeout period.")

       
    # -- Below code is one time data fetch filter Parameter
    # qry="truncate table dept_time RESTART IDENTITY"
    # cursor.execute(qry)
    # con.commit()
    # qry=""
    # # Print the filters
    # for filter_name in deptime_filters:
    #     filter_name=re.sub("\(.*?\)"," ",filter_name).rstrip()
    #     qry ='''INSERT INTO dept_time (TimeName)VALUES('%s')'''% (filter_name)
    #     # print(qry)
    #     cursor.execute(qry)
    #     con.commit()
    # qry ='DELETE from dept_time s1 USING dept_time s2 where s1.id > s2.id and s1.TimeName = s2.TimeName'
    # cursor.execute(qry)
    # con.commit()
    # qry=""
    # qry="truncate table bus_type RESTART IDENTITY"
    # cursor.execute(qry)
    # con.commit()
    # qry=""
    # bustype_element = filters_section.find_elements(By.XPATH, "//ul[contains(@class, 'list-chkbox')]//li")
    # bustype_filters = [filter_element.text.strip() for filter_element in bustype_element]
    # for filter_name in bustype_filters:
    #     filter_name=re.sub("\(.*?\)"," ",filter_name).rstrip()
    #     qry ='''INSERT INTO bus_type (bus_type)VALUES('%s')'''% (filter_name)
    #     # print(qry)
    #     cursor.execute(qry)
    #     con.commit()

    # amenity_element = filters_section.find_elements(By.XPATH, "//ul[contains(@class, 'amenity-list')]//li")
    # amenity_filters = [filter_element.text.strip() for filter_element in amenity_element]
    # for filter_name in amenity_filters:
    #     print("amenity_Filter",filter_name)
    # qry="truncate table bus_routes RESTART IDENTITY"
    # cursor.execute(qry)
    # con.commit()
    # Find all the bus services
    
    # df=pd.DataFrame(bus_services)
    # print(df)
    # Print the bus services
        # print(f"Bus: {bus_name} | Dep :{dep_time} | Duration :{dur} | Price : {prices}| Arrival time: {arr_time} | rating: {rating}")


finally:
    # Close the browser window

    cursor.close()
    con.close()
    
   
