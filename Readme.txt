Book bus details online with the bus ticketing platform - redBus.
Compare the ticket prices, find bus schedules.
Usage of the files :
tbl.sql       :  create table scripts related to this project
Routes.py     :  Its itermediate page to collects all routes of 10 states of Goverment bus and also other private buses 
                 and stored it in sql table. Based on this routes collection the next page [Busdetails.py] 
                 will collect the individual bus details like (route_name, busname, bustype,Departure,
                  Duration, Arrival, Fare, seats_available star_rating)
Busdetails.py :  Its itermediate page which is used to collect all the data from respective Url's 
                 using Web Scraping with Selenium technology and storing this data to sql 
RedBus.py     :  Its UI page which is in streamlit technology and pandas and postgresql 
                 which is used to create an a interactive page for Data Analysis 
                 to compare the prices and find bus schedules
