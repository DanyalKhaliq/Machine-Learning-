# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#

from typing import Dict, Text, Any, List, Union, Optional
from rasa_sdk.events import SlotSet, FollowupAction , AllSlotsReset
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction , REQUESTED_SLOT
import datetime
from datetime import datetime
import re
from APIClass import APIClass
from DataClasses import Policy , PaymentDetail , Claim
from helper import Helper
import base64
from rasa_sdk.events import (
    SlotSet,
    EventType,
    ActionExecuted,
    SessionStarted,
    Restarted,
    FollowupAction,
)


def custom_request_next_slot(
    form,
    dispatcher: "CollectingDispatcher",
    tracker: "Tracker",
    domain: Dict[Text, Any],
) -> Optional[List[EventType]]:
    """Request the next slot and utter template if needed,
        else return None"""

    for slot in form.required_slots(tracker):
        if form._should_request_slot(tracker, slot):
            
            dispatcher.utter_message(
                template=f"utter_ask_{form.name()}_{slot}", **tracker.slots
            )
            return [SlotSet(REQUESTED_SLOT, slot)]

    return None


customData = {}

policyDict = {
        "Mosquito":"PS2018KAR-P000016",
        "Hybrid":"PS2018KAR-P000021",
        "Water":"PS2018KAR-P000019",
        "Shehsawar":"PS2018KAR-P000020",
        "Bodyguard":"PS2018KAR-P000018",
        "HCA5K":"PS2018KAR-P000017",
        "HCA10K":"PS2018KAR-P000015",
        "Sahulat":"PS2019KHI-P000062",
        "Level Term Assurance":"PS2020KHI-P000006"
    }

digitalplanCodeDict = {
        "Mosquito":"P0012",
        "Hybrid":"P0014",
        "Water":"P0013",
        "HCA5K":"P000",
        "Shehsawar":"P000",
        "Bodyguard":"P000",
        "Sahulat":"P000",
        "Level Term Assurance":"P000"
        
    }
     
