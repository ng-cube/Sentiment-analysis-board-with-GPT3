import tkinter as tk
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
plt.style.use('seaborn-whitegrid')
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import datetime as dt
import twitterConnectionClass, sqlConnectionClass
import seaborn as sns
sns.color_palette("tab10")

directory = '/Users/jacky/Repo/CZ2006/'

class Graph:
    def __init__(self, dataframe, keyword):
        self.dataframe = dataframe
        self.keyword = keyword

    def showGraph(self):
        #val = ((self.dataframe['date'][len(self.dataframe)-1]-self.dataframe['date'][0]).days)//5
        fig = plt.Figure(figsize=(8,6), dpi=80)
        ax = fig.add_subplot()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        #ax.xaxis.set_major_locator(mdates.DayLocator(interval=val))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        ax.scatter(self.dataframe['datetime'],self.dataframe['sentiments'],color='cadetblue',linewidth=2,s=10,label='Actual')
        ax.axhline(y=0, color = '#616161')
        ax.spines['right'].set_color((.8,.8,.8))
        ax.spines['top'].set_color((.8,.8,.8))
        ax.spines['left'].set_color((0.1,0.1,0.1))
        ax.spines['bottom'].set_color((0.1,0.1,0.1))
        ax.set_title(f'Sentiments of each tweet', fontsize=20, fontweight='bold', color='#30302f', loc='center')
        ax.tick_params(axis='x', labelrotation=45)
        fig.savefig(directory+'Interfaces/fig_line.png')
        return fig

    def chooseIndicator(self, indicator):
        if indicator=='Moving Average 5':
            a = MovingAverage(self.dataframe, indicator, self.keyword, 5)
        elif indicator=='Moving Average 10':
            a = MovingAverage(self.dataframe, indicator, self.keyword, 10)
        elif indicator=='Moving Average 20':
            a = MovingAverage(self.dataframe, indicator, self.keyword, 20)    
        elif indicator=='Exponential Average 0.1':
            a = ExponentialAverage(self.dataframe, indicator, self.keyword, eaRange=0.1)
        elif indicator=='Exponential Average 0.2':
            a = ExponentialAverage(self.dataframe, indicator, self.keyword, eaRange=0.2)
        elif indicator=='Exponential Average 0.3':
            a = ExponentialAverage(self.dataframe, indicator, self.keyword, eaRange=0.3)
        elif indicator=='Quantile Interval':
            a = QuantileIntervals(self.dataframe, indicator, self.keyword, pctPopulationLower=0.25, pctPopulationUpper=0.75)
        elif indicator=='Maximum and Minimum':
            a = MaxMin(self.dataframe, indicator, self.keyword)
        elif indicator in ('Positive', 'Negative', 'Neutral'):
            a = Count(self.dataframe, indicator, self.keyword)
        elif indicator=='Quantile Day':
            a = QuantileDay(self.dataframe, indicator, self.keyword, pctPopulationLower=0.25, pctPopulationUpper=0.75)
        elif indicator=='MaxMin Day':
            a = MaxminDay(self.dataframe, indicator, self.keyword)
        elif indicator=='Histogram':
            a = HistogramPlot(self.dataframe, indicator, self.keyword)
        return a

    def getDataframe(self):
        #tC = twitterConnectionClass.twitterConnection()
        #keyword = "microsoft"
        sC = sqlConnectionClass.sqlConnection()
        data = sC.get_timestamp_sentiment(self.keyword)
        self.dataframe = pd.DataFrame(data, columns=['timestamp','sentiments']) 
        #self.dataframe = self.dataframe.sort_values('timestamp')
        datetime1 = []
        for i in range(len(self.dataframe)):
            datetime1.append(datetime.fromtimestamp(self.dataframe['timestamp'][i]))
        self.dataframe['datetime'] = datetime1
        self.dataframe['date'] = self.dataframe['datetime'].dt.date
        end_day = max(self.dataframe['date'])
        days = timedelta(7) 
        start_day = end_day-days
        self.dataframe = self.dataframe[(self.dataframe.date <= end_day) & (self.dataframe.date > start_day)]
        self.dataframe = self.dataframe.reset_index(drop=True)
        self.dataframe = self.dataframe.sort_values(by=["timestamp"])
        #print(self.dataframe)
        return self.dataframe

    def getKeyword(self):
        return self.keyword 

