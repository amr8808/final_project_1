import panel as pn
import hvplot.pandas
import pandas as pd
from panel.interact import interact
from panel import widgets


class nba:
    """Analyze NBA TopShot output csv from otmnft.com

    Keyword arguments:
    collection -- set transaction details, 10s of thousands of rows
    total -- set totals details
    summary -- player level details
    
    """
    def __init__ (self, collection, total, summary):
        self.csv = collection #assign csv to the class
        self.clean_csv() #run data cleaning
        self.allstar_total_csv(total)
        self.allstar_summary_csv(summary)
        
    def clean_csv(self):
        df = pd.read_csv(self.csv,infer_datetime_format=True,parse_dates=True, index_col='Transaction Date')
        df.index = df.index.date
        df.sort_index(inplace=True)
        self.df = df
    
    def allstar_total_csv(self, total):
        allstartotal_df = pd.read_csv(total, infer_datetime_format=True,parse_dates=True, index_col='DateTime')
        self.allstartot = allstartotal_df
        
    def allstar_summary_csv(self, summary):
        summary_df = pd.read_csv(summary, index_col='Player Name')
        summary_df.sort_values('Low Ask',ascending=False, inplace=True)
        self.all_summary = summary_df
    
    def hist_player_prices(self):
        return self.df.hvplot.line(y='Purchase Price',groupby='Player Name')
    
    def price_serial_corr(self):
        correlation_df = self.df.filter(['Player Name','Serial','Purchase Price'],axis=1)
        correlation_df.sort_index(inplace=True)
        psc_plot = correlation_df.corr().hvplot.heatmap()
        return psc_plot
    
    def transaction_count(self):
        number_of_transactions_df = self.df.groupby('Player Name').count().filter(['Player Name','Set'])
        number_of_transactions_df.columns = ['Transaction Count']
        number_of_transactions_df.sort_values('Transaction Count',inplace=True,ascending=False)
        txn_plot = number_of_transactions_df.hvplot.bar(rot=90,color='green')
        return txn_plot
    
    def serial_price(self):
        return self.df.hvplot.scatter(x='Serial', y='Purchase Price', groupby = 'Player Name',width = 1200, height =500,xticks = 25)
     
    def market_cap(self):
        return self.allstartot.hvplot.line(ylim=(0,18000), rot=90)
    
    def low_ask(self):
        return self.all_summary.hvplot.bar(y='Low Ask', rot=90)
    
    def dash(self):
        dashboard_title = "NBA TopShot Evaluator"
        welcome_message = "This is our NBA TopShot Evaluator.  Our mission is to help collectors accurately value their NFT portfolios and identify opportunities."
        pricing_vs_transcount_findings = "Observations: We found that, generally speaking, the number of transactions did not seem to be affected by floor price.  This shows that demand for individual moments was not detered by cost of moments."
        serial_findings = "Observations: We observe a slightly negative correlation between serial numbers and prices. However, this relationship is heavily weighted in the top 100 serial numbers as shown in the scatter and heatmap plots. With the current portfolio eval tools, an investors portfolio will not be accurately represented if they own low serials. Evaluation tools simply take the floor price of moments, and use that to determine portfolio value, leading to deflated portfolio valuation."
        all_star_icon = pn.pane.PNG('2021allstar.png', height=150, width=150)


        welcome_column = pn.Column(
                dashboard_title,
                all_star_icon,
                welcome_message,
                '2021 All Star Set Value', self.market_cap            
        )

        floor_column = pn.Column(
                all_star_icon,
                pricing_vs_transcount_findings,
                'Historal Prices by Player', self.hist_player_prices(),
                'Player Floor Price', self.low_ask(),
                'Number of Transactions by Player', self.transaction_count()
        )

        serial_column = pn.Column(
                all_star_icon,
                serial_findings,
                self.serial_price(),
                self.price_serial_corr()
        )
        
        tabs = pn.Tabs(
        ("Welcome",welcome_column),
        ("2021 All Star Pricing",floor_column),
        ("Serial Number/Price",serial_column)
        
        )
        
        tabs.servable()
        
        return tabs