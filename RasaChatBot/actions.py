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
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction , REQUESTED_SLOT
import datetime
from datetime import datetime
import re
from APIClass import APIClass
from DataClasses import Policy , PaymentDetail , Claim
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

class PolicyForm(FormAction):
        
    def name(self):
        return "policy_form"
    
            
    @staticmethod
    def required_slots(tracker):
        return ["cnic","cdate","dob","gender","province","city","address"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:

        return {
            "cnic": self.from_text(not_intent='out_of_scope'),
            "cdate": self.from_text(not_intent='out_of_scope'),
            "dob": self.from_text(not_intent='out_of_scope'),
            "city": self.from_text(not_intent='out_of_scope'),
            "address": self.from_text(),
        }
    
    def request_next_slot( self, dispatcher: "CollectingDispatcher", tracker: "Tracker",   domain: Dict[Text, Any], ) -> Dict[Text, Any]:
        """Request the next slot and utter template if needed,else return None"""
        print("in req next slot" + str(tracker.sender_id))
        print(customData)
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
    
    def validate_dob(self,
                      value: Text,
                      dispatcher: CollectingDispatcher,
                      tracker: Tracker,
                      domain: Dict[Text, Any],
                      ) -> Dict[Text, Any]:

        err_msg = "Incorrect data format, should be Year/Month/Day"

        occurance = str(value).count("/")
        if (occurance != 2):
            dispatcher.utter_message(err_msg)
            return {"dob": None}

        year,month,day = value.split('/')

       
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
                                
        err_msg = "Incorrect data format, should be Year/Month/Day"

        occurance = str(value).count("/")
        if (occurance != 2):
            dispatcher.utter_message(err_msg)
            return {"cdate": None}

        year,month,day = value.split('/')

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
        
        err_msg = "Incorrect cnic format, should be xxxxx-xxxxxxxx-x"

        occurance = str(value).count("-")
        if (occurance != 2):
            dispatcher.utter_message(err_msg)
            return {"cnic": None}

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

   

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        dispatcher.utter_message("Thank you for the information ! It is being processed ... ")

        apiObj = APIClass()
        token = apiObj.getToken()

        ProductId, ProductNum, PlanName = apiObj.getProductNum_Id("PS2018KAR-P000016",token)

        DoB = str(tracker.get_slot("dob"))
        FName = str(tracker.get_slot("fname")) 
        LName = str(tracker.get_slot("lname"))
        Cnic = str(tracker.get_slot("cnic"))
        Cell = str(tracker.get_slot("mobile"))
        Email = str(tracker.get_slot("email"))
        Address = str(tracker.get_slot("address"))
        City = str(tracker.get_slot("city"))
        Province = str(tracker.get_slot("province"))
        Gender = str(tracker.get_slot("gender"))
        Cdate = str(tracker.get_slot("cdate"))

        StartDate = datetime.today().strftime('%Y/%m/%d')
        Age = apiObj.calculateYears(DoB,StartDate)
        
        response = apiObj.validateMember(token,FName + ' ' + LName,Cnic,DoB,ProductId)

        if str(response.json()['Status']) != "100":
            dispatcher.utter_message("There is an Error Validating for CNIC \n " + response.json()['Message'])
            return []
        
        totalPremium = int(response.json()['Data'][0]['GrossPremium']) + int(response.json()['Data'][0]['Charges'])

        dispatcher.utter_message("\n Your Total Premium would be PKR " + str(int(totalPremium)))

        CityId = apiObj.searchCity(City,apiObj.getCities(token))
        
        if CityId == -1:
            dispatcher.utter_message("\n City is not found , plz try again with correct city name")
            return []
        
        policyObj = Policy([],[],[],[],FName,LName,"",Cnic,Email,None,
        Cell,Address,City,"Pakistan","",DoB,Gender,Age,"0",1,Cdate,"",None,"",ProductNum,PlanName,
        "P0012",None,"20","0","2",None,None,StartDate,1,CityId,False,False,0.0,0.0,None,totalPremium,None,None,None,
        0,0,0,None,1,1)

        response = apiObj.issuePolicy(token,policyObj)
        policyId = -1 

        if (response['Status'] == 100):
            policyId = response['Data']
            dispatcher.utter_message("\n Policy Data is successfully saved .")
        else:
            dispatcher.utter_message("\n Policy Data cannot be saved ! ")
            dispatcher.utter_message(response['Message'])
            for msg in response['Data']:
                dispatcher.utter_message(msg)
            return []

        response = apiObj.paymentDetails(token,totalPremium,policyId,Cnic)
        if (response['Status'] == 100):
            dispatcher.utter_message("\n For payments Follow the Url below .")
            
            str_policyid = str(policyId)
            str_policyid_bytes = str_policyid.encode("ascii") 
            
            base64_bytes = base64.b64encode(str_policyid_bytes) 
            base64_string = base64_bytes.decode("ascii") 
            
            dispatcher.utter_message( "https://uat-payments.tpllife.com/Payment.aspx?data="+base64_string)
        else:
            dispatcher.utter_message(response['Message'])
            for msg in response['Data']:
                dispatcher.utter_message(msg)
     
        
        
        return [ ]


class CommonForm(FormAction):

    def name(self):
        return "common_form"

    @staticmethod
    def required_slots(tracker):
        return ["fname","lname","mobile","email"]


    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:

        return {
            "mobile": self.from_text(not_intent='out_of_scope'),
            "fname" : self.from_text(not_intent='out_of_scope'),
            "lname" : self.from_text(not_intent='out_of_scope'),
            "email" : self.from_text(not_intent='out_of_scope'),
        }
   

        
    def request_next_slot(
                    self,
                    dispatcher: "CollectingDispatcher",
                    tracker: "Tracker",
                    domain: Dict[Text, Any],
                ) -> Dict[Text, Any]:
 
        lastIntent = tracker.latest_message['intent'].get('name') 
        
        # if lastIntent == 'deny':
        #     dispatcher.utter_message(text="Sorry, I can't help you with that Now !!")
        #     return self.deactivate()

        """Request the next slot and utter template if needed,else return None"""
        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):

                ## Condition of validated slot that triggers deactivation
                if slot == "cuisine" and tracker.get_slot("cuisine") == "caribbean":
                    dispatcher.utter_message(text="Sorry, I can't help you with that!!")
                    return self.deactivate()

                ## For all other slots, continue as usual
                #logger.debug(f"Request next slot '{slot}'")
                dispatcher.utter_message(
                    template=f"utter_ask_{slot}", **tracker.slots
                )
                return [SlotSet(REQUESTED_SLOT, slot)]
        return None

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        #dispatcher.utter_message("Thank you for the information ! It is being processed ... ")


        return []

class ActionCheckDigital(Action):
    def name(self):
        return "action_check_digital"
    
    def run(self,dispatcher,tracker,domain):
        digitalPolicy = (tracker.latest_message)['text']
        return [SlotSet("digital",digitalPolicy)]
