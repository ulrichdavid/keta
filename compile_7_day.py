# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 21:50:17 2017

@author: dulrich@kargo.com

Quick and dirty way of preparing a 7 day window of article data

"""
import csv
import matplotlib.pyplot as plt
import numpy as np

file = 'metrolyrics_top_3000.csv'
series = dict()

# initialize the graph
X = []
y = []

with open(file, 'r', newline='', encoding='utf8') as csvfile:
    reader = csv.DictReader(csvfile)
    # create empty array for 7-day window for each article
    day = 1
    for row in reader:
        if row["PAGE"] != '':
            if row["PAGE"] in series:
                day += 1
                if day < 8:
                    series[row["PAGE"]].update({day:row["IMPRESSIONS"]})
            else:
                day = 1
                series[row["PAGE"]] = {}
                series[row["PAGE"]].update({day:row["IMPRESSIONS"]})

print("Series has:",len(series),"pages")

# calculate average rate of change for each article
def get_roc(avg = True, grad = True, change = True):
    day_1 = day_2 = day_3 = day_4 = day_5 = day_6 = day_7 = 0
    for key in series:
        day_1 += int(series.get(key)[1])
        if 2 in series.get(key):    
            day_2 += int(series.get(key)[2])
        if 3 in series.get(key):    
            day_3 += int(series.get(key)[3])
        if 4 in series.get(key):    
            day_4 += int(series.get(key)[4])
        if 5 in series.get(key):    
            day_5 += int(series.get(key)[5])
        if 6 in series.get(key):    
            day_6 += int(series.get(key)[6])
        if 7 in series.get(key):    
            day_7 += int(series.get(key)[7])  

    # build y axis        
    y.append(round(day_1 / len(series),2))
    y.append(round(day_2 / len(series),2))
    y.append(round(day_3 / len(series),2))
    y.append(round(day_4 / len(series),2))
    y.append(round(day_5 / len(series),2))
    y.append(round(day_6 / len(series),2))
    y.append(round(day_7 / len(series),2))
    
    roc = np.gradient(y)
    p_change = np.diff(y) / y[:-1] * 100.

    print(p_change)
    
    # build x axis
    j = 0
    for i in range(7):
        j+=1
        X.append(j)
    
    if avg:
        graph_avg()
        
    if grad:
        graph_grad(roc)
        
    if change:
        graph_percent_diff(p_change)
        
# graph the average impressions per day
def graph_avg():
    plt.figure(figsize=(10,5)) 
    lifecycle = plt.figure(1)
    ax1 = lifecycle.add_subplot(111)
    ax1.plot(X, y, label='7 Day Lifecycle')
    
    # add markers
    for i,j in zip(X,y):
        ax1.annotate(str(j),xy=(i,j))
    
    ax1.legend(loc='upper center', shadow=True)
    ax1.set_xlabel('Days')
    ax1.set_ylabel('Average Impressions')
    
# graph the average rate of change per day
def graph_grad(y):
    plt.figure(figsize=(10,5)) 
    gradient = plt.figure(2)
    ax2 = gradient.add_subplot(111)
    ax2.plot(X, y, 'r',label='Average Impressions by Day')
    
    # add markers
    for i,j in zip(X,y):
        ax2.annotate(str(j),xy=(i,j))
        
    ax2.legend(loc='upper center', shadow=True)
    ax2.set_xlabel('Days')
    ax2.set_ylabel('Impressions Gradient by Day')
    
# graph the average rate of change per day
def graph_percent_diff(y):
    plt.figure(figsize=(10,5)) 
    gradient = plt.figure(3)
    ax3 = gradient.add_subplot(111)
    
    # requires smaller x-axis
    j = 0
    x = []
    for i in range(6):
        j+=1
        x.append(j)
    ax3.plot(x, y, 'g',label='% Impression Change by Day')
    
    # add markers
    for i,j in zip(X,y):
        ax3.annotate(str(round(j,2)) + '%',xy=(i,j))
        
    ax3.legend(loc='upper center', shadow=True)
    ax3.set_xlabel('Days')
    ax3.set_ylabel('Impressions % Change')
   