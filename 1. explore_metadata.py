
# coding: utf-8

# In[ ]:

BOKEH_LOG_LEVEL='trace'


# In[9]:

from IPython.display import HTML
import bokeh
import pandas as pd
#
get_ipython().magic('pylab inline')

from bokeh.plotting import figure, show, output_file
from bokeh.io import output_notebook


# In[2]:

cypern = pd.read_excel("./excel-export.xls",sheetname="Cypern")
mexiko = pd.read_excel("./excel-export.xls",sheetname="Mexiko")


# In[3]:

cypern.info()


# In[4]:

mexiko.info()


# # General fill-ins analysis

# In[11]:

cyp = pd.DataFrame({"Ifyllda":cypern.count(),"Tomma":cypern.isnull().sum()})
cyp["Prc"] = cyp["Tomma"] / 1442
cyp = cyp.sort_values(by="Prc",ascending=False, inplace=False)
cyp.to_html()


# In[14]:

mex = pd.DataFrame({"Ifyllda":mexiko.count(),"Tomma":mexiko.isnull().sum()})
mex["Prc"] = mex["Tomma"] / 1442
mex = mex.sort_values(by="Prc",ascending=False, inplace=False)
mex


# In[16]:

fillins_df = pd.concat([cyp,mex], keys=("Mexiko","Cypern"), axis=1)
fillins_df


# In[17]:

fillins_p = figure(height=600, 
                   width=1000, 
                   x_range=list(fillins_df.index), 
                   y_range=[0,100],
                   tools="pan,box_zoom,save")
fillins_p.logo = None

fillins_p.title = "Fillins Mexiko vs Cypern"
fillins_p.line(fillins_df["Mexiko"].index, fillins_df["Mexiko"]["Prc"] * 100, color="blue", legend="Mexiko")
fillins_p.line(fillins_df["Cypern"].index, fillins_df["Cypern"]["Prc"] * 100, color="green", legend="Cypern")

# X-Axis
fillins_p.xaxis.major_label_orientation = 0.75
fillins_p.xaxis.axis_label_standoff = 3
fillins_p.xaxis.axis_label = "Column in metadata document"

# Y-axis
fillins_p.yaxis.axis_label = "Procent tomma"

output_file("Fillins_comparison.html")
show(fillins_p)


# # Row fill-ins analysis

# In[11]:

cyp_dict = {}
for index, row in cypern.iterrows():
    cyp_dict[index] = row.isnull().sum()
cypern_s = pd.Series(cyp_dict, index=range(len(cyp_dict)))
cyp_empty_s = pd.Series()
cypern_df = pd.concat([cypern_s,cyp_empty_s],axis=1)
cypern_df.describe()


# In[26]:

cyp_res = {}
cyp_bins = [0, 2, 4, 6, 9] # max is 9 non-empty columns
cyp_group_names = ['Lousy', 'Bad', 'Good', 'Great']
cyp_categories = pd.cut(cypern_s, cyp_bins, labels=cyp_group_names)
for tupl in cyp_categories.value_counts().items():
    #print("{} {} perc: {:.0f}".format(tupl[0], tupl[1], (tupl[1]/sum(cyp_categories.value_counts())*100)))
    cyp_res[tupl[0]] = {"cnt":tupl[1], "prc":(tupl[1]/sum(cyp_categories.value_counts()) *100)}
cyp_df = pd.DataFrame(cyp_res)
cyp_df["Above_bad"] = 0
cyp_df["Above_bad"]["cnt"] = cyp_df["Good"]["cnt"] + cyp_df["Great"]["cnt"]
cyp_df["Above_bad"]["prc"] = cyp_df["Good"]["prc"] + cyp_df["Great"]["prc"]
cyp_df[["Great","Good","Bad","Lousy"]].T.prc.plot()


# In[25]:

cyp_df


# In[16]:

mex_dict = {}
for index, row in mexiko.iterrows():
    mex_dict[index] = row.isnull().sum()
