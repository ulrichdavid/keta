# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 03:41:14 2017

@author: dulrich@kargo.com
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

class keta():
    def __init__(self, in_file='top_50_in_window.csv', out_file='top_50_out_window.csv', apd_file='top_50_attn_scale.csv', kf='PUBLISHER', attn_key='AVG_APD', graph=True):
        self.vectors = dict()
        apd = pd.read_csv(apd_file)
        out_window = pd.read_csv(out_file)
        in_window = pd.read_csv(in_file)
        
        df = apd.merge(out_window,on='PUBLISHER').merge(in_window,on='PUBLISHER')
        
        # lower "relevancy" numbers are good, so we want to invert the calculation to represent that
        df['relevancy'] = abs(1 - (df['OUT_WINDOW'] / df['IN_WINDOW']))
        
        apd_min, apd_max = apd.AVG_APD.min(), apd.AVG_APD.max()
        
        # relevancy min/max
        rel_min, rel_max = df['relevancy'].min(), df['relevancy'].max()
        
        # article count (impressions) min/max
        articles_min, articles_max = df['IMPRESSIONS'].min(), df['IMPRESSIONS'].max()
        print("Initializing vectors with [relevancy] and [popularity]...")
        for row in df.iterrows():
            self.vectors[row[1][kf]] = {}
            self.vectors[row[1][kf]].update({"relevancy":self.scale_unity(row[1]['relevancy'], rel_min, rel_max)})
            self.vectors[row[1][kf]].update({"popularity":self.scale_unity(row[1]['IMPRESSIONS'], articles_min, articles_max)})
            self.vectors[row[1][kf]].update({"attention":self.scale_unity(row[1][attn_key], apd_min, apd_max)})
            
            
        print("Vector initialization complete")
        
        graph_file = "Top 50 Topography Analysis"
            
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
                            color=x, 
                            size = 12,
                            colorscale='Viridis',
                            opacity=0.8
                            ),
                text=titles
                )
            data = [trace]
            layout = go.Layout(
                                title=file,
                                scene = dict(
                                xaxis = dict(
                                     title="X: RELEVANCY",
                                     backgroundcolor="rgb(74,200,235)",
                                     gridcolor="rgb(255, 255, 255)",
                                     showbackground=True,
                                     zerolinecolor="rgb(0,0, 0)",),
                                yaxis = dict(
                                    title="Y: ATTENTION DEMAND",
                                    backgroundcolor="rgb(202,238,94)",
                                    gridcolor="rgb(255, 255, 255)",
                                    showbackground=True,
                                    zerolinecolor="rgb(0,0, 0)"),
                                zaxis = dict(
                                    title="Z: POPULARITY",
                                    backgroundcolor="rgb(237,83,175)",
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