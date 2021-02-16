import requests
import json 
from DataClasses import Policy , PaymentDetail , Claim , IntimationDetailRequest
from datetime import datetime
import os
from configparser import ConfigParser



class APIClass:

    config_object = ConfigParser()
    #config_object.read("./actions/config.ini")
    config_object.read("config.ini")
    serverInfo = config_object["SERVERAPICONFIG"]
    
    uid = serverInfo["uid"] 
    pwd = serverInfo["pwd"] 
    ltauid = serverInfo["ltauid"]  
    ltapwd = serverInfo["ltapwd"]
    
    # with open('./actions/occupations.json') as f:
    #     occupationListjson = json.load(f)
        
    with open('occupations.json') as f:
        occupationListjson = json.load(f)
    
    occupationListjson = occupationListjson['Occupation']

    occupationList = []
    for i in range(0,len(occupationListjson)):
        occupationList.append({"label":occupationListjson[i]['Desc'],"value":occupationListjson[i]['Desc']})

    
    # with open('./actions/cities.json') as f:
    #     cityListjson = json.load(f)
        
    with open('cities.json') as f:
        cityListjson = json.load(f)
    
    cityListjson = cityListjson['City']
    
    cityList = []
    for i in range(0,len(cityListjson)):
        cityList.append({"label":cityListjson[i]['Name'],"value":cityListjson[i]['Name']})