class PolicyDataForm(FormAction):   
    
    def name(self):
        return "policy_data_form"
    
            
    @staticmethod
    def required_slots(tracker):
        ## if Digital policy 
        if str(tracker.get_slot('policyname')) in ['Water','Hybrid','Mosquito']:
            return ["cnic","cdate","dob","city"]
        ## if HCA 
        elif str(tracker.get_slot('policyname')) in ['HCA5K']:
            return ["HCArange","cnic","cdate","dob","city"]
        ## Rest Of Policies 
        else:
            return ["cnic","cdate","dob","city","address"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:

        return {
            "cnic": self.from_text(not_intent="out_of_scope"),
            "cdate": self.from_text(not_intent="out_of_scope"),
            "dob": self.from_text(not_intent="out_of_scope"),
            "city": self.from_text(),
            "address": self.from_text(),
            "HCArange":self.from_text()
        }
    
    def request_next_slot( self, dispatcher: "CollectingDispatcher", tracker: "Tracker",   domain: Dict[Text, Any], ) -> Dict[Text, Any]:
        """Request the next slot and utter template if needed,else return None"""
        
        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):
                ## Condition of validated slot that triggers deactivation
                if (slot == "city"):

                    data=APIClass.cityList

                    message={"payload":"dropDown","data":data}
  
                    dispatcher.utter_message(text="Please select you city .. ",json_message=message)
                else:
                    dispatcher.utter_message(template=f"utter_ask_{slot}", **tracker.slots)
                return [SlotSet(REQUESTED_SLOT, slot)]
        return None
    
    def validate_dob(self,
                      value: Text,
                      dispatcher: CollectingDispatcher,
                      tracker: Tracker,
                      domain: Dict[Text, Any],
                      ) -> Dict[Text, Any]:

        err_msg = "Incorrect data format, should be Day/Month/Year like (04/05/2000)"

        occurance = str(value).count("/")
        if (occurance != 2):
            dispatcher.utter_message(err_msg)
            return {"dob": None}

        day,month,year = value.split('/')

       
        try:
            date_obj = datetime(int(year),int(month),int(day)).strftime("%Y/%m/%d")
            return {"dob": str(date_obj)}
        except ValueError:
            dispatcher.utter_message(err_msg)
            return {"dob": None}

    def validate_cdate(self,
                      value: Text,
                      dispatcher: CollectingDispatcher,
                      tracker: Tracker,
                      domain: Dict[Text, Any],
                      ) -> Dict[Text, Any]:
                                
        err_msg = "Incorrect data format, should be Day/Month/Year like (04/05/2000)"

        occurance = str(value).count("/")
        if (occurance != 2):
            dispatcher.utter_message(err_msg)
            return {"cdate": None}

        day,month,year = value.split('/')

        try:
            date_obj = datetime(int(year),int(month),int(day)).strftime("%Y/%m/%d")
            return {"cdate": str(date_obj)}
        except ValueError:
            dispatcher.utter_message(err_msg)
            return {"cdate": None}

    def validate_cnic(self,
                      value: Text,
                      dispatcher: CollectingDispatcher,
                      tracker: Tracker,
                      domain: Dict[Text, Any],
                      ) -> Dict[Text, Any]:
        
        err_msg = "Incorrect cnic format, should be 42101-4566670-8 OR 4210145666708"

        occurance = str(value).count("-")
        
        if (occurance == 0) & (len(str(value)) == 13):
            cnicValue = "-".join([str(value)[:5],str(value)[5:12],str(value)[12:]])
            return {"cnic": str(cnicValue)}

        if (occurance == 2):
            start,mid,end = str(value).split('-')
    
            try:
                if((len(start) == 5) & (len(mid) == 7) & (len(end) == 1)):
                    return {"cnic": str(value)}
                else:
                    dispatcher.utter_message(err_msg)
                    return {"cnic": None}
            except ValueError:
                dispatcher.utter_message(err_msg)
                return {"cnic": None}
        
        if (occurance != 2):
            dispatcher.utter_message(err_msg)
            return {"cnic": None}
  

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        
        apiObj = APIClass()
        token = apiObj.getToken()

        ProductId, ProductNum, PlanName = apiObj.getProductNum_Id(policyDict[str(tracker.get_slot("policyname"))],token)

        DoB = str(tracker.get_slot("dob"))
        FName = str(tracker.get_slot("fname")) 
        LName = str(tracker.get_slot("lname"))
        Cnic = str(tracker.get_slot("cnic"))
        Cell = str(tracker.get_slot("mobile"))
        Email = str(tracker.get_slot("email"))
        Address = str(tracker.get_slot("address"))
        City = str(tracker.get_slot("city"))
        Cdate = str(tracker.get_slot("cdate"))

        StartDate = datetime.today().strftime('%Y/%m/%d')
        Age = apiObj.calculateYears(DoB,StartDate)
        
        planCode = digitalplanCodeDict[str(tracker.get_slot("policyname"))]
            
        response = apiObj.validateMember(token,FName + ' ' + LName,Cnic,DoB,ProductId,planCode)

        if str(response.json()['Status']) != "100":
            dispatcher.utter_message("There is an Error Validating for CNIC \n " + response.json()['Message'])
            
            return [ ]
        
        totalPremium = int(response.json()['Data'][0]['GrossPremium']) + int(response.json()['Data'][0]['Charges'])

        dispatcher.utter_message("\n Your Total Premium would be PKR " + str(int(totalPremium)))

        CityId = apiObj.searchCity(City,apiObj.getCities(token))
        
        if CityId == -1:
            dispatcher.utter_message("\n City is not found , plz try again with correct city name")
            return [SlotSet("city",None) ]

        gender  = 2 if (int(Cnic[-1]) % 2) == 0 else 1
        
        policyObj = Policy([],[],[],[],FName,LName,"",Cnic,Email,None,
        Cell,Address,City,"Pakistan","",apiObj.changeYearFrom2to4Digit(DoB),gender,Age,"0",1,Cdate,"",None,"",ProductNum,PlanName,
        planCode,None,"20","0","2",None,None,StartDate,1,CityId,False,False,0.0,0.0,None,totalPremium,None,None,None,
        0,0,0,None,1,1)

        response = apiObj.issuePolicy(token,policyObj)
     
        policyId = -1 

        if (response['Status'] == 100):
            policyId = response['Data']
            dispatcher.utter_message("Policy Data is successfully saved .")
        else:
            dispatcher.utter_message("Policy Data cannot be saved ! ")
            dispatcher.utter_message(response['Message'])
            for msg in response['Data']:
                dispatcher.utter_message(msg)
            return [AllSlotsReset()]

        response = apiObj.paymentDetails(token,totalPremium,policyId,Cnic)
        if (response['Status'] == 100):
            dispatcher.utter_message("\n For payments Follow the Url below .")
            
            str_policyid = str(policyId)
            str_policyid_bytes = str_policyid.encode("ascii") 
            
            base64_bytes = base64.b64encode(str_policyid_bytes) 
            base64_string = base64_bytes.decode("ascii") 
            
            dispatcher.utter_message(APIClass.serverInfo["paymentUrl"]+base64_string)
        else:
            dispatcher.utter_message(response['Message'])
            for msg in response['Data']:
                dispatcher.utter_message(msg)
     
        
        
        return [ AllSlotsReset() ]

