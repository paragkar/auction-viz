import pandas as pd
import streamlit as st
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import io
import msoffcrypto

# Set page layout configuration
st.set_page_config(layout="wide")

# Define a dictionary for auction end-of-month dates
auction_eom_dates_dict = {
	2010: pd.Timestamp('2010-06-30'), 2012: pd.Timestamp('2012-11-30'),
	2013: pd.Timestamp('2013-03-31'), 2014: pd.Timestamp('2014-02-28'),
	2015: pd.Timestamp('2015-03-31'), 2016: pd.Timestamp('2016-10-31'),
	2021: pd.Timestamp('2021-03-31'), 2022: pd.Timestamp('2022-08-31'),
	2024: pd.Timestamp('2024-06-03')
}

# Function to load auction data from an Excel file
@st.cache(allow_output_mutation=True)
def loadauctionbiddatayearbandcomb():
	password = st.secrets["db_password"]
	excel_content = io.BytesIO()
	with open("auctionbiddatayearbandcomb.xlsx", 'rb') as f:
		excel = msoffcrypto.OfficeFile(f)
		excel.load_key(password)
		excel.decrypt(excel_content)

	xl = pd.ExcelFile(excel_content)
	df = pd.read_excel(excel_content, sheet_name=xl.sheet_names[0])
	return df

# Function to create Plotly charts
def create_plotly_charts(df):
	fig = make_subplots(rows=1, cols=2, specs=[[{"type": "scatter"}, {"type": "bar"}]])

	# Scatter Plot
	scatter_chart = px.scatter(df, x="Date", y="Value", title="Scatter Plot")
	fig.add_trace(scatter_chart['data'][0], row=1, col=1)

	# Bar Chart
	bar_chart = px.bar(df, x="Category", y="Value", title="Bar Chart")
	fig.add_trace(bar_chart['data'][0], row=1, col=2)

	st.plotly_chart(fig, use_container_width=True)

# Main function to load data and call plotting function
def main():
	st.title("Auction Data Analysis")
	df = loadauctionbiddatayearbandcomb()
	st.write("Preview of the data loaded:")
	st.dataframe(df.head())
	
	create_plotly_charts(df)

if __name__ == "__main__":
	main()
