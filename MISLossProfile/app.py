
import streamlit as st
import pickle
import pandas as pd
import numpy as np
import time 
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
import humanize as hm
from datetime import datetime
import pyodbc
from datetime import timedelta
import base64

toDate = datetime.today()
fromDate = toDate - timedelta(days=364 + datetime.now().timetuple().tm_yday)
toDate = toDate.date()
fromDate = fromDate.date()

# fromDate = '2019-01-01'
# toDate = '2020-02-28'
def buildFilter(dataKVP):
    s = ''
    
    for k,v in dataKVP.items():
        if v != 'All':
            s += k + '==' + f'"{v}"' + ' and '
    
    if ('and' in s):
        return s[:s.rindex('and')]
    else:
        return -1


def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=True)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download as CSV File</a>'
    return href

def MISReport(BusinessType,SalesBranch,Channel,Make,Year,ClaimTypes,High_Claim_Details,Misc_Report,premData,claimData,claimsPaidData):
    
    premData.fillna(0,inplace=True)
       
    
    claimData.fillna(0,inplace=True)
       
    
    if (High_Claim_Details == False) & (Misc_Report == False):
         
        dataKVP = {'BusinessType': BusinessType, 'SalesBranch': SalesBranch, 'Channel': Channel, 'Year':Year, 'Make': Make, 'ClaimTypes':ClaimTypes}
        
        filter_str = buildFilter(dataKVP)
        
        if filter_str != -1:  ##if any filter applied 
            
            if "ClaimTypes" in filter_str: ## if ClaimFilter then dont use with PremData
                if len(filter_str.rsplit('and',1)) > 1: ## if len is 2 means other filters also selected with claimType
                    dfp_grpT = premData.query(filter_str.rsplit('and',1)[0])
                    dfc_grpT = claimData.query(filter_str)
                else:
                    dfp_grpT = premData
                    dfc_grpT = claimData.query(filter_str)
            else:
                dfp_grpT = premData.query(filter_str)
                dfc_grpT = claimData.query(filter_str)
        else:
            dfp_grpT = premData
            dfc_grpT = claimData
            
        DefaultGroupByList = ['Year','Make']
        if Make != 'All':
            print('Selected Makes/Models')
            DefaultGroupByList.extend(['Model'])
            tdf_prem = dfp_grpT.groupby(DefaultGroupByList)['Gross Premium','Policy Count'].agg(['sum']).reset_index()
            tdf_claim = dfc_grpT.groupby(DefaultGroupByList)['TotalClaimed','Claim Count'].agg(['sum']).reset_index()
        else:
            tdf_prem = dfp_grpT.groupby(DefaultGroupByList)['Gross Premium','Policy Count'].agg(['sum']).reset_index()
            tdf_claim = dfc_grpT.groupby(DefaultGroupByList)['TotalClaimed','Claim Count'].agg(['sum']).reset_index()
            
        print(tdf_prem['Gross Premium'].sum())
        print(tdf_claim.TotalClaimed.sum())

        tdf_prem.columns = tdf_prem.columns.get_level_values(0)
        tdf_claim.columns = tdf_claim.columns.get_level_values(0)
        
        if Make != 'All':## Any Make Selected specially then include Model too 
            tdf = tdf_prem.merge(tdf_claim.drop_duplicates(),on=['Year','Make','Model'],how="left")
            tdf = pd.pivot_table(tdf,index=['Make','Model'],values=[ 'Gross Premium','Policy Count','TotalClaimed','Claim Count'])
        else:
            tdf = tdf_prem.merge(tdf_claim.drop_duplicates(),on=['Year','Make'],how="left")
            tdf = pd.pivot_table(tdf,index='Make',values=[ 'Gross Premium','Policy Count','TotalClaimed','Claim Count'],aggfunc=np.sum, margins=True)

        pd.options.display.float_format = '{:,.2f}'.format

        if tdf.shape[0] > 0:
            tdf['Claim Ratio%'] = (tdf['TotalClaimed'].astype(float) / tdf['Gross Premium'].astype(float)) * 100
            tdf['Claim Freq%'] = (tdf['Claim Count'].astype(float) / tdf['Policy Count'].astype(float)) * 100
        else:
            print('No Records Found')
            return None

        tdf.fillna(0,inplace=True)
        tdf.replace(np.inf, 0, inplace=True)
        tdf = tdf.astype(int)
        
        columnOrder = ['Gross Premium','Policy Count','TotalClaimed','Claim Count','Claim Ratio%'
,'Claim Freq%']

        indexOrder = ['Toyota','Honda','Suzuki','Kia','Imported','Others','All']
        if Make == 'All':
            tdf  = tdf.reindex(columnOrder, axis=1).reindex(indexOrder,axis=0)
        else:
            tdf  = tdf.reset_index()
            
       

        #tdf = tdf.style.format('{:,}')
        
        return tdf#.applymap(hm.intword)
    elif High_Claim_Details == True :
        values = st.slider('Select a the range of claimed amount',   200000, 3000000, (500000, 1000000),10000)
        tdf = claimData[(claimData.TotalClaimed >= values[0]) & (claimData.TotalClaimed <= values[1]) ][claimData.columns.difference(['CircumstancesOfLoss'])]
        
        for col in tdf.select_dtypes(float).columns:
            tdf[col] = tdf[col].astype('int')
            
        return tdf #.applymap(hm.intword)
    else : 
        tdf = claimsPaidData[['ClaimStage','PaymentHead','PaidAmount']]
        
        #tdf['RecieptDate'] =  pd.to_datetime(tdf['RecieptDate'],errors='coerce', format='%Y-%m-%d %H:%M:%S')
        tdf = tdf[tdf.ClaimStage != 'ClaimClose'].groupby(['PaymentHead'])['PaidAmount'].agg(['sum','count']).reset_index()
        print(tdf.columns)
        tdf.columns = ['PaymentHead', 'Claim Sum','No of Claims']
        tdf = pd.pivot_table(tdf,index='PaymentHead',values=[ 'No of Claims','Claim Sum' ])
        #tdf = tdf.pivot(index='PaymentHead',columns='RecieptDate',values=[ 'No of Claims','Claim Sum'])
        #tdf = tdf.stack(level=1)
        tdf = tdf.astype(int)
        #tdf = tdf.applymap(hm.intword)
        
        
        return tdf.reset_index()

