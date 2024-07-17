import streamlit as st
import pandas as pd
import psycopg2 as pg
from datetime import datetime
import sys,re
try :
    def create_connection():
        engine = pg.connect(database="Casestudy1",user="postgres",password="1234567",host="localhost",port="5432")
        print("Connected to PostgreSQL database!")
        return engine
except pg.Error as e:
        print(f"Error connecting to PostgreSQL database: {e}")
    # Function to fetch data from PostgreSQL into a DataFrame
def fetch_data(query, conn,param=""):
    try:
        if param == "":
            df = pd.read_sql(query, conn)
        else:
            df = pd.read_sql(query, conn,params=param)
        return df
    except pg.Error as e:
        print(f"Error executing query: {e}")
def Removecomma(lst):
    res = [string[:-1] if string =="," else string for string in [string.rsplit(' ', 1)[0] for string in lst]]
    return res 
st.set_page_config(page_title="Bus Details",
                    layout='wide',
                    initial_sidebar_state="expanded")
 
conn = create_connection()
cursor=conn.cursor()
def selectQuery(selectQry):
     df = fetch_data(selectQry, conn)
     return df
def AllRoute():
    query = '''select state_name,route_name, SPLIT_PART(route_name,'to',1)fromroute,
        SPLIT_PART(route_name,'to',2)toroute,isdone from routes '''
    df = fetch_data(query, conn)
    df= df.loc[(df["isdone"] == "1")] 
    return df
dfAllRoute =AllRoute()
def get_unique_values(tbl,column_name):
    return tbl[column_name].unique()
header_left,header_mid,header_right = st.columns([1,12,1],gap = "large")
def AllBuses():
    query = '''SELECT route_name, busname, bustype, to_char(departing_time, 'hh24:mi') as Departure,
            duration as Duration, to_char(reaching_time, 'hh24:mi') as Arrival, 
            price as Fare, seats_available as SeatsAvailable,star_rating as Ratings FROM bus_routes ;'''
    df = fetch_data(query, conn)
    return df
def Sort():
    data = { 'Low': [0]  ,'High': [1]}
    df = pd.DataFrame(data)
    return df

def load_data():
    with header_mid:
        
        dfallBuses=AllBuses()
        dfsort =Sort()
        with st.sidebar:
            State_List = get_unique_values(dfAllRoute,'state_name')
            State_Selected = st.selectbox("States:",State_List)
            if State_Selected:
                df =dfAllRoute[dfAllRoute['state_name'].isin([State_Selected])]
                From_List = get_unique_values(df,'fromroute')
                SelectedFrom_List = st.selectbox("From :",From_List)
                To_List = get_unique_values(df,'toroute')
                SelectedTo_List = st.selectbox("To :",To_List)
            sort_column = st.selectbox('Select column to sort by:', dfallBuses.columns[3:])
            sort_asc = st.selectbox('Sort ', dfsort.columns[0:])
    
        new = dfallBuses["route_name"].str.split("to", n = 1, expand = True)  
        dfallBuses["From Route"]= new[0]
        dfallBuses["To Route"]= new[1]
        dfallBuses.drop(columns =["route_name"], inplace = True)
        if SelectedFrom_List or SelectedTo_List:
            selected_bus = dfallBuses.loc[(dfallBuses["From Route"] == SelectedFrom_List)
                                & (dfallBuses["To Route"] == SelectedTo_List)
                                ] 
        selected_bus=selected_bus[selected_bus.columns[0:8]]
        if sort_column and sort_asc:
            if sort_asc == "Low":
                selected_bus = selected_bus.sort_values(by=[sort_column], ascending=True)
            else:
                selected_bus = selected_bus.sort_values(by=[sort_column], ascending=False)
        st.title(f"Bus Details From : {SelectedFrom_List} -  {SelectedTo_List} " )
        st.dataframe(selected_bus,hide_index=True)
        conn.close()

if __name__ == '__main__':
    load_data()  # Ensure data is loaded on app start

