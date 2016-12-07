
# coding: utf-8

# In[1]:

import os, shutil


# In[2]:

testimages = ["0307.a.0002.b.tif","0307.a.0025.tif","0307.f.0004.b.tif","0307.a.0054.tif","0307.a.0056.tif","0307.a.0140.tif","0307.b.0052.tif","0307.a.0055.tif","0307.f.0069.b.tif","0307.f.0079.tif"]


# In[21]:

inpath = "/media/mos/My passport1/Wikimedia/Mexiko/"
#inpath = os.path.abspath(inpath)

outpath = "./testimages/"
try:
    os.mkdir(outpath)
except:
    print("Hooray! Outpath is already there!")


# In[24]:

for image_name in testimages:
    shutil.copy(inpath + image_name, outpath + image_name)


# In[10]:

file = "/media/mos/My Passport1/Wikimedia/Mexiko/0307.a.0002.b.tif"
opened_file = open(file)


# In[ ]:



