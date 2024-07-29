import streamlit as st
import pandas as pd
import psycopg2 as pg
from datetime import datetime
from datetime import date, timedelta
import numpy as np
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
def AllBusesFilters(filters =None,sort_by=None, sort_order='ASC'):
    base_query = '''SELECT route_name,SPLIT_PART(duration, ':', 1)durhrs,
            SPLIT_PART(duration, ':', 2)dursec, busname, bustype, 
            to_char(departing_time, 'hh24:mi') as departure,
            duration as Duration, to_char(reaching_time, 'hh24:mi') as Arrival, 
            price as Fare, seats_available as SeatsAvailable,star_rating as Ratings FROM bus_routes  '''
    query = base_query
    params = []
    if filters:
        query += " WHERE "
        conditions = []
        for key, value in filters.items():
            conditions.append(f"{key} ='{str(value).strip()}'")
            params.append(value)
        query += " AND ".join(conditions)
    if sort_by:
        # Validate sort_order
        if sort_order.upper() not in ['ASC', 'DESC']:
            sort_order = 'ASC'
        
        query += f" ORDER BY {sort_by} {sort_order}"

    # print("Executing query:", query)
    # print("With parameters:", params)
    df = fetch_data(query, conn,params)
    return df
dfAllRoute =AllRoute()
def get_unique_values(tbl,column_name):
    return tbl[column_name].unique()
header_left,header_mid,header_right = st.columns([1,25,1],gap = "small",vertical_alignment="top")
def AllBuses():
    query = '''SELECT route_name,SPLIT_PART(duration, ':', 1)durhrs,
            SPLIT_PART(duration, ':', 2)dursec, busname, bustype, 
            to_char(departing_time, 'hh24:mi') as departure,
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
            State_Selected = st.selectbox("STATE:",State_List)
            if State_Selected:
                df =dfAllRoute[dfAllRoute['state_name'].isin([State_Selected])]
                From_List = get_unique_values(df,'fromroute')
                SelectedFrom_List = st.selectbox("FROM :",From_List)
                To_List = get_unique_values(df,'toroute')
                SelectedTo_List = st.selectbox("TO :",To_List)
                today = date.today()
                start_date = st.date_input('ONWARD DATE', key='start',min_value=today)
                
            sort_column = st.selectbox('Select column to sort by:', dfallBuses.columns[3:])
            sort_asc = st.selectbox('Sort ', dfsort.columns[0:])
        
        new = dfallBuses["route_name"].str.split("to", n = 1, expand = True)  
        dfallBuses["From Route"]= new[0]
        dfallBuses["To Route"]= new[1]
        dfallBuses.drop(columns =["route_name"], inplace = True)
        if SelectedFrom_List or SelectedTo_List:
            filters = {
                        'route_name': SelectedFrom_List + "to" + SelectedTo_List,
                      }
        
        if sort_column and sort_asc:
            sort_by = sort_column
            if sort_asc == "Low":
                 sort_order = 'ASC'  # or 'ASC'
            else:
                sort_order = 'DESC'  # or 'ASC'
        # st.title(f"Bus Details From : {SelectedFrom_List} -  {SelectedTo_List} " )
        df =AllBusesFilters(filters=filters, sort_by=sort_by, sort_order=sort_order)
        df["departure"] = str(start_date) + " " + df[['departure']]
        df['departure'] = pd.to_datetime(df['departure'])
        df['arrival'] = df['departure'] +df['durhrs'].apply(lambda x: np.timedelta64(x,'h') )
        df['arrival'] = df['arrival'] +df['dursec'].apply(lambda x: np.timedelta64(x,'s') )
        df['arrival'] = pd.to_datetime(df['arrival'])
        
        df=df[df.columns[3:11]]
        new_title = f'<p style="font-family:sans-serif; color:Black; font-size: 22px;">{SelectedFrom_List}-{SelectedTo_List}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        st.dataframe(df,hide_index=True)
        conn.close()

if __name__ == '__main__':
    load_data()  # Ensure data is loaded on app start

