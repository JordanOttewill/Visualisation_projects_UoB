# -*- coding: utf-8 -*-
"""
Created on Wed May 25 19:58:04 2022

@author: jordan.ottewill
"""

import numpy as np
import pandas as pd
import json, urllib.request
import matplotlib.pyplot as plt
import seaborn as sns

"""Part 1, Q1"""

#open a request to read the data
data = urllib.request.urlopen('https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/date-range/2020-01-22/2020-05-10').read()

# load the data (will be saved as dictionary in output)
output = json.loads(data)
    
###we have 3 dictionaries within a dictionary...Make each one a dictionary then convert to a DF.

#create empty dictionary
cases = {}
#create empty keys within dictionary for each country
for country in output["data"]["2020-01-22"]:
    cases["{0}".format(country)] = []

#populate keys with data for each date record
for date in output["data"]:
    for country in output["data"][date]: 
            cases["{0}".format(country)].append(output["data"][date][country]["confirmed"])
            
#repeat for other two dictionaries

deaths = {}
#create empty keys within dictionary for each country
for country in output["data"]["2020-01-22"]:
    deaths["{0}".format(country)] = []

#populate keys with data for each date record
for date in output["data"]:
    for country in output["data"][date]: 
            deaths["{0}".format(country)].append(output["data"][date][country]["deaths"])
            
stringency = {}
#create empty keys within dictionary for each country
for country in output["data"]["2020-01-22"]:
    stringency["{0}".format(country)] = []

#populate keys with data for each date record
for date in output["data"]:
    for country in output["data"][date]: 
            stringency["{0}".format(country)].append(output["data"][date][country]["stringency"])
            
##Conversion of each dictionary into a seperate dataframe for exporting into a file. Will need to combine sheets too.
#create list of dates
dates = []
for date in output["data"]:
    dates.append(date)

#convert dict to df with dates as columns
casesdf = pd.DataFrame.from_dict(cases,orient='index',columns=dates)
#rename index
casesdf.rename_axis('country_code',inplace=True)

#repeat for the other two

deathsdf = pd.DataFrame.from_dict(deaths,orient='index',columns=dates)
#rename index
deathsdf.rename_axis('country_code',inplace=True)

stringencydf = pd.DataFrame.from_dict(stringency,orient='index',columns=dates)
#rename index
stringencydf.rename_axis('country_code',inplace=True)

#convert to excel with pd.to_excel()

#with pd.ExcelWriter(r'C:\Users\jordan.ottewill\OneDrive - Wesco Aircraft Hardware Corporation\Apprenticeship\DEVA\My_OxCGRT_summary.xlsx') as writer:
#    casesdf.sort_values('country_code').to_excel(writer, sheet_name='confirmedcases')
#    deathsdf.sort_values('country_code').to_excel(writer, sheet_name='confrimeddeaths')
#    stringencydf.sort_values('country_code').to_excel(writer, sheet_name='stringencyindex')
    
"""Part 1, Q2"""
##Import dataset and then pre-processing

oxcases = pd.read_excel(r'C:\Users\jordan.ottewill\OneDrive - Wesco Aircraft Hardware Corporation\Apprenticeship\DEVA\OxCGRT_summary.xlsx', 
                        sheet_name=0)

oxdeaths = pd.read_excel(r'C:\Users\jordan.ottewill\OneDrive - Wesco Aircraft Hardware Corporation\Apprenticeship\DEVA\OxCGRT_summary.xlsx', 
                        sheet_name=1)

oxstringency = pd.read_excel(r'C:\Users\jordan.ottewill\OneDrive - Wesco Aircraft Hardware Corporation\Apprenticeship\DEVA\OxCGRT_summary.xlsx', 
                        sheet_name=2)

#overview of data
print("CASES DATA")
print(oxcases.describe())
print(oxcases.info())
#info is too large to show NaN values
#do value counts of isnull provide an insight to a trend?
print(oxcases.isnull().value_counts())
#one row is missing all data...drop the row.

oxcases.dropna(axis=0,inplace=True)

#check for other two datasets.
print("DEATHS DATA")
print(oxdeaths.describe())
print(oxdeaths.info())
print(oxdeaths.isnull().value_counts())

oxdeaths.dropna(axis=0,inplace=True)

print("STRINGENCY DATA")
print(oxstringency.describe())
print(oxstringency.info())
print(oxstringency.isnull().value_counts())

#find rows with missing values
missingstringency = []
   
for x,y in oxstringency.iterrows():
    rowhasNaN = y.isnull()
    if rowhasNaN.any():
        missingstringency.append(x)

#drop two rows with completely missing data
oxstringency.drop(axis=0,index=[38,67],inplace=True)

#fill rest of NaN values with prior.
##oxstringency_clean = oxstringency.ffill(axis=1) - Returns an object df so cannot use!

oxstringency.loc[107,["08May2020","09May2020","10May2020"]] = 75
oxstringency.loc[111,["05May2020","06May2020","07May2020"]] = 69.44

"""Part 2, Q3"""
"""Q3"""

print(oxcases[oxcases["country_name"].isin(['United States','United Kingdom','China','South Korea','France','Italy'])])

q3case = oxcases[oxcases["country_name"].isin(['United States','United Kingdom','China','South Korea','France','Italy'])]
q3string = oxstringency[oxstringency["country_name"].isin(['United States','United Kingdom','China','South Korea','France','Italy'])]

##q3data = q3case.merge(q3string, how = 'left', on = 'carrier')

print(q3case.iloc[0,2:112])

plt.figure()
plt.title("Non-logarithmic comparison of the strignency of COVID-19 rsponses in six countries")
plt.scatter(x=q3case.iloc[0,2:112],y=q3string.iloc[0,2:112],color='blue',label='China')
plt.scatter(x=q3case.iloc[1,2:112],y=q3string.iloc[1,2:112],color='yellow',label='France')
plt.scatter(x=q3case.iloc[2,2:112],y=q3string.iloc[2,2:112],color='orange',label='UK')
plt.scatter(x=q3case.iloc[3,2:112],y=q3string.iloc[3,2:112],color='green',label='Italy')
plt.scatter(x=q3case.iloc[4,2:112],y=q3string.iloc[4,2:112],color='purple',label='South Korea')
plt.scatter(x=q3case.iloc[5,2:112],y=q3string.iloc[5,2:112],color='red',label='US')
plt.legend()
plt.xlabel('Cases')
plt.ylabel('Stringency')
plt.xticks([0,200000,400000,600000,800000,1000000,1200000],labels=[0,200000,400000,600000,800000,1000000,1200000])
#plt.plot(q3case.iloc[0,2:112],q3string.iloc[0,2:112])
plt.show()

"""Q4 WE NEED TO DERIVE THE NEW CASES PER DAY...THIS WILL BE CONFIRMED CASES - CONFIRMED CASES FROM THE DAY BEFRORE..."""
###Use dictionary like before, then convert to a DF.
###

"""missing rows will cause issues cycling through index. Need to reset index"""
oxcases.reset_index(drop=True,inplace=True)

#create empty dictionary
newcasesdict = {}

#create empty keys within dictionary for each country
for x in oxcases.country_name:
    newcasesdict["{0}".format(x)] = []

#Cannot create new cases for first date (22Jan, so start with index 3, 23Jan)
for x in oxcases.country_name.index:
#country_name.index is used instead of a range due to removed rows    
        for y in np.arange(3,112):
        #can use arange as no dropped columns
            #print("Country: ",oxcases.country_name[x])
            #print("x: ", x)
            #print("Value: ", oxcases.iloc[x-1,y]-oxcases.iloc[x-1,y-1])
            newcasesdict["{0}".format(oxcases.country_name[x])].append(oxcases.iloc[x,y]-oxcases.iloc[x,y-1])

#Dict now has changes from 23Jan until 10May
##Convert to a DF will require date columns.
#create list of dates
newdates = []
for y in np.arange(3,112):
    newdates.append(oxcases.columns[y])

#convert dict to df with dates as columns
newcases = pd.DataFrame.from_dict(newcasesdict,orient='index',columns=newdates)
#rename index
newcases.rename_axis('country_name',inplace=True)
newcases.reset_index(inplace=True)
print(newcases.info())

#copy df to trim
q4 = newcases.copy(deep=True)
#to keep country, set as index and trim dates
q4.set_index("country_name",drop=True,inplace=True) 
#filter on dates
q4slim = q4.loc[:,"20Mar2020":"10Apr2020"]
q4slim.reset_index(inplace=True)
#restored country name

#find top 10
print(oxcases["10Apr2020"].nlargest(10))
#store index
q4top10 = oxcases["10Apr2020"].nlargest(10).index

for x in q4top10:
    print(oxcases.country_name[x])
#print top 10 names
    
"""Heatmap pre-processing"""
#set index
q4slim.set_index("country_name",drop=True,inplace=True) 
#Filter DF
q4data = q4slim.iloc[q4top10,:].copy(deep=True)

#generate total values for secondary plot   
q4totals = []
for x in np.arange(0,len(q4data)):
    q4totals.append(q4data.iloc[x,:].sum())

#append totals to data for sort.
q4data['total']=q4totals
q4data.sort_values(by='total',ascending=False,inplace=True)
#drop totals for heatmap

#sort list values for 2nd axis
q4totals = pd.DataFrame(q4totals)
q4totals.sort_values(by=0,ascending=False,inplace=True)

##drop totals from main heatmap
#q4data = q4data.copy(deep=True)
q4data.drop(columns='total',inplace=True)

"""create heatmap"""
#creating subplots to contain plot, and totals
fig = plt.figure()
ax0 = plt.subplot2grid((14,27),(0,4),colspan=19,rowspan=1) ##shape, location, cols, rows
ax1 = plt.subplot2grid((14,27),(4,2),colspan=22,rowspan=10)
ax2 = plt.subplot2grid((14,27),(4,25),colspan=2,rowspan=10)
#format heatmap
heatmap = sns.heatmap(q4data,
            ax = ax1,
            cmap='YlOrRd',
            center=5000,
            linewidths=0.5,
            yticklabels=True,
            xticklabels=7, #plot every 7th label
            vmax=30000, #set 30K as limit
            #vmin=0, #add a min to shift the colorbar along
            cbar_ax = ax0,
            cbar_kws = dict(orientation='horizontal',
                            #location='top',          ##argument removed as cbar_ax employed
                            #label='New daily confirmed cases', ##moved to plt.title
                            ticks=[-20000,-10000,0,10000,20000,30000],
                            ticklocation='bottom')
            )
heatmap.set_xticklabels(['03/20','03/27','04/03','']) #replace tick labels with list values
heatmap.xaxis.tick_top() ##set x_axis on top
heatmap.tick_params(left=False,top=False,labelcolor='grey') #tick parameters
#add vlines for the xticks
heatmap.vlines(x=[7,14],
               ymin=0,
               ymax=100000000,
               colors=['grey'],
               linestyles='solid')
heatmap.set_ylabel('') #remove y label that comes from making a heatmap w/ a DataFrame
#format totals
totals = sns.heatmap(q4totals,
                     ax = ax2,
                     annot=True,
                     fmt='g', #int cannot format
                     annot_kws=dict(color='grey'),
                     cbar=None,
                     cmap=['white'],
                     yticklabels=False)
totals.xaxis.tick_top() ##set x_axis on top
totals.set_xticklabels(['Totals'])
totals.tick_params(left=False,top=False,labelcolor='grey')
#format colorbar
ax0.set_xticklabels(['-20K','-10K','0','10K','20K','30K'])
ax0.tick_params(left=False,bottom=False,labelcolor='grey') #tick parameters
ax0.vlines(x=[-20000,-10000,0,10000,20000,30000],
          ymin=-10000000,
          ymax=100000000,
          color='white',
          linestyles='solid')
#title
ax1.set_title(loc='left',
              label='New daily confirmed cases',
              fontdict=dict(fontweight='bold',
                            color='black'
                            ),
              pad=60
              )
