# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 21:50:17 2017
@author: dulrich@kargo.com
Traffic analysis for editorial content

ETA(): Used for topograhic (3D) graph data
Stitches growth data (growth_file) to metric data (apd_file) and calculates the gradient growth/decay of 
the traffic (impressions) for each key_feature.  The data is normalized by the aggregate mean to remove outliers (growth 
anomalies).

PriceAnalysis(): Pricing data for a given publisher or key feature

"""
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# graphing tools
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D

# plotly
import plotly
plotly.offline.init_notebook_mode()
import plotly.graph_objs as go
from plotly.graph_objs import *

# builds eta vector without using the gradient method
# apd_file [ATTENTION, HOST, IMPRESSIONS]
# relevancy_file [RELEVANCY, HOST]
# graph [True/False]
# kf: key feature column name

class iab():
    def __init__(self, apd_file='domain_apd.csv', iab_dict='iab_list.csv', graph = False, kf = 'NAME'):
        
        # correlation coefficient of impressions to apd
        self.apd_imp_coef = 0.0
        
        # load CSV files into Pandas DataFrames
        apd = pd.read_csv(apd_file)
        iab = pd.read_csv(iab_dict)
        
        # merge both files
        df_merge = pd.merge(apd, iab, how='right')
        
        # remove NaN (empty) rows
        df_merge = df_merge[np.isfinite(df_merge['APD'])]
        df_merge = df_merge[np.isfinite(df_merge['IMPRESSIONS'])]
                            
        # get mean apd by IAB category
        iab_apd = df_merge.groupby(kf).APD.mean().to_dict()
        
        # get mean impressions by IAB category
        iab_impressions = df_merge.groupby(kf).IMPRESSIONS.mean().to_dict()
    
        # move calculated columns into separate arrays for graphing
        names = []
        apd = []
        impressions = []
        for key, val in iab_apd.items():
            names.append(key)
            apd.append(val)
            
        for key, val in iab_impressions.items():
            impressions.append(val)
            
        # calculate correlation coefficient for impressions + apd
        self.apd_imp_coef = np.corrcoef(impressions,apd)[1,0]
            
        # graph using Plotly
        if graph:
            self.chart(names, apd, impressions)
        
    def chart(self, categories, apd, impressions):
        
        # convert variables into Numpy arrays for plotting
        labels = np.asarray(categories)
        pie_values = np.asarray(impressions)
        bar_values = np.asarray(apd)
        
        # abbreviate categories for better Pie chart appearance
        abbvs = np.asarray(['Business','Home','Entertainment','Family','Hobbies','Auto','Health','Travel','News','Tech','Sports','Politics','Fashion','Food'])
        
        # generate colors for pie/bar charts
        N = len(categories) * 2
        c = ['hsl('+str(h)+',50%'+',50%)' for h in np.linspace(0, 360, N)]
        c = c[1::2]
        traces = []
        
        # pie chart data
        trace = go.Pie(labels = abbvs,
                       values = pie_values,
                       domain = {'x': [0, 1], 'y': [.5, 1]},
                       hoverinfo = 'label+percent',
                       textinfo='label+percent',
                       name='% of Traffic',
                       hole=.4,
                       marker=dict(colors=c, 
                           line=dict(color='#000000', width=1))
                       )
        traces.append(trace)
        
        # bar chart data
        trace = go.Bar(x = labels,
                       y = bar_values,
                       hoverinfo = 'label+percent',
                       name='MS',
                       marker=dict(
                        color=c)
                        )
        traces.append(trace)     

        # format the graph domain
        # Plotly doesn't easily allow us to add multiple graphs to a single page,
        # so we have to specify what regions each graph will be in
        layout = go.Layout(height = 900,
                           width = 1200,
                           autosize = True,
                           title = 'IAB Category Distribution',
                           xaxis = dict(
                              nticks = 14,
                              domain = [.0, 1] # entire width of page
                            ),
                            yaxis = dict(
                              scaleanchor = "x",
                              domain = [.0, .5], # top half page
                              title = "Time Spent on Page (MS)"
                            ),
                            paper_bgcolor='black',
                            plot_bgcolor='black',
                            font=dict(
                            size=14,
                            color='lightgrey'),
                            dragmode='zoom',
                            annotations=[
                                    dict(                            
                                        text="% Impressions",    
                                        x=.5,                         
                                        xref="paper",                
                                        y=.76,                         
                                        yref="paper",
                                        showarrow=False
                                    )
                                ],
                                margin=go.Margin(
                                l=100,
                                r=50,
                                b=125,
                                t=50,
                                pad=4
                            )
                        )
        fig = go.Figure(data = traces, layout = layout)
        
        # save graph to html file
        plotly.offline.plot(fig, filename="iab_metrics.html") 
        
class simple_eta():
    def __init__(self, apd_file = 'iab2_attention.csv', relevancy_file = 'iab2_relevancy.csv', graph = True, kf = 'HOST'):
        self.vectors = dict()
        print("Loading CSV data...")
        apd = pd.read_csv(apd_file)
        relevancy = pd.read_csv(relevancy_file)
        
        # active page dwell min/max
        apd_min, apd_max = apd.ATTENTION.min(), apd.ATTENTION.max()
        
        # merge rank and relevancy data
        df_merge = pd.merge(relevancy, apd, how='left')
        
        # drop publishers with no impressions (possibly outside of network)
        df_merge = df_merge[np.isfinite(df_merge['IMPRESSIONS'])]
        
        # lower "relevancy" numbers are good, so we want to invert the calculation to represent that
        df_merge['rel_scale'] = abs(1 - (df_merge['RELEVANCY'] / df_merge['IMPRESSIONS']))
        
        
        # relevancy min/max
        rel_min, rel_max = df_merge['rel_scale'].min(), df_merge['rel_scale'].max()
        
        # article count (impressions) min/max
        articles_min, articles_max = df_merge['IMPRESSIONS'].min(), df_merge['IMPRESSIONS'].max()
        print("Initializing vectors with [relevancy] and [popularity]...")
        for row in df_merge.iterrows():
            self.vectors[row[1][kf]] = {}
            self.vectors[row[1][kf]].update({"relevancy":self.scale_unity(row[1]['rel_scale'], rel_min, rel_max)})
            self.vectors[row[1][kf]].update({"popularity":self.scale_unity(row[1]['IMPRESSIONS'], articles_min, articles_max)})
            self.vectors[row[1][kf]].update({"attention":self.scale_unity(row[1]['ATTENTION'], apd_min, apd_max)})
            
            
        print("Vector initialization complete")
        
        graph_file = apd_file.split("_")[0] + " Topography Analysis"
            
        if graph:
            Graph().graph(vectors = self.vectors, file = graph_file)
        
    # use unity scale (-1,1)
    def scale_unity(self,value,v_min,v_max):
        avg = (v_min + v_max) / 2
        rng = (v_max - v_min) / 2
        return (value - avg) / rng
        #return (value - v_min) / (v_max - v_min)
    
    # use log10 scale
    def scale_log(self,value,average):
        return np.log10(abs((value / average)))
        
# initialize topographic analysis variables using gradient method
class ETA():
    def __init__(self, apd_file = 'apd_count.csv', growth_file = 'top_50_growth.csv', key_feature = 'PUBLISHER', smooth_outliers = 0.05, graph = True):
        self.vectors = dict()
        self.avg = 0.0
        # calculate gradient change for publisher
        print("Calculating vector gradients")
        growth_df = pd.read_csv(growth_file)
        
        growth_df['CHANGE'] = growth_df.groupby(key_feature).IMPRESSIONS.pct_change()
        
        # drop NaN values
        growth_df = growth_df[np.isfinite(growth_df['CHANGE'])]
        
        # remove outliers
        growth_normalized = growth_df[~(np.abs(growth_df.CHANGE-growth_df.CHANGE.mean())>(smooth_outliers*growth_df.CHANGE.std()))]
        
        # calculate gradient mean for each feature
        gradient_mean = growth_normalized.groupby(key_feature).CHANGE.mean()
        
        # mean of data set
        self.mean = np.mean(gradient_mean)
        
        # cast gradient to dictionary for iteration
        self.gradient_dict = gradient_mean.to_dict()
    
        # build vector dictionary with scaled gradient values
        for key in self.gradient_dict:
            self.vectors[key] = {}
            grad = self.scale_log(self.gradient_dict[key],self.mean)
            self.vectors[key].update({"gradient":grad})

        print("Vector gradients initialized.  Appending metrics...")
        # append MOAT metrics and impression data to vector dictionary
        metrics = pd.read_csv(apd_file)
        
        # mean values
        self.mean_apd = np.mean(metrics['APD'])
        self.mean_impressions = np.mean(metrics['IMPRESSIONS'])
        
        # row[0] = moat
        # row[1] = publisher
        # row[2] = impressions
        for index, row in metrics.iterrows():
            if row[1] in self.vectors:
                apd = self.scale_log(row[0],self.mean_apd)
                imp = self.scale_log(row[2],self.mean_impressions)
                self.vectors[row[1]].update({'apd':apd})
                self.vectors[row[1]].update({'imps':imp})
        
        print("Finished appending metrics\nReady")
        
        if graph:
            self.graph()
    
    def get_vectors(self):
        print(self.vectors)
        
    # scale data, converting values to percentages
    def scale_log(self,value,average):
        return np.log10(abs((value / average)))
        
# graph topographic analysis            
class Graph():
    def graph(self, vectors, as_plotly = True, precision = 2, file = ""):
        x = [] # grad (recency)
        y = [] # apd (attention demand)
        z = [] # imps (impressions)
        titles = [] # hover titles for Plotly
        
        # split vectors into X, Y, Z coordinates
        for key, value in vectors.items():
            x.append(value['relevancy'])
            y.append(value['attention'])
            z.append(value['popularity'])
            titles.append(key)
        
        # scale values
        x = np.asarray(x)
        y = np.asarray(y)
        z = np.asarray(z)
               
        if as_plotly:
            trace = go.Scatter3d(
                x = x, y = y, z = z,
                mode='markers',
                marker = dict(
                            color='rgba(97,123,155)', 
                            size = 12,
                            symbol='circle',
                            line = dict(color='rgb(22, 25, 32)', width=2),
                            opacity=0.9
                            ),
                text=titles
                )
            data = [trace]
            layout = go.Layout(
                                title=file,
                                scene = dict(
                                xaxis = dict(
                                     title="X: RELEVANCY",
                                     backgroundcolor="rgb(215,25,28)",
                                     gridcolor="rgb(255, 255, 255)",
                                     showbackground=True,
                                     zerolinecolor="rgb(0,0, 0)",),
                                yaxis = dict(
                                    title="Y: ATTENTION DEMAND",
                                    backgroundcolor="rgb(253,174,97)",
                                    gridcolor="rgb(255, 255, 255)",
                                    showbackground=True,
                                    zerolinecolor="rgb(0,0, 0)"),
                                zaxis = dict(
                                    title="Z: POPULARITY",
                                    backgroundcolor="rgb(171,217,233)",
                                    gridcolor="rgb(255, 255, 255)",
                                    showbackground=True,
                                    zerolinecolor="rgb(0, 0, 0)",),),
                                width=1000,
                                margin=dict(
                                r=10, l=10,
                                b=10, t=50)
                              )                        
            fig = go.Figure(data=data, layout=layout)
            
            #plotly.offline.iplot(fig, filename='eta_scatter')
            plotly.offline.plot(fig, filename=file+".html")
            
        else:
            # format graph
            mpl.rcParams['legend.fontsize'] = 10
            fig = plt.figure()
            ax = fig.gca(projection='3d')
            fig.set_size_inches(10,5,forward=True)
    
            
            # plot data
            ax.scatter(x, y, z)
            ax.set_xlim(min(x), max(x))
            ax.set_ylim(min(y), max(y))
            ax.set_zlim(min(z), max(z))
            ax.set_xlabel('Relevancy')
            ax.set_ylabel('Attention Demand')
            ax.set_zlabel('Popularity')
            plt.show()
        
class PriceAnalysis():
    
    def __init__(self, file = 'cnn_price_data.csv', days = 7, feature_name = "ARTICLE"):
        self.days = days
        self.X = [] # x-axis
        self.y = [] # y-axis
        self.graph_init = False
        self.roc = []
        self.series = dict()
        self.p_change = 0.0
        self.feature = feature_name
        
        self.df = pd.read_csv(file)
        
        day = 1
        print("Initializing DataFrame...")
        # init an N-day window for each article filling in blanks 
        for index, row in self.df.iterrows():
            if row[feature_name] != '':
                if row[feature_name] in self.series:
                    day += 1
                    if day < (self.days + 1):
                        self.series[row[feature_name]].update({day:row["IMPRESSIONS"]})
                else:
                    day = 1
                    self.series[row[feature_name]] = {}
                    self.series[row[feature_name]].update({day:row["IMPRESSIONS"]})               
            
        

        print("DataFrame series initialized with",len(self.series),"records")
        
        #self.init_axes()
        self.prices()
        
    def prices(self):
        # remove the duplicates
        prices = self.df.drop_duplicates([self.feature,'AVG_PRICE'])
        
        print(prices.describe())
        plt.figure(figsize=(10,4))
        plt.scatter(prices['AVG_PRICE'],prices['AVG_PRICE'])
        plt.show()
        #prices.plot.scatter(x='AVG_PRICE', y='AVG_PRICE');
    
    # populate X,y variables for graph
    def init_axes(self):
        # initialize empty list of days
        day_sum = [0] * int(self.days)
        i = k = 0
        
        print("Initializing axes...")
        # sum the respective days
        for key in self.series:
            for i in range(self.days):
                if i == 0:
                    if 1 in self.series.get(key):
                        day_sum[0] += int(self.series.get(key)[1])
                else: 
                    # offset array to account for first day
                    if i+1 in self.series.get(key):
                        day_sum[i] += int(self.series.get(key)[i])
                      
        # build y-axis
        for k in day_sum:
            self.y.append(round(k / len(self.series),2))
            
        print(self.y)
            
            
        # calculate gradient
        self.roc = np.gradient(self.y)
        
        # calculate percent change
        self.p_change = np.diff(self.y) / self.y[:-1] * 100.
        
        # build x-axis
        for i in range(len(day_sum)):
            self.X.append(i)
        
        print("Axes initialized, y:",len(self.y),"X:",len(self.X))
            
    # graph the average impressions per day
    def graph_avg(self):
        lifecycle = plt.figure(1)
        ax1 = lifecycle.add_subplot(111)
        lifecycle.set_size_inches(10,5,forward=True)
        ax1.plot(self.X, self.y, label='7 Day Lifecycle')
        
        # add markers
        for i,j in zip(self.X,self.y):
            ax1.annotate(str(j),xy=(i,j))
        
        ax1.legend(loc='upper center', shadow=True)
        ax1.set_xlabel('Days')
        ax1.set_ylabel('Average Impressions')
        
    # graph the average rate of change per day
    def graph_grad(self):
        gradient = plt.figure(2)
        ax2 = gradient.add_subplot(111)
        gradient.set_size_inches(10,5,forward=True)
        ax2.plot(self.X, self.roc, 'r',label='Average Impressions by Day')
        
        # add markers
        for i,j in zip(self.X,self.roc):
            ax2.annotate(str(j),xy=(i,j))
            
        ax2.legend(loc='upper center', shadow=True)
        ax2.set_xlabel('Days')
        ax2.set_ylabel('Impressions Gradient by Day')
        
    # graph the average rate of change per day
    def graph_percent_diff(self):
        p_diff = plt.figure(3)
        ax3 = p_diff.add_subplot(111)
        p_diff.set_size_inches(10,5,forward=True)
        
        # requires smaller x-axis
        j = 0
        x = []
        for i in range(len(self.p_change)):
            j+=1
            x.append(j)
          
        ax3.plot(x, self.p_change, 'g',label='% Impression Change by Day')
        
        # add markers
        for i,j in zip(self.X,self.p_change):
            ax3.annotate(str(round(j,2)) + '%',xy=(i,j))
            
        ax3.legend(loc='upper center', shadow=True)
        ax3.set_xlabel('Days')
        ax3.set_ylabel('Impressions Change')
        