#############################################Get Token ################################################################

    def getToken(self):

        url = APIClass.serverInfo["tokenUrl"] #"https://uat-api.tpllife.com/token?"
        tokenFile = "data.txt"

        if os.path.exists(tokenFile):

            with open(tokenFile) as json_file:
                data = json.load(json_file)
            
            expiredate = datetime.strptime(data[".expires"], "%a, %d %b %Y %H:%M:%S GMT")
            expiredate = datetime.strptime(expiredate.strftime("%m-%d-%Y"),"%m-%d-%Y")

            todayDate =datetime.strptime( datetime.today().strftime("%m-%d-%Y"),"%m-%d-%Y")

            if expiredate > todayDate:
                return "Bearer " + data['access_token']

        payload = 'grant_type=password&password='+APIClass.pwd+'&username='+APIClass.uid
        headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data = payload)
        jsonResponse = response.json()
        
        with open(tokenFile, 'w') as outfile:
            json.dump(jsonResponse, outfile)
        
        return "Bearer " + jsonResponse['access_token']

    def getLTAToken(self):

        url = APIClass.serverInfo["ltatokenUrl"] #"https://uat-lifeapi.tpllife.com/token?"
        tokenFile = "ltadata.txt"

        if os.path.exists(tokenFile):

            with open(tokenFile) as json_file:
                data = json.load(json_file)
            
            expiredate = datetime.strptime(data[".expires"], "%a, %d %b %Y %H:%M:%S GMT")
            expiredate = datetime.strptime(expiredate.strftime("%m-%d-%Y"),"%m-%d-%Y")

            todayDate =datetime.strptime( datetime.today().strftime("%m-%d-%Y"),"%m-%d-%Y")

            if expiredate > todayDate:
                return "Bearer " + data['access_token']

        payload = 'grant_type=password&password='+APIClass.ltapwd+'&username='+APIClass.ltauid
        headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data = payload)
        jsonResponse = response.json()
        
        with open(tokenFile, 'w') as outfile:
            json.dump(jsonResponse, outfile)
        
        return "Bearer " + jsonResponse['access_token']

    def sendOTP(self,cnic,phone,token):

        url = APIClass.serverInfo["mobileOTPUrl"] #"https://uat-api.tpllife.com/api/account/MobileRegister"

        payload = 'CNIC='+ cnic + '&PhoneNumber=' + phone
        headers = {
        'Authorization': ''+ token +'',
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data = payload)
        jsonResponse = response.json()
        
        return jsonResponse

    def verifyOTP(self,cnic,phone,otp,token):

        url = APIClass.serverInfo["mobileVerifyUrl"] #"https://uat-api.tpllife.com/api/account/verifyMobileOTP"

        payload = 'CNIC='+ cnic + '&PhoneNumber=' + phone + '&OTPCode=' + otp 
        headers = {
        'Authorization': ''+ token +'',
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data = payload)
        jsonResponse = response.json()
    
        return jsonResponse


        
    ##########################################Get Product Id and Num#######################################################

    def getProductNum_Id(self,code,token):
        url = APIClass.serverInfo["productNumUrl"] #"https://uat-api.tpllife.com/api/Policy/Products"

        payload = "[\r\n    \""+ code +"\",\r\n ]"
        headers = {
        'Authorization': ''+ token +'',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data = payload)

        jsonResponse = response.json()

        ProductId = jsonResponse['Data'][0]['ProductID']
        ProductNum = jsonResponse['Data'][0]['ProductNumber']
        PlanName = jsonResponse['Data'][0]['PlanName']
        return ProductId, ProductNum, PlanName

     #ProductId, ProductNum, PlanName = getProductNum_Id("PS2018KAR-P000020",token)


    ######################################Product/Policy Specific Details API##############################################

    def getProductDetails(self,token,ProductId):

        querystring = {"ProductID":str(ProductId)}
        
        url = APIClass.serverInfo["ltapolicyDetailUrl"]

        headers = {
            'Authorization': ''+ token +'',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
            }

        
        response = requests.request("POST", url, headers=headers, params=querystring)

        jsonResponse = response.json()

        minAge = int(jsonResponse['Data']['PolicyBenefitCoverages'][0]['MinAge'])
        maxAge = int(jsonResponse['Data']['PolicyBenefitCoverages'][0]['MaxAge'])
        minTerm = int(jsonResponse['Data']['PolicyBenefitCoverages'][0]['MinTerm'])
        maxTerm = int(jsonResponse['Data']['PolicyBenefitCoverages'][0]['MaxTerm'])
        maxOverAge = int(jsonResponse['Data']['PolicyBenefitCoverages'][0]['MaxOverAge'])
        maxSumAssured = int(jsonResponse['Data']['PolicyBenefitCoverages'][0]['MaxSumAssured'])
        minSumAssured = int(jsonResponse['Data']['PolicyBenefitCoverages'][0]['MinSumAssured'])

        return str(minAge),str(maxAge),str(minTerm),str(maxTerm),str(maxOverAge),str(maxSumAssured),str(minSumAssured)

    ###################################### LTA Premium Details ###############################################

    def getLTAPremiumDetails(self,token,productId,term,sumInsured,dob,gender,fk_occupationId,ifDeclarationAgree):

        url = APIClass.serverInfo["ltapremiumCalcUrl"]

        payload = "{\"ProductId\": 574, \"Term\": 25, \"SumAssured\": 3500000, \"DateOfBirth\": \"12/12/1990\", \"Gender\": \"Male\", \"FK_Occupation_ID\": 61, \"HeightinFt\": 5, \"HeightinIn\": 11, \"Weight\": 70, \"Declaration\": true, \"PlanCode\": \"P000\", \"BenefitIdList\": [3]}"
        
        premiumDict = json.loads(payload)
        
        headers = {
            'Authorization': ''+ token +'',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
            }

        premiumDict['ProductId'] = productId
        premiumDict['Term'] = term
        premiumDict['SumAssured'] = sumInsured
        premiumDict['Declaration'] = ifDeclarationAgree

        dob = self.changeYearFrom2to4Digit(dob)

        dobObj = datetime.strptime(dob,"%Y/%m/%d")
        dobObj = dobObj.strftime("%d/%m/%Y")

        premiumDict['DateOfBirth'] = dobObj
        premiumDict['Gender'] = gender
        premiumDict['FK_Occupation_ID'] = fk_occupationId

        payload = json.dumps(premiumDict)

        response = requests.request("POST", url, headers=headers, data = payload)

        jsonResponse = response.json()

        return jsonResponse
    
    ######################################### Get Proposal Number  ##############################################

    def getProposalNumber(self,token,ProductId):

        querystring = {"Id":str(ProductId)}
        
        url = APIClass.serverInfo["proposalNumUrl"]

        headers = {
            'Authorization': ''+ token +'',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
            }

        response = requests.request("POST", url, headers=headers, params=querystring)

        jsonResponse = response.json()

        return jsonResponse

    ######################################if Policy LTA exists API##################################################

    def ifLTAPolicyExists(self,token,policyObj):

        url = APIClass.serverInfo["ltapolicyExistsUrl"] #"https://uat-api.tpllife.com/api/Policy/PolicyIssuance"

        headers = {
                    'Authorization': ''+ token +'',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                    }

        payload = json.dumps(policyObj.__dict__)
        
        response = requests.request("POST", url, headers=headers, data = payload)

        jsonResponse = response.json()

        return jsonResponse


    ######################################Validate Member API##################################################

    #insuredName = "Danyal Test"
    #cnic = "42303-3456654-8"
    #dob = "1987/03/08"


    def validateMember(self,token,insuredName,cnic,dob,policyDetailId,planCode):
        url = APIClass.serverInfo["validateMemberUrl"] #"https://uat-api.tpllife.com/api/Policy/ValidateMembers"

        headers = {
            'Authorization': ''+ token +'',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
            }

        payload = "{\r\n    \"PolicyInsuredDetail\": \"[\\r\\n  {\\r\\n    \\\"MemberCode\\\": \\\"000001\\\",\\r\\n    \\\"InsuredName\\\": \\\"Testing Test\\\",\\r\\n    \\\"Gender\\\": \\\"2\\\",\\r\\n    \\\"CNIC\\\": \\\"56235-4515545-4\\\",\\r\\n    \\\"DateOfBirth\\\": \\\"01/12/1991\\\",\\r\\n    \\\"Relations\\\": 1,\\r\\n    \\\"PlanCode\\\": \\\"P0012\\\",\\r\\n    \\\"EffectiveDate\\\": \\\"21/08/2020\\\",\\r\\n    \\\"MaritalStatus\\\": \\\"Single\\\"\\r\\n  }\\r\\n]\",\r\n    \"FK_Policy_ID\": 8,\r\n    \"FK_Product_ID\": 8,\r\n    \"PolicyNumber\": \"PS2019KHI-P000062\",\r\n    \"PolicyTransactionType\": 2,\r\n    \"BusinessType\": 3,\r\n    \"ParentPolicyId\": 8,\r\n    \"Activity\": 1,\r\n    \"EndorsementType\": null,\r\n    \"PolicyMode\": 1,\r\n    \"ContactId\": null,\r\n    \"isASO\": false,\r\n    \"FK_Company_ID\": 1,\r\n    \"CompanyType\": 1\r\n}"

        insuranceDict = json.loads(payload)
        insuranceDict['FK_Policy_ID'] = insuranceDict['FK_Product_ID'] = insuranceDict['ParentPolicyId'] = policyDetailId
       
        insuredDetail = json.loads(insuranceDict['PolicyInsuredDetail'])
        insuredDetail[0]['CNIC'] = cnic
        insuredDetail[0]['InsuredName'] = insuredName
        insuredDetail[0]['PlanCode'] = planCode

        dob = self.changeYearFrom2to4Digit(dob)

        dobObj = datetime.strptime(dob,"%Y/%m/%d")
        dobObj = dobObj.strftime("%d/%m/%Y")

        insuredDetail[0]['DateOfBirth'] = dobObj
        insuranceDict['PolicyInsuredDetail'] = json.dumps(insuredDetail)

        payload = json.dumps(insuranceDict)

        response = requests.request("POST", url, headers=headers, data = payload)

        return response

    #response = validateMember(token,insuredName,cnic,dob)

    #totalPremium = int(response.json()['Data'][0]['GrossPremium']) + int(response.json()['Data'][0]['Charges'])

    ###################################Get Cities API ############################################################

    #userCity = 'Lahore'

    def getCities(self,token):
        url = APIClass.serverInfo["getCityUrl"] #"https://uat-api.tpllife.com/api/Package/GetCity"

        headers = {
                'Authorization': ''+ token +'',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
                }

        payload = {}

        response = requests.request("GET", url, headers=headers, data = payload)

        jsonResponse = response.json()
        return jsonResponse

    #jsonResponse = getCities(token)

    def searchCity(self,name,jsonData):
        for keyval in jsonData['Data']:
            if name.lower().strip() ==  keyval['Name'].lower().strip():
                return keyval['Id']
        return -1

    #cityId = searchCity(userCity,jsonResponse)

    ###################################Policy Issuance API########################################################

    def calculateYears(self,dateFrom,dateTo):
        year,_,_ = str(dateFrom).split('/')
        if (len(year) == 2):
            year_f = int(year[0:2])
            if 30 <= year_f <= 99:
                dateFrom = '19' + dateFrom
            else:
                dateFrom = '20' + dateFrom
        date_from = datetime.strptime(dateFrom, '%Y/%m/%d').date()
        date_to = datetime.strptime(dateTo, '%Y/%m/%d').date()
        return int(((date_to - date_from).days)/365)
    
    def changeYearFrom2to4Digit(self,dateFrom):
        year,_,_ = str(dateFrom).split('/')
        if (len(year) == 2):
            year_f = int(year[0:2])
            if 30 <= year_f <= 99:
                dateFrom = '19' + dateFrom
                return dateFrom
            else:
                dateFrom = '20' + dateFrom
                return dateFrom
        else:
            return dateFrom
        

    # startDate = datetime.today().strftime('%Y/%m/%d')
    # gender = "2"
    # firstName = "Danyal"
    # lastName = "Khaliq"
    # email = "test@email.com"
    # cell = "03334354223"
    # address = "B 766 Block G , Sindh"
    # age = calculateYears(dob,startDate)
    # cdate = "2006/03/08"

    # policyObj = Policy([],[],[],[],firstName,lastName,"",cnic,email,None,
    # cell,address,userCity,"Pakistan","",dob,gender,age,"0",1,cdate,"",None,"",ProductNum,"Shehsawar"
    # ,"P000",None,"20","0","2",None,None,startDate,1,cityId,False,False,0.0,0.0,None,totalPremium,None,None,None,
    # 0,0,0,None,1,1)


    def issuePolicy(self,token,policyObj):
        url = APIClass.serverInfo["policyIssueUrl"] #"https://uat-api.tpllife.com/api/Policy/PolicyIssuance"

        headers = {
                    'Authorization': ''+ token +'',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                    }

        payload = json.dumps(policyObj.__dict__)
        
        response = requests.request("POST", url, headers=headers, data = payload)

        jsonResponse = response.json()

        return jsonResponse

    #jsonResponse = issuePolicy(token,policyObj)

    #policyId = jsonResponse['Data']

    ########################################### Payment Details API ################################################################


    def paymentDetails(self,token,totalPremium,policyId,cnic):
        url = APIClass.serverInfo["paymentDetailUrl"] #"https://uat-api.tpllife.com/api/Policy/PaymentDetails"

        paymentdetailObj = PaymentDetail(totalPremium,policyId,cnic)

        headers = {
                        'Authorization': ''+ token +'',
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                        }

        payload = json.dumps(paymentdetailObj.__dict__)

        response = requests.request("POST", url, headers=headers, data = payload)

        jsonResponse = response.json() 

        return jsonResponse

    #paymentDetails(token,totalPremium,policyId,cnic) 