plt.show()

"""Create Pie Charts"""
#US v ROW
#population, total cases, total deaths
##from oxcases and oxdeaths
oxcases10may = oxcases.loc[:,['country_name','10May2020']]
oxdeaths10may = oxdeaths.loc[:,['country_name','10May2020']]

#find index
print(oxcases10may[oxcases10may['country_name']=='United States'])
#index=176

#create seperate datasets for USA and ROW
usacases = oxcases10may[oxcases10may['country_name']=='United States']
usadeaths = oxdeaths10may[oxdeaths10may['country_name']=='United States']

#create ROW data
oxcases10may.drop(index=176,inplace=True)
oxdeaths10may.drop(index=176,inplace=True)

print(oxcases10may.sum())
##is this low compared to 1May??
oxcases1may = oxcases.loc[:,['country_name','01May2020']]
oxcases1may.drop(index=176,inplace=True)
print(oxcases1may.sum())
##YES - question data source must not be the same?

#resume creation of ROW data
q5data = {'Country':['United States','Rest of World'],
          'Population':[328000000,7800000000],  #fig 3 data
           'Cases':[],
           'Deaths':[]}
#us data
q5data['Cases'].append(usacases.iloc[0,1])
q5data['Deaths'].append(usadeaths.iloc[0,1])
#row data
q5data['Cases'].append(oxcases10may.iloc[:,1].sum())
q5data['Deaths'].append(oxdeaths10may.iloc[:,1].sum())

#Data ready, now piechart
figure, (pie1,pie2,pie3) = plt.subplots(nrows=1,ncols=3,figsize=(10,5))
colors = ['tab:blue','tab:orange']
plt.suptitle("US COVID-19 vs Rest of World")
#population
pie1.set_title('Population', pad=20, fontdict = dict(color='grey'))
pie1.pie(q5data['Population'],
         colors=colors,
         counterclock=False, #wedge angel to be drawn clockwise
         startangle=90, #start at the top
         textprops=dict(color='black',size='smaller'
             ),
         wedgeprops=dict(edgecolor='white',
                         linewidth=1
                         )
         )
#totals
pie1.set_xlabel(' 328,000,000\n7,800,000,000',loc='center') #propulate total values
#annotations
pie1.annotate('United States\n     4%',xy=(0.11,0.98), #location of annotation anchor
              xytext=(0.54,1.3), #location of text
              size='xx-small', #annotation size
              arrowprops=dict(linewidth=0.3,
                              color='black',
                              arrowstyle='-',
                              connectionstyle="arc,angleA=180,armA=40") #connection style defines arrow shape
              )
pie1.annotate('Rest of World\n     96%',xy=(-0.58,-0.70),size='xx-small')
#cases
pie2.set_title('Confirmed Cases', pad=10, fontdict = dict(color='grey')
               )
pie2.pie(q5data['Cases'],
         labels=q5data['Country'], 
         colors=colors,
         counterclock=False,
         startangle=90,
         textprops=dict(color='white'
             ),
         wedgeprops=dict(edgecolor='white',
                         linewidth=1
                         ),
         autopct ='%1.1f%%'
         )
pie2.set_xlabel('1,332,332\n2,762,942',loc='center')
#deaths
pie3.set_title('Deaths', pad=10, fontdict = dict(color='grey')
               )
pie3.pie(q5data['Deaths'], 
         #labels=q5data['Country'], 
         colors=colors,
         counterclock=False,
         startangle=90,
         textprops=dict(color='white'
             ),
         wedgeprops=dict(edgecolor='white',
                         linewidth=1,
                         #label=['27.3%']
                         ),
         autopct ='%1.1f%%'
         )
pie3.set_xlabel(' 83,059\n294,231',loc='center')
plt.show()


"""Part 3"""
"""Q6, UK deaths May 7th-10th"""

ukdeaths = pd.DataFrame(oxdeaths.loc[61,'07Mar2020':'10May2020'])
ukdeaths.reset_index(inplace=True)
ukdeaths.rename(columns={'index':'Date',61:'Deaths'}, inplace=True)
#trim date
ukdeaths['Date'] = ukdeaths['Date'].apply(lambda x: x[:5])

