import requests
import json 
from DataClasses import Policy , PaymentDetail , Claim , IntimationDetailRequest
from datetime import datetime
import os

class APIClass:
    
    uid = "" 
    pwd = ""

#############################################Get Token ################################################################

    def getToken(self):

        url = ""
        tokenFile = "data.txt"

        if os.path.exists(tokenFile):

            with open(tokenFile) as json_file:
                data = json.load(json_file)
            
            expiredate = datetime.strptime(data[".expires"], "%a, %d %b %Y %H:%M:%S GMT")
            expiredate = datetime.strptime(expiredate.strftime("%m-%d-%Y"),"%m-%d-%Y")

            todayDate =datetime.strptime( datetime.today().strftime("%m-%d-%Y"),"%m-%d-%Y")

            if expiredate > todayDate:
                return "Bearer " + data['access_token']

        payload = 'grant_type=password&password=&username='
        headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data = payload)
        jsonResponse = response.json()
        
        with open(tokenFile, 'w') as outfile:
            json.dump(jsonResponse, outfile)
        
        return "Bearer " + jsonResponse['access_token']


        #return "Bearer " + "O3FCPraKmwWwtWU8rZd8G9nH87M3Zr8pcbckmfjxhSoA_UKzpc0cksrUywiHvRjja9kAO-eLqczFjAeNjR6ShHwiKiV9Y_l9xZU4CGv3Htj4tYbhOiUYD57fJsAgZzvdn9naagKCVl4Pz16aR_5kOtpGL03oyh0xKy0MYSN8bmXJYB_yzUNMUe5kUeN5V7ZpczYn2aoSeIDhaO1ATVZJfjo-9nHV2h04bUeQ4G2-lwR8Y3qnzdczZO1DZd4aawRUHnROYRfXQTsXTIyPS3Y9TW_ojcDUZaMlXMS6NA1JDH80mfqgKyS-Yypuu4JYtXflKYJSMnIRkJh4CPpou2nZ7yzuX3-av5PWZxtVB6eI9mYFJjbEG18iRXfWjdhbs9xyFC8kHn2DIVZCPwldWb6aPnJIVbuFsst2m19OW6G0dJi9oONjKPz8j2hKWqEENxpUZdqCoZVvNfbN1JSbwrHeTjmHpR58ei1U4vwLVX8K96YkYx6jkxahl4dhFx-lZWebT20JTWJNTaFJ-1RYtzvThf3hENiacfDx05H41Dy54dskcUgKBqVRhB6ul_0bYkVXIfnn3AZc91nw4CV8dsnr4GaJdsNjfKD9T-DCHDW8oFM"
        
    #token = getToken()

    ##########################################Get Product Id and Num#######################################################

    def getProductNum_Id(self,code,token):
        url = "https://uat-api.tpllife.com/api/Policy/Products"

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


    ######################################Product Specific Details API##############################################

    def getProductDetails(self,token,ProductId):
        url = "https://uat-api.tpllife.com/api/Policy/ProductDetails?ProductID=" +  str(ProductId)

        headers = {
            'Authorization': ''+ token +'',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
            }

        payload = {}

        response = requests.request("GET", url, headers=headers, data = payload)

        jsonResponse = response.json()

        minAge = int(jsonResponse['Data']['PolicyRatingSheet'][0]['Min'])
        maxAge = int(jsonResponse['Data']['PolicyRatingSheet'][0]['Max'])

        return minAge,maxAge

    #minAge,maxAge = getProductDetails(token,ProductId)

    ######################################Validate Member API##################################################

    #insuredName = "Danyal Test"
    #cnic = "42303-3456654-8"
    #dob = "1987/03/08"


    def validateMember(self,token,insuredName,cnic,dob,policyDetailId):
        url = "https://uat-api.tpllife.com/api/Policy/ValidateMembers"

        headers = {
            'Authorization': ''+ token +'',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
            }

        payload = "{\r\n    \"PolicyInsuredDetail\": \"[\\r\\n  {\\r\\n    \\\"MemberCode\\\": \\\"000001\\\",\\r\\n    \\\"InsuredName\\\": \\\"Testing Test\\\",\\r\\n    \\\"Gender\\\": \\\"2\\\",\\r\\n    \\\"CNIC\\\": \\\"56235-4515545-4\\\",\\r\\n    \\\"DateOfBirth\\\": \\\"01/12/1991\\\",\\r\\n    \\\"Relations\\\": 1,\\r\\n    \\\"PlanCode\\\": \\\"P0012\\\",\\r\\n    \\\"EffectiveDate\\\": \\\"21/08/2020\\\",\\r\\n    \\\"MaritalStatus\\\": \\\"Single\\\"\\r\\n  }\\r\\n]\",\r\n    \"FK_Policy_ID\": 8,\r\n    \"FK_Product_ID\": 8,\r\n    \"PolicyNumber\": \"PS2017KAR-P000008\",\r\n    \"PolicyTransactionType\": 2,\r\n    \"BusinessType\": 3,\r\n    \"ParentPolicyId\": 8,\r\n    \"Activity\": 1,\r\n    \"EndorsementType\": null,\r\n    \"PolicyMode\": 1,\r\n    \"ContactId\": null,\r\n    \"isASO\": false,\r\n    \"FK_Company_ID\": 1,\r\n    \"CompanyType\": 1\r\n}"

        insuranceDict = json.loads(payload)
        insuranceDict['FK_Policy_ID'] = insuranceDict['FK_Product_ID'] = insuranceDict['ParentPolicyId'] = policyDetailId
       
        insuredDetail = json.loads(insuranceDict['PolicyInsuredDetail'])
        insuredDetail[0]['CNIC'] = cnic
        insuredDetail[0]['InsuredName'] = insuredName

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
        url = "https://uat-api.tpllife.com/api/Package/GetCity"

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
        date_from = datetime.strptime(dateFrom, '%Y/%m/%d').date()
        date_to = datetime.strptime(dateTo, '%Y/%m/%d').date()
        return int(((date_to - date_from).days)/365)

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
        url = "https://uat-api.tpllife.com/api/Policy/PolicyIssuance"

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
        url = "https://uat-api.tpllife.com/api/Policy/PaymentDetails"

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
        url = "https://uat-api.tpllife.com/api/Policy/GetPolicies"

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
        url = "https://uat-api.tpllife.com/api/Policy/Insureds"

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
        url = "https://uat-api.tpllife.com/api/Intimation/SaveIntimationRequestMobile"

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
    
    



# apiObj = APIClass()
# token = apiObj.getToken()
# cnic = "42101-2959141-1"
# cell = "03363398654"

# result = apiObj.getPolicies(token,cnic,cell)

# jsonData = result.json()
# dictPolicyId = {}
# for keyval in jsonData['Data']:
#     dictPolicyId[keyval['CardNo']] = keyval['PolicyID']

# cardNo = "A-000156-0520-0520-000001"
# result = apiObj.getIsureds(token,cnic,cell,dictPolicyId[cardNo])

# insuredDetailId = result.json()['Data'][0]['InsuredID']

# policyNumber = result.json()['Data'][0]['PolicyNumber']

# fileListObj = [IntimationDetailRequest(1,"","").__dict__ for i in range(1)]
# fileListObj = [ ]

# claimObj = Claim("","2000",cardNo,"2","","","",str(insuredDetailId),str(dictPolicyId[cardNo]),str(insuredDetailId),"","0","15/9/2020","Asim Ali Test"
# ,"",fileListObj,"create","","",policyNumber,"","","","25/9/2020","")

# apiObj.submitClaimIntimation(token,claimObj)