def readClaimsData():
    # Stored Procedure Create Statement
    with open('./SPs/CLA_MotorIntimateReport_Current_DS_SP.sql', 'r') as file:
        sqlCreateSP = file.read()
    
    # Stored Procedure Drop Statement
    sqlDropSP="IF EXISTS (SELECT * FROM sys.objects \
           WHERE type='P' AND name='CLA_MotorIntimateReport_Current_DS_SP') \
           DROP PROCEDURE CLA_MotorIntimateReport_Current_DS_SP"


    start_time = datetime.now() 
    print(start_time)
    start_date_2015 = [fromDate]
    end_date_2015 = [toDate]

    conn = pyodbc.connect("DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={0}; database={1};UID={2};PWD={3}".format('172.16.2.86\SQL14','TDIIMSDAILY','bigdata','BIG!@#data'))
    
    cursor=conn.cursor()
    # Drop SP if exists
    cursor.execute(sqlDropSP)

    # Create SP using Create statement
    cursor.execute(sqlCreateSP)

    tempDf1 = pd.DataFrame()
    for f , b in zip(start_date_2015, end_date_2015):
        #st.info('ClaimsData From:' + str(f) + ' to ' + str(toDate))
        print('ClaimsData From:' + str(f) + ' to ' + str(toDate))
        storedProc = "EXEC [CLA_MotorIntimateReport_Current_DS_SP] @Company_Id=4, @ClaimStartDateFrom='"+str(f)+"', @EndTime='"+str(b)+"' "
        dfCurrent = pd.read_sql_query(storedProc, conn)
        dfCurrent = pd.concat([dfCurrent,tempDf1])
        tempDf1 = dfCurrent

    st.info('Time elapsed (hh:mm:ss.ms) {}'.format(datetime.now() - start_time))

    df_claims = tempDf1
    df_claims['EffectiveDate'] =  pd.to_datetime(df_claims['EffectiveDate'],errors='coerce', format='%Y-%m-%d %H:%M:%S')
    df_claims['IncidentDate'] =  pd.to_datetime(df_claims['IncidentDate'],errors='coerce', format='%Y-%m-%d %H:%M:%S')
    df_claims['IncidentYear'] = df_claims['IncidentDate'].dt.year
    df_claims['IntimationDate'] =  pd.to_datetime(df_claims['IntimationDate'],errors='coerce', format='%Y-%m-%d %H:%M:%S')
    df_claims['IntimationYear'] = df_claims['IntimationDate'].dt.year
    
    df_claims['VehicleMake'] = np.where(df_claims.VehicleMake.isin(['Suzuki','Toyota','Honda','Kia']) == False, 'Others', df_claims['VehicleMake'])
        
    df_claims.VehicleType =  np.where((df_claims.VehicleMake == 'Others') & (df_claims['VehicleModel'].str.lower().str.contains("moov|mira|dazey|n-wagon") == True), 'Imported', df_claims.VehicleType)
    df_claims.VehicleType =  np.where((df_claims.VehicleMake == 'Others') & (df_claims['VehicleModel'].str.lower().str.contains("power|rickshaw") == True), 'Others', df_claims.VehicleType)
    df_claims['VehicleMake'] = np.where((df_claims.VehicleType.isna() == True), 'Others', df_claims.VehicleMake)
    df_claims.VehicleType =  np.where((df_claims.VehicleType.isna() == True), 'Others', df_claims.VehicleType)

    df_claims['VehicleMake'] = np.where(df_claims.VehicleType == 'Imported', 'Imported', df_claims.VehicleMake)
    
    
    df_claims.Amount_Reserve.fillna(0,inplace=True)
    df_claims.PaidTo.fillna(0,inplace=True)
    df_claims.EstSalvage.fillna(0,inplace=True)
    df_claims.SalvageRecovery.fillna(0,inplace=True)
    df_claims.PaymentAmount.fillna(0,inplace=True)
    df_claims.CI_Amount.fillna(0,inplace=True)
    df_claims.CI_Percent.fillna(0,inplace=True)

    df_claims.CI_Amount = (df_claims.Amount_Reserve + df_claims.PaidTo) * (df_claims.CI_Percent/100)

    claimCols = [
             'IntimationYear',
             'PaidTo',
             'SalvageRecovery',
             'VehicleMake',
             'VehicleModel',
             'ClaimTypes',
             'BusinessType',
             'BranchName',
             'LeadSource',
             'VehicleType',
             'CI_Amount',
             'Amount_Reserve',   
             'ClaimNo',
             'EstSalvage'
         
            ]

    groupbyCols = [
                 'IntimationYear',
                 'VehicleMake',
                 'VehicleModel',
                 'ClaimTypes',
                 'BusinessType',
                 'BranchName',
                 'LeadSource',
                 'VehicleType',
                 'PaidTo',
                 'SalvageRecovery',
                 'CI_Amount',
                 'Amount_Reserve', 
                 'ClaimNo',
                 'EstSalvage'
               
              ]

    df_claims['VehicleType'] = np.where(df_claims.VehicleType == 0, 'Others', df_claims.VehicleType)
    
    dfc_grp = df_claims[claimCols]

    dfc_grp = dfc_grp.groupby(groupbyCols)['PaidTo'].agg(['sum','count']).reset_index()
    dfc_grp['sum'] = (dfc_grp.Amount_Reserve + dfc_grp.PaidTo) - (dfc_grp.SalvageRecovery + dfc_grp.EstSalvage) -  dfc_grp.CI_Amount
    dfc_grp.rename(columns={'BusinessType':'VoucherType','BranchName':'SalesBranch'}, inplace=True)
    dfc_grp['ClaimTypes'] = np.where(dfc_grp.ClaimTypes.str.strip() == 'Snatch', 'Theft', dfc_grp.ClaimTypes)
    dfc_grp['ClaimTypes'] = dfc_grp['ClaimTypes'].str.strip()
    
    dfc_grp['VehicleModel'] = dfc_grp.VehicleModel.str.strip()

    dfc_grp.rename(columns={'IntimationYear':'Year', 'VehicleMake':'Make','VehicleModel':'Model', 'VehicleType': 'VehicleCategory','VoucherType':'BusinessType','LeadSource':'Channel','sum':'TotalClaimed','count':'Claim Count'}, inplace=True)

    return dfc_grp


def readPremiumData():
    # Stored Procedure Create Statement
    with open('./SPs/SLS_GetVehicleWisePremiumRegister_DS_SP.sql', 'r') as file:
        sqlCreateSP = file.read()
    
    # Stored Procedure Drop Statement
    sqlDropSP="IF EXISTS (SELECT * FROM sys.objects \
           WHERE type='P' AND name='SLS_GetVehicleWisePremiumRegister_DS_SP') \
           DROP PROCEDURE SLS_GetVehicleWisePremiumRegister_DS_SP"

    
    start_time = datetime.now() 
    print(start_time)

    start_date = [fromDate]
    end_date = [toDate]

    conn = pyodbc.connect("DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={0}; database={1};UID={2};PWD={3}".format('172.16.2.86\SQL14','TDIIMSDAILY','bigdata','BIG!@#data'))
    
    cursor=conn.cursor()
    # Drop SP if exists
    cursor.execute(sqlDropSP)

    # Create SP using Create statement
    cursor.execute(sqlCreateSP)

    tempDf2 = pd.DataFrame()
    for f, b in zip(start_date, end_date):
        #st.info('PremiumData From :' + str(f) + " to " + str(b))
        print('PremiumData From :' + str(f) + " to " + str(b))
        storedProc = "EXEC [SLS_GetVehicleWisePremiumRegister_DS_SP] @Company_Id1=4, @StartDate1='"+str(f)+"', @EndDate1='"+str(b)+"' , @Account_Type1=NULL "
        dfCurrent = pd.read_sql_query(storedProc, conn)
        dfCurrent = pd.concat([dfCurrent,tempDf2])
        tempDf2 = dfCurrent
    
    st.info('Time elapsed (hh:mm:ss.ms) {}'.format(datetime.now() - start_time))

    tempDf2.rename(columns={'branch': 'SalesBranch','PolicyNo':'SalesFormNo'}, inplace=True)
    df_prem = tempDf2.copy()
    df_prem.VoucherType = np.where( (df_prem.VoucherType.str.contains("NB") == True), "Fresh","Renewal")

    df_prem['BillDate'] =  pd.to_datetime(df_prem['BillDate'],errors='coerce', format='%Y-%m-%d %H:%M:%S')

    df_prem['Year'] = df_prem['BillDate'].dt.year

    df_prem['ExpiryDate'] =  pd.to_datetime(df_prem['ExpiryDate'],errors='coerce', format='%Y-%m-%d %H:%M:%S')

    df_prem['EffectiveDate'] =  pd.to_datetime(df_prem['EffectiveDate'],errors='coerce', format='%Y-%m-%d %H:%M:%S')

    df_prem['InsuredAmount'] = pd.to_numeric(df_prem['InsuredAmount'],errors='coerce')
    df_prem['Adv_Tax'] = pd.to_numeric(df_prem['Adv_Tax'],errors='coerce')

    df_prem.VehicleType = df_prem.VehicleType.fillna('None')

    df_prem.drop((df_prem[df_prem['EffectiveDate'].isnull()].index) | (df_prem[df_prem['ExpiryDate'].isnull()].index), inplace = True)

    df_prem.dropna(subset=['VehicleMake'],inplace=True)

    #     df_prem['test'] = df_prem.VehicleMake.map(lambda x: to_make_model(x))

    #     new = pd.DataFrame(df_prem['test'].tolist(), index=df_prem.index)
    #     new.columns = ['Make','Model','CarYear']

    #     df_prem = pd.concat([df_prem, new], axis= 1)
    #     df_prem.drop('test', axis=1, inplace=True)
    df_prem['Make'] = np.where(df_prem.Make.isin(['Suzuki','Toyota','Honda','Kia']) == False, 'Others', df_prem['Make'])
    
    df_prem.VehicleCategory =  np.where((df_prem.Make == 'Others') & (df_prem['Model'].str.lower().str.contains("moov|mira|dazey|n-wagon") == True), 'Imported', df_prem.VehicleCategory)
    df_prem.VehicleCategory =  np.where((df_prem.Make == 'Others') & (df_prem['Model'].str.lower().str.contains("power|rickshaw") == True), 'Others', df_prem.VehicleCategory)
    df_prem['Make'] = np.where((df_prem.VehicleCategory.isna() == True), 'Others', df_prem.Make)
    df_prem.VehicleCategory =  np.where((df_prem.VehicleCategory.isna() == True), 'Others', df_prem.VehicleCategory)

    df_prem['Make'] = np.where(df_prem.VehicleCategory == 'Imported', 'Imported', df_prem.Make)
    #print(df_prem[df_prem.VehicleCategory.isna()].Model.value_counts())

    df_prem['Policy Count'] = df_prem.groupby(['Make',
                                               'Model',
                                               'Year',
                                               'VoucherType',
                                               'SalesBranch',
                                               'VehicleCategory',
                                               'LeadSource'])['SalesFormNo'].transform('nunique')
    

    premCols = [
         'SalesFormNo',
         'Year',
         'Product',
         'Make',
         'Model',
         'VoucherType',
         'SalesBranch',
         'Account_Name',
         'Account_Number',
         'LeadSource',
         'VehicleCategory',
         'VehicleGrossAmount',
         'Policy Count',
            
    ]

    groupbyCols = [
               'Year',
               'Make',
               'Model',
               'VoucherType',
               'SalesBranch',
               'LeadSource',
               'VehicleCategory',
               'Policy Count',
                
                ]
    dfp_grp = df_prem#[premCols]
    dfp_grp = dfp_grp.groupby(groupbyCols)['VehicleGrossAmount'].agg(['sum']).reset_index()
    dfp_grp.columns = dfp_grp.columns.get_level_values(0)
    
    dfp_grp['Model'] = dfp_grp.Model.str.strip()

    dfp_grp.rename(columns={'branch': 'SalesBranch','VoucherType':'BusinessType','LeadSource':'Channel','sum':'Gross Premium','count':'Policy Count'}, inplace=True)

    return dfp_grp