plt.figure(figsize=(12,9))
plt.title('Confirmed COVID-19 Deaths in the UK between 7th March and 10th May 2020')
q6 = sns.lineplot(data=ukdeaths,x='Date',y='Deaths',marker='o'
             )
plt.xticks(ticks=np.arange(0,65,4), #every 4th day
           rotation=45)
plt.yticks(ticks=np.arange(0,35000,2500))
plt.grid(visible=True)

"""Q7, New Daily cases between UK, Spain, Italy, France, USA"""

q7data = newcases.set_index("country_name").loc[["United Kingdom","Spain","Italy","France","United States"],"01Mar2020":"01May2020"]
q7data.reset_index(inplace=True)
##reshape data
q7data = pd.melt(frame=q7data,id_vars='country_name')
q7data.rename(columns={'value':'New_Cases','variable':'Date','country_name':'Country'},inplace=True)
q7data['Date'] = q7data['Date'].apply(lambda x: x[:5])

plt.figure()
plt.title('New COVID-19 Cases between 1st March and 1st May 2020')
q7 = sns.lineplot(data=q7data, x='Date', y='New_Cases', hue='Country')
q7.spines['bottom'].set_position('zero')
plt.ylabel('New Cases')
plt.yticks(ticks=np.arange(-20000,52000,5000))
plt.xticks(ticks=np.arange(0,62,4),rotation=45)
q7.tick_params(axis='x',pad=60)
q7.fill_between(x=np.arange(0,62,1),
                y1=q7data[q7data['Country']=='France'].New_Cases,
                color=('red'),alpha=0.2)
q7.fill_between(x=np.arange(0,62,1),
                y1=q7data[q7data['Country']=='United Kingdom'].New_Cases,
                color=('blue'),alpha=0.3)
q7.fill_between(x=np.arange(0,62,1),
                y1=q7data[q7data['Country']=='Spain'].New_Cases,
                color=('orange'),alpha=0.3)
q7.fill_between(x=np.arange(0,62,1),
                y1=q7data[q7data['Country']=='Italy'].New_Cases,
                color=('green'),alpha=0.3)
q7.fill_between(x=np.arange(0,62,1),
                y1=q7data[q7data['Country']=='United States'].New_Cases,
                color=('purple'),alpha=0.05)

"""Q8 4th May Correlation - Cases and Stringency, DOT SIZE = DEATHS"""

##Assemble data - oxcases and oxstringency
may4cases = oxcases.loc[:,['country_name','04May2020']]
may4str = oxstringency.loc[:,['country_name','04May2020']]
may4deaths = oxdeaths.loc[:,['country_name','04May2020']]
##join
may4data = may4cases.merge(may4str,how='left', on ='country_name')
may4data = may4data.merge(may4deaths,how='left', on ='country_name')
may4data.rename(columns={'country_name':'Country','04May2020_x':'Cases','04May2020_y':'Stringency', '04May2020':'Deaths'},inplace=True)
#two null values. No data correlation to be mapped so drop.
may4data.dropna(inplace=True)
may4data = may4data[may4data['Cases']>1000]

"correlation"
import mplcursors
# default radius of the biggest bubble is 20px, you can change it by size_max
plt.figure(figsize=(10,10))
plt.title('Stringency index vs confirmed cases with > 1000 confirmed COVID-19 cases on May 4th 2020')
scatter = sns.scatterplot(data=may4data, x='Cases', y='Stringency', hue='Country',
                      size='Deaths', sizes=(5,500))
scatter.set_xscale('log')
animation = mplcursors.cursor(hover=True)
animation.connect("add", lambda dot: dot.annotation.set_text(
    "Cases {},\nStringency {}".format(dot.target[0],dot.target[1]))
    )
plt.legend(ncol=2,loc='lower right',fontsize='xx-small', bbox_to_anchor=(1.35,0))
plt.tight_layout()
plt.show()

print(np.corrcoef(x=may4data['Cases'], y=may4data['Deaths']))