class CommonDataForm(FormAction):

    def name(self):
        return "common_data_form"

    @staticmethod
    def required_slots(tracker):
        return ["fname","lname","mobile","email"]


    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:

        return {
            "mobile": self.from_text(not_intent="out_of_scope"),
            "fname" : self.from_text(not_intent="out_of_scope"),
            "lname" : self.from_text(not_intent="out_of_scope"),
            "email" : self.from_text(not_intent="out_of_scope"),
        }

    def validate_mobile(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> Dict[Text, Any]:
        """Check to see if a tel meets requirements."""
        value = Helper.clean_number(value)
        if Helper.is_int(value) and (15 > len(value) > 6):
            return {"mobile": value}
        else:
            dispatcher.utter_message("Phone Number doesnt look valid")
            return {"mobile": None}
    
    def validate_email(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> Dict[Text, Any]:
        """Check to see if an email meets requirements"""
        if Helper.email_regex(value):
            return {"email": value}
        else:
            dispatcher.utter_message("Email doesnt look valid")
            return {"email": None}

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        
        return []

class OTPDataForm(FormAction):

    def name(self):
        return "otp_data_form"

    @staticmethod
    def required_slots(tracker):
        return ["cnic","mobile"]


    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:

        return {
            "cnic": self.from_text(),
            "mobile" : self.from_text(),
        }
    
    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        

        return []

class PolicySelectForm(FormAction):

    def name(self):
        return "policy_select_form"

    @staticmethod
    def required_slots(tracker):
        if tracker.get_slot('policyname') != None:
            return['policyname']
        else:
            # if Life section selected then go to LTA policy
            if (tracker.get_slot('healthlife') == None):
                return ["healthlife"]
            elif ("life" in str(tracker.get_slot('healthlife')).lower()):
                return ["healthlife","LTApolicy"]
            # if health section selected then show Health Section menu
            elif ("health" in str(tracker.get_slot('healthlife')).lower()):
                if tracker.get_slot('policytype') == "Digital":
                    return ["healthlife","policytype","Digitalpolicy"]
                elif tracker.get_slot('policytype') == "Instant":
                    return ["healthlife","policytype","Instapolicy"]
                else:
                    return ["healthlife","policytype","Telepolicy"]


    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:

        return {
            "policyname": [self.from_entity(entity="policyname",
                                            intent=["policy_inquire","inform"]),
                           self.from_entity(entity="policyname")],

            "healthlife": [self.from_entity(entity="healthpolicy",
                                            intent=["policy_inquire","inform"]),
                           self.from_entity(entity="lifepolicy",
                                            intent=["policy_inquire","inform"]),
                           self.from_text()],
            "policytype": self.from_text(),
            "Digitalpolicy": self.from_text(),
            "Instapolicy": self.from_text(),
            "Telepolicy": self.from_text(),
            "LTApolicy": self.from_text()
        }
    
    def validate_policyname(self,
                      value: Text,
                      dispatcher: CollectingDispatcher,
                      tracker: Tracker,
                      domain: Dict[Text, Any],
                      ) -> Dict[Text, Any]:
        err_msg = "Incorrect selection , there is no Policy named : "

        result = [x for x in list(policyDict.keys()) if(x in str(value)) ]

        # if 1 match was found
        if len(result) == 1:
            return {"policyname": result[0]}
        else:
            dispatcher.utter_message(err_msg + str(value))
            return {"policyname": None}

    def validate_Digitalpolicy(self,
                      value: Text,
                      dispatcher: CollectingDispatcher,
                      tracker: Tracker,
                      domain: Dict[Text, Any],
                      ) -> Dict[Text, Any]:
        
        err_msg = "Incorrect selection .. "

        try:

            result = [x for x in list(policyDict.keys()) if(x in str(value)) ]

            if len(result) == 1:
                return {"policyname": str(value)}
            else:
                dispatcher.utter_message(err_msg)
                return {"policyname": None}
        except ValueError:
            dispatcher.utter_message(err_msg + ".")
            return {"policyname": None}
    
    def validate_Instapolicy(self,
                      value: Text,
                      dispatcher: CollectingDispatcher,
                      tracker: Tracker,
                      domain: Dict[Text, Any],
                      ) -> Dict[Text, Any]:
        
        err_msg = "Incorrect selection .. "

        try:

            result = [x for x in list(policyDict.keys()) if(x in str(value)) ]

            if len(result) == 1:
                return {"policyname": str(value)}
            else:
                dispatcher.utter_message(err_msg)
                return {"policyname": None}
        except ValueError:
            dispatcher.utter_message(err_msg + ".")
            return {"policyname": None}

    def validate_Telepolicy(self,
                      value: Text,
                      dispatcher: CollectingDispatcher,
                      tracker: Tracker,
                      domain: Dict[Text, Any],
                      ) -> Dict[Text, Any]:
        
        err_msg = "Incorrect selection .. "

        try:

            result = [x for x in list(policyDict.keys()) if(x in str(value)) ]

            if len(result) == 1:
                return {"policyname": str(value)}
            else:
                dispatcher.utter_message(err_msg)
                return {"policyname": None}
        except ValueError:
            dispatcher.utter_message(err_msg + ".")
            return {"policyname": None}

    def validate_LTApolicy(self,
                      value: Text,
                      dispatcher: CollectingDispatcher,
                      tracker: Tracker,
                      domain: Dict[Text, Any],
                      ) -> Dict[Text, Any]:
        
        err_msg = "Incorrect selection .. "

        try:

            result = [x for x in list(policyDict.keys()) if(x in str(value)) ]

            if len(result) == 1:
                return {"policyname": str(value)}
            else:
                dispatcher.utter_message(err_msg)
                return {"policyname": None}
        except ValueError:
            dispatcher.utter_message(err_msg + ".")
            return {"policyname": None}
    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:


        return []

class ActionCheckIfDigital(Action):

    def name(self) -> Text:
        return "action_check_ifdigital"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        policy = str(tracker.get_slot("policyname"))
        if policy in ['Water','Hybrid','Mosquito']:
            return [SlotSet("isDigital",True)]
        else:
            return [SlotSet("isDigital",False)]

class ActionCheckIfLTA(Action):

    def name(self) -> Text:
        return "action_check_ifLTA"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        policy = str(tracker.get_slot("policyname"))
        if policy == "Level Term Assurance":
            return [SlotSet("isLTA",True)]
        else:
            return [SlotSet("isLTA",False)]

class ActionCheckLTAConsent(Action):

    def name(self) -> Text:
        return "action_checkLTAConsent"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        intentName = tracker.latest_message['intent'].get('name')
        if intentName == "affirm":
            return [SlotSet("LTADeclarationAgree",True)]
        else:
            return [SlotSet("LTADeclarationAgree",False)]

class ActionShowLTAinfo(Action):

    def name(self) -> Text:
        return "action_show_LTA_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        policy = str(tracker.get_slot("policyname"))
        
        if policy == "Level Term Assurance":
            
            apiObj = APIClass()
            
            lta_token = apiObj.getLTAToken()
            
            minAge,maxAge,minTerm,maxTerm,maxOverAge,maxSumAssured,minSumAssured = apiObj.getProductDetails(lta_token,574)

            infoMsg = ("Important Details regarding Level Term Assurance\n" +
            "\n" + "Age Limit is " + minAge + " - " + maxAge + "\n" + 
            "\n" + "Term Limit is " + minTerm + " - " + maxTerm + "\n" +
            "\n" + "Sum Assured Limit is " + '{:,}'.format(int(minSumAssured)) + " - " + '{:,}'.format(int(maxSumAssured)))

            dispatcher.utter_message(infoMsg)
  
            return [SlotSet("lta_TermRange",minTerm + " - " + maxTerm),SlotSet("lta_SumRangeMin",'{:,}'.format(int(minSumAssured))), SlotSet("lta_SumRangeMax",'{:,}'.format(int(maxSumAssured)))]
        else:
            return []
    
class ActionGenerateLTApolicy(Action):

    def name(self) -> Text:
        return "action_generate_LTApolicy"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        policy = str(tracker.get_slot("policyname"))
        
        if policy == "Level Term Assurance":
            
            apiObj = APIClass()
            
            lta_token = apiObj.getLTAToken()
            token = apiObj.getToken()

            fname = str(tracker.get_slot("fname"))
            lname = str(tracker.get_slot("lname"))
            cnic = str(tracker.get_slot("cnic"))
            email = str(tracker.get_slot("email"))
            mobile = str(tracker.get_slot("mobile"))
            occupation = str(tracker.get_slot("occupation"))
            
            income = str(tracker.get_slot("income"))
            termYears = str(tracker.get_slot("termYears"))
            sumInsured = str(tracker.get_slot("sumInsured"))
            ifDeclarationAgree = str(tracker.get_slot("LTADeclarationAgree"))
            dob = str(tracker.get_slot("dob"))

            occupationId = [obj for obj in APIClass.occupationListjson if obj['Desc']== occupation.upper()]

            if len(occupationId) > 0:
                occupationId = occupationId[0]['Id']
            else:
                occupationId = [obj for obj in APIClass.occupationListjson if obj['Desc']== 'Unknown'][0]['Id']

            StartDate = datetime.today().strftime('%Y/%m/%d')
            
            Age = apiObj.calculateYears(dob,StartDate)
            
            planCode = digitalplanCodeDict[str(tracker.get_slot("policyname"))]
                
            gender  = "Female" if (int(cnic[-1]) % 2) == 0 else "Male"

            response = apiObj.getLTAPremiumDetails(lta_token,574,termYears,sumInsured,dob,gender,str(occupationId),ifDeclarationAgree)
        
            if str(response['Status']) != "100":
                dispatcher.utter_message(response['Message'])
                return [ ]
        
            dispatcher.utter_message("Expected Gross Premium : " + str(int(response['Data']['GrossPremium'])))
        
            totalPremium = int(response['Data']['GrossPremium'])

            UWFlag = 0 if int(response['Data']['UnderWritingFlag']) == 1 else 1

            policyObj = Policy([],[],[],[],fname,lname,"",cnic,email,None,
            mobile,"No Address","","Pakistan","",apiObj.changeYearFrom2to4Digit(dob),gender,str(Age),"0",1,"","",None,"","PS2020KHI-P000006","Level Term Assurance",
            planCode,None,"19","0","10",None,None,StartDate,1,1,False,False,0.0,0.0,None,totalPremium,None,None,None,
            0,0,0,None,1,1,Term=termYears,Nationality="Pakistan",FKOccupationID=occupationId,SumInsured=sumInsured,UnderWritingFlag=UWFlag,MonthlyIncome=income,UnderwritingReason="None")

            response = apiObj.ifLTAPolicyExists(lta_token,policyObj)

            print(response)


            if str(response['Status']) == "100":
                             
                print("Data validation complete !")

                response = apiObj.issuePolicy(token,policyObj)
     
                policyId = -1 

                #print(response)

                if (str(response['Status']) == "100") or (str(response['Status']) == "400"):
                    policyId = response['Data']
                    print("LTA Data is successfully saved .")
                else:
                    dispatcher.utter_message("LTA Data cannot be saved ! ")
                    dispatcher.utter_message(response['Message'])
                    return [AllSlotsReset()]

                response = apiObj.paymentDetails(token,totalPremium,policyId,cnic)

                print("payment details save")

                print(response)

                if str(response['Status']) == "100":
                    
                    str_policyid = str(policyId)
                    str_policyid_bytes = str_policyid.encode("ascii") 
                    
                    base64_bytes = base64.b64encode(str_policyid_bytes) 
                    base64_string = base64_bytes.decode("ascii") 
                    
                    infoMsg = ( "For payments Follow the Url below \n" + 
                    APIClass.serverInfo["paymentUrl"]+base64_string )

                    dispatcher.utter_message(infoMsg)
                else:
                    dispatcher.utter_message(response['Message'])
                
            else:
                dispatcher.utter_message("Policy already exists against given CNIC!")
                return [AllSlotsReset()]
                

            
                        
            return [AllSlotsReset()]
        else:
            print("Non LTA Called this function")
            return [AllSlotsReset()]

class ActionDiseaseQuestion(Action):

    def name(self) -> Text:
        return "action_disease_question"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        policyType = str(tracker.get_slot("policyname"))
        if policyType == "Mosquito":
            dispatcher.utter_message(template="utter_ask_diseaseMosquito")
        elif policyType == "Water":
            dispatcher.utter_message(template="utter_ask_diseaseWater")
        else:
            dispatcher.utter_message(template="utter_ask_diseaseHyper")

        return []

class ActionSendOTP(Action):

    def name(self) -> Text:
        return "action_send_otp"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> Dict[Text, Any]:

        apiObj = APIClass()
        token = apiObj.getToken()
        cnic = str(tracker.get_slot("cnic"))
        phone = str(tracker.get_slot("mobile"))

        dispatcher.utter_message(phone)
        dispatcher.utter_message(cnic)

        response = apiObj.sendOTP(cnic,phone,token)
        
        if (response['Status'] == 100):

            dispatcher.utter_message(template="utter_inform_otpsend")

        else:
            dispatcher.utter_message(template="utter_inform_otpNotsend")

       
        return []

class ActionCheckOTP(Action):

    def name(self) -> Text:
        return "action_check_otp"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        apiObj = APIClass()
        token = apiObj.getToken()
        cnic = str(tracker.get_slot("cnic"))
        phone = str(tracker.get_slot("mobile"))
        otp = (tracker.latest_message)['text']

        response = apiObj.verifyOTP(cnic,phone,otp,token)

        if (response['Status'] == 100):

            dispatcher.utter_message("\n OTP Verified.")
        else:
            dispatcher.utter_message("\n OTP Can't be verified ! ")

        return []

class LTADataForm(FormAction):
    
    
    def name(self):
        return "lta_data_form"
    
            
    @staticmethod
    def required_slots(tracker):
        return ["fname","lname","dob","cnic","email","mobile","occupation","income","termYears","sumInsured"]
        
    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:

        return {
            "fname": self.from_text(not_intent="out_of_scope"),
            "lname": self.from_text(not_intent="out_of_scope"),
            "dob": self.from_text(not_intent="out_of_scope"),
            "cnic": self.from_text(not_intent="out_of_scope"),
            "email": self.from_text(not_intent="out_of_scope"),
            "mobile": self.from_text(not_intent="out_of_scope"),
            "occupation": self.from_text(),
            "income": self.from_text(not_intent="out_of_scope"),
            "termYears": self.from_text(not_intent="out_of_scope"),
            "sumInsured": self.from_text(not_intent="out_of_scope")
        }
    
    def validate_dob(self,
                      value: Text,
                      dispatcher: CollectingDispatcher,
                      tracker: Tracker,
                      domain: Dict[Text, Any],
                      ) -> Dict[Text, Any]:

        err_msg = "Incorrect data format, should be Day/Month/Year like (04/05/2000)"

        occurance = str(value).count("/")
        if (occurance != 2):
            dispatcher.utter_message(err_msg)
            return {"dob": None}

        day,month,year = value.split('/')

       
        try:
            date_obj = datetime(int(year),int(month),int(day)).strftime("%Y/%m/%d")
            return {"dob": str(date_obj)}
        except ValueError:
            dispatcher.utter_message(err_msg)
            return {"dob": None}

    def validate_cnic(self,
                      value: Text,
                      dispatcher: CollectingDispatcher,
                      tracker: Tracker,
                      domain: Dict[Text, Any],
                      ) -> Dict[Text, Any]:
        
        err_msg = "Incorrect cnic format, should be 42101-4566670-8 OR 4210145666708"

        occurance = str(value).count("-")
        
        if (occurance == 0) & (len(str(value)) == 13):
            cnicValue = "-".join([str(value)[:5],str(value)[5:12],str(value)[12:]])
            return {"cnic": str(cnicValue)}

        if (occurance == 2):
            start,mid,end = str(value).split('-')
    
            try:
                if((len(start) == 5) & (len(mid) == 7) & (len(end) == 1)):
                    return {"cnic": str(value)}
                else:
                    dispatcher.utter_message(err_msg)
                    return {"cnic": None}
            except ValueError:
                dispatcher.utter_message(err_msg)
                return {"cnic": None}
        
        if (occurance != 2):
            dispatcher.utter_message(err_msg)
            return {"cnic": None}
    
    def validate_termYears(self,
                      value: Text,
                      dispatcher: CollectingDispatcher,
                      tracker: Tracker,
                      domain: Dict[Text, Any],
                      ) -> Dict[Text, Any]:
        
        lta_TermRange = str(tracker.get_slot("lta_TermRange"))
        err_msg = "Incorrect range for Term Years , please select in range " + lta_TermRange 
        print('in validate termyears', lta_TermRange)
        try:
            lower,upper = lta_TermRange.split('-')
        except ValueError:
            lower,upper = 5,25

        try:
            if( ( int(lower) <=  int(value) ) & (int(upper) >= int(value)) ):
                return {"termYears": str(value)}
            else:
                dispatcher.utter_message(err_msg)
                return {"termYears": None}
        except ValueError:
            dispatcher.utter_message(err_msg)
            return {"termYears": None}

    def validate_sumInsured(self,
                      value: Text,
                      dispatcher: CollectingDispatcher,
                      tracker: Tracker,
                      domain: Dict[Text, Any],
                      ) -> Dict[Text, Any]:
        
        lta_SumRangeMin = Helper.clean_number(str(tracker.get_slot("lta_SumRangeMin")))
        lta_SumRangeMax = Helper.clean_number(str(tracker.get_slot("lta_SumRangeMax")))
        print(lta_SumRangeMin,lta_SumRangeMax)
        err_msg = "Incorrect range for Sum Insured , please select in range between " + lta_SumRangeMin + " and " + lta_SumRangeMax 
        
        try:
            if( ( int(lta_SumRangeMin) <=  int(value) ) & (int(lta_SumRangeMax) >= int(value)) ):
                return {"sumInsured": str(value)}
            else:
                dispatcher.utter_message(err_msg)
                return {"sumInsured": None}
        except ValueError:
            dispatcher.utter_message(err_msg)
            return {"sumInsured": None} 
    

    def request_next_slot( self, dispatcher: "CollectingDispatcher", tracker: "Tracker",   domain: Dict[Text, Any], ) -> Dict[Text, Any]:
        """Request the next slot and utter template if needed,else return None"""
        
        for slot in self.required_slots(tracker):
            
            if self._should_request_slot(tracker, slot):

                ## Condition of validated slot that triggers deactivation
                if (slot == "occupation"):

                    data=APIClass.occupationList

                    message={"payload":"dropDown","data":data}
  
                    dispatcher.utter_message(text="Please select a occupation",json_message=message)
                       
                    ## For all other slots, continue as usual
                    #logger.debug(f"Request next slot '{slot}'")
                else:
                    dispatcher.utter_message(template=f"utter_ask_{slot}", **tracker.slots)
                return [SlotSet(REQUESTED_SLOT, slot)]
        return None
    
    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        
        
        return [ ]

class ClaimDataForm(FormAction):
        
    def name(self):
        return "claim_data_form"
        
    @staticmethod
    def required_slots(tracker):
        return ["cnic","mobile4claim","card","insuredname","accidentdate","dischargedate","claimamount"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:

        return {
            "cnic": self.from_text(intent="number"),
            "mobile4claim": self.from_text(intent="number"),
            "card": self.from_text(not_intent="out_of_scope"),
            "insuredname": self.from_text(not_intent="out_of_scope"),
            "accidentdate": self.from_text(not_intent="out_of_scope"),
            "dischargedate": self.from_text(not_intent="out_of_scope"),
            "claimamount": self.from_text(not_intent="out_of_scope"),
        }
    
    def request_next_slot( self, dispatcher: "CollectingDispatcher", tracker: "Tracker",   domain: Dict[Text, Any], ) -> Dict[Text, Any]:
        """Request the next slot and utter template if needed,else return None"""
        
        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):
                ## Condition of validated slot that triggers deactivation
                if (slot == "card") & (customData != None):
                    if customData[tracker.sender_id] == False:
                        dispatcher.utter_message(text="Sorry, stopping the data collection process!")
                       
                        return self.deactivate()

                    ## For all other slots, continue as usual
                    #logger.debug(f"Request next slot '{slot}'")
                dispatcher.utter_message(template=f"utter_ask_{slot}", **tracker.slots)
                return [SlotSet(REQUESTED_SLOT, slot)]
        return None

    def validate_claimamount(self,
                      value: Text,
                      dispatcher: CollectingDispatcher,
                      tracker: Tracker,
                      domain: Dict[Text, Any],
                      ) -> Dict[Text, Any]:
        
        err_msg = "Please enter Numeric value only ..This doesnt look like a Number .. "

        try:

            lastIntent = tracker.latest_message['intent'].get('name')

            if lastIntent == "number":
                value = int(str(value).replace(',',''))
                return {"claimamount": str(value)}
            else:
                dispatcher.utter_message(err_msg)
                return {"claimamount": None}
        except ValueError:
            dispatcher.utter_message("Exception : " + err_msg)
            return {"claimamount": None}

    def validate_accidentdate(self,
                      value: Text,
                      dispatcher: CollectingDispatcher,
                      tracker: Tracker,
                      domain: Dict[Text, Any],
                      ) -> Dict[Text, Any]:
        
        err_msg = "This doesnt look like date ... "

        try:

            lastIntent = tracker.latest_message['intent'].get('name')

            if lastIntent == "date":
                return {"accidentdate": str(value)}
            else:
                dispatcher.utter_message(err_msg)
                return {"accidentdate": None}
        except ValueError:
            dispatcher.utter_message("Exception : " + err_msg)
            return {"accidentdate": None}

    def validate_dischargedate(self,
                      value: Text,
                      dispatcher: CollectingDispatcher,
                      tracker: Tracker,
                      domain: Dict[Text, Any],
                      ) -> Dict[Text, Any]:
        
        err_msg = "This doesnt look like date ... "

        try:

            lastIntent = tracker.latest_message['intent'].get('name')

            if lastIntent == "date":
                return {"dischargedate": str(value)}
            else:
                dispatcher.utter_message(err_msg)
                return {"dischargedate": None}
        except ValueError:
            dispatcher.utter_message("Exception : " + err_msg)
            return {"dischargedate": None}

    def validate_mobile4claim(self,
                      value: Text,
                      dispatcher: CollectingDispatcher,
                      tracker: Tracker,
                      domain: Dict[Text, Any],
                      ) -> Dict[Text, Any]:
        
        apiObj = APIClass()
        token = apiObj.getToken()
        
        cnic = tracker.get_slot("cnic")
        cell = value

        result = apiObj.getPolicies(token,cnic,cell)

        jsonData = result.json()
        dictPolicyId = {}
        
        if(jsonData['Data'] != None):
            
            dispatcher.utter_message("Type the Card # from below assocaited policy cards against the CNIC")
            
            for keyval in jsonData['Data']:
                dictPolicyId[keyval['CardNo']] = str(keyval['PolicyID'])
                dispatcher.utter_message(keyval['CardNo'])
            
            customData[tracker.sender_id] = dictPolicyId

        else:
            dispatcher.utter_message("No Card against the provided CNIC & Cell combination")
            customData[tracker.sender_id] = False
              
           

        return {"mobile4claim": str(value)}

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        dispatcher.utter_message("Thank you for the information ! It is being processed ... ")
        
        cnic = str(tracker.get_slot("cnic"))
        cell = str(tracker.get_slot("mobile4claim"))
        card = str(tracker.get_slot("card"))
        insuredName = str(tracker.get_slot("insuredname"))
        recoveryDate = str(tracker.get_slot("dischargedate"))
        illnessDate = str(tracker.get_slot("accidentdate"))
        claimAmount = str(tracker.get_slot("claimamount"))

        temp = customData[tracker.sender_id]
        
        apiObj = APIClass()
        
        token = apiObj.getToken()

        result = apiObj.getIsureds(token,cnic,cell,temp[card])

        insuredDetailId = result.json()['Data'][0]['InsuredID']

        policyNumber = result.json()['Data'][0]['PolicyNumber']

        policyId = result.json()['Data'][0]['PolicyID']

        claimObj = Claim("",str(claimAmount),card,"2","","","",str(insuredDetailId),policyId,str(insuredDetailId),"","0",illnessDate,insuredName
        ,"",[],"create","","",policyNumber,"","","",recoveryDate,"")

        response = apiObj.submitClaimIntimation(token,claimObj)

        
        if (response['Status'] == 100):

            dispatcher.utter_message("Claim intimated successfully , you will be contacted soon by our representative .")
            dispatcher.utter_message("Please Note the Request Number for further refrence : " + response['Data']['RequestNo'])
        else:
            dispatcher.utter_message("Claim could not be initiated ! ")
            dispatcher.utter_message(response['Message'])
            for msg in response['Data']:
                dispatcher.utter_message(msg)

        
        
        
        return [ AllSlotsReset() ]