def readClaimsPaidVendors():
    start_date = ['2020-01-01']
    end_date = [toDate]

    conn = pyodbc.connect("DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={0}; database={1};UID={2};PWD={3}".format('172.16.2.86\SQL14','TDIIMSDAILY','bigdata','BIG!@#data'))
    dfCurrent1 = pd.DataFrame()
    tempDf1 = pd.DataFrame()

    for f, b in zip(start_date, end_date):
        #st.info('ClaimsVendorData From :' + str(f) + " to " + str(b))
        print('ClaimsVendorData From :' + str(f) + " to " + str(b))
        storedProc = "EXEC [CLA_MotorPaidReport_SP_New] @Company_Id=4, @ClaimStartDateFrom='"+str(f)+"', @ClaimStartDateTo='"+str(b)+"'"
        dfCurrent1 = pd.read_sql_query(storedProc, conn)
        dfCurrent1 = pd.concat([dfCurrent1,tempDf1])
        tempDf1 = dfCurrent1
        st.info('Done reading Claims Paid to Vendors')
    return tempDf1

def float_apply(x):
    try:
        obj = float(x)
        return True
    except ValueError:
        return False
    
def to_make_model(s):
    make  = str(s.split(" ",1)[0])
    model = s[len(make):-4]
    year  = s[-4:]
    return make, model, year

import os 
ClaimDatafilePath = './pickle/claimData.pickle'
premDatafilePath = './pickle/premiumData.pickle'
claimsPaidfilePath = './pickle/claimsPaidVendorData.pickle'

if st.sidebar.button('Re-Fetch Data'):
    st.warning('This will take time .. please be patient !')
    # Handle errors while calling os.remove()
    try:        
        os.remove(claimsPaidfilePath)
        st.info('Claims Vendor Cache Cleard !')
    except:
        st.error("Error while deleting file " + claimsPaidfilePath)
    
    try:        
        os.remove(premDatafilePath)
        st.info('Premium Cache Cleard !')
    except:
        st.error("Error while deleting file " + premDatafilePath)
    
    try:        
        os.remove(ClaimDatafilePath)
        st.info('Claims Cache Cleard !')
    except:
        st.error("Error while deleting file " + ClaimDatafilePath)
    

######################Claim Data#######################
if os.path.exists(ClaimDatafilePath):
    with open(ClaimDatafilePath,'rb') as f:
        dfc_grp = pickle.load(f)
else:
    dfc_grp = readClaimsData()
    with open(ClaimDatafilePath, 'wb') as f:
        st.info('ClaimsFile Written')
        pickle.dump(dfc_grp, f)

######################Premium Data#######################
if os.path.exists(premDatafilePath):
    with open(premDatafilePath,'rb') as f:
        dfp_grp = pickle.load(f)
