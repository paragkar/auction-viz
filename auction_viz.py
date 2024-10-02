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


# #end of month auction completion dates dictionary for the purpose of evaluting rs-usd rates 

auction_eom_dates_dict = {2010 : datetime(2010,6,30), 2012: datetime(2012,11,30),2013: datetime(2013,3,31), 2014: datetime(2014,2,28),
					2015 : datetime(2015,3,31), 2016 : datetime(2016,10,31), 2021: datetime(2021,3,31), 2022: datetime(2022,8,31),
					2024 : datetime(2024,6,3)}


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



# #processing hovertext for auction data 

# @st.cache_resource
# def htext_colormatrix_auctiondata_2010_3G_BWA_BidsCircleWise(dfbidcirclwise, dftemp, selected_lsa,start_round,end_round,dfprovallcblks_endrd):

# 	filt_last_round = (dfbidcirclwise["Clk_Round"] == end_round)

# 	dfbidcirclwiselastrd = dfbidcirclwise[filt_last_round].drop(columns = ["Clk_Round","PWB_Start_ClkRd","Rank_PWB_Start_ClkRd",
# 		"Possible_Raise_Bid_ClkRd","Bid_Decision","PWB_End_ClkRd"], axis =1).reset_index()

# 	dfbidcirclwiselastrd = dfbidcirclwiselastrd.pivot(index="Bidder", columns='LSA', values="Rank_PWB_End_ClkRd").sort_index(ascending=False)
# 	dftempheatperc = dftemp.pivot(index="Bidder", columns='LSA', values="Bid_Decision_Perc")
# 	dftempheatperc = dftempheatperc.sort_values(selected_lsa, ascending = True)
# 	dftempheatabs = dftemp.pivot(index="Bidder", columns='LSA', values="Bid_Decision")
# 	dftempheatabs = dftempheatabs.sort_values(selected_lsa, ascending = True)


# 	hovertext = []
# 	dict_col={}
# 	dict_result={}
# 	for yi,yy in enumerate(dftempheatabs.index):
# 		hovertext.append([])
# 		list_col=[]
# 		list_result=[]
# 		for xi,xx in enumerate(dftempheatabs.columns):

# 			totalbidsagg = dftempheatabs.loc[yy,xx]
# 			totalbissperc = dftempheatperc.loc[yy,xx]
# 			totalblksrdend = dfprovallcblks_endrd.loc[yy,xx]
# 			finalrank = dfbidcirclwiselastrd.loc[yy,xx]
		
# 			if finalrank in [1,2,3,4]:
# 				result = "WON"
# 				ccode = '#008000' #(green)
# 			else:
# 				result = "LOST"
# 				ccode = '#FF0000' #(red)

# 			list_result.append(result)

# 			list_col.append(ccode)

# 			hovertext[-1].append(
# 						'Bidder: {}\
# 						<br>Circle: {}\
# 						<br>Agg Bids : {} Nos\
# 						<br>Agg Bids: {} % of Total\
# 						<br>Prov Result : {}\
# 						<br>Prov Rank: {}\
# 						<br>Prov BLKs: {}'

# 					 .format( 
# 						yy,
# 						state_dict[xx],
# 						totalbidsagg,
# 						round(totalbissperc,2),
# 						result,
# 						finalrank,
# 						round(totalblksrdend,0),
# 						)
# 						)

# 		dict_col[yy]=list_col
# 		dict_result[yy]=list_result

# 	temp = pd.DataFrame(dict_col).T
# 	temp.columns = dftempheatabs.columns
# 	resultdf = pd.DataFrame(dict_result).T
# 	resultdf.columns = dftempheatabs.columns 
# 	colormatrix = list(temp.values)
# 	return hovertext, colormatrix, resultdf


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

# dfrsrate = loadrstousd()
# auction_rsrate_dict ={} #the dictionary which stores all the values of the rupee usd rates
# dfrsrate["Date"] = pd.to_datetime(dfrsrate["Date"])
# dfrsrate = dfrsrate.set_index("Date").asfreq("ME")

# for index in dfrsrate.index:
# 	if index.date() in auction_eom_list:
# 		auction_rsrate_dict[index.year] = dfrsrate.loc[index,:].values[0]


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

	vertical_spacing_mul_dict = {2024:0.035, 2022:0.035, 2021:0.04, 2016:0.04, 2015 : 0.04, 2014 : 0.06, 2012 : 0.04, 2010 : 0.05}

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
