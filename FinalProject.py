"""
Name: Penelope Soto
CS230: 5
Date: 12/08/2021
URL:


Description: This program has a side bar that allows its users to select preferences for what day they want to visit the stadium, what time of day they want to watch the game and how many tickets they need.
Then it gives them the option to look for stadiums either by looking up which state they are in or by directly looking for the name of the stadium or by directly looking for which team they are interested in.

"""

import csv
import pandas as pd
import pprint as pp  # to make the output look pretty
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pydeck as pdk
import os
import webbrowser
from heapq import nlargest
import string
PUNCTUATION = string.punctuation

stadiums = pd.read_csv('stadiums.csv',encoding='utf8')
#print(stadiums)
pd.set_option("display.max_rows", None, "display.max_columns", None, 'display.width', None, 'max_colwidth', None)
#print(stadiums)

st.title("Football Stadiums")
st.image("stadium.jpg", width = 500)

#This code turns all the state names into its short names
state_column = stadiums.iloc[:,2]
states = []
for s in state_column:
    if s not in states:
        states.append(s)
short = ["AL","AK","AZ","AR","CA","CO","CT","DC","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"]

full = ["alabama","alaska","arizona","arkansas","california","colorado","connecticut","washington dc","delaware","florida","georgia","hawaii","idaho","illinois","indiana","iowa","kansas","kentucky","louisiana","maine","maryland","massachusetts","michigan","minnesota","mississippi","missouri","montana","nebraska","nevada","new hampshire","new jersey","new mexico","new york","north carolina","north dakota","ohio","oklahoma","oregon","pennsylvania","puerto rico","rhode island","south carolina","south dakota","tennessee","texas","utah","vermont","virginia","washington","west virginia","wisconsin","wyoming"]
#print(state_column)
state_column = state_column.str.replace("Washington D.C.","washington DC")
state_column = state_column.str.replace("D.C.","DC")


short_name_column = []
for i in state_column:
    if i.upper() in short:
        short_name_column.append(i)
    elif i.lower() in full:
        index = full.index(i.lower())
        short_name_column.append(short[index])
    else:
        print(i)
stadiums['Short_names'] = short_name_column

#This code lets the user select in which state they would like to visit a stadium
select_state = st.selectbox("Please select the state you're interested in", short).upper()
st.success("These are all of the stadiums in the state you selected:")
show_state = stadiums.loc[stadiums["Short_names"] == select_state, ["stadium", "city", "state","team"]]
st.write(show_state)
st.write("Number of results: ",len(show_state))


#This code lets the user select which statidum they want to visit by the stadium name
stadium_column = list(stadiums.iloc[:,0])
unique_stadiums = []
for s in stadium_column:
    if s not in unique_stadiums:
        unique_stadiums.append(s)
unique_stadiums.sort()
select_stadium =st.selectbox("Please select the stadium you're interested in", unique_stadiums).lower()
st.success("Here is the information for the stadium you selected:")
show_stadium = stadiums.loc[stadiums["stadium"].str.lower() ==  select_stadium, ["stadium", "team", "city","capacity"]]
st.write(show_stadium)

#This code lets the user select which team they would like to see by the team name
team_column = list(stadiums.iloc[:,3])
team_column.sort()
select_team =st.selectbox("Please select the team you're interested in", team_column)
st.success("Here is the information for the team you selected:")
show_team = stadiums.loc[stadiums["team"] == select_team, ["stadium", "city", "state"]]
st.write(show_team)

#bar chart that shows many stadiums are in each state
def bar_chart():

    count_states = {}
    for i in short_name_column:
        if i in count_states:
            count_states[i] = count_states[i]+1
        else:
            count_states[i] = 1
    x = list(count_states.keys(),)
    y = []
    for i in range(len(x)):
        y.append(count_states[x[i]])
    plt.figure(figsize=(20,10))
    plt.bar(x,y, width=0.5, color = "r")
    plt.xticks(rotation=90)
    plt.rcParams.update({'font.size':25})
    plt.xlabel("State")
    plt.ylabel("Number of Stadiums")
    plt.title("Number of Stadiums in the Each State")
    return plt
st.pyplot(bar_chart())

#pie chart that shows the top conferences
conference_column = stadiums.iloc[:,4]
st.subheader("Top 8 Football Conferences")
frequencies = {}
for item in conference_column:
    if item in frequencies:
        frequencies[item] += 1
    else:
        frequencies[item] = 1
#print(frequencies)
N=8
highest=nlargest(N,frequencies,key=frequencies.get)
#print(highest)
conference = ['Big Ten', 'SEC', 'ACC', 'C-USA', 'MAC', 'Big Sky', 'Pac-12', 'Mountain West']
conference_count=[14,14,14,13,13,13,12,12]
myexplode = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
fig1, ax1 = plt.subplots()
ax1.pie(conference_count, labels=conference, autopct='%.1f%%', textprops={'fontsize': 12},explode= myexplode)
#plt.legend(loc=0)
st.pyplot(fig1)



#Map that displays where the stadiums are on the map
st.subheader("Map with the locations of all the stadiums")
def generate_map(stadiums):
    stadium_map = stadiums.filter(['stadium', 'latitude', 'longitude'])

    view_state = pdk.ViewState(latitude = stadium_map["latitude"].mean(),
                               longtitude = stadium_map["longitude"].mean(),
                               zoom = 12,
                               )
    layer = pdk.Layer('ScatterplotLayer',
                      data=stadium_map,
                      get_position='[longitude, latitude]',
                      get_radius=50,
                      get_color = [25,20,400],
                      pickable =True)

    tool_tip = {'html':'Listing:<br><b>{stadiums}</b>', 'style': {'backgroundColor': 'orange', 'color': 'white'}}

    map = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                   initial_view_state=view_state,
                   layers=[layer],
                   tooltip=tool_tip)

    st.map(stadium_map)

generate_map(stadiums)


#Sidebar for the user to specify the preferences for the stadium they wish to visit
st.sidebar.header("User Preferences")

name = st.sidebar.text_input("Enter your name:")

date = st.sidebar.date_input("What day would you like to visit the stadium")
st.sidebar.write("You will visit the stadium on", date, ".")

time = st.sidebar.radio("What time of day would you like to watch the game", ("Afternoon", "Evening", "Night"))
st.sidebar.write("You selected", time, "as your preferred time to watch the game." )

tickets = st.sidebar.slider("How many tickets will you like", 1, 10)
st.sidebar.write("You will need", tickets, "tickets.")

st.sidebar.write(f"Hello {name}, you will need {tickets} tickets to attend the {time} game on {date}.")