# apiObj = APIClass()
# token = apiObj.getToken()
# id,num,plan = apiObj.getProductNum_Id("PS2018KAR-P000020",token)
# response = apiObj.validateMember(token,"Danyal Test 1","42101-7654432-9","1987/4/3",id)

###################################################################################################################
################################################CLAIMS APIS########################################################

    def getPolicies(self,token,cnic,phone):
        url = APIClass.serverInfo["getPoliciesUrl"] #"https://uat-api.tpllife.com/api/Policy/GetPolicies"

        headers = {
            'Authorization': ''+ token +'',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
            }

        payload = "{\r\n  \"CNIC\": \"42101-2959141-1\",\r\n  \"PhoneNumber\": \"03363398654\",\r\n  \"AllProducts\": 1\r\n}"

        policyDict = json.loads(payload)
        policyDict['CNIC'] = cnic
        policyDict['PhoneNumber'] = phone
        payload = json.dumps(policyDict)

        response = requests.request("POST", url, headers=headers, data = payload)

        return response
    
    def getIsureds(self,token,cnic,phone,policyId):
        url = APIClass.serverInfo["getInsuredsUrl"] #"https://uat-api.tpllife.com/api/Policy/Insureds"

        headers = {
            'Authorization': ''+ token +'',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
            }

        payload = "{\r\n  \"CNIC\": \"42101-2959141-1\",\r\n  \"MobileNo\": \"03363398654\",\r\n  \"FK_Policy_ID\": 26542\r\n}"

        policyDict = json.loads(payload)
        policyDict['CNIC'] = cnic
        policyDict['MobileNo'] = phone
        policyDict['FK_Policy_ID'] = policyId
        payload = json.dumps(policyDict)

        response = requests.request("POST", url, headers=headers, data = payload)

        return response
    
    def submitClaimIntimation(self,token,claimObj):
        url = APIClass.serverInfo["claimIntimationUrl"] #"https://uat-api.tpllife.com/api/Intimation/SaveIntimationRequestMobile"

        headers = {
                    'Authorization': ''+ token +'',
                    'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
                    'cache-control': "no-cache"
                  }

        payload = json.dumps(claimObj.__dict__)

        
        payload = '------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="model"\r\n\r\n' + payload + '\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--'
        #payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\n{{\"Admit\": \"\",\n    \"Amount\": \"15\",\n    \"CardNo\": \"A-000156-0520-0520-000001\",\n    \"ClaimType\": \"2\",\n    \"ConfinementFrom\": \"\",\n    \"ConfinementTo\": \"\",\n    \"Expense\": \"\",\n    \"FK_InsuredDetail_ID\": \"654617\",\n    \"FK_Policy_ID\": \"265419\",\n    \"FK_PolicyInsuredDetail_ID\": \"654617\",\n    \"HospitalAttended\": \"\",\n    \"Id\": \"0\",\n    \"IllnessDate\": \"15/9/2020\",\n    \"InsuredName\": \"Daniyal Ahmed\",\n    \"IntimationDate\": \"\",\n    \"IntimationDetailRequest\": [  ],\n    \"IntimationMode\": \"create\",\n    \"MedicinesPrescribed\": \"\",\n    \"Note\": \"\",\n    \"PolicyNumber\": \"{policyNo}\",\n    \"PractitionerName\": \"\",\n    \"ReceiptDate\": \"\",\n    \"ReceiptNo\": \"\",\n    \"RecoveryDate\": \"{recoveryDate}\",\n    \"RelationwithInsured\": \"\"}}\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
        headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'authorization': ''+ token +'',
        'cache-control': "no-cache"
        }

         
        response = requests.request("POST", url, headers=headers, data = payload, files=[])

        jsonResponse = response.json()

        return jsonResponse
    
    



