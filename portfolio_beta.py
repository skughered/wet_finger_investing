"""

Description: This script fetches ETF prices from Tiingo API and calculates the portfolio's rolling beta to the SPY.
The rolling beta is then plotted and a histogram of the rolling beta is also plotted with standard deviations and
the current value highlighted. To enable the script to run, you need to have a Tiingo API token and the tiingo
python package installed. You also need to have a csv file containing the portfolio returns. The csv file should
contain a column with the name of the portfolio and the daily percentage returns of the portfolio. The csv file
should be located at the location specified by the variable portfolio_returns_csv_loc.
The script can be run by using

"""


# Import necessary libraries
import pandas as pd
from tiingo import TiingoClient as tii
from datetime import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns

# Define the location of the portfolio return csv file
portfolio_returns_csv_loc = r'c:\abc\123\portfolio.csv'


def tiingo_data(metric_name='adjClose'):
    """
  This function fetches data from Tiingo API and returns a DataFrame of adjusted close prices for a list of symbols.
  """
    # Your Tinngo.com API Token
    api = '9c6d1991a2f70ee6e29f20df344feb9e1d90267d'

    # Configuration
    config = {'api_key': api, 'session': True}
    client = tii(config)

    # List of instruments
    instrument_list = ['SPY', 'QQQ', 'VT', 'VTI']

    # Define the start and end dates
    start_date = '2015-01-01'
    end_date = dt.now().strftime('%Y-%m-%d')

    # Fetch the adjusted close prices
    ticker_history = client.get_dataframe(instrument_list,
                                          frequency='daily',
                                          metric_name='adjClose',
                                          startDate=start_date,
                                          endDate=end_date)

    # Convert the index to datetime
    ticker_history.index = pd.to_datetime(ticker_history.index)

    return ticker_history


# Fetch the ETF prices and calculate the daily percentage change
load_etf_prices = tiingo_data(metric_name='adjClose')
etf_pct_returns = load_etf_prices.pct_change()

# Create a new DataFrame with an additional column for portfolio returns
portfolio_index_returns_pct = etf_pct_returns.copy()
portfolio_index_returns_pct['portfolio'] = 0

# Read the portfolio csv into a DataFrame
# Change this line to read the portfolio csv or select an asset from etf_pct_returns DataFrame i.e. 'QQQ'
portfolio = etf_pct_returns['QQQ']
# portfolio = pd.read_csv(portfolio_returns_csv_loc)

# Rename the column to portfolio
portfolio = portfolio.rename('portfolio')

# Update the portfolio returns in the DataFrame
portfolio_index_returns_pct.update(portfolio)

# Calculate the portfolio's rolling beta over a 63-day window to the SPY
rolling_covariance = portfolio_index_returns_pct['portfolio'].rolling(window=63).cov(portfolio_index_returns_pct['SPY'])
rolling_variance = portfolio_index_returns_pct['SPY'].rolling(window=63).var()
rolling_beta = rolling_covariance / rolling_variance

# Plot the rolling beta
fig, ax = plt.subplots()
ax.plot(rolling_beta.index, rolling_beta, label='63 Day Rolling Beta')
ax.set_xlabel('Date')
ax.set_ylabel('Beta')
ax.legend()
plt.show()

# Plot histogram of the rolling beta, with standard deviations & current value highlighted
fig, ax = plt.subplots()
sns.histplot(rolling_beta, kde=True, ax=ax)
ax.set_xlabel('Beta')
ax.set_ylabel('Frequency')
ax.axvline(x=rolling_beta.mean(), color='r', linestyle='--', label='Mean')
ax.axvline(x=rolling_beta.mean() + rolling_beta.std(), color='g', linestyle='--', label='1 Stdev')
ax.axvline(x=rolling_beta.mean() - rolling_beta.std(), color='g', linestyle='--')
ax.axvline(x=rolling_beta.mean() + 2 * rolling_beta.std(), color='b', linestyle='--', label='2 Stdev')
ax.axvline(x=rolling_beta.mean() - 2 * rolling_beta.std(), color='b', linestyle='--')
ax.axvline(x=rolling_beta.iloc[-1], color='y', linestyle='--', label='Current Value')
ax.legend()
plt.show()
