#Python MELT Function implementation example 

from collections import OrderedDict
from pandas import DataFrame
import pandas as pd
import numpy as np

from google.colab import files

uploaded = files.upload()

for fn in uploaded.keys():
  print('User uploaded file "{name}" with length {length} bytes'.format(
      name=fn, length=len(uploaded[fn])))

for name, data in uploaded.items():
  with open(name, 'wb') as f:
    f.write(data)
    print ('saved file', name)
    
!ls

dframe = pd.read_excel("Armenia.xlsx", sheet_name=1,skiprows=20)
print(dframe.head())

dfmelt = dframe.melt(id_vars=['Type','Coverage','OdName','AREA','AreaName','REG','RegName','DEV','DevName'],var_name='Year')
print(dfmelt[1:50])