apiObj = APIClass()

token = apiObj.getLTAToken()

# _,_,_,_,_,_, temp = apiObj.getProductDetails(token,574)

# temp = apiObj.getLTAPremiumDetails(token,574,"15","600000","1990/4/5","Male",604,"true")
#print(temp['Data']['GrossPremium'])
#token = apiObj.getToken()
# CityId = apiObj.searchCity("Karachi",apiObj.getCities(token))
        
# policyObj = Policy([],[],[],[],"Dan","Kha","","42101-0987765-4","dan@mail.com",None,
#         "0999-8765443","test address","Karachi","Pakistan","",apiObj.changeYearFrom2to4Digit("90/2/2"),"2","25","0",1,"2010/4/4","",None,"","PS2020KHI-P000006","Level Term Assurance",
#         "P000",None,"19","0","10",None,None,"2021-01-21T20:35:38.9544839+05:00",1,1,False,False,0.0,0.0,None,"10000",None,None,None,
#         0,0,0,None,1,1,Term=20,Nationality="Pakistan",FKOccupationID=604,SumInsured=700000,UnderWritingFlag=1,MonthlyIncome=57000,UnderwritingReason="None")

# response = apiObj.ifLTAPolicyExists(token,policyObj)
# print(response)
#token = apiObj.getToken()
#response = apiObj.issuePolicy(token,policyObj)

# print(response)
# policyId = response['Data']
# response = apiObj.paymentDetails(token,"500000",policyId,"42101-0987765-4")
# pass

# response = apiObj.getProposalNumber(token,policyId)
# pass

# print(response)
# response = apiObj.validateMember(token,"Dan2" + ' ' + 'Kha',"42010-3456678-9","1999/05/05","230221","P000")

# print(response)
#cnic = "42101-2959141-1"
#cell = "03363398654"

#apiObj.sendOTP(cnic,cell,token)

# result = apiObj.verifyOTP(cnic,cell,'8589',token)
# print(result)
#result = apiObj.getPolicies(token,cnic,cell)

#jsonData = result.json()
#dictPolicyId = {}
#for keyval in jsonData['Data']:
#    dictPolicyId[keyval['CardNo']] = keyval['PolicyID']

#cardNo = "A-000156-0520-0520-000001"
#result = apiObj.getIsureds(token,cnic,cell,dictPolicyId[cardNo])

#insuredDetailId = result.json()['Data'][0]['InsuredID']

#policyNumber = result.json()['Data'][0]['PolicyNumber']

# fileListObj = [IntimationDetailRequest(1,"","").__dict__ for i in range(1)]
#fileListObj = [ ]

#claimObj = Claim("","2000",cardNo,"2","","","",str(insuredDetailId),str(dictPolicyId[cardNo]),str(insuredDetailId),"","0","15/9/2020","Asim Ali Test"
# ,"",fileListObj,"create","","",policyNumber,"","","","25/9/2020","")

#result = apiObj.submitClaimIntimation(token,claimObj)
#print(result)