class Indicators:
    def __init__(self, dataframe, indicator, keyword):
        self.dataframe = dataframe
        self.indicator = indicator
        self.keyword = keyword

    def applyIndicator():
        pass

class HistogramPlot(Indicators):
    def __init__(self, dataframe, indicator, keyword):
        super().__init__(dataframe,indicator,keyword)
    
    def indicatorTransform(self):   
        data = self.dataframe['sentiments'].to_list()
        ax1 = Graph(self.dataframe,self.keyword).showGraph().gca()
        fig = plt.Figure(figsize=(6,4), dpi=80)
        fig, ax = plt.subplots()
        n, bins, patches = ax.hist(data, bins=20, alpha=0.5,
         histtype='stepfilled', color='steelblue',
         edgecolor='none')
        ax.set_xticks(np.round(bins,1))
        #ax.set_xticklabels(np.round(bins,1),rotation=90)
        fig.savefig(directory+'Interfaces/fig_histogram.png')
        return fig 
        

class MovingAverage(Indicators):
    def __init__(self, dataframe, indicator, keyword, maRange):
        super().__init__(dataframe,indicator,keyword)
        self.maRange = maRange

    def indicatorTransform(self):
        name = 'SMA'+str(self.maRange)
        self.dataframe[name] = self.dataframe.iloc[:,1].rolling(self.maRange).mean()
        ax1 = Graph(self.dataframe,self.keyword).showGraph().gca()
        #fig = plt.Figure(figsize=(5,4), dpi=100)
        #ax1 = fig.add_subplot()
        line1 = ax1.plot(self.dataframe['datetime'][self.maRange+1:],self.dataframe[name][self.maRange+1:], color = 'r',label='Moving Average')
        ax1.legend()
        ax1.figure.savefig(directory+'Interfaces/fig_ma.png')
        return ax1, line1
        
    def removeIndicator(self):
        fig, line = self.indicatorTransform()
        l = line.pop(0)
        l.remove()

class ExponentialAverage(Indicators):
    def __init__(self, dataframe, indicator, keyword, eaRange):
        super().__init__(dataframe,indicator,keyword)
        self.eaRange = eaRange

    def indicatorTransform(self):
        name = 'EMA'+str(self.eaRange)
        self.dataframe[name] = round(self.dataframe.sentiments.ewm(alpha=self.eaRange, adjust=False).mean(), 2)
        #moving_averages_list = moving_averages.tolist()
        #dataframe[name] = moving_averages_list
        ax2 = Graph(self.dataframe,self.keyword).showGraph().gca()
        line2 = ax2.plot(self.dataframe['datetime'],self.dataframe[name], color = 'b', label='Exponential Average')
        ax2.legend()
        ax2.figure.savefig(directory+'Interfaces/fig_exp.png')
        return ax2, line2
        
    def removeIndicator(self):
        fig, line = self.indicatorTransform()
        l = line.pop(0)
        l.remove()

class QuantileIntervals(Indicators):
    def __init__(self, dataframe,indicator,keyword, pctPopulationLower, pctPopulationUpper):
        super().__init__(dataframe,indicator,keyword)
        self.pctPopulationLower = pctPopulationLower
        self.pctPopulationUpper = pctPopulationUpper

    def indicatorTransform(self):
        p1 = self.dataframe['sentiments'].quantile(.25)
        p2 = self.dataframe['sentiments'].quantile(.75)
        p3 = self.dataframe['sentiments'].quantile(.5)
        ax3 = Graph(self.dataframe,self.keyword).showGraph().gca()
        ax3.axhline(y=p1, color = 'y', linestyle = 'dashed', label = "25th percentile")
        ax3.axhline(y=p2, color = 'y', linestyle = 'dashed', label = "75th percentile")
        ax3.axhline(y=p3, color = 'y', linestyle = 'dashed', label = "50th percentile")
        #lines = ax3.gca().get_lines()
        style = dict(size=10, color='gray')
        #xvals = [0,0,1648100400,1648100400]
        ax3.text(self.dataframe['datetime'][len(self.dataframe)-1],p1,"25th percentile",**style)
        ax3.text(self.dataframe['datetime'][len(self.dataframe)-1],p2,"75th percentile",**style)
        ax3.text(self.dataframe['datetime'][len(self.dataframe)-1],p3,"50th percentile",**style)
        ax3.figure.savefig(directory+'Interfaces/fig_qi.png')
    
    def getValues(self):
        p1 = self.dataframe['sentiments'].quantile(.25) #25th percentile sentiment score overall
        p2 = self.dataframe['sentiments'].quantile(.75) #75th percentile sentiment score overall
        p3 = self.dataframe['sentiments'].quantile(.5) #median sentiment score overall
        return p1, p2, p3    

class QuantileDay(Indicators):
    def __init__(self, dataframe,indicator,keyword, pctPopulationLower, pctPopulationUpper):
        super().__init__(dataframe,indicator,keyword)
        self.pctPopulationLower = pctPopulationLower
        self.pctPopulationUpper = pctPopulationUpper

    def indicatorTransform(self):
        ax3 = Graph(self.dataframe,self.keyword).showGraph().gca()
        p1 = self.dataframe.groupby('date').quantile(.25)
        p2 = self.dataframe.groupby('date').quantile(.75)
        p3 = self.dataframe.groupby('date').quantile(.5)
        line3 = ax3.plot(p1.index,p1['sentiments'], color = 'b', label='25th percentile', marker = "+")
        line4 = ax3.plot(p2.index,p2['sentiments'], color = 'g', label='75th percentile', marker = 10)
        line5 = ax3.plot(p3.index,p3['sentiments'], color = 'orange', label='50th percentile', marker = "x")
        ax3.legend()
        ax3.figure.savefig(directory+'Interfaces/fig_25qi.png')
        return line3,line4,line5, ax3
    
    def getValues(self):
        p1 = self.dataframe.groupby('date').quantile(.25) #25th percentile sentiment score of each day
        p1_ = p1[['sentiments']]
        p2 = self.dataframe.groupby('date').quantile(.75) #75th percentile sentiment score of each day
        p2_ = p2[['sentiments']]
        p3 = self.dataframe.groupby('date').quantile(.5) #median sentiment score of each day
        p3_ = p3[['sentiments']]
        return p1_, p2_, p3_
        
class MaxminDay(Indicators):
    def __init__(self, dataframe,indicator,keyword):
        super().__init__(dataframe,indicator,keyword)

    def indicatorTransform(self):
        ax3 = Graph(self.dataframe,self.keyword).showGraph().gca()
        p1 = self.dataframe.groupby('date').max()
        p2 = self.dataframe.groupby('date').min()
        line3 = ax3.plot(p1.index,p1['sentiments'], color = 'b', label='Maximum')
        line4 = ax3.plot(p2.index,p2['sentiments'], color = 'g', label='Minimum')
        ax3.legend()
        ax3.figure.savefig(directory+'Interfaces/fig_maxminday.png')
        return line3,line4, ax3
    
    def getValues(self):
        p1 = self.dataframe.groupby('date').max() #max sentiment score of each day
        p1_ = p1[['sentiments']]
        p2 = self.dataframe.groupby('date').min() #min sentiment score of each day
        p2_ = p2[['sentiments']]
        return p1_, p2_  

class MaxMin(Indicators):
    def __init__(self, dataframe,indicator,keyword):
        super().__init__(dataframe,indicator,keyword)

    def indicatorTransform(self):
        p1 = self.dataframe['sentiments'].min()
        p2 = self.dataframe['sentiments'].max()
        ax3 = Graph(self.dataframe,self.keyword).showGraph().gca()
        ax3.axhline(y=p1, color = 'salmon', linestyle = 'dashed', label = "Minimum")
        ax3.axhline(y=p2, color = 'salmon', linestyle = 'dashed', label = "Maximum")
        #lines = ax3.gca().get_lines()
        style = dict(size=10, color='gray')
        ax3.text(self.dataframe['datetime'][len(self.dataframe)-1],p1,"Min: "+str(round(p1,5)),**style)
        ax3.text(self.dataframe['datetime'][len(self.dataframe)-1],p2,"Max: "+str(round(p2,5)),**style)
        ax3.figure.savefig(directory+'Interfaces/fig_minmax.png')
        
    def getValues(self):
        p1 = self.dataframe['sentiments'].min() #min sentiment score overall
        p2 = self.dataframe['sentiments'].max() #max sentiment score overall
        return p1, p2
        
class Count(Indicators):
    def __init__(self, dataframe,indicator,keyword):
        super().__init__(dataframe,indicator,keyword)

    def indicatorTransform(self):
        sentiments_label = []
        for i in range(len(self.dataframe)):
            if self.dataframe['sentiments'][i]> 0.05:
                sentiments_label.append('Positive')
            elif self.dataframe['sentiments'][i] < -0.05:
                sentiments_label.append('Negative')
            else:
                sentiments_label.append('Neutral')
        self.dataframe['sentiments_label'] = sentiments_label
        count_df = self.dataframe.groupby(['date','sentiments_label']).size().reset_index(name='Counts')
        return count_df
    
    def getValues(self):
        count_df = self.indicatorTransform()
        total = len(count_df)
        pos = len(count_df[count_df['sentiments_label'] == 'Positive'])
        neu = len(count_df[count_df['sentiments_label'] == 'Neutral'])
        neg = len(count_df[count_df['sentiments_label'] == 'Negative'])
        p_pos = round((pos/total)*100,2)
        p_neu = round((neu/total)*100,2)
        p_neg = round((neg/total)*100,2)
        return p_pos, p_neu, p_neg
        
    def PositiveCount(self):
        count_df = self.indicatorTransform()
        positive_df = pd.DataFrame(count_df[count_df['sentiments_label']=='Positive'])
        fig1 = Graph(self.dataframe,self.keyword).showGraph().gca()
        #x = positive_df['month'].to_list()
        x = positive_df['date'].to_list()
        x1 = [i for i in range(len(x))]
        y = positive_df['Counts'].to_list()
        fig = plt.Figure(figsize=(6,4), dpi=80)
        fig, ax = plt.subplots()
        ax.bar(x1, y, width=0.4, color = '#1f77b4')
        ax.set_xticks(x1)
        ax.set_xticklabels(x,rotation=30)
        fig.savefig(directory+'Interfaces/fig_positive.png')
        ax.set_title(f'Count of Positive tweets', fontsize=20, fontweight='bold', color='#30302f', loc='center')
        return fig
    
    def NegativeCount(self):
        count_df = self.indicatorTransform()
        negative_df = pd.DataFrame(count_df[count_df['sentiments_label']=='Negative'])
        fig1 = Graph(self.dataframe,self.keyword).showGraph().gca()
        #x = negative_df['month'].to_list()
        x = negative_df['date'].to_list()
        x1 = [i for i in range(len(x))]
        y = negative_df['Counts'].to_list()
        fig = plt.Figure(figsize=(6,4), dpi=80)
        fig, ax = plt.subplots()
        ax.bar(x1, y, width=0.4, color = '#ff7f0e')
        ax.set_xticks(x1)
        ax.set_xticklabels(x,rotation=30)
        ax.set_title(f'Count of Negative tweets', fontsize=20, fontweight='bold', color='#30302f', loc='center')
        fig.savefig(directory+'Interfaces/fig_negative.png')
        return fig
        
    def NeutralCount(self):
        count_df = self.indicatorTransform()
        neutral_df = pd.DataFrame(count_df[count_df['sentiments_label']=='Neutral'])
        fig1 = Graph(self.dataframe,self.keyword).showGraph().gca()
        #x = neutral_df['month'].to_list()
        x = neutral_df['date'].to_list()
        x1 = [i for i in range(len(x))]
        y = neutral_df['Counts'].to_list()
        fig = plt.Figure(figsize=(6,4), dpi=80)
        fig, ax = plt.subplots()
        ax.bar(x1, y, width=0.4, color = '#2ca02c')
        ax.set_xticks(x1)
        ax.set_xticklabels(x,rotation=30)
        ax.set_title(f'Count of Neutral tweets', fontsize=20, fontweight='bold', color='#30302f', loc='center')
        fig.savefig(directory+'Interfaces/fig_neutral.png')
        return fig
    
    def allCount(self):
        fig1 = Graph(self.dataframe,self.keyword).showGraph()
        count_df = self.indicatorTransform()
        fig, axes = plt.subplots(figsize =(8, 6),dpi=80)
        #sns.barplot(ax=axes, x="month", y="Counts", hue="sentiments_label", data=count_df)
        sns.barplot(ax=axes, x="date", y="Counts", hue="sentiments_label", data=count_df).set_title(f'Count of sentiments of tweets', fontsize=20, fontweight='bold', color='#30302f', loc='center')
        plt.xticks(rotation=30)
        fig.savefig(directory+'Interfaces/fig_allCount.png')
        return fig       