else:
    dfp_grp = readPremiumData()
    with open(premDatafilePath, 'wb') as f:
        st.info('PremiumFile Written')
        pickle.dump(dfp_grp, f)

##################Claim Paid Vendor Data##################
if os.path.exists(claimsPaidfilePath):
    with open(claimsPaidfilePath,'rb') as f:
        dfClaimsPaid = pickle.load(f)
else:
    dfClaimsPaid = readClaimsPaidVendors()
    with open(claimsPaidfilePath, 'wb') as f:
        st.info('ClaimsVendorFile Written')
        pickle.dump(dfClaimsPaid, f)



#######################VehicleCategory#############################
vehicleMakeList = dfp_grp.Make.str.strip().unique().tolist()
vehicleMakeList.insert(0, 'All')

optionsVMT = st.sidebar.selectbox('Select Make/Type',vehicleMakeList)

#######################BussinesType###############################
businessTypeList = dfp_grp.BusinessType.unique().tolist()
businessTypeList.insert(0, 'All')

optionsBT = st.sidebar.selectbox('Select Business',businessTypeList)

#######################SalesBranch##################################
branchList = dfp_grp.SalesBranch.unique().tolist()
branchList.insert(0, 'All')

optionsBR = st.sidebar.selectbox('Select Branches',branchList)

#######################ClaimType##################################
claimTypeList = dfc_grp.ClaimTypes.str.strip().unique().tolist()
claimTypeList.insert(0, 'All')

optionsCT = st.sidebar.selectbox('Select ClaimTypes',claimTypeList)

#######################ChannelType##################################
channelList = dfp_grp.Channel.str.strip().unique().tolist()
channelList.insert(0, 'All')

optionsCHT = st.sidebar.selectbox('Select ChannelTypes',channelList)

#######################YearList##################################
yearList = dfp_grp.Year.unique().tolist()
yearList.insert(2, 'All')

optionsYearList = st.sidebar.selectbox('Select Year',yearList)


High_Claim_Details = st.sidebar.checkbox('High_Claim_Details')
Misc_Report = st.sidebar.checkbox('Misc_Report')

if (High_Claim_Details == False) & (Misc_Report == False):
    st.markdown('### MIS Loss Profile Interactive Report for year : ' + str(optionsYearList) )
elif High_Claim_Details == True:
    st.markdown('### All High Claims Records : ')
else:
    st.markdown('### Vendor Paid Details : ')
    

with st.spinner('Processing...'):
    data = MISReport(BusinessType=optionsBT,SalesBranch=optionsBR,ClaimTypes=optionsCT
    ,Channel=optionsCHT,Make=optionsVMT,Year=optionsYearList, High_Claim_Details=High_Claim_Details
    ,Misc_Report=Misc_Report,premData=dfp_grp,claimData=dfc_grp,claimsPaidData=dfClaimsPaid)

st.markdown(get_table_download_link(data), unsafe_allow_html=True)

data = data.style.format('{:,}',data.select_dtypes(int).columns)
data