mexiko_s = pd.Series(mex_dict, index=range(len(mex_dict)))
mex_empty_s = pd.Series()
mexiko_df = pd.concat([mexiko_s,mex_empty_s],axis=1)
mexiko_df.describe()


# In[74]:

mex_res = {}
mex_bins = [0, 2, 4, 6, 9] # max is 9 non-empty columns
mex_group_names = ['Lousy', 'Bad', 'Good', 'Great']
mex_categories = pd.cut(mexiko_s, mex_bins, labels=mex_group_names)
for tupl in mex_categories.value_counts().items():
    #print("{} {} perc: {:.0f}".format(tupl[0], tupl[1], (tupl[1]/sum(mex_categories.value_counts())*100)))
    mex_res[tupl[0]] = {"cnt":tupl[1], "prc":(tupl[1]/sum(mex_categories.value_counts()) *100)}
mex_df = pd.DataFrame(mex_res)
mex_df = mex_df.T.stack(0)
mex_df["Above_bad"] = 0
mex_df["Above_bad"]["cnt"] = 0
mex_df["Above_bad"]["prc"] = 0
mex_df["Above_bad"]["cnt"] = "" #mex_df["Good"]["cnt"] + mex_df["Great"]["cnt"]
mex_df["Above_bad"]["prc"] = "" #mex_df["Good"]["prc"] + mex_df["Great"]["prc"]
mex_df


# In[66]:

mex_df["Above_bad"]["cnt"]


# In[58]:

mex_stacked = mex_df.T.stack()
mex_stacked


# In[56]:

mex_stacked["Above_bad"] = ""
mex_stacked


# In[22]:

cyp_tot_values_count = 0

cyp_cols = pd.DataFrame()
for col in cypern.columns:
    print("{} {}".format(col, len(cypern[col].value_counts())))
    for value in cypern[col].value_counts().values:
        cyp_tot_values_count += value
print("\n-------------------------------")    
print("Data shape: {}".format(cypern.shape))
print("Max possible data density (rows * columns): {}".format(cypern.shape[0] * cypern.shape[1]))

print("Actual data density (Total values count +1 for NaN): {} ".format(cyp_tot_values_count + 1))
print("Data density percentage: {}".format((cyp_tot_values_count + 1) / (cypern.shape[0] * cypern.shape[1])))


# In[23]:

mex_tot_values_count = 0

mex_cols = pd.DataFrame()
for col in mexiko.columns:
    print("{} {}".format(col, len(mexiko[col].value_counts())))
    for value in mexiko[col].value_counts().values:
        mex_tot_values_count += value
print("\n-------------------------------")    
print("Data shape: {}".format(cypern.shape))
print("Max possible data density (rows * columns): {}".format(mexiko.shape[0] * mexiko.shape[1]))

print("Actual data density (Total values count +1 for NaN): {} ".format(mex_tot_values_count + 1))
print("Data density percentage: {}".format((mex_tot_values_count + 1) / (mexiko.shape[0] * mexiko.shape[1])))


# In[3]:

from bokeh.plotting import output_notebook, figure, show
output_notebook()
fig = figure(heigth=600,
             width=800,
             y_range=(0,100)
             
            
            )
fig.circle(x=,
           y=["0.6038855281526291","0.6833267287497523"],
           )


# In[75]:

data = {"A":[42,4,8],"Boll":[562,76,34],"Citron":[543,94,2],"D":[34,76,2],"David":[654,34,3]}
d = pd.DataFrame(data)


# In[80]:

d


# In[81]:

d.columns


# In[100]:

d.loc[0:1,"B":"D"]


# In[104]:

mex_df


# In[107]:

mex_df.xs("prc",level=1) # xs, cross-selection


# In[110]:

mex_df.unstack()


# In[118]:

new = pd.concat([mex_df,cyp_df], keys=["mex","cyp"])


# In[ ]:



