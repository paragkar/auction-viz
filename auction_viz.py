#importing libraries
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
import numpy as np
from collections import OrderedDict
from plotly.subplots import make_subplots
from streamlit_option_menu import option_menu
import plotly
import pandas as pd
import plotly.figure_factory as ff
import streamlit as st
import matplotlib.pyplot as plt
import altair as alt
from datetime import datetime
import datetime as dt 
import calendar
import time
from PIL import Image
from dateutil import relativedelta
import re
from collections import defaultdict
from dateutil.relativedelta import relativedelta
import io
import msoffcrypto
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from deta import Deta
import seaborn as sns

pd.set_option('future.no_silent_downcasting', True)


#Set page layout here
st.set_page_config(layout="wide")



#--------Fuctions, Constants, Configurations and Flags-------------


SummaryFlag = False # Code below will toggle to True to show summary chart

#--------hide streamlit style and buttons--------------

hide_st_style = '''
				<style>
				#MainMenu {visibility : hidden;}
				footer {visibility : hidder;}
				header {visibility :hidden;}
				<style>
				'''
st.markdown(hide_st_style, unsafe_allow_html =True)

#--------Functions for loading File Starts---------------------

@st.cache_resource
def loadrstousd():
	df = pd.read_csv("rs_to_usd.csv")
	return df

@st.cache_resource
def loadauctionbiddatayearbandcomb():
	password = st.secrets["db_password"]
	excel_content = io.BytesIO()
	with open("auctionbiddatayearbandcomb.xlsx", 'rb') as f:
		excel = msoffcrypto.OfficeFile(f)
		excel.load_key(password)
		excel.decrypt(excel_content)

	xl = pd.ExcelFile(excel_content)
	sheetauctiondata = xl.sheet_names
	df = pd.read_excel(excel_content, sheet_name=sheetauctiondata)
	return df


@st.cache_resource
def auctionbiddatayearactivitycomb():
	password = st.secrets["db_password"]
	excel_content = io.BytesIO()
	with open("auctionbiddatayearactivitycomb.xlsx", 'rb') as f:
		excel = msoffcrypto.OfficeFile(f)
		excel.load_key(password)
		excel.decrypt(excel_content)

	xl = pd.ExcelFile(excel_content)
	sheetauctiondata = xl.sheet_names
	df = pd.read_excel(excel_content, sheet_name=sheetauctiondata)
	return df

#--------Fuctions for loading File Ends--------------------



#--------Setting up the Constants Starts-------------------

state_dict = {'AP': 'Andhra Pradesh', 'AS': 'Assam', 'BH': 'Bihar', 'DL': 'Delhi', 'GU': 'Gujarat',
	'HA': 'Haryana','HP': 'Himachal Pradesh','JK': 'Jammu & Kashmir','KA': 'Karnataka',
	'KE': 'Kerala','KO': 'Kolkata','MP': 'Madhya Pradesh','MA': 'Maharashtra','MU': 'Mumbai',
	'NE': 'Northeast','OR': 'Odisha','PU': 'Punjab','RA': 'Rajasthan','TN': 'Tamil Nadu',
	'UPE': 'Uttar Pradesh (East)','UPW': 'Uttar Pradesh (West)','WB': 'West Bengal' }

subtitle_freqlayout_dict = {700:"FDD: Uplink - 703-748 MHz(shown); Downlink - 758-803(notshown); ",
		 800:"Uplink - 824-844 MHz(shown); Downlink - 869-889 MHz(not shown); ", 
		 900:"Uplink - 890-915 MHz(shown); Downlink - 935-960 MHz(not shown); ", 
		 1800:"Uplink - 1710-1785 MHz(shown); Downlink - 1805-1880 MHz(notshown); ", 
		 2100:"Uplink - 1919-1979 MHz(shown); Downlink - 2109-2169 MHz(notshown); ",
		 2300:"Up & Downlinks - 2300-2400 MHz(shown); ",
		 2500:"Up & Downlinks - 2500-2690 MHz(shown); ",
		 3500:"Up & Downlinks - 3300-3670 MHz(shown); ",
		 26000:"Up & Downlinks - 24250-27500 MHz(shown); "}

#Operators who are the current owners of blocks of spectrum in these bands 
newoperators_dict = {700: {'Vacant':0,'Railways':1,'Govt':2,'RJIO':3,'BSNL':4},
			 800: {'Vacant':0,'RCOM':1,'Govt':2,'RJIO':3,'Bharti':4, 'MTS':5, 'BSNL':6},
			 900:{'Vacant':0,'RCOM':1,'Govt':2,'Railways':3,'Bharti':4, 'AircelU':5, 
				  'BSNLU':6,'MTNLU':7,'BhartiU':8,'VI':9,'VIU':10},
			 1800: {'Vacant':0,'RCOM':1,'Govt':2,'RJIO':3,'Bharti':4,
					'BhartiU':5, 'AircelR':6, 'BSNL':7,'MTNL':8,'VI':9,'VIU':10,'AircelU':11, 'Aircel':12},
			 2100: {'Vacant':0,'RCOM':1,'Govt':2,'Bharti':3, 'BSNL':4,'MTNL':5,'VI':6, 'Aircel':7},
			 2300: {'Vacant':0,'RJIO':1,'Govt':2,'Bharti':3, 'VI':4},
			 2500: {'Vacant':0,'Govt':1,'BSNL':2, 'VI':3},
			 3500: {'Vacant':0,'Bharti':1,'RJIO':2,'BSNL':3, 'MTNL':4,'VI':5},
			 26000: {'Vacant':0,'Bharti':1,'RJIO':2,'BSNL':3, 'MTNL':4,'VI':5,'Adani':6}
			}

#Operators who were the original buyer of spectrum
oldoperators_dict = {2010 : ["Bharti", "QCOM", "Augere", "Vodafone", "Idea", "RJIO", "RCOM", "STel", "Tata", "Aircel", "Tikona"],
			2012 : ["Bharti", "Vodafone", "Idea", "Telenor", "Videocon"],
			2013 : ["MTS"],
			2014 : ["Bharti", "Vodafone", "Idea", "RJIO", "RCOM", "Aircel", "Telenor"],
			2015 : ["Bharti", "Vodafone", "Idea", "RJIO", "RCOM", "Tata", "Aircel"],
			2016 : ["Bharti", "Vodafone", "Idea", "RJIO", "RCOM", "Tata", "Aircel"],
			2021 : ["Bharti", "RJIO", "VodaIdea"],
			2022 : ["Bharti", "RJIO", "VodaIdea", "Adani"],
			2024 : ["Bharti", "RJIO", "VodaIdea"]}

#Spectrum Bands Auctioned in that Calender Year
bands_auctioned_dict = {2010 : [2100, 2300],
		   2012 : [800, 1800],
		   2013 : [800, 900, 1800],
		   2014 : [900, 1800],
		   2015 : [800, 900, 1800, 2100],
		   2016 : [700, 800, 900, 1800, 2100, 2300, 2500],
		   2021 : [700, 800, 900, 1800, 2100, 2300, 2500],
		   2022 : [600, 700, 800, 900, 1800, 2100, 2300, 2500, 3500, 26000],
		   2024 : [800, 900, 1800, 2100, 2300, 2500, 3500, 26000]}
			

#if "1" the expiry tab in spectrum_map file is present and if "0" then not present
exptab_dict = {700:1, 800:1, 900:1, 1800:1, 2100:1, 2300:1, 2500:1, 3500:1, 26000:1}

#Setting the channel sizes for respective frequency maps
channelsize_dict = {700:2.5, 800:0.625, 900:0.2, 1800:0.2, 2100:2.5, 2300:2.5, 2500:5, 3500:5, 26000:25}

#scaling the granularity of the layout of the x axis in the heatmap plot for the respective bands
xdtickfreq_dict = {700:1, 800:0.25, 900:0.4, 1800:1, 2100:1, 2300:1, 2500:2, 3500:5, 26000:50}

#used to control the number of ticks on xaxis for chosen feature = AuctionMap
dtickauction_dict = {700:1, 800:1, 900:1, 1800:1, 2100:1, 2300:1, 2500:1, 3500:1, 26000:1}

# used to set the vertical line widths for the heatmap chart 
xgap_dict = {700:1, 800:1, 900:0.5, 1800:0, 2100:1, 2300:1, 2500:1, 3500:1, 26000:1}

#Minor adjustment for tool tip display data for channel frequency on heatmap
#The reason is that the start freq of the spectrum tab is shifted delpberately by few MHz
#This is to align the labels on the xaxis to align properly with the edge of the heatmap
xaxisadj_dict = {700:1, 800:0.25, 900:0, 1800:0, 2100:1, 2300:1, 2500:2, 3500:0, 26000:0}

#Setting the constant to describe the type of band TDD/FDD
bandtype_dict = {700:"FDD", 800:"FDD", 900:"FDD", 1800:"FDD", 2100:"FDD", 2300:"TDD", 2500:"TDD", 3500:"TDD", 26000:"TDD"}

#auctionfailyears when the auction prices for all LSAs were zero and there are no takers 
auctionfailyears_dict = {700:["2016","2021"], 800:["2012"], 900:["2013","2016"], 1800:["2013"], 
		2100:[], 2300:["2022", "2024"], 2500:["2021"], 3500:["2024"], 26000:["2024"]}

#auction sucess years are years where at least in one of the LASs there was a winner
auctionsucessyears_dict = {700:[2022], 
		800:[2013, 2015, 2016, 2021, 2022], 
		900:[2014, 2015, 2021, 2022, 2024], 
		1800:[2012, 2014, 2015, 2016, 2021, 2022, 2024], 
		2100:[2010, 2015, 2016, 2021, 2022, 2024], 
		2300:[2010, 2016, 2021, 2022],  #added 2022 an as exception (due to error) need to revist the logic of succes and failure
		2500:[2010, 2016, 2022, 2024], 
		3500:[2022], 
		26000:[2022]}

#end of month auction completion dates dictionary for the purpose of evaluting rs-usd rates 

auction_eom_dates_dict = {2010 : datetime(2010,6,30), 2012: datetime(2012,11,30),2013: datetime(2013,3,31), 2014: datetime(2014,2,28),
					2015 : datetime(2015,3,31), 2016 : datetime(2016,10,31), 2021: datetime(2021,3,31), 2022: datetime(2022,8,31),
					2024 : datetime(2024,6,3)}

#Error dicts defines the window width = difference between the auction closing date and the auction freq assignment dates
#This values is used to map expiry year of a particular freq spot to the operator owning that spot
# errors_dict= {700:0.25, 800:1, 900:1, 1800:1, 2100:1.5, 2300:1.25, 2500:1, 3500:0.1, 26000:0.5}

errors_dict= {700:0.25, 800:1, 900:1, 1800:1, 2100:1.5, 2300:1.25, 2500:1, 3500:1, 26000:10} #debug 2024 (Feb)

list_of_circles_codes = ['AP','AS', 'BH', 'DL', 'GU', 'HA', 'HP', 'JK', 'KA', 'KE', 'KO', 'MA', 'MP',
		   'MU', 'NE', 'OR', 'PU', 'RA', 'TN', 'UPE', 'UPW', 'WB']

#Debug 10th June 2024
year_band =["2010-Band2100","2010-Band2300", "2012-Band1800","2014-Band1800","2014-Band900",
									"2015-Band800", "2015-Band900","2015-Band1800", "2015-Band2100", "2016-Band800","2016-Band1800",
									"2016-Band2100", "2016-Band2300", "2016-Band2500","2021-Band700","2021-Band800","2021-Band900","2021-Band1800",
									"2021-Band2100","2021-Band2300","2022-Band700","2022-Band800","2022-Band900","2022-Band1800",
									"2022-Band2100","2022-Band2500","2022-Band3500","2022-Band26000"]

#Debug 19th June 2024
year_band_exp =["2021-Band800","2021-Band900","2021-Band1800","2021-Band2100","2021-Band2300"] # As the DOT auction data is incomplete for these years

#Constants for Charts 
heatmapheight = 900 #Height of Heatmaps
heatmapwidth = 900 #Width of Heatmaps
#Heatmap Chart Margins
t=80
b=60
l=10
r=10
pad=0
summarychartheight = 200 #Summary Chart at Bottom Height 
text_embed_in_chart_size = 20 #Size of Text Embedded in all Charts 
text_embed_in_hover_size = 16 #Size of Text Embedded in tooltips
plot_row_total_chart_ht_mul = 1.018 #This multiplier aligns the row total chart with the heatmap
stcol1 = 9 #No of Columns for Heatmap to Fit 
stcol2 = 1 #No of Columns for row total chart to Fit

#Dictionary to Aggregrated Choosen year_band features 
Auction_Year_Band_Features = {
	"2022-Band26000": {
		"totalrounds": 40,
		"mainsheet": "2022_5G_26000",
		"mainsheetoriginal": "2022_5G_26000_Original",
		"mainoriflag": True,
		"activitysheet": "2022_4G_5G_Activity",
		"demandsheet": "2022_5G_26000_AD",
		"titlesubpart": "26000 MHz Auctions (CY-2022)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2022,
		"band": 26000,
		"xdtick": 1,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "%{z}",
		"blocksize": 50,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	"2022-Band3500": {
		"totalrounds": 40,
		"mainsheet": "2022_5G_3500",
		"mainsheetoriginal": "2022_5G_3500_Original",
		"mainoriflag": True,
		"activitysheet": "2022_4G_5G_Activity",
		"demandsheet": "2022_5G_3500_AD",
		"titlesubpart": "3500 MHz Auctions (CY-2022)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2022,
		"band": 3500,
		"xdtick": 1,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "%{z}",
		"blocksize": 10,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	"2022-Band2500": {
		"totalrounds": 40,
		"mainsheet": "2022_4G_2500",
		"mainsheetoriginal": "2022_4G_2500_Original",
		"mainoriflag": True,
		"activitysheet": "2022_4G_5G_Activity",
		"demandsheet": "2022_4G_2500_AD",
		"titlesubpart": "2500 MHz Auctions (CY-2022)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2022,
		"band": 2500,
		"xdtick": 1,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "%{z}",
		"blocksize": 10,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	"2022-Band2100": {
		"totalrounds": 40,
		"mainsheet": "2022_4G_2100",
		"mainsheetoriginal": "2022_4G_2100_Original",
		"mainoriflag": True,
		"activitysheet": "2022_4G_5G_Activity",
		"demandsheet": "2022_4G_2100_AD",
		"titlesubpart": "2100 MHz Auctions (CY-2022)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2022,
		"band": 2100,
		"xdtick": 1,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "%{z}",
		"blocksize": 5,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	"2022-Band1800": {
		"totalrounds": 40,
		"mainsheet": "2022_4G_1800",
		"mainsheetoriginal": "2022_4G_1800_Original",
		"mainoriflag": True,
		"activitysheet": "2022_4G_5G_Activity",
		"demandsheet": "2022_4G_1800_AD",
		"titlesubpart": "1800 MHz Auctions (CY-2022)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2022,
		"band": 1800,
		"xdtick": 1,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "%{z}",
		"blocksize": 0.2,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	 "2022-Band900": {
		"totalrounds": 40,
		"mainsheet": "2022_4G_900",
		"mainsheetoriginal": "2022_4G_900_Original",
		"mainoriflag": True,
		"activitysheet": "2022_4G_5G_Activity",
		"demandsheet": "2022_4G_900_AD",
		"titlesubpart": "900 MHz Auctions (CY-2022)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2022,
		"band": 900,
		"xdtick": 1,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "%{z}",  # Debug 10th June 2024
		"blocksize": 0.2,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	"2022-Band800": {
		"totalrounds": 40,
		"mainsheet": "2022_4G_800",
		"mainsheetoriginal": "2022_4G_800_Original",
		"mainoriflag": True,
		"activitysheet": "2022_4G_5G_Activity",
		"demandsheet": "2022_4G_800_AD",
		"titlesubpart": "800 MHz Auctions (CY-2022)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2022,
		"band": 800,
		"xdtick": 1,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "%{z}",  # Debug 10th June 2024
		"blocksize": 1.25,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	"2022-Band700": {
		"totalrounds": 40,
		"mainsheet": "2022_5G_700",
		"mainsheetoriginal": "2022_5G_700_Original",
		"mainoriflag": True,
		"activitysheet": "2022_4G_5G_Activity",
		"demandsheet": "2022_5G_700_AD",
		"titlesubpart": "700 MHz Auctions (CY-2022)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2022,
		"band": 700,
		"xdtick": 1,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "%{z}",  # Debug 10th June 2024
		"blocksize": 5,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	"2021-Band700": {
		"totalrounds": 6,
		"mainsheet": "2021_4G_700",
		"mainsheetoriginal": "2021_4G_700_Original",
		"mainoriflag": True,
		"activitysheet": "2021_4G_Activity",
		"demandsheet": "2021_4G_700_AD",
		"titlesubpart": "700 MHz Auctions (CY-2021)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2021,
		"band": 700,
		"xdtick": 1,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "%{z}",
		"blocksize": 5,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
		},

	"2021-Band800": {
		"totalrounds": 6,
		"mainsheet": "2021_4G_800",
		"mainsheetoriginal": "2021_4G_800_Original",
		"mainoriflag": True,
		"activitysheet": "2021_4G_Activity",
		"demandsheet": "2021_4G_800_AD",
		"titlesubpart": "800 MHz Auctions (CY-2021)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2021,
		"band": 800,
		"xdtick": 1,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "%{z}",
		"blocksize": 1.25,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	"2021-Band900": {
		"totalrounds": 6,
		"mainsheet": "2021_4G_900",
		"mainsheetoriginal": "2021_4G_900_Original",
		"mainoriflag": True,
		"activitysheet": "2021_4G_Activity",
		"demandsheet": "2021_4G_900_AD",
		"titlesubpart": "900 MHz Auctions (CY-2021)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2021,
		"band": 900,
		"xdtick": 1,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "%{z}",
		"blocksize": 0.2,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	"2021-Band1800": {
		"totalrounds": 6,
		"mainsheet": "2021_4G_1800",
		"mainsheetoriginal": "2021_4G_1800_Original",
		"mainoriflag": True,
		"activitysheet": "2021_4G_Activity",
		"demandsheet": "2021_4G_1800_AD",
		"titlesubpart": "1800 MHz Auctions (CY-2021)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2021,
		"band": 1800,
		"xdtick": 1,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "%{z}",
		"blocksize": 0.2,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	"2021-Band2100": {
		"totalrounds": 6,
		"mainsheet": "2021_4G_2100",
		"mainsheetoriginal": "2021_4G_2100_Original",
		"mainoriflag": True,
		"activitysheet": "2021_4G_Activity",
		"demandsheet": "2021_4G_2100_AD",
		"titlesubpart": "2100 MHz Auctions (CY-2021)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2021,
		"band": 2100,
		"xdtick": 1,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "%{z}",
		"blocksize": 5,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	"2021-Band2300": {
		"totalrounds": 6,
		"mainsheet": "2021_4G_2300",
		"mainsheetoriginal": "2021_4G_2300_Original",
		"mainoriflag": True,
		"activitysheet": "2021_4G_Activity",
		"demandsheet": "2021_4G_2300_AD",
		"titlesubpart": "2300 MHz Auctions (CY-2021)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2021,
		"band": 2300,
		"xdtick": 1,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "%{z}",
		"blocksize": 10,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	"2016-Band2500": {
		"totalrounds": 31,
		"mainsheet": "2016_4G_2500",
		"mainsheetoriginal": "2016_4G_2500_Original",
		"mainoriflag": True,
		"activitysheet": "2016_4G_Activity",
		"demandsheet": "2016_4G_2500_AD",
		"titlesubpart": "2500 MHz Auctions (CY-2016)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2016,
		"band": 2500,
		"xdtick": 5,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "%{z}",
		"blocksize": 10,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	"2016-Band2300": {
		"totalrounds": 31,
		"mainsheet": "2016_4G_2300",
		"mainsheetoriginal": "2016_4G_2300_Original",
		"mainoriflag": True,
		"activitysheet": "2016_4G_Activity",
		"demandsheet": "2016_4G_2300_AD",
		"titlesubpart": "2300 MHz Auctions (CY-2016)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2016,
		"band": 2300,
		"xdtick": 5,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "%{z}",
		"blocksize": 10,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	"2016-Band2100": {
		"totalrounds": 31,
		"mainsheet": "2016_4G_2100",
		"mainsheetoriginal": "2016_4G_2100_Original",
		"mainoriflag": True,
		"activitysheet": "2016_4G_Activity",
		"demandsheet": "2016_4G_2100_AD",
		"titlesubpart": "2100 MHz Auctions (CY-2016)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2016,
		"band": 2100,
		"xdtick": 5,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "%{z}",
		"blocksize": 5,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	 "2016-Band1800": {
		"totalrounds": 31,
		"mainsheet": "2016_4G_1800",
		"mainsheetoriginal": "2016_4G_1800_Original",
		"mainoriflag": True,
		"activitysheet": "2016_4G_Activity",
		"demandsheet": "2016_4G_1800_AD",
		"titlesubpart": "1800 MHz Auctions (CY-2016)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2016,
		"band": 1800,
		"xdtick": 5,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "%{z}",
		"blocksize": 0.2,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	"2016-Band800": {
		"totalrounds": 31,
		"mainsheet": "2016_4G_800",
		"mainsheetoriginal": "2016_4G_800_Original",
		"mainoriflag": True,
		"activitysheet": "2016_4G_Activity",
		"demandsheet": "2016_4G_800_AD",
		"titlesubpart": "800 MHz Auctions (CY-2016)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2016,
		"band": 800,
		"xdtick": 5,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "%{z}",
		"blocksize": 1.25,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	"2015-Band2100": {
		"totalrounds": 115,
		"mainsheet": "2015_3G_2100",
		"mainsheetoriginal": "2015_3G_2100_Original",
		"mainoriflag": True,
		"activitysheet": "2015_2G_3G_Activity",
		"demandsheet": "2015_3G_2100_AD",
		"titlesubpart": "2100 MHz Auctions (CY-2015)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2015,
		"band": 2100,
		"xdtick": 5,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "",
		"blocksize": 5,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	 "2015-Band1800": {
		"totalrounds": 115,
		"mainsheet": "2015_2G_1800",
		"mainsheetoriginal": "2015_2G_1800_Original",
		"mainoriflag": True,
		"activitysheet": "2015_2G_3G_Activity",
		"demandsheet": "2015_2G_1800_AD",
		"titlesubpart": "1800 MHz Auctions (CY-2015)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2015,
		"band": 1800,
		"xdtick": 5,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "",
		"blocksize": 0.2,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	"2015-Band900": {
		"totalrounds": 115,
		"mainsheet": "2015_2G_900",
		"mainsheetoriginal": "2015_2G_900_Original",
		"mainoriflag": True,
		"activitysheet": "2015_2G_3G_Activity",
		"demandsheet": "2015_2G_900_AD",
		"titlesubpart": "900 MHz Auctions (CY-2015)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2015,
		"band": 900,
		"xdtick": 5,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "",
		"blocksize": 0.2,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	"2015-Band800": {
		"totalrounds": 115,
		"mainsheet": "2015_2G_800",
		"mainsheetoriginal": "2015_2G_800_Original",
		"mainoriflag": True,
		"activitysheet": "2015_2G_3G_Activity",
		"demandsheet": "2015_2G_800_AD",
		"titlesubpart": "800 MHz Auctions (CY-2015)",
		"subtitlesubpartbidactivity": "; Combined for All Bands",
		"year": 2015,
		"band": 800,
		"xdtick": 5,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "",
		"blocksize": 1.25,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	"2014-Band1800": {
		"totalrounds": 68,
		"mainsheet": "2014_2G_1800",
		"mainsheetoriginal": "2014_2G_1800_Original",
		"mainoriflag": True,
		"activitysheet": "2014_2G_Activity",
		"demandsheet": "2014_2G_1800_AD",
		"titlesubpart": "1800 MHz Auctions (CY-2014)",
		"subtitlesubpartbidactivity": "; Combined for both 1800 & 900 MHz Bands",
		"year": 2014,
		"band": 1800,
		"xdtick": 5,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "",
		"blocksize": 0.2,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	"2014-Band900": {
		"totalrounds": 68,
		"mainsheet": "2014_2G_900",
		"mainsheetoriginal": "2014_2G_900_Original",
		"mainoriflag": True,
		"activitysheet": "2014_2G_Activity",
		"demandsheet": "2014_2G_900_AD",
		"titlesubpart": "900 MHz Auctions (CY-2014)",
		"subtitlesubpartbidactivity": "; Combined for both 1800 & 900 MHz Bands",
		"year": 2014,
		"band": 900,
		"xdtick": 5,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "",
		"blocksize": 1,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	},
	"2010-Band2100": {
		"totalrounds": 183,
		"mainsheet": "2010_3G_2100",
		"mainoriflag": False,
		"activitysheet": "2010_3G_2100_Activity",
		"demandsheet": "2010_3G_2100_AD",
		"titlesubpart": "2100 MHz Auctions (CY-2010)",
		"subtitlesubpartbidactivity": "",
		"year": 2010,
		"band": 2100,
		"xdtick": 10,
		"zmin": 1,
		"zmax": 5,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "",
		"blocksize": 5,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 1
	},
	"2010-Band2300": {
		"totalrounds": 117,
		"mainsheet": "2010_BWA_2300",
		"mainoriflag": False,
		"activitysheet": "2010_BWA_2300_Activity",
		"demandsheet": "2010_BWA_2300_AD",
		"titlesubpart": "2300 MHz Auctions (CY-2010)",
		"subtitlesubpartbidactivity": "",
		"year": 2010,
		"band": 2300,
		"xdtick": 10,
		"zmin": 1,
		"zmax": 3,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "",
		"blocksize": 20,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 1
	},
	 "2012-Band1800": {
		"totalrounds": 14,
		"mainsheet": "2012_2G_1800",
		"mainoriflag": False,
		"activitysheet": "2012_2G_1800_Activity",
		"demandsheet": "2012_2G_1800_AD",
		"titlesubpart": "1800 MHz Auctions (CY-2012)",
		"subtitlesubpartbidactivity": "",
		"year": 2012,
		"band": 1800,
		"xdtick": 1,
		"zmin": 1,
		"zmax": 3,
		"zmin_af": 0.5,
		"zmax_af": 1,
		"texttempbiddemandactivity": "%{z}",
		"blocksize": 1.25,
		"zmin_blk_sec": 0,
		"zmax_blk_sec": 4
	}
 
}

#-----------All Constant Deceleration End and Function Starts from Here -----

#Wrapper Function Auction BandWise Selected Feature
def get_value(feature_dict, feature_key, var_name):
	"""
	Retrieves a value from a nested dictionary using the variable name as the key.
	Args:
	- feature_dict (dict): The main dictionary containing feature data.
	- feature_key (str): The key to access the specific feature data.
	- var_name (str): The variable name used as the key in the nested dictionary.
	Returns:
	- The value from the nested dictionary or 'Key not found' if the key does not exist.
	"""
	return feature_dict.get(feature_key, {}).get(var_name, "Key not found")


#function to count number of items in a list and outputs the result as dictionary
#Used to extract data table for Spectrum Layout Dimension when it is filtered by Operators             
def count_items_in_dataframe(df):
	counts = {}

	for col in df.columns:
		for idx, item in enumerate(df[col]):
			if isinstance(item, (int, float)) and not pd.isnull(item):
				# item_key = str(item)  # Convert float item to string
				item_key = int(item) #adding this item solved the problem
				if item_key not in counts:
					counts[item_key] = [0] * len(df)
				counts[item_key][idx] += 1

	df_counts = pd.DataFrame.from_dict(counts, orient='columns')
	return df_counts


#function used to prepare the color scale for the freqmap
@st.cache_resource
def colscalefreqlayout(operators, colcodes):
	operators = dict(sorted(operators.items(), key=lambda x:x[1]))
	operator_names = list(operators.keys())
	operator_codes = list(operators.values())
	scale = [round(x/(len(operators)),2) for x in range(len(operator_names)+1)]
	colorscale =[]
	for i, op in enumerate(operator_names):
		if op in colcodes.index:
			colorscale.append([scale[i],colcodes.loc[op,:][0]])
	colorscale.append([1, np.nan])
	col= pd.DataFrame(colorscale)
	col.columns =["colscale", "colors"]
	col["colscaleshift"] = col.iloc[:,0].shift(-1)
	col = col.iloc[:-1,:]
	colorscale=[]
	for line in col.values:
		colorscale.append((line[0],line[1]))
		colorscale.append((line[2],line[1]))
	return colorscale

#function used for calculating the expiry year heatmap for the subfeature yearly trends
@st.cache_resource
def exp_year_cal_yearly_trends(ef, selected_operator):
	lst1 =[]
	for i, line1 in enumerate(ef.values):
		explst = list(set(line1))
		l1 = [[ef.index[i],round(list(line1).count(x)*channelsize_dict[Band],2), round(x,2)] for x in explst]
		lst1.append(l1)

	lst2 =[]
	for i, val in enumerate(lst1):
		for item in val:
			lst2.append(item)
	df = pd.DataFrame(lst2)
	df.columns = ["LSA", "Spectrum", "ExpYrs"]
	df = df.groupby(['LSA','ExpYrs']).sum()
	df = df.reset_index()
	df = df.pivot(index ='LSA', columns ='ExpYrs', values ='Spectrum') 
	df.columns = [str(x) for x in df.columns]
	if selected_operator == "All":
		df = df.iloc[:,1:]
	else:
		pass
	df = df.fillna(0)
	return df

#function used for calculating the quantum of spectrum expiring mapped to LSA and Years 
#This is for feature expiry map and the subfeature yearly trends 
@st.cache_resource
def bw_exp_cal_yearly_trends(sff,ef):
	lst=[]
	for j, index in enumerate(ef.index):
		for i, col in enumerate(ef.columns):
			l= [index, sff.iloc[j,i],ef.iloc[j,i]]
			lst.append(l)
			
	df = pd.DataFrame(lst)
	df.columns = ["LSA","Operators", "ExpYear"]
	df = df.groupby(["ExpYear"])[["LSA","Operators"]].value_counts()*channelsize_dict[Band]
	df = df.reset_index()
	df.columns =["ExpYear","LSA", "Operators","BW"]
	return df

#funtion used for processing pricing datframe for hovertext for the feature auction map
#The feature auction map is under the dimension Spectrum Bands
# @st.cache_resource
def cal_bw_mapped_to_operators_auctionmap(dff):
	dff = dff.replace(0,np.nan).fillna(0)
	dff = dff.map(lambda x: round(x,2) if type(x)!=str else x)
	dff = dff[(dff["Band"]==Band) & (dff["Cat"]=="L") & (dff["OperatorOld"] != "Free") & (dff["Year"] >= 2010)]
	dff = dff.drop(['OperatorNew', 'Band','Cat'], axis = 1)
	for col in dff.columns[3:]:
		dff[col]=dff[col].astype(float)
	dff = dff.groupby(["OperatorOld", "Year"]).sum()
	dff = dff.drop(['Batch No',], axis = 1) 
	if bandtype_dict[Band]=="TDD": #doubling the TDD spectrum for aligning with normal convention 
		dff = (dff*2).round(2)
	dff = dff.replace(0,"")
	dff= dff.reset_index().set_index("Year")
	dff =dff.replace("Voda Idea","VI")
	dff = dff.replace("Vodafone", "Voda")
	dff = dff.astype(str)
	lst =[]
	for index, row in zip(dff.index,dff.values):
		lst.append([index]+[row[0]+" "+x+" MHz, " for x in row[1:]])
	temp = pd.DataFrame(lst)
	col = dff.reset_index().columns
	col = list(col)
	col.pop(1)
	temp.columns = col
	temp = temp.replace('[a-zA-Z]+\s+MHz, ',"", regex = True)
	dff = temp.groupby("Year").sum()
	dff =dff.T
	dff = dff.reset_index()
	dff.columns = ["LSA"]+auctionsucessyears_dict[Band]
	dff = dff.set_index("LSA")
	return dff

#This general function for converting columns of dataframe into string
@st.cache_resource
def coltostr(df):
	lst =[]
	for col in df.columns:
		lst.append(str(col))
	df.columns=lst
	return df

#This functions adds dummy columns to the dataframe for auction failed years
@st.cache_resource
def adddummycols(df,col):
	df[col]="NA  " # space with NA is delibelitratly added.
	cols = sorted(df.columns)
	df =df[cols]
	return df

#This function maps the year in which the spectrum was acquired
@st.cache_resource
def cal_year_spectrum_acquired(ef,excepf,pf1):
	lst=[]
	for col in ef.columns:
		for i, (efval,excepfval) in enumerate(zip(ef[col].values, excepf[col].values)):
			for j, pf1val in enumerate(pf1.values):
				if excepfval == 0:
					error = abs(efval-pf1val[6]) #orignal
				else:
					error = 0
				if (ef.index[i] == pf1val[0]) and error <= errors_dict[Band]:
					lst.append([ef.index[i],col-xaxisadj_dict[Band],pf1val[1],pf1val[2], pf1val[3], pf1val[4], error]) 
				
	df_final = pd.DataFrame(lst)

	df_final.columns = ["LSA", "StartFreq", "TP", "RP", "AP", "Year", "Error"]
	df_final["Year"] = df_final["Year"].astype(int)
	ayear = df_final.pivot_table(index=["LSA"], columns='StartFreq', values="Year", aggfunc='first').fillna("NA")
	return ayear
  
#This fuctions processes the hovertext for the Feature Spectrum Map, and Sub Feature Frequency Layout
@st.cache_resource
def htext_specmap_freq_layout(sf):  
	hovertext = []
	for yi, yy in enumerate(sf.index):
		hovertext.append([])
		for xi, xx in enumerate(sf.columns):
			if exptab_dict[Band]==1: #1 means that the expiry table in the excel sheet has been set and working 
				expiry = round(ef.values[yi][xi],2)
			else:
				expiry = "NA"
			try:
				auction_year = round(ayear.loc[yy,round(xx-xaxisadj_dict[Band],3)])
			except:
				auction_year ="NA"
				
			operatornew = sff.values[yi][xi]
			operatorold = of.values[yi][xi]
			bandwidth = bandf.values[yi][xi]
			hovertext[-1].append(
						'StartFreq: {} MHz\
						 <br>Channel Size : {} MHz\
						 <br>Circle : {}\
							 <br>Operator: {}\
						 <br>Total BW: {} MHz\
						 <br>ChExp In: {} Years\
						 <br>Acquired In: {} by {}'

					 .format(
						round(xx-xaxisadj_dict[Band],2),
						channelsize_dict[Band],
						state_dict.get(yy),
						operatornew,
						bandwidth,
						expiry,
						auction_year,
						operatorold,
						)
						)
	return hovertext

#This function processes the hovertext for Feature expiry map, and SubFeature Freq Layout
@st.cache_resource
def htext_expmap_freq_layout(sf):
	hovertext = []
	for yi, yy in enumerate(sf.index):
		hovertext.append([])
		for xi, xx in enumerate(sf.columns):
			if exptab_dict[Band]==1: #1 means that the expiry table in the excel sheet has been set and working 
				expiry = round(ef.values[yi][xi],2)
			else:
				expiry = "NA"
			try:
				auction_year = round(ayear.loc[yy,round(xx-xaxisadj_dict[Band],3)])
			except:
				auction_year ="NA"
			operatornew = sff.values[yi][xi]
			operatorold = of.values[yi][xi]
			bandwidthexpiring = bandexpf.values[yi][xi]
			bandwidth = bandf.values[yi][xi]
			hovertext[-1].append(
						'StartFreq: {} MHz\
						 <br>Channel Size : {} MHz\
						 <br>Circle : {}\
							 <br>Operator: {}\
						 <br>Expiring BW: {} of {} MHz\
						 <br>Expiring In: {} Years\
						 <br>Acquired In: {} by {}'

					 .format(
						round(xx-xaxisadj_dict[Band],2),
						channelsize_dict[Band],
						state_dict.get(yy),
						operatornew,
						bandwidthexpiring,
						bandwidth,
						expiry,
						auction_year,
						operatorold,
						)
						)
	return hovertext

#This function is used for processing hovertext for Feature expiry map, and subfeature Yearly Trends with operator selection "All"
@st.cache_resource
def htext_expmap_yearly_trends_with_all_select(bwf,eff): 
	bwf["Op&BW"] = bwf["Operators"]+" - "+round(bwf["BW"],2).astype(str)+" MHz"
	bwff = bwf.set_index("LSA").drop(['Operators'], axis=1)
	xaxisyears = sorted(list(set(bwff["ExpYear"])))[1:]
	hovertext = []
	for yi, yy in enumerate(eff.index):
		hovertext.append([])
		for xi, xx in enumerate(xaxisyears):
			opwiseexpMHz = list(bwff[(bwff["ExpYear"]==xx) & (bwff.index ==yy)]["Op&BW"].values)
			if opwiseexpMHz==[]:
				opwiseexpMHz="NA"
			else:
				opwiseexpMHz = ', '.join(str(e) for e in opwiseexpMHz) #converting a list into string

			TotalBW = list(bwff[(bwff["ExpYear"]==xx) & (bwff.index ==yy)]["BW"].values)
			
			if TotalBW==[]:
				TotalBW="NA"
			else:
				TotalBW = round(sum([float(x) for x in TotalBW]),2)

			hovertext[-1].append(
						'{} : Expiry in {} Years\
						<br />Break Up : {}'

					 .format(
						state_dict.get(yy),
						xx, 
						opwiseexpMHz,
						)
						)
	return hovertext


#processing for hovertext for Fearure expiry map, and SubFeature Yearly Trends along with operator menue
@st.cache_resource
def htext_expmap_yearly_trends_with_op_select(eff): 
	hovertext = []
	for yi, yy in enumerate(eff.index):
		hovertext.append([])
		for xi, xx in enumerate(eff.columns):

			hovertext[-1].append(
						'Circle: {}\
						<br />Expiring In: {} Years'

					 .format(
						state_dict.get(yy),
						xx, 
						)
						)
	return hovertext
	
#This if for processing for hovertext for the Feature Auction Map
@st.cache_resource
def htext_auctionmap(dff): 
	hovertext=[]
	for yi, yy in enumerate(dff.index):
		hovertext.append([])
		for xi, xx in enumerate(dff.columns):
			winners = dff.values[yi][xi][:-2] #removing comma in the end
			resprice = reserveprice.values[yi][xi]
			aucprice = auctionprice.values[yi][xi]
			offmhz = offeredspectrum.values[yi][xi]
			soldmhz = soldspectrum.values[yi][xi]
			unsoldmhz = unsoldspectrum.values[yi][xi]

			hovertext[-1].append(
						'{} , {}\
						 <br / >RP/AP: Rs {}/ {} Cr/MHz\
						 <br / >Offered/Sold/Unsold: {} / {} / {} MHz\
						 <br>Winners: {}'

					 .format( 
						state_dict.get(yy),
						xx,
						resprice,
						aucprice,
						round(offmhz,2),
						round(soldmhz,2),
						round(unsoldmhz,2),
						winners,
						)
						)
	return hovertext


#processing for hovertext and colormatrix for Spectrum Band, Features- Spectrum Map, SubFeature - Operator Holdings 
@st.cache_resource
def htext_colmatrix_spec_map_op_hold_share(dfff, selected_operators, operatorlist):

	operators_to_process = list(dfff.columns)
	dfffcopy =dfff.copy()
	dfffcopy["Total"] = dfffcopy.sum(axis=1)
	lst =[]

	dfffshare = pd.DataFrame()
	for op in operators_to_process:
		dfffcopy[op+"1"] = dfffcopy[op]/dfffcopy["Total"]
		lst.append(op+"1")
	
	dfffshare = dfffcopy[lst]
	for col in dfffshare.columns:
		dfffshare.rename(columns = {col:col[:-1]}, inplace = True) #stripping the last digit "1"

	hovertext=[]
	lst = []
	for yi, yy in enumerate(dfffshare.index):
		hovertext.append([])
		for xi, xx in enumerate(dfffshare.columns):
			share = dfffshare.values[yi][xi]
			holdings = dfff.values[yi][xi]
			
			if share >= 0.4 :
				ccode = '#008000' #% spectrum share more than 40% (green)
			elif (share < 0.4) & (share >= 0.2):
				ccode = '#808080' # spectrum share between 40 to 20% (grey)
			else:
				ccode = '#FF0000' # spectrum share less than 20% (red)
			lst.append([yy,xx,ccode])
			temp = pd.DataFrame(lst)
			temp.columns = ["Circle", "Operator", "Color"]
			colormatrix = temp.pivot(index='Circle', columns='Operator', values="Color")
			colormatrix = list(colormatrix.values)
			
			hovertext[-1].append(
						'Circle: {}\
						 <br>Operator: {}\
						 <br>Holdings: {} MHz\
						 <br>Market Share: {} %'

					 .format( 
						state_dict.get(yy),
						xx,
						round(holdings,2),
						round(share*100,2),
						)
						)
	return hovertext, colormatrix


#processing for hovertext and colormatrix for Dim - Auction Years, Fearure - Band Metric, SubFeatures Reserve Price etc
@st.cache_resource
def htext_colmatrix_auction_year_band_metric(df1):
	auctionprice =  df1.pivot(index="Circle", columns='Band', values=subfeature_dict["Auction Price"])
	reserveprice =  df1.pivot(index="Circle", columns='Band', values=subfeature_dict["Reserve Price"])
	qtyoffered = df1.pivot(index="Circle", columns='Band', values=subfeature_dict["Quantum Offered"])
	qtysold = df1.pivot(index="Circle", columns='Band', values=subfeature_dict["Quantum Sold"])
	qtyunsold = df1.pivot(index="Circle", columns='Band', values=subfeature_dict["Quantum Unsold"])
	
	hovertext=[]
	lst = []
	for yi, yy in enumerate(reserveprice.index):
		hovertext.append([])
		for xi, xx in enumerate(reserveprice.columns):
			resprice = reserveprice.values[yi][xi]
			aucprice = auctionprice.values[yi][xi]
			offered = qtyoffered.values[yi][xi]
			sold = qtysold.values[yi][xi]
			unsold = qtyunsold.values[yi][xi]
			delta = round(aucprice - resprice,0)
			if delta < 0 :
				ccode = '#000000' #auction failed (black)
			elif delta == 0:
				ccode = '#008000' #auction price = reserve price (green)
			elif delta > 0:
				ccode = '#FF0000' #auction price > reserve price (red)
			else:
				ccode = '#C0C0C0' #No Auction (silver)
			lst.append([yy,xx,ccode])
			temp = pd.DataFrame(lst)
			temp.columns = ["Circle", "Year", "Color"]
			colormatrix = temp.pivot(index='Circle', columns='Year', values="Color")
			colormatrix = list(colormatrix.values)
			
			hovertext[-1].append(
						'Circle: {}\
						 <br>Band: {} MHz\
						 <br>Reserve Price: {} Rs Cr/MHz\
						 <br>Auction Price: {} Rs Cr/MHz\
						 <br>Offered: {} MHz\
						 <br>Sold: {} MHz\
						 <br>Unsold: {} MHz'

					 .format( 
						state_dict.get(yy),
						xx,
						round(resprice,1),
						round(aucprice,1),
						round(offered,2),
						round(sold,2),
						round(unsold,2),
						)
						)
	return hovertext, colormatrix

#processing for hovertext and colormatrix for Auction Year, Operator Metric, SubFeatures - Total Outflow, Total Purchase
@st.cache_resource
def htext_colmatrix_auction_year_operator_metric(df1, selectedbands, SelectedSubFeature, df_subfeature):    
	temp1 = pd.DataFrame()
	if selectedbands != []:
		for band in selectedbands:
			temp2= df1[df1["Band"]==band]
			temp1 = pd.concat([temp2,temp1], axis =0)
		df1  = temp1
	
	if SelectedSubFeature == "Total Purchase": #then process for total purchase
		df_purchase = df_subfeature
	else: 
		columnstoextract = ["Circle", "Band"]+oldoperators_dict[Year]
		df2_temp2 = df1[columnstoextract]
		df2_temp2.drop("Band", inplace = True, axis =1)
		df2_temp2 = df2_temp2.groupby(["Circle"]).sum().round(2)
		df2_temp2 = df2_temp2.reindex(sorted(df2_temp2.columns), axis=1)
		df_purchase = df2_temp2
	
	if SelectedSubFeature == "Total Ouflow": #then process for total outflow
		df_outflow = df_subfeature
	else:
		operators_dim_cy_new=[]
		for op in oldoperators_dict[Year]:
			df1[op+"1"] = df1["Auction Price/MHz"]*df1[op]
			operators_dim_cy_new.append(op+"1")
		columnstoextract = ["Circle", "Band"]+operators_dim_cy_new
		df2_temp1 = df1[columnstoextract]
		operators_dim_cy_new = [x[:-1] for x in operators_dim_cy_new] # removing the last letter "1" from operator name
		df2_temp1.columns = ["Circle", "Band"]+ operators_dim_cy_new
		df2_temp1.drop("Band", inplace = True, axis =1)
		df2_temp1 = df2_temp1.groupby(["Circle"]).sum().round(0)
		df2_temp1 = df2_temp1.reindex(sorted(df2_temp1.columns), axis=1)
		df_outflow = df2_temp1
	
	hovertext=[]
	lst = []
	for yi, yy in enumerate(df_subfeature.index): #dataframe of total outflow (any one of them can be used)
		hovertext.append([])
		for xi, xx in enumerate(df_subfeature.columns): #dataframe of total outflow (any one of them can be used)
			outflow = df_outflow.values[yi][xi]
			purchase = df_purchase.values[yi][xi]
			if outflow > 0 :
				ccode = '#008000' # Purchased (green)
			else:
				ccode = '#C0C0C0' #No Purchase (silver)
			lst.append([yy,xx,ccode])
			temp = pd.DataFrame(lst)
			temp.columns = ["Circle", "Operator", "Color"]
			colormatrix = temp.pivot(index='Circle', columns='Operator', values="Color")
			colormatrix = list(colormatrix.values)
			
			hovertext[-1].append(
						'Circle: {}\
						 <br>Operator: {}\
						 <br>Outflow: {} Rs Cr\
						 <br>Purchase: {} MHz'

					 .format( 
						state_dict.get(yy),
						xx,
						round(outflow,0),
						round(purchase,2),
						)
						)
	return hovertext, colormatrix


#---------------Hovertest for BlocksAllocated Starts---------------------

@st.cache_resource
def htext_businessdata_FinancialSPWise(df_finmetric,df_finmetric_prec,df_finmetricINC):

	hovertext = []
	for yi,yy in enumerate(df_finmetric.index):
		hovertext.append([])

		for xi,xx in enumerate(df_finmetric.columns):

			absvalue = df_finmetric.loc[yy,xx]
			percentoftotal = df_finmetric_prec.loc[yy,xx]
			increments = df_finmetricINC.loc[yy,xx]

			hovertext[-1].append(
						'Bidder: {}\
						<br>Date: {}\
						<br>Abs Value : {} Rs K Cr\
						<br>Perc : {} of Total \
						<br>Increments : {} Rs K Cr'
				
					 .format( 
						yy,
						xx,
						absvalue,
						percentoftotal,
						round(increments,2),
						)
						)

	return hovertext

#---------------Hovertest for BlocksAllocated Ends--------------------- 

#processing hovertext for auction data 

@st.cache_resource
def htext_colormatrix_auctiondata_2010_3G_BWA_BidsCircleWise(dfbidcirclwise, dftemp, selected_lsa,start_round,end_round,dfprovallcblks_endrd):

	filt_last_round = (dfbidcirclwise["Clk_Round"] == end_round)

	dfbidcirclwiselastrd = dfbidcirclwise[filt_last_round].drop(columns = ["Clk_Round","PWB_Start_ClkRd","Rank_PWB_Start_ClkRd",
		"Possible_Raise_Bid_ClkRd","Bid_Decision","PWB_End_ClkRd"], axis =1).reset_index()

	dfbidcirclwiselastrd = dfbidcirclwiselastrd.pivot(index="Bidder", columns='LSA', values="Rank_PWB_End_ClkRd").sort_index(ascending=False)
	dftempheatperc = dftemp.pivot(index="Bidder", columns='LSA', values="Bid_Decision_Perc")
	dftempheatperc = dftempheatperc.sort_values(selected_lsa, ascending = True)
	dftempheatabs = dftemp.pivot(index="Bidder", columns='LSA', values="Bid_Decision")
	dftempheatabs = dftempheatabs.sort_values(selected_lsa, ascending = True)


	hovertext = []
	dict_col={}
	dict_result={}
	for yi,yy in enumerate(dftempheatabs.index):
		hovertext.append([])
		list_col=[]
		list_result=[]
		for xi,xx in enumerate(dftempheatabs.columns):

			totalbidsagg = dftempheatabs.loc[yy,xx]
			totalbissperc = dftempheatperc.loc[yy,xx]
			totalblksrdend = dfprovallcblks_endrd.loc[yy,xx]
			finalrank = dfbidcirclwiselastrd.loc[yy,xx]
		
			if finalrank in [1,2,3,4]:
				result = "WON"
				ccode = '#008000' #(green)
			else:
				result = "LOST"
				ccode = '#FF0000' #(red)

			list_result.append(result)

			list_col.append(ccode)

			hovertext[-1].append(
						'Bidder: {}\
						<br>Circle: {}\
						<br>Agg Bids : {} Nos\
						<br>Agg Bids: {} % of Total\
						<br>Prov Result : {}\
						<br>Prov Rank: {}\
						<br>Prov BLKs: {}'

					 .format( 
						yy,
						state_dict[xx],
						totalbidsagg,
						round(totalbissperc,2),
						result,
						finalrank,
						round(totalblksrdend,0),
						)
						)

		dict_col[yy]=list_col
		dict_result[yy]=list_result

	temp = pd.DataFrame(dict_col).T
	temp.columns = dftempheatabs.columns
	resultdf = pd.DataFrame(dict_result).T
	resultdf.columns = dftempheatabs.columns 
	colormatrix = list(temp.values)
	return hovertext, colormatrix, resultdf


#-----------------Hovertext for Provisional Winning Bids Starts----------------------

@st.cache_resource
def htext_colormatrix_auctiondata_2010_3G_BWA_ProvWinningBid(dfrp, dftemp, pwbtype, round_number):


	dftemp = dftemp.sort_index(ascending=True)
	dftemprpmul = round(dftemp/dfrp.values,1)

	hovertext = []
	dict_col={}
	for yi,yy in enumerate(dftemp.index):
		hovertext.append([])
		list_col=[]
		for xi,xx in enumerate(dftemp.columns):

			pwb = dftemp.loc[yy,xx]
			pwbmulofrp = dftemprpmul.loc[yy,xx]
			if str(pwb)  == "nan":
				ccode = '#808080' #(grey)
			else:
				ccode = '#228B22' #(green)

			list_col.append(ccode)

			hovertext[-1].append(
						'Bidder: {}\
						<br>Circle: {}\
						<br>PWB : {} Rs Cr\
						<br>PWB / Reserve P: {}\
						<br>PWB Type : {}\
						<br>Round No: {}'

					 .format( 
						yy,
						state_dict[xx],
						pwb,
						pwbmulofrp,
						pwbtype,
						round_number,
						)
						)

		dict_col[yy]=list_col

	temp = pd.DataFrame(dict_col).T
	temp.columns = dftemp.columns
	colormatrix = list(temp.values)
	return hovertext, colormatrix

#-----------------Hovertext for Provisional Winning Bids Ends----------------------


#---------------Hovertest for Demand Intensity---------------------

@st.cache_resource
def htext_auctiondata_2010_3G_BWA_DemandIntensity(dfbid,ADPrecOfBlksforSale):

	dfbidaAD = dfbid.pivot(index="LSA", columns='Clock Round', values="Aggregate Demand").sort_index(ascending=True)

	dfbidaED = dfbid.pivot(index="LSA", columns='Clock Round', values="Excess Demand").sort_index(ascending=True)

	hovertext = []
	for yi,yy in enumerate(dfbidaAD.index):
		hovertext.append([])

		for xi,xx in enumerate(dfbidaAD.columns):

			aggdemand = dfbidaAD.loc[yy,xx]
			aggdemperc = ADPrecOfBlksforSale.loc[yy,xx]
			excessdemand = dfbidaED.loc[yy,xx]

			hovertext[-1].append(
						'Circle: {}\
						<br>Round No: {}\
						<br>Agg Demand : {} Blocks\
						<br>Ratio (AD/Total) : {} \
						<br>Excess Demand : {} Blocks'
				

					 .format( 
						yy,
						xx,
						aggdemand,
						aggdemperc,
						excessdemand,
						)
						)

	return hovertext


#---------------Hovertest for Demand Intensity Ends---------------------


#---------------Hovertest for Bidding Activity Total---------------------

@st.cache_resource
def htext_auctiondata_2010_3G_BWA_BiddingActivity(dfbid, column_name):

	filt = dfbid["Clk_Round"]==1

	dfbidRD1 = dfbid[filt]

	dfbidactivity = dfbid.pivot(index="Bidder", columns='Clk_Round', values=column_name).sort_index(ascending=True)

	dfbidactivityRd1 = dfbidRD1.pivot(index="Bidder", columns='Clk_Round', values="Pts_Start_Round").sort_index(ascending=True)

	dfbidactivityratio = round((dfbidactivity/dfbidactivityRd1.values),2)


	hovertext = []
	for yi,yy in enumerate(dfbidactivity.index):
		hovertext.append([])

		for xi,xx in enumerate(dfbidactivity.columns):

			pointsinplay = dfbidactivity.loc[yy,xx]
			pointsratio = dfbidactivityratio.loc[yy,xx]


			hovertext[-1].append(
						'Bidder: {}\
						<br>Round No: {}\
						<br>Points in Play : {} Nos\
						<br>Ratio (Actual/Initial) : {}'
				
					 .format( 
						yy,
						xx,
						pointsinplay,
						pointsratio,
						)
						)

	return hovertext


#---------------Hovertest for Bidding Activity Total Ends---------------------



#---------------Hovertest for Points Lost---------------------

@st.cache_resource
def htext_auctiondata_2010_3G_BWA_PointsLost(dfbidactivity, dfbidactivityperc):


	hovertext = []
	for yi,yy in enumerate(dfbidactivity.index):
		hovertext.append([])

		for xi,xx in enumerate(dfbidactivity.columns):

			pointslost = dfbidactivity.loc[yy,xx]
			pointslostperc = dfbidactivityperc.loc[yy,xx]


			hovertext[-1].append(
						'Bidder: {}\
						<br>Round No: {}\
						<br>Points Lost : {} Nos\
						<br>Points Lost : {} % of Initial'
				
					 .format( 
						yy,
						xx,
						pointslost,
						pointslostperc,
						)
						)

	return hovertext


#---------------Hovertest for Points Lost Ends---------------------


#---------------Hovertest for BlocksAllocated Starts---------------------

@st.cache_resource
def htext_auctiondata_2010_3G_BWA_BlocksAllocated(dftemp):

	dftemp = dftemp.sort_index(ascending=True)

	hovertext = []
	for yi,yy in enumerate(dftemp.index):
		hovertext.append([])

		for xi,xx in enumerate(dftemp.columns):

			blocksalloc = dftemp.loc[yy,xx]
			spectrumMHz = (dftemp.loc[yy,xx])*blocksize


			hovertext[-1].append(
						'Bidder: {}\
						<br>Circle: {}\
						<br>BLKs Allocated : {} Nos\
						<br>Spectrum : {} MHz'
				
					 .format( 
						yy,
						xx,
						blocksalloc,
						round(spectrumMHz,2),
						)
						)

	return hovertext


#---------------Hovertest for BlocksAllocated Ends---------------------



#---------------Hovertest for LastBidPrice Starts---------------------

@st.cache_resource
def htext_colormatrix_auctiondata_2010_3G_BWA_LastBidPrice(dflastsubbidheat,dflastsubbidratio,dfbid):


	hovertext = []
	dict_col = {}
	for yi,yy in enumerate(dflastsubbidheat.index):
		hovertext.append([])
		list_col=[]
		for xi,xx in enumerate(dflastsubbidheat.columns):

			lastbid = dflastsubbidheat.loc[yy,xx]
			lastbidratiorp = dflastsubbidratio.loc[yy,xx]
			blocksforsale = dfbid.T.loc["Blocks For Sale",xx]

			if lastbid > 0:
				ccode = '#880808' #(red)
			else:
				ccode = '#808080' #(grey)

			list_col.append(ccode)



			hovertext[-1].append(
						'Bidder: {}\
						<br>Circle: {}\
						<br>LastBid : {} RsCr/BLK\
						<br>LastBidRatio : {} Bid/RP\
						<br>BLKsForSale : {} Nos'
				
					 .format( 
						yy,
						xx,
						lastbid,
						round(lastbidratiorp,2),
						blocksforsale,
						)
						)

		dict_col[yy]=list_col

	temp = pd.DataFrame(dict_col).T

	temp.columns = dflastsubbidheat.columns

	colormatrix = list(temp.values)

	return hovertext, colormatrix


#---------------Hovertest for LastBidPrice Ends---------------------

#preparing color scale for hoverbox for Spectrum and Expiry maps
@st.cache_resource
def colscale_hbox_spectrum_expiry_maps(operators, colcodes):
	scale = [round(x/(len(operators)-1),2) for x in range(len(operators))]
	colors =[]
	for k, v  in operators.items():
		colors.append(colcodes.loc[k,:].values[0])
	colorscale=[]
	for i in range(len(scale)):
		colorscale.append([scale[i],colors[i]])
	return colorscale

#shaping colorscale for driving the color of hoverbox of Spectrum and Expiry maps
@st.cache_resource
def transform_colscale_for_spec_exp_maps(colorscale, sf):
	hlabel_bgcolor = [[x[1] for x in colorscale if x[0] == round(value/(len(colorscale) - 1),2)] 
				  for row in sf.values for value in row]
	hlabel_bgcolor = list(np.array(hlabel_bgcolor).reshape(22,int(len(hlabel_bgcolor)/22)))
	return hlabel_bgcolor

#preparing and shaping the colors for hoverbox for auction map
@st.cache_resource
def transform_colscale_for_hbox_auction_map(dff,reserveprice, auctionprice): 
	lst =[]
	for yi, yy in enumerate(dff.index):
		reserveprice = reserveprice.replace("NA\s*", np.nan, regex = True)
		auctionprice = auctionprice.replace("NA\s*", np.nan, regex = True)
		delta = auctionprice-reserveprice
		delta = delta.replace(np.nan, "NA")
		for xi, xx in enumerate(dff.columns):
			delval = delta.values[yi][xi]
			if delval =="NA":
				ccode = '#000000' #auction failed #black
			elif delval == 0:
				ccode = '#008000' #auction price = reserve price #green
			else:
				ccode = '#FF0000' #auction price > reserve price #red
			lst.append([yy,xx,ccode])
			temp = pd.DataFrame(lst)
			temp.columns = ["LSA", "Year", "Color"]
			colormatrix = temp.pivot(index='LSA', columns='Year', values="Color")
			colormatrix = list(colormatrix.values)
	return colormatrix

#function for preparing the summary chart 
def summarychart(summarydf, xcolumn, ycolumn):
	bar = alt.Chart(summarydf).mark_bar().encode(
	y = alt.Y(ycolumn+':Q', axis=alt.Axis(labels=True, titleAngle =270, titleFontSize=text_embed_in_chart_size,labelAngle=0,labelFontSize=text_embed_in_chart_size)),
	x = alt.X(xcolumn+':O', axis=alt.Axis(labels=True, labelAngle=0, labelFontSize=text_embed_in_chart_size, titleFontSize=text_embed_in_chart_size)),
	color = alt.Color(xcolumn+':N', legend=None))

	text = bar.mark_text(size = text_embed_in_chart_size, dx=0, dy=-7, color = 'white').encode(text=ycolumn+':Q')
	chart = (bar + text).properties(width=heatmapwidth, height =summarychartheight)
	chart = chart.configure_title(fontSize = text_embed_in_chart_size, font ='Arial', anchor = 'middle', color ='black')
	return chart

#function for preparing the chart for row total
def plotrwototal(sumrows, ydim, xdim):
	fig = px.bar(sumrows, y = ydim, x=xdim, orientation ='h', height = heatmapheight*plot_row_total_chart_ht_mul)
	fig.update_layout(xaxis=dict(title='India Total',side='top', title_standoff=0, ticklen=0,title_font=dict(size=text_embed_in_chart_size)), 
		yaxis=dict(title='', showticklabels=True))
	fig.update_traces(text=sumrows[xdim], textposition='inside',textfont=dict(size=text_embed_in_chart_size, color='white')) 
	fig.update_xaxes(tickvals=[])
	fig.update_yaxes(tickfont=dict(size=text_embed_in_chart_size))  # Change '16' to your desired font size for y-axis tick labels
	fig.update_layout(xaxis=dict(side='top', title_standoff=0, ticklen=0, title_font=dict(size=text_embed_in_chart_size))) 
	fig.update_layout(xaxis_title_standoff=5) 
	fig.update_traces(marker=dict(color='red'))
	# Simulate a border by using a larger margin and setting the background color
	fig.update_layout(
		margin=dict(t=t, b=b*1.1, l=l*0, r=r, pad=pad+5),  # Adjust margins if necessary
		paper_bgcolor='yellow',  # Outer color
		plot_bgcolor='white',  # Inner color simulates the border
	)

	return fig

# function used to calculate the total bid values 
def bidvalue(df,dfblocks):

	df = df.replace(np.nan, 0)
	min_values=[]
	for col in df.columns:
		lst =[]
		if sum(list(df[col])) > 0:
			for value in list(df[col]):
				if value != 0:
					lst.append(value)
			min_values.append(min(lst))
		if sum(list(df[col])) == 0:
			min_values.append(np.nan)

	mindf = pd.DataFrame(min_values).T

	mindf.columns = df.columns
	df_final = dfblocks*mindf.values #calculating the total value of bids

	df_final = df_final.sum(axis =1).round(1)

	return df_final

def plotbiddertotal(dftemp,dfblocksalloc_rdend):

	dftemp = round(dftemp,1)
					
	panindiabids = bidvalue(dftemp,dfblocksalloc_rdend).reset_index()

	panindiabids.columns =["Bidder","PanIndiaBid"]
	panindiabids = panindiabids.round(0)
	panindiabids = panindiabids.sort_values("Bidder", ascending=False)

	fig = px.bar(panindiabids, y = 'Bidder', x='PanIndiaBid', orientation ='h', height = heatmapheight)

	fig.update_layout(xaxis=dict(title='Total Value'), yaxis=dict(title=''))
	fig.update_traces(text=panindiabids['PanIndiaBid'], textposition='auto',textfont=dict(size=text_embed_in_chart_size, color='white')) #Debug 12th June 2024 (Changed 14 to 20)
	fig.update_xaxes(tickvals=[])
	fig.update_layout(xaxis=dict(side='top', title_standoff=0, ticklen=0, title_font=dict(size=text_embed_in_chart_size)))
	fig.update_layout(xaxis_title_standoff=5)
	fig.update_traces(marker=dict(color='red'))

	return fig

def plotlosttotal(df,ydim,xdim):
	fig = px.bar(df, y =ydim, x=xdim, orientation ='h', height = heatmapheight)
	fig.update_layout(xaxis=dict(title="Total"), yaxis=dict(title=''))
	fig.update_traces(text=df[xdim], textposition='auto',textfont=dict(size=text_embed_in_chart_size, color='white')) #Debug 12th June 2024 (Changed 14 to 20)
	fig.update_xaxes(tickvals=[])
	fig.update_layout(xaxis=dict(side='top', title_standoff=0, ticklen=0, title_font=dict(size=text_embed_in_chart_size))) #Debug 12th June 2024 (Changed 14 to 20)
	fig.update_layout(xaxis_title_standoff=5)
	fig.update_traces(marker=dict(color='red'))
	return fig


#------------------------- debug 30th Mar 2024
def select_round_range(total_rounds):
	# Sidebar elements for selecting round numbers
	col1, col2 = st.sidebar.columns(2)
	with col1:
		min_round = st.number_input('From Round', min_value=1, max_value=total_rounds, value=1)
	with col2:
		max_round = st.number_input('To Round', min_value=1, max_value=total_rounds, value=total_rounds)
	
	# Ensure 'From Round' is always less than 'To Round'
	if min_round >= max_round:
		st.sidebar.error('Please ensure From Round is less than To Round.')
		max_round = min_round + 1

	return min_round, max_round
#------------------------- debug 30th Mar 2024


#**********  Main Program Starts here ***************

# authenticator.logout("Logout", "sidebar") #logging out authentication
# st.sidebar.title(f"Welcome {name}")
# image = Image.open('parag_kar.jpg') #debug
# st.sidebar.image(image) #debug

#set flags extracting chart data in the data tab
chart_data_flag = False #set this to true only if this chart exists.

with st.sidebar:
	selected_dimension = option_menu(
		menu_title = "Select a Menu",
		options = [ "AuctionYear AllBands"], #Debug 14th June 2024
		# icons = ["1-circle-fill", ],
		# menu_icon = "arrow-down-circle-fill",
		default_index =0,
		)

#loading file rupee to USD and finding the exchange rate in the auction eom
auction_eom_list = [x.date() for x in list(auction_eom_dates_dict.values())]

dfrsrate = loadrstousd()
auction_rsrate_dict ={} #the dictionary which stores all the values of the rupee usd rates
dfrsrate["Date"] = pd.to_datetime(dfrsrate["Date"])
dfrsrate = dfrsrate.set_index("Date").asfreq("ME")

for index in dfrsrate.index:
	if index.date() in auction_eom_list:
		auction_rsrate_dict[index.year] = dfrsrate.loc[index,:].values[0]


# if selected_dimension == "AuctionYear Activity": #Incompete Still working this section

# 	currency_flag = "NA" #This is dummy variiable for this option done to preserve the current structure of the code 

# 	df = auctionbiddatayearactivitycomb()["Sheet1"] #Loading the auction bid year activity data

# 	st.write(df)


if selected_dimension == "AuctionYear AllBands": #This is the new dimension Added on June 2024

	currency_flag = "NA" #This is dummy variiable for this option done to preserve the current structure of the code 

	def filt_round(df, round_number):
		# Filter the dataframe based on the round number
		return df[df['Clock Round'] == round_number].replace(["-", ""], 0).fillna(0)

	#Loading the auction bid year and band data 
	df = loadauctionbiddatayearbandcomb()["Sheet1"]

	#Loading the auction bid year activity data 
	dfactvity = auctionbiddatayearactivitycomb()["Sheet1"] [["Clock Round", "Auction Year", "Activity Factor"]]


	# Initialize session state variables
	if 'selected_year' not in st.session_state:
		st.session_state.selected_year = 2022
	if 'selected_bands' not in st.session_state:
		st.session_state.selected_bands = []
	if 'selected_areas' not in st.session_state:
		st.session_state.selected_areas = []
	# if 'round_number' not in st.session_state:
	# 	st.session_state.round_number = 1
	if 'selected_dimension' not in st.session_state:
		st.session_state.selected_dimension = "Bid Value ActivePlusPWB"

	# Select Auction Year
	AuctionYears = sorted(df['Auction Year'].unique())
	selected_year = st.sidebar.selectbox('Select an Auction Year', AuctionYears, on_change=None)

	# Apply filter for Auction Year
	df = df[df['Auction Year'] == selected_year]
	dfactvity = dfactvity[dfactvity['Auction Year'] == selected_year]



	# Choose bands to view
	available_bands = sorted(list(set(df["Band"])))
	# Adjust selection interface based on the auction year
	if selected_year == 2010:
		# For the year 2010, provide a selectbox with default to 2100
		selected_bands = st.sidebar.selectbox('Select Band to View', available_bands, index=available_bands.index("2100") if "2100" in available_bands else 0)
		# Wrap the selection into a list since the rest of the code expects a list
		selected_bands = [selected_bands]
	else:
		# For other years, use a multiselect with all bands selected by default
		selected_bands = st.sidebar.multiselect('Select Bands to View', available_bands, default=available_bands)

	# Reset round number when bands change
	if st.session_state.selected_bands != selected_bands:
		st.session_state.round_number = 1  # Reset round number to 1
	st.session_state.selected_bands = selected_bands

	# Further filter dataframe by selected bands if any
	if selected_bands:
		df = df[df["Band"].isin(selected_bands)]


	# Choose service areas to view
	available_areas = sorted(df['Service Area'].unique())
	# Use a unique key for multiselect to force reset when needed
	selected_areas = st.sidebar.multiselect(
		'Select Service Areas to View', 
		available_areas, 
		default=available_areas, 
		key='service_area_select'
	)

	# Check if no service area is selected, and if so, reset to all areas
	if not selected_areas:
		selected_areas = available_areas
		st.sidebar.warning('No service area selected. Resetting to all areas.')
		# Force the multiselect to reset by using a new key
		st.sidebar.multiselect('Select Service Areas to View', available_areas, default=available_areas, key='reset_service_area_select')

	# Apply the service area filter to the dataframe
	df = df[df['Service Area'].isin(selected_areas)]


	# Make copies of the dataframe before selecting dimension
	dfcopy = df.copy()
	dftext = df.copy()

	# Select Dimension
	dimensions = ["Bid Value ProvWinners", "Bid Value ActiveBidders","Bid Value ActivePlusPWB","RatioPWPtoRP EndRd", "ProvWinBid StartRd","Rank StartRd","ProvWinBid EndRd", "Rank EndRd","Blocks Selected", "MHz Selected",
					"ProvAllocBLKs StartRd","ProvAllocMHz StartRd", "ProvAllocBLKs EndRd", "ProvAllocMHz EndRd", "Blocks ForSale","MHz ForSale"]
	selected_dimension = st.sidebar.selectbox('Select a Dimension', dimensions)

	# Apply dimension filter
	df = df[['Clock Round', 'Bidder', 'Service Area', 'Band', selected_dimension]]

	# Clock Round selection
	# clkrounds = sorted(df['Clock Round'].unique())
	# with st.sidebar.form("round_form"):
	# 	round_number = st.number_input("Select Auction Round Number"+";Total Rounds= "+str(max(clkrounds)), min_value=min(clkrounds), max_value=max(clkrounds), value=st.session_state.round_number)
	# 	submitted = st.form_submit_button('Apply Round Number')
	# 	if submitted:
	# 		st.session_state.round_number = round_number
	# 		# st.experimental_rerun() 

	# df = filt_round(df, st.session_state.round_number)
	# dftext = filt_round(dftext, st.session_state.round_number)
	# dfcopy = filt_round(dfcopy, st.session_state.round_number)
	# dfactvity = filt_round(dfactvity, st.session_state.round_number)


	# Clock Round selection
	clkrounds = sorted(df['Clock Round'].unique())
	# Set default round number to 1 or the minimum available round if 1 is not available
	default_round_number = 1 if 1 in clkrounds else min(clkrounds)

	# Use number_input directly for interactive updates
	round_number = st.sidebar.number_input(
	    "Select Auction Round Number; Total Rounds= " + str(max(clkrounds)),
	    min_value=min(clkrounds),
	    max_value=max(clkrounds),
	    value=default_round_number
	)

	# Filter data based on the selected round number
	df = filt_round(df, round_number)
	dftext = filt_round(dftext, round_number)
	dfcopy = filt_round(dfcopy, round_number)
	dfactvity = filt_round(dfactvity, round_number)


	activity_factor_for_selected_round = dfactvity.drop_duplicates()["Activity Factor"].values[0] #Note this will be used in the title 

	# Function to Pivot Dataframe based on selected dimention
	def pivot_dataframe(df, selected_dimension):
		df = df.pivot_table(
		index='Service Area', 
		columns=['Bidder', 'Band'], 
		values= selected_dimension, 
		# aggfunc='first'  # you can change this to 'sum' if that's more appropriate
		aggfunc='sum'  # you can change this to 'sum' if that's more appropriate
		)
		return df

	df = pivot_dataframe(df, selected_dimension)

	dim_to_select_for_total_dict = {
		# "Bid Decision" : "Bid Decision",
		"Bid Value ProvWinners" : "Bid Value ProvWinners", 
		"Bid Value ActiveBidders" : "Bid Value ActiveBidders",
		"Bid Value ActivePlusPWB" : "Bid Value ActivePlusPWB",
		"RatioPWPtoRP EndRd" : "Bid Value ProvWinners",
		"ProvWinBid StartRd" : "ProvWinBid StartRd",
		"Rank StartRd" : "ProvWinBid StartRd",
		"ProvWinBid EndRd" : "Bid Value ProvWinners",
		"Rank EndRd" : "ProvWinBid EndRd",
		"Blocks Selected" : "Blocks Selected",
		"MHz Selected" : "MHz Selected",
		"ProvAllocBLKs StartRd" : "ProvAllocBLKs StartRd",
		"ProvAllocMHz StartRd" : "ProvAllocMHz StartRd",
		"ProvAllocBLKs EndRd" : "ProvAllocBLKs EndRd",
		"ProvAllocMHz EndRd" : "ProvAllocMHz EndRd",
		"Blocks ForSale" : "Blocks ForSale",
		"MHz ForSale" : "MHz ForSale",
		 }

	selected_dimension_for_total = dim_to_select_for_total_dict[selected_dimension]
	dfcopy = dfcopy[[ "Clock Round", "Bidder", "Service Area","Band", selected_dimension_for_total]]
	dfcopy = pivot_dataframe(dfcopy, selected_dimension_for_total)

	# Generate a fixed color palette first
	all_bidders = ['Adani', 'Aircel', 'Augere', 'Bharti', 'Etisalat', 'Idea', 'Infotel', 'Qualcomm', 'RCOM', 
	'RJIO', 'Reliance', 'STel', 'Spice', 'Tata', 'Telewings', 'Tikona', 'Videocon', 'VodaIdea', 'Vodafone']
	
	# Manually assign colors to each bidder
	bidder_colors = {
	"Adani": "#FF6347",      # Tomato
	"Aircel": "#FF4500",     # OrangeRed
	"Augere": "#FFD700",     # Gold
	"Bharti": "#32CD32",     # LimeGreen
	"Etisalat": "#4682B4",   # SteelBlue
	"Idea": "#FFA500",       # Orange
	"Infotel": "#DA70D6",    # Orchid
	"Qualcomm": "#6495ED",   # CornflowerBlue
	"RCOM": "#FFFF00",       # Yellow
	"RJIO": "#FF0000",       # Red
	"Reliance": "#6B8E23",   # OliveDrab
	"STel": "#20B2AA",       # LightSeaGreen
	"Spice": "#EE82EE",      # Violet
	"Tata": "#0000FF",       # Blue
	"Telewings": "#FFDAB9",  # PeachPuff
	"Tikona": "#800080",     # Purple
	"Videocon": "#40E0D0",   # Turquoise
	"VodaIdea": "#BA55D3",   # MediumOrchid
	"Vodafone": "#FFC0CB"    # Pink
	}

	def colorscale_and_color_index_map(bidder_colors):
		# Create a colorscale for Plotly, mapping indices to colors
		colorscale = [(i / (len(bidder_colors) - 1), color) for i, color in enumerate(bidder_colors.values())]
		colorscale.append((1, list(bidder_colors.values())[-1]))  # Ensure the last color is included

		# Create color_df using indices for the colorscale
		color_index_map = {bidder: i / (len(bidder_colors) - 1) for i, bidder in enumerate(bidder_colors.keys())}

		return colorscale, color_index_map

	colorscale, color_index_map = colorscale_and_color_index_map(bidder_colors)

	# Simplify column names for display
	column_labels = [f"{col[1]} ({col[0]})" for col in df.columns]
	df.columns = column_labels
	dfcopy.columns = column_labels

	def create_color_df(df, color_index_map):
		# Assuming 'df' is your DataFrame with columns formatted as "Band (Bidder)"
		color_df = pd.DataFrame(index=df.index, columns=df.columns)
		for col in df.columns:
			bidder = col.split('(')[1].split(')')[0]
			color_df[col] = df[col].apply(lambda x: color_index_map[bidder] if pd.notna(x) and x != 0 else None)

		return color_df

	#Creating Color DataFrame for each of the instants
	color_df = create_color_df(df, color_index_map)

	# Transpose and prepare df for visualization
	df = df.T.sort_index(ascending=False).replace(0, "").replace("", np.nan)

	# Transpose and prepare dfcopy to align with df structure
	dfcopy = dfcopy.T.sort_index(ascending=False).replace(0, "").replace("", np.nan)

	# Calculate row totals for each bidder across selected bands
	row_totals = dfcopy.sum(axis=1).reset_index(name='Total')
	row_totals.columns = ["BandBidder", "Total"]
	row_totals["Total"] = row_totals["Total"].astype(float).round(0)
	# Calculate the maximum total value to set a consistent x-axis range across all bar charts
	max_total_value = row_totals['Total'].max()  # Assuming 'Total' holds the values you need

	total_value_all_bands = row_totals["Total"].astype(float).sum(axis=0) #This is to be used in title text

	# Map the bidder names back to colors using the color_index_map
	row_totals['color'] = row_totals['BandBidder'].apply(lambda x: bidder_colors[x.split('(')[1].split(')')[0]])

	# Transpose and prepare color_df for visualization
	def transpose_color_df(color_df):
		color_df = color_df.T.sort_index(ascending=False)
		return color_df

	color_df = transpose_color_df(color_df)

	# Define the order of the bands
	band_order = ["700", "800", "900", "1800", "2100", "2300", "2500", "3500", "26000"]

	def sort_in_band_order(df, band_order):
		# Extract band information more reliably
		df["Band"] = list(df.index.str.extract(r'(\d+)')[0])
		# Dictionary to hold dataframes for each band
		df_dict = {band: group.drop('Band', axis=1) for band, group in df.groupby('Band')}
		# Organizing df_dict according to band_order
		df_dict = {band: df_dict[band] for band in band_order if band in df_dict}

		return df_dict

	df_dict = sort_in_band_order(df, band_order)

	vertical_spacing_mul_dict = {2022:0.035, 2021:0.04, 2016:0.04, 2015 : 0.04, 2014 : 0.06, 2012 : 0.04, 2010 : 0.05}

	# Adjusting subplot setup to include two columns, one for the heatmap and one for the bar chart
	fig = make_subplots(rows=len(df_dict), cols=2, specs=[[{"type": "heatmap"}, {"type": "bar"}] for _ in range(len(df_dict))],
						vertical_spacing=vertical_spacing_mul_dict[selected_year],
						horizontal_spacing=0.01,  # Set minimal horizontal spacing between columns
						column_widths=[0.9, 0.10])  # Adjust the width of columns if necessary

	# Determine the range for z values - it should cover all indices used in your colorscale
	zmin, zmax = 0, 1  # Since your colorscale is likely mapped from 0 to 1

	#Prepare dataframe to be used to process textvalues by making comparision
	def selected_dimension_df_text(dftext,selected_dimension):
		#Processing the dataframe which has been prapared for processing text values
		dftext = pivot_dataframe(dftext, selected_dimension)
		dftext.columns = column_labels
		dftext = dftext.T.sort_index(ascending=False).replace(0, "").replace("", np.nan)
		return dftext
	

	def map_win_loss_provwinners(df_active, df_winners):
		result_df = pd.DataFrame(index=df_active.index, columns=df_active.columns)
		for col in df_active.columns:
			for idx in df_active.index:
				active_value = df_active.at[idx, col]
				winner_value = df_winners.at[idx, col]
				if pd.notna(active_value) and active_value != 0:
					result_df.at[idx, col] = '(W)' if pd.notna(winner_value) and winner_value != 0 else '(L)'
				else:
					result_df.at[idx, col] = ''
		return result_df


	def map_alloc_slots_with_sale(df_alloc, df_sale):
		result_df = pd.DataFrame(index=df_alloc.index, columns=df_sale.columns)
		for col in df_alloc.columns:
			for idx in df_alloc.index:
				alloc_value = df_alloc.at[idx, col]
				sale_value = df_sale.at[idx, col]
				if pd.notna(alloc_value) and alloc_value != 0:
					result_df.at[idx, col] = '('+df_sale.at[idx, col].astype(str)+')' if pd.notna(sale_value) and sale_value != 0 else ''
				else:
					result_df.at[idx, col] = ''
		return result_df

	
	#1. Extract the dataframe where blocks of sales has to be appended
	df_blocks_for_sale = selected_dimension_df_text(dftext, "Blocks ForSale").round(0).fillna(0).astype('int')
	df_prov_alloc_blks_endround = selected_dimension_df_text(dftext, "ProvAllocBLKs EndRd").round(0).fillna(0).astype('int')
	df_prov_alloc_blks_startround = selected_dimension_df_text(dftext, "ProvAllocBLKs StartRd").round(0).fillna(0).astype('int')
	df_blks_selected = selected_dimension_df_text(dftext, "Blocks Selected").round(0).fillna(0).astype('int')

	#2. Mapping allocated slots with those up with blocks for sale
	result_df_prov_alloc_blks_endround = map_alloc_slots_with_sale(df_prov_alloc_blks_endround, df_blocks_for_sale)
	result_df_prov_alloc_blks_startround = map_alloc_slots_with_sale(df_prov_alloc_blks_startround, df_blocks_for_sale)
	result_df_blks_selected = map_alloc_slots_with_sale(df_blks_selected, df_blocks_for_sale)

	#3. Sorting with band order and converting allocated blocks dataframe into dict
	result_df_prov_alloc_blks_endround_dict=sort_in_band_order(result_df_prov_alloc_blks_endround, band_order)
	df_prov_alloc_blks_endround_dict=sort_in_band_order(df_prov_alloc_blks_endround, band_order)
	result_df_prov_alloc_blks_startround_dict=sort_in_band_order(result_df_prov_alloc_blks_startround, band_order)
	df_prov_alloc_blks_startround_dict=sort_in_band_order(df_prov_alloc_blks_startround, band_order)
	result_df_blks_selected_dict=sort_in_band_order(result_df_blks_selected, band_order)
	df_blks_selected_dict=sort_in_band_order(df_blks_selected, band_order)



	#1. Extract the dataframe where MHz of sales has to be appended
	df_mhz_for_sale = selected_dimension_df_text(dftext, "MHz ForSale").round(1).fillna(0)
	df_prov_alloc_mhz_endround = selected_dimension_df_text(dftext, "ProvAllocMHz EndRd").round(1).fillna(0)
	df_prov_alloc_mhz_startround = selected_dimension_df_text(dftext, "ProvAllocMHz StartRd").round(1).fillna(0)
	df_mhz_selected = selected_dimension_df_text(dftext, "MHz Selected").round(1).fillna(0)

	#2. Mapping allocated mhz with those up with mhz for sale
	result_df_prov_alloc_mhz_endround = map_alloc_slots_with_sale(df_prov_alloc_mhz_endround, df_mhz_for_sale)
	result_df_prov_alloc_mhz_startround = map_alloc_slots_with_sale(df_prov_alloc_mhz_startround,df_mhz_for_sale)
	result_df_mhz_selected = map_alloc_slots_with_sale(df_mhz_selected,df_mhz_for_sale)

	#3. Sorting with band order and converting allocated mhz dataframe into dict
	result_df_prov_alloc_mhz_endround_dict=sort_in_band_order(result_df_prov_alloc_mhz_endround, band_order)
	df_prov_alloc_mhz_endround_dict=sort_in_band_order(df_prov_alloc_mhz_endround, band_order)
	result_df_prov_alloc_mhz_startround_dict=sort_in_band_order(result_df_prov_alloc_mhz_startround, band_order)
	df_prov_alloc_mhz_startround_dict=sort_in_band_order(df_prov_alloc_mhz_startround, band_order)
	result_df_mhz_selected_dict=sort_in_band_order(result_df_mhz_selected, band_order)
	df_mhz_selected_dict=sort_in_band_order(df_mhz_selected, band_order)


	#1. Extract the dataframe where the "Win" and "Loss" has to be appended
	df_bid_value_provwinners = selected_dimension_df_text(dftext, "Bid Value ProvWinners").round(0).fillna(0).astype('int') #This is the ref dataframe 
	df_bid_value_activebidders = selected_dimension_df_text(dftext, "Bid Value ActiveBidders").round(0).fillna(0).astype('int')
	df_bid_value_activepluspwbbidders = selected_dimension_df_text(dftext, "Bid Value ActivePlusPWB").round(0).fillna(0).astype('int')

	#2. Mapping results for selected dataframe to map
	result_df_active_bidders = map_win_loss_provwinners(df_bid_value_activebidders, df_bid_value_provwinners)
	result_df_active_pluspwb_bidders = map_win_loss_provwinners(df_bid_value_activepluspwbbidders, df_bid_value_provwinners)

	#3. Sorting and converting all mapped and result dataframe into dict
	result_df_active_bidders_dict = sort_in_band_order(result_df_active_bidders, band_order)
	df_bid_value_activebidders_dict = sort_in_band_order(df_bid_value_activebidders, band_order)
	result_df_active_pluspwb_bidders_dict = sort_in_band_order(result_df_active_pluspwb_bidders, band_order)
	df_bid_value_activepluspwbbidders_dict = sort_in_band_order(df_bid_value_activepluspwbbidders, band_order)


	def prepare_text_values(df_dict, result_df_dict, band):
		df = df_dict[band].map(lambda x : round(x,1)).astype(str).replace('nan', '')
		result_df = result_df_dict[band].astype(str)
		combined_df = df + '\n' + result_df
		return combined_df

	#4. Finally add the selected_dimnsion in this fuctions as a final step
	lambda_function_dict = {
	"Bid Value ActiveBidders": lambda band: prepare_text_values(df_bid_value_activebidders_dict, result_df_active_bidders_dict, band),
	"Bid Value ActivePlusPWB": lambda band: prepare_text_values(df_bid_value_activepluspwbbidders_dict, result_df_active_pluspwb_bidders_dict, band),
	"ProvAllocBLKs EndRd": lambda band: prepare_text_values(df_prov_alloc_blks_endround_dict, result_df_prov_alloc_blks_endround_dict, band),
	"ProvAllocBLKs StartRd": lambda band: prepare_text_values(df_prov_alloc_blks_startround_dict, result_df_prov_alloc_blks_startround_dict, band),
	"ProvAllocMHz EndRd": lambda band: prepare_text_values(df_prov_alloc_mhz_endround_dict, result_df_prov_alloc_mhz_endround_dict, band),
	"ProvAllocMHz StartRd": lambda band: prepare_text_values(df_prov_alloc_mhz_startround_dict, result_df_prov_alloc_mhz_startround_dict, band),
	"Blocks Selected": lambda band: prepare_text_values(df_blks_selected_dict, result_df_blks_selected_dict, band),
	"MHz Selected" : lambda band: prepare_text_values(df_mhz_selected_dict, result_df_mhz_selected_dict, band),

	}

	def text_values_heatmap(selected_dimension, df_segment, band):
		if selected_dimension in  lambda_function_dict:
			text_values = lambda_function_dict[selected_dimension](band)
			texttemplate ="%{text}"
		else:
			text_values = df_segment.astype(float).round(1).astype(str).replace('nan',"")
			texttemplate ="%{text:.1f}"
		return text_values, texttemplate


	# Iterate through each band and its corresponding dataframe
	for i, (band, df_segment) in enumerate(df_dict.items(), start=1):

		if selected_dimension not in ["RatioPWPtoRP EndRd"]: #IF statatement for using a different colorscale for ratio

			text_values, texttemplate = text_values_heatmap(selected_dimension,df_segment,band)
			# text_values = text_values.replace("0","", regex = True)

			text_values = text_values.map(lambda x: x.strip() if isinstance(x, str) else x).replace("0","", regex = False).replace("0.0", "",regex = False)

			aligned_color_df = color_df.loc[df_segment.index, df_segment.columns].replace(np.nan, "")
			# Create a heatmap for each band
			fig.add_trace(
				go.Heatmap(
					z=aligned_color_df.values,
					x=df_segment.columns,
					y=df_segment.index,
					colorscale=colorscale,
					text=text_values.values,  
					texttemplate=texttemplate,
					textfont={"size": text_embed_in_chart_size*0.9}, 
					showscale=False,
					# reversescale=True,
					zmin=zmin,  # Set minimum z value
					zmax=zmax,  # Set maximum z value
				),
				row=i, col=1
			)

		if selected_dimension in ["RatioPWPtoRP EndRd"]: #IF statatement for using a different colorscale for ratio
			# Create a heatmap for each band
			fig.add_trace(
				go.Heatmap(
					z=df_segment.values,
					x=df_segment.columns,
					y=df_segment.index,
					colorscale="YlGnBu",
					# text=text_values.values,  # Assuming 'df' contains the values you want to display
					texttemplate="%{z:.1f}",
					textfont={"size": text_embed_in_chart_size*0.9}, 
					showscale=False,
					# reversescale=True,
					# zmin=zmin,  # Set minimum z value
					# zmax=zmax,  # Set maximum z value
				),
				row=i, col=1
			)

		# Extract row totals for the current segment aligned with the bidders/bands
		segment_totals = row_totals[row_totals['BandBidder'].isin(df_segment.index)]

		# Add bar chart trace
		fig.add_trace(
			go.Bar(
				y=segment_totals['BandBidder'],
				x=segment_totals['Total'],
				orientation='h',  # Horizontal bar chart
				# marker_color='red',  # Bar color
				marker=dict(color=row_totals['color']),  
				text=segment_totals['Total'],  # To show the totals on the bars
				textfont=dict(color='white', size = text_embed_in_chart_size*0.8),  # Dynamic text size
				showlegend = False,
				textposition="auto",
				width=1,  # Adjust bar width, closer to 1 means wider
			),
			row=i, col=2
		)

		 # Update axis settings to hide y-axis labels and fit tightly
		fig.update_yaxes(row=i, col=2, showticklabels=False)  # Hide y-axis tick labels
		fig.update_xaxes(row=i, col=2, showticklabels=False)   # Optionally adjust x-axis labels if necessary
		# Set the x-axis range for bar charts to be the same across all subplots
		fig.update_xaxes(row=i, col=2, range=[0, max_total_value])

		title = "Total " + selected_dimension_for_total #X axis title for Bar Chart

		# Create a Retangular Block on Bar
		fig.update_xaxes(row=i, col=2, fixedrange=True, showline=True, linewidth=2.5, linecolor='black', mirror=True, showgrid=True, gridcolor='lightgrey', title=title, title_standoff=8)
		fig.update_yaxes(row=i, col=2, fixedrange=True, showline=True, linewidth=2.5, linecolor='black', mirror=True, showgrid=True, gridcolor='lightgrey')

		# Calculate whether the dataframe has any non-zero values
		has_non_zero_values = df_segment.sum().sum() > 0  # This sums all values and checks if the total is greater than 0

		# Update axes to their original settings
		fig.update_xaxes(row=i, col=1, fixedrange=True, showline=True, linewidth=2.5, linecolor='black', mirror=True, showgrid=True, gridcolor='lightgrey')
		fig.update_yaxes(row=i, col=1, fixedrange=True, showline=True, linewidth=2.5, linecolor='black', mirror=True, showgrid=True, gridcolor='lightgrey')

		# Update axes for each subplot to set the tick font size
		fig.update_xaxes(row=i, col=1, tickfont=dict(size=text_embed_in_chart_size*0.8))
		fig.update_yaxes(row=i, col=1, tickfont=dict(size=text_embed_in_chart_size*0.8),
						title_text="" if has_non_zero_values else str(band))  # Set the y-axis title here)

	bands_in_view = len(df_dict.keys())

	height_mul_dict = {1:0.8, 2:1, 3: 1.2, 4 :1.4 , 5 :1.4, 6 : 1.45 , 7: 1.45, 8: 1.45, 9:1.45}

	# Update the overall layout
	fig.update_layout(uniformtext_minsize=text_embed_in_chart_size*0.75,
		uniformtext_mode='hide', 
		xaxis_title=None, 
		yaxis_title=None, 
		showlegend=False,  # Ensure legend is not shown
		# yaxis_autorange='reversed',
		font=dict(size=text_embed_in_chart_size),#Debug 12th June 2024
		template='simple_white',
		# title='Heatmap of No. of Blocks Selected by Service Area and Band',
		width=heatmapwidth,
		height=heatmapheight*height_mul_dict[bands_in_view],  # Total height based on the number of subplots
		autosize=True,
		# plot_bgcolor='#B0C4DE',  # Background color for the plot area light greay
		plot_bgcolor='white',  # Background color for the plot area light greay
		paper_bgcolor='white',
		margin=dict(t=10, b=10, l=10, r=10, pad=4),
		yaxis=dict(
		  tickmode='array',
		  tickfont=dict(size=text_embed_in_chart_size*0.75),
		  ),
		  xaxis = dict(
		  side = 'bottom',
		  tickmode = 'linear',
		  tickangle=0,
		  dtick = 1,
		  # tickfont=dict(size=text_embed_in_chart_size),
		   ), 
	)


	title_text = f"""
	<span style='color: #8B0000;'>Auction Year: {selected_year}</span>, 
	<span style='color: #00008B;'>Dimension: {dim_to_select_for_total_dict[selected_dimension]} - {total_value_all_bands}</span>, 
	<span style='color: #3357FF;'>Round: {round_number}</span>, 
	<span style='color: #FF33F6;'>Activity Factor: {activity_factor_for_selected_round:.1f}</span>
	"""

	st.markdown(f"<h1 style='font-size:40px; margin-top: -40px;'>{title_text}</h1>", unsafe_allow_html=True)


	# Display the figure in Streamlit
	with st.spinner('Processing...'):
		placeholder = st.empty()
		st.plotly_chart(fig, use_container_width=True)
