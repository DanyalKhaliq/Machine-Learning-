from flask import Flask, jsonify, request
import requests
import tempfile
import os
import camelot
import pandas as pd
from datetime import datetime 
from pathlib import Path


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

@app.route('/upload', methods=['POST'])
def upload():
    file_ = request.files['file']
    handle, filename = tempfile.mkstemp()
    print(filename)
    os.close(handle)
    file_.save(filename + '.pdf')
    data = getParseData(filename + '.pdf')
    return data

@app.route('/download', methods=['GET'])
def download():
    filename = Path('Proscribed-OrganizationsEng.pdf')
    url = 'https://nacta.gov.pk/wp-content/uploads/2017/08/Proscribed-OrganizationsEng.pdf'
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Wrong , try again later",err)
        return "OOps: Something Wrong , try again later : \n " + str(err)
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
        return "Http Error : \n " + str(errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
        return "Error Connecting : \n " + str(errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
        return "Timeout Error : \n " + str(errt)
    filename.write_bytes(response.content)
    data = getParseData(filename.name)
    return data


def getParseData(filepath):
    #reding upper bigger table
    tables = camelot.read_pdf(filepath,flavor='lattice', table_areas=['27.890597738287564,779.3928781547891,586.183424878837,54.463041167308354'],line_size_scaling=5,split_text='true',flag_size='false')
    
    tdf = tables[0].df
    
    #get header row
    new_header = tdf.iloc[0] 

    last_rows = tdf.tail(1)

    tdf = tdf[1:] 

    tdf.columns = new_header 
    tdf.drop(columns=['S#'],inplace=True)
    
    #get 3rd & 4th cols
    tdf2 = tdf.iloc[:,[2,3]]
    #get 1st & 2nd cols
    tdf = tdf.iloc[:,[0,1]]
   
    #merge 2 dfs horizontally
    tdf_merged = pd.concat([tdf,tdf2])
    #sroping empty rows by Name
    tdf_merged = tdf_merged[tdf_merged['Name of Organization'] != '']
    
    #replace unwanted HTML tags 
    tdf_merged['Name of Organization'] = tdf_merged['Name of Organization'].str.replace('<[^<]+?>', '')
    tdf_merged['Date of Notification'] = tdf_merged['Date of Notification'].str.replace('<[^<]+?>', '')

    dumping_date = datetime.today().strftime('%Y-%m-%d')
    
    #reading bottom smaller tables
    tables_d = camelot.read_pdf(filepath,flavor='stream', table_areas=['27.315145853073922,113.61750306703894,586.731731794465,55.07305706466556'],line_size_scaling=0,split_text='true',flag_size='false')

    tdf_d = tables_d[0].df
    #filtering rows containing table Heading 
    tdf_d = tdf_d[tdf_d.iloc[:,[0]][0].str.contains('enlisted ') == False]
    
    tdf_d2 = tdf_d.iloc[:,[2,3]]

    tdf_d = tdf_d.iloc[:,[0,1]]

    tdf_d.columns = tdf.columns
    tdf_d2.columns = tdf.columns

    tdf_merged2 = pd.concat([tdf_d,tdf_d2])


    tdf_merged2 = tdf_merged2[tdf_merged2['Name of Organization'] != '']
    tdf_merged2['Name of Organization'] = tdf_merged2['Name of Organization'].str.replace('<[^<]+?>', '')
    tdf_merged2['Date of Notification'] = tdf_merged2['Date of Notification'].str.replace('<[^<]+?>', '')
    #filtering Integer data from Name column
    tdf_merged2['Name of Organization'] = tdf_merged2['Name of Organization'].str.replace('\d+', '') 


    tdf_merged = pd.concat([tdf_merged,tdf_merged2])
    #Spelling correction
    tdf_merged['Name of Organization'] = tdf_merged['Name of Organization'].str.replace('ffiliated', 'Affiliated') 
    
    tdf_merged['data_source_name'] = 'nacta-entities'
    tdf_merged['data_source_link'] = 'https://nacta.gov.pk/proscribed-organizations/'
    tdf_merged['dumping_date'] = dumping_date
    #rename cols as per json to return 
    tdf_merged.rename(columns={'Name of Organization':'name','Date of Notification':'notification_date'}, inplace=True)
    
    tdf_merged['notification_date'] = pd.to_datetime(tdf_merged['notification_date']).dt.strftime('%Y-%m-%d')
    

    #removing Roman numbering from Affiliated organization data
    remove_words = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x','Organizations','organizations']
    pat = r'\b(?:{})\b'.format('|'.join(remove_words))

    new = tdf_merged["name"].str.split("Affiliated", n = 1, expand = True) 

    # making separate first name column from new data frame 
    tdf_merged["name"]= new[0].str.strip()
    tdf_merged["affiliated_entities"]= new[1].str.strip()
    tdf_merged['affiliated_entities'] = tdf_merged['affiliated_entities'].str.replace(',', ' ||').str.replace('\n', '', 1).str.replace(pat, '').str.replace('[:.]', '').str.strip()
    tdf_merged["affiliated_entities"]=  tdf_merged["affiliated_entities"].str.split("\n",expand = False) 
    
    tdf_merged = tdf_merged.reset_index(drop=True)

    dd = pd.DataFrame(tdf_merged[tdf_merged['affiliated_entities'].isna() == False]['affiliated_entities'].apply(lambda itemlist : [item for item in itemlist if item.isspace() == False]))
    tdf_merged = tdf_merged.join(dd, lsuffix='_caller', rsuffix='_other')
    tdf_merged.rename(columns = {'affiliated_entities_other':'affiliated_entities'}, inplace = True)
    tdf_merged.drop(['affiliated_entities_caller'], axis = 1,inplace=True)

    tdf_merged.to_csv('pdfToTable.csv',index=False)

    return tdf_merged.to_json(orient='records')

        

# if __name__ == '__main__':
#     app.run(host='0.0.0.0' ,port=8086,debug=True)