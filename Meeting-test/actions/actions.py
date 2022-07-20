# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

#***********************************************************************************************************************************************************
#This is a sample database file
action_items = [
    {
        "id": "1",
        #"meeting_id": "1",
        "text": "Complete the presentation",
        "owners": ["1"],
        #"status": "yet to start",
        "deadline": "",
        #"time":"",
    },
    {
        "id": "2",
        #"meeting_id": "1",
        "text": "Join slack channel",
        "owners": ["1","2"],
        "deadline": "",
        #"status": "yet to start",
        #"time":"",
    },
    {
        "id": "3",
        #"meeting_id": "2",
        "text": "Deploy on Docker",
        "owners": ["2"],
        "deadline": "",
        #"status": "yet to start",
        #"time":"",
    },
]

talking_points = [
    {
        "id": "1",
        #"agenda": "General Knowledge",
        "notes":"",
        #"attendees": ["1","2"],
        #"action_items": ["1","2"],
    },
    {
        "id": "2",
        #"agenda": "Delhi Tourism",
        "notes": "",
        #"attendees": ["1"],
        #"action_items": ["3"],
    }
]

#********************************************************************************************************************************************************

from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import AllSlotsReset, SlotSet
#import spacy
#from transformers import SLOW_TO_FAST_CONVERTERS
#import data
from datetime import datetime as dt
from datetime import timedelta as td
import requests as req
import json
import os
from dotenv import load_dotenv
import uuid
from difflib import get_close_matches
import re
#
#

load_dotenv()
#url = os.getenv("url")
#token = os.getenv("token")
url="https://qaapidjano.fogteams.com/"
print(url)
token="Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjo0MjQ4MDY1NDQ5LCJpYXQiOjE2NTYwNjU0NDksImp0aSI6IjU0MTVmZDJlM2I3MzQ1NjQ5ZDQ2OWNiM2FjY2M2MjI0IiwidXNlcl9pZCI6NX0.W71xYFmAQ0lRGHH6-IvPkJnQuQEG2YRSsH-AEHuVbd4"
headers = {"Authorization": token}

class ActionAddTalkingPoint(Action):
    def name(self) -> Text:
        return 'action_add_talking_point'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #talking_points.append(tracker.latest_message.get("text"))
        text=tracker.get_slot('talking_point_text')
        #last_ind=len(data.talking_points)-1
        #id=data.talking_points[last_ind]['id']+1
        id=tracker.get_slot('talking_point_id')
        dict={}
        dict["id"]=id
        dict["notes"]=text
        talking_points.append(dict)
        #----------------------------API-------------------------
        meeting_id=282
        speaker="Sanika Padegaonkar"
        print(url)
        res = req.get(url = url+"api/v1/notes/fetch/group/notes/by/id/", params={'group_note_id': meeting_id}, headers=headers)  

        if(res.status_code == 200):
            data = res.json()["data"]["data"]
            action_items_=data["action_items"]
            talking_points_=data["talking_points"]
        else:
            dispatcher.utter_message("API returned an incorrect status code")
            print("Couldn't fetch group data, Error code: ", res.status_code)
            return []

        action_items_list=[]
        action_items_list+=action_items_
        talking_points_list=[] 
        talking_points_list+=talking_points_   
        uid=str(uuid.uuid1())
        now=dt.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z")

        created_by={}
        res = req.get(url = url+"api/v1/user/get/all/users", headers=headers)  

        if(res.status_code == 200):
            users = res.json()["data"]
        else:
            dispatcher.utter_message("API returned an incorrect status code")
            print("Couldn't fetch group data, Error code: ", res.status_code)
            return []

        for user in users:
            if user["name"].lower()==speaker.lower():
                created_by["name"]=speaker
                created_by["user_id"]=user["user_alias_id"]
        
        updated_by={}
        updated_by["name"]=""
        updated_by["user_id"]=""

        new_talking_point={}
        new_talking_point["text"]=text
        new_talking_point["uuid"]=uid
        new_talking_point["created_at"]=now
        new_talking_point["created_by"]=created_by["user_id"]
        new_talking_point["updated_at"]=""
        new_talking_point["updated_by"]=""

        talking_points_list.clear()
        action_items_list.clear()
        talking_points_list.append(new_talking_point)

        updated_notes={"notes_id":meeting_id, "action_items":action_items_list,"talking_points":talking_points_list}
        
        upload = req.post(url=url+"api/v1/notes/group/note/json/data/update/", json=updated_notes, headers=headers)

        if(upload.status_code == 200):
            print("Upload Successful")
        else:
            print("Upload Unsuccessful", upload.status_code)

        dispatcher.utter_message("Talking Point added to database!")
        return []

class ActionAddTalkingPoint2(Action):
    def name(self) -> Text:
        return 'action_add_talking_point_2'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #talking_points.append(tracker.latest_message.get("text"))
        text=tracker.get_slot('talking_point_text_2')
        #last_ind=len(data.talking_points)-1
        #id=data.talking_points[last_ind]['id']+1
        id=tracker.get_slot('talking_point_id_2')
        dict={}
        dict["id"]=id
        dict["notes"]=text
        talking_points.append(dict)
        dispatcher.utter_message("Talking Point added to database!")
        return []

class ActionAddActionItem(Action):
    def name(self) -> Text:
        return 'action_add_action_item'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("Line: 190")
        #talking_points.append(tracker.latest_message.get("text"))
        text=tracker.get_slot('action_item_text')
        owner=tracker.get_slot('owner')
        deadline=tracker.get_slot('deadline')
        time=tracker.get_slot("time")
        #last_ind=len(data.action_items)-1
        #id=data.action_items[last_ind]['id']+1
        #id=tracker.get_slot('action_item_id')
        dictionary={}
        last_ind=len(action_items)-1
        id=int(action_items[last_ind]['id'])+1
        dictionary["id"]=id
        dictionary["text"]=text
        dictionary["deadline"]=deadline
        owners_ref=["sanika","aayush","ayushman","neeshi","samarth","kanik","amit","ravin","tanmay","safari"]
        owners=tracker.get_slot('owner')
        owners=re.sub(' and ', "and", owners)
        #owners=re.sub(',', " ", owners)
        #owners=re.sub('  ', " ", owners)
        print(owners)
        owner_list=owners.split("and")
        for owner in owner_list:
            index=owner_list.index(owner)
            owner=re.sub(' ', "", owner)
            print(owner)
            matches=get_close_matches(owner,owners_ref,n=1,cutoff=0)
            print(matches)
            owner_list[index]=matches[0]
        dictionary["owners"]=owner_list
        dictionary["deadline"]=deadline
        action_items.append(dictionary)
        print("Line: 221")

        if(type(time) is dict):
            if (time["to"]!=None):
                deadline["to"] = dt.strptime(str(time["to"]), "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%dT%H:%M:%S.%f%z")
            if (time["from"]!=None):
                deadline["from"] = dt.strptime(str(time["from"]), "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%dT%H:%M:%S.%f%z")
            deadline_field=deadline
        elif(time!=None):
            time=dt.strptime(time, "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%dT%H:%M:%S.%f%z")
            deadline_field=time
        else:
            deadline_field="None"
        
        #-------------------API-------------------------------#
        meeting_id=282
        speaker="Sanika Padegaonkar"
        print(url)
        res = req.get(url = url+"api/v1/notes/fetch/group/notes/by/id/", params={'group_note_id': meeting_id}, headers=headers)  

        if(res.status_code == 200):
            data = res.json()["data"]["data"]
            action_items_=data["action_items"]
            talking_points_=data["talking_points"]
        else:
            dispatcher.utter_message("API returned an incorrect status code")
            print("Couldn't fetch group data, Error code: ", res.status_code)
            return []

        action_items_list=[]
        action_items_list+=action_items_
        talking_points_list=[] 
        talking_points_list+=talking_points_   
        uid=str(uuid.uuid1())
        now=dt.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z")

        created_by={}

        print(url)
        #Getting all users
        res = req.get(url = url+"api/v1/user/get/all/users", headers=headers)  

        if(res.status_code == 200):
            users = res.json()["data"]
        else:
            dispatcher.utter_message("API returned an incorrect status code")
            print("Couldn't fetch group data, Error code: ", res.status_code)
            return []

        print("Line: 271")
        for user in users:
            if user["name"].lower()==speaker.lower():
                created_by["name"]=speaker
                created_by["user_id"]=user["user_alias_id"]

        users_lower=[user["name"].lower() for user in users]
        
        updated_by={}
        updated_by["name"]=""
        updated_by["user_id"]=""

        assignee_id=[]
        print("Line: 284")
        new_action_item={}
        new_action_item["uuid"]=uid
        new_action_item["title"]=text
        new_action_item["status"]="0"
        new_action_item["comment"]=""
        new_action_item["deadline"]=deadline_field
        new_action_item["created_at"]=now
        new_action_item["created_by"]=created_by
        new_action_item["updated_at"]=""
        new_action_item["updated_by"]=updated_by
        new_action_item["updated_at"]=""
        for owner in owner_list:
            info={}
            if owner.lower() in users_lower:
                for user in users:
                    if user["name"].lower()==owner.lower():
                        info["name"]=owner
                        info["role"]="owner"
                        info["color"]=user["color"]
                        info["email_id"]=user["email_id"]
                        info["dark_color"]=user["dark_color"]
                        info["short_name"]=user["short_name"]
                        info["user_id"]=user["user_alias_id"]
            else:
                dispatcher.utter_message("Please enter the name of the user as mentioned in the database")
                return[]

            assignee_id.append(info)
        print("Line: 313")
        new_action_item["assignee_id"]=assignee_id
        new_action_item["is_complete"]="0"

        talking_points_list.clear()
        action_items_list.clear()
        action_items_list.append(new_action_item)

        updated_notes={"notes_id":meeting_id, "action_items":action_items_list,"talking_points":talking_points_list}
        
        print("Line: 323")
        upload = req.post(url=url+"api/v1/notes/group/note/json/data/update/", json=updated_notes, headers=headers)

        if(upload.status_code == 200):
            print("Upload Successful")
        else:
            print("Upload Unsuccessful", upload.status_code)


        dispatcher.utter_message("Action Item added to database!")
        print("end")
        return[]

class ActionAddActionItem2(Action):
    def name(self) -> Text:
        return 'action_add_action_item_2'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #talking_points.append(tracker.latest_message.get("text"))
        text=tracker.get_slot('action_item_text_2')
        owner=tracker.get_slot('owner_2')
        deadline=tracker.get_slot('deadline_2')
        #last_ind=len(data.action_items)-1
        #id=data.action_items[last_ind]['id']+1
        id=tracker.get_slot('action_item_id_2')
        dict={}
        dict["id"]=id
        dict["text"]=text
        owners=tracker.get_latest_entity_values("owner")
        owner_list=[]
        for owner in owners:
            owner_list.append(owner)
        dict["owners"]=owner_list
        dict["deadline"]=deadline
        action_items.append(dict)
        dispatcher.utter_message("Action Item added to database!")
        return []

class ActionGetOwner(Action):
    def name(self) -> Text:
        return 'action_get_owner'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #owner=next(tracker.get_latest_entity_values("owner"), None)
        owners=tracker.get_latest_entity_values("owner")
        owner=[]
        for o in owners:
            owner.append(o)
        owner_str = ','.join(map(str, owner))
        str1="Entities detected"+str(owner_str)
        dispatcher.utter_message(str1)
        #owner=tracker.latest_message.get("text")
        dispatcher.utter_message("Owner slot set")
        return [SlotSet(key='owner', value=owner_str),SlotSet(key='owner_2', value=owner_str)]


class ActionGetDeadline(Action):
    def name(self) -> Text:
        return 'action_get_deadline'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #deadline=tracker.latest_message.get("text")
        time=tracker.get_slot('time')
        deadline={}
        #grain=tracker.get_slot('time')['grain']
        #deadline["from"] =time["from"].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        #deadline["to"] = time["to"].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        #deadline['from']= dt.strptime(time['from'], "%Y-%m-%dT%H:%M:%S.%f%z")
        #deadline['to']= dt.strptime(time['to'], "%Y-%m-%dT%H:%M:%S.%f%z")
        #deadline["to"] = dt.strptime(str(time["to"]), "%Y-%m-%dT%H:%M:%S.%f%z")
        #deadline["from"] = dt.strptime(str(time["from"]), "%Y-%m-%dT%H:%M:%S.%f%z")
        #dispatcher.utter_message("Deadline slot set")
        if(type(time) is dict):
            if (time["to"]!=None):
                deadline["to"] = dt.strptime(str(time["to"]), "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%H:%M:%S %d %b %Y")
            if (time["from"]!=None):
                deadline["from"] = dt.strptime(str(time["from"]), "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%H:%M:%S %d %b %Y")
            return [SlotSet(key='deadline', value=deadline),SlotSet(key='deadline_2', value=deadline)]
        elif(time!=None):
            time=dt.strptime(time, "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%H:%M:%S %d %b %Y")
            return [SlotSet(key='deadline', value=time),SlotSet(key='deadline_2', value=time)]
        else:
            return [SlotSet(key='deadline', value=time),SlotSet(key='deadline_2', value=time)]

        #return [SlotSet(key='deadline', value=time),SlotSet(key='deadline_2', value=time)]

class ActionGetActionItemText(Action):
    def name(self) -> Text:
        return 'action_get_action_item_text'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        text=tracker.latest_message.get("text")
        dispatcher.utter_message("Action Item Text slot set")
        #return [SlotSet(key='action_item_text', value=text)]
        return[]

class ActionGetActionItemId(Action):
    def name(self) -> Text:
        return 'action_get_action_item_id'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        last_ind=len(action_items)-1
        id=int(action_items[last_ind]['id'])+1
        dispatcher.utter_message("Action Item id updated!")
        #return [SlotSet(key='action_item_id', value=str(id)),SlotSet(key='action_item_id_2',value=str(id))]
        return[]


class ActionGetTalkingPointText(Action):
    def name(self) -> Text:
        return 'action_get_talking_point_text'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        text=tracker.latest_message.get("text")
        dispatcher.utter_message("Talking Point Text slot set")
        #return [SlotSet(key='talking_point_text', value=text)]
        return[]

class ActionGetTalkingPointId(Action):
    def name(self) -> Text:
        return 'action_get_talking_point_id'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        last_ind=len(talking_points)-1
        id=int(talking_points[last_ind]['id'])+1
        dispatcher.utter_message("Talking point id updated!")
        #return [SlotSet(key='talking_point_id', value=str(id)), SlotSet(key='talking_point_id_2', value=str(id))]
        return []


class ActionResetSlots(Action):
     def name(self) -> Text:
            return "action_reset_slots"

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

         dispatcher.utter_message("All slots have been reset")

         return [AllSlotsReset()]

class DisplayTalkingPoints(Action):
    def name(self) -> Text:
        return 'display_talking_points'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        for talking_point in talking_points:
            id_str="Id : "+str(talking_point['id'])
            text_str="Notes : "+talking_point['notes']
            dispatcher.utter_message(id_str)
            dispatcher.utter_message(text_str)
        return[]

class DisplayActionItems(Action):
    def name(self) -> Text:
        return 'display_action_items'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        for action_item in action_items:
            if action_item['id']!=None:
                id_str="Id : "+str(action_item['id'])
            else:
                id_str="Id : None"
            text_str="Text : "+action_item['text']
            str1=""
            for owner in action_item['owners']:
                str1+=owner+" , "
            owner_str="Owners : "+str1
            deadline_str="Deadline : "+str(action_item['deadline'])
            time_str="Time : "+str(tracker.get_slot('time'))
            dispatcher.utter_message(id_str)
            dispatcher.utter_message(text_str)
            dispatcher.utter_message(owner_str)
            dispatcher.utter_message(deadline_str)
            dispatcher.utter_message(time_str)
        return[]

class GetId(Action):
    def name(self) -> Text:
        return 'action_get_id'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #id=tracker.latest_message.get("text")
        id=tracker.latest_message.get("entities")
        dispatcher.utter_message(tracker.latest_message.get("entities"))
        #return[SlotSet(key="id",value=str(id))]
        return[]

#class AskField(Action):
    #def name(self) -> Text:
        #return 'action_ask_field'

    #async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #dispatcher.utter_message(buttons = [
                #{"payload": "/text", "title": "Text"},
                #{"payload": "/owners", "title": "Owners"},
                #{"payload": "/deadline", "title": "Deadline"},
            #])
        #return[]

#class GetField(Action):
    #def name(self) -> Text:
        #return 'action_get_field'

    #async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #field=tracker.latest_message.get("text")
        #return[SlotSet(key="field",value=field)]


class GetNewTalkingPointText(Action):
    def name(self) -> Text:
        return 'action_get_new_talking_point_text'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        new=tracker.latest_message.get("text")
        #return[SlotSet(key="new_talking_point_text",value=new)]
        return[]


class EditTalkingPoint(Action):
    def name(self) -> Text:
        return 'action_edit_talking_point'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        id=tracker.get_slot('talking_point_id_modify')
        new_notes=tracker.get_slot('new_talking_point_text')
        for t in talking_points:
            if t['id']==str(id):
                t['notes']=str(new_notes)
                dispatcher.utter_message("Talking point edited successfully!")
                #return[]
        
        #----------------------API-----------------------------

        meeting_id=282
        speaker="Sanika Padegaonkar"
        res = req.get(url = url+"api/v1/notes/fetch/group/notes/by/id/", params={'group_note_id': meeting_id}, headers=headers)  

        if(res.status_code == 200):
            data = res.json()["data"]["data"]
        else:
            dispatcher.utter_message("API returned an incorrect status code")
            print("Couldn't fetch group data, Error code: ", res.status_code)
            return []
        
        talking_points_=data["talking_points"]
        action_items_=data["action_items"]
        point=talking_points_[int(id)-1]
        point["text"]=new_notes
        now=dt.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z")

        #Getting all users
        res = req.get(url = url+"api/v1/user/get/all/users", headers=headers)  

        if(res.status_code == 200):
            users = res.json()["data"]
        else:
            dispatcher.utter_message("API returned an incorrect status code")
            print("Couldn't fetch group data, Error code: ", res.status_code)
            return []


        for user in users:
            if user["name"].lower()==speaker.lower():
                updated_by=user["user_alias_id"]

        point["updated_by"]=updated_by
        point["updated_at"]=now
        talking_points_[int(id)-1]=point


        updated_notes={"notes_id":meeting_id, "talking_points":talking_points_,"action_items": action_items_}

        upload = req.post(url=url+"api/v1/notes/group/note/data/update/", json=updated_notes, headers=headers)
        if(upload.status_code == 200):
            print("Upload Successful")
        else:
            print("Upload Unsuccessful", upload.status_code)    

        dispatcher.utter_message("Please enter a valid ID")


        dispatcher.utter_message("Please enter a valid ID")
        #return[{SlotSet(key='talking_point_id_modify',value=None)}]
        return[{"talking_point_id_modify":None}]

class DeleteTalkingPoint(Action):
    def name(self) -> Text:
        return 'action_delete_talking_point'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        id=tracker.get_slot('id')
        for t in talking_points:
            if t['id']==str(id):
                talking_points.remove(t)
                dispatcher.utter_message("Talking point deleted successfully!")
                #return[]

        #---------------------API---------------------------
        
        meeting_id=282
        speaker="Sanika Padegaonkar"
        res = req.get(url = url+"api/v1/notes/fetch/group/notes/by/id/", params={'group_note_id': meeting_id}, headers=headers)  

        if(res.status_code == 200):
            data = res.json()["data"]["data"]
            talking_points_=data["talking_points"]
            action_items_=data["action_items"]
            del talking_points_[int(id)-1]
        else:
            dispatcher.utter_message("API returned an incorrect status code")
            print("Couldn't fetch group data, Error code: ", res.status_code)
            return []

        updated_notes={"notes_id":meeting_id, "talking_points":talking_points_,"action_items": action_items_}

        upload = req.post(url=url+"api/v1/notes/group/note/data/update/", json=updated_notes, headers=headers)
        if(upload.status_code == 200):
            print("Upload Successful")
        else:
            print("Upload Unsuccessful", upload.status_code) 
        dispatcher.utter_message("Please enter a valid ID")
        #return[SlotSet(key='id',value=None)]
        return[{"id":None}]

class AskNewFieldValue(Action):
    def name(self) -> Text:
        return 'action_ask_new_field_value'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        field=tracker.get_slot('field')
        if str(field).lower()=="owners":
            dispatcher.utter_message("Enter new owners")
        elif str(field).lower()=="deadline":
            dispatcher.utter_message("Enter updated deadline")
        elif str(field).lower()=="text":
            dispatcher.utter_message("Enter updated text")
        else:
            dispatcher.utter_message("No such field exists")
        return[]

class GetNewFieldValue(Action):
    def name(self) -> Text:
        return 'action_get_new_field_value'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        new_field_value=tracker.get_slot('field')
        return[SlotSet(key="new_field_value",value=new_field_value)]    

class EditActionItem(Action):
    def name(self) -> Text:
        return 'action_edit_action_item'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        id=tracker.get_slot('action_item_id_modify')
        field=tracker.get_slot('field')
        new_field_value=tracker.get_slot('new_field_value')
        for a in action_items:
            if field.lower() not in list(a.keys()):
                dispatcher.utter_message("Please enter a valid field")
                return[SlotSet(key='field',value=None)]
            if field.lower()=="owners":
                owners_ref=["sanika","aayush","ayushman","neeshi","samarth","kanik","amit","ravin","tanmay","safari"]
                owners=new_field_value
                owners=re.sub(' and ', "and", owners)
                #owners=re.sub(',', " ", owners)
                #owners=re.sub('  ', " ", owners)
                print(owners)
                owner_list=owners.split("and")
                for owner in owner_list:
                    index=owner_list.index(owner)
                    owner=re.sub(' ', "", owner)
                    print(owner)
                    matches=get_close_matches(owner,owners_ref,n=1,cutoff=0)
                    print(matches)
                    owner_list[index]=matches[0]
                a[field].clear()
                a[field]=owner_list
                #return[]
            if a['id']==str(id):
                a[field.lower()]=str(new_field_value)
                dispatcher.utter_message("Action Item edited successfully!")
                #return[]

        #-----------------------API--------------------------------#
        meeting_id=282
        speaker="Sanika Padegaonkar"
        res = req.get(url = url+"api/v1/notes/fetch/group/notes/by/id/", params={'group_note_id': meeting_id}, headers=headers)  

        if(res.status_code == 200):
            data = res.json()["data"]["data"]
            talking_points_=data["talking_points"]
            action_items_=data["action_items"]
        else:
            dispatcher.utter_message("API returned an incorrect status code")
            print("Couldn't fetch group data, Error code: ", res.status_code)
            return []
        
        #Getting all users
        res = req.get(url = url+"api/v1/user/get/all/users", headers=headers)  

        if(res.status_code == 200):
            users = res.json()["data"]
        else:
            dispatcher.utter_message("API returned an incorrect status code")
            print("Couldn't fetch group data, Error code: ", res.status_code)
            return []

        users_lower=[user["name"].lower() for user in users]

        item=action_items_[int(id)-1]
        assignee_id=item["assignee_id"]

        
        if field.lower()=="owners" or field.lower()=="owner":
            #Deleting old Owners
            for assignee in assignee_id:
                if assignee["role"]=="owner":
                    assignee_id.remove(assignee)
 
            #Adding new Owners
            for owner in owner_list:
                info={}
                if owner.lower() in users_lower:
                    for user in users:
                        if user["name"].lower()==owner.lower():
                            info["name"]=owner
                            info["role"]="owner"
                            info["color"]=user["color"]
                            info["email_id"]=user["email_id"]
                            info["dark_color"]=user["dark_color"]
                            info["short_name"]=user["short_name"]
                            info["user_id"]=user["user_alias_id"]
                else:
                    dispatcher.utter_message("Please enter the name of the user as mentioned in the database")
                    return[]
                assignee_id.append(info)
            item["assignee_id"]=assignee_id


        elif field.lower()=="deadline":
            time=tracker.get_slot('time')
            deadline={}
            if(type(time) is dict):
                if (time["to"]!=None):
                    deadline["to"] = dt.strptime(str(time["to"]), "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%dT%H:%M:%S.%f%z")
                if (time["from"]!=None):
                    deadline["from"] = dt.strptime(str(time["from"]), "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%dT%H:%M:%S.%f%z")
                item["deadline"]=deadline
                return []
            elif(time!=None):
                time=dt.strptime(time, "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%dT%H:%M:%S.%f%z")
                item["deadline"]=time
                return []
            else:
                item["deadline"]="None"
                return []

        elif field.lower()=="text":
            item["title"]=new_field_value

        now=dt.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        for user in users:
            if user["name"].lower()==speaker.lower():
                updated_by=user["user_alias_id"]

        item["updated_by"]=updated_by
        item["updated_at"]=now

        action_items_[int(id)-1]=item

        updated_notes={"notes_id":meeting_id, "talking_points":talking_points_,"action_items": action_items_}

        upload = req.post(url=url+"api/v1/notes/group/note/data/update/", json=updated_notes, headers=headers)
        if(upload.status_code == 200):
            print("Upload Successful")
        else:
            print("Upload Unsuccessful", upload.status_code)

        dispatcher.utter_message("Please enter a valid ID and try again")
        #return[SlotSet(key='action_item_id_modify',value=None)]
        return[{"action_item_id_modify":None}]
        

class DeleteActionItem(Action):
    def name(self) -> Text:
        return 'action_delete_action_item'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        id=tracker.get_slot('id')
        for a in action_items:
            if a['id']==str(id):
                action_items.remove(a)
                dispatcher.utter_message("Action Item deleted successfully!")
                #return[]

        #-------------------------------API---------------------------------------

        meeting_id=282
        speaker="Sanika Padegaonkar"
        res = req.get(url = url+"api/v1/notes/fetch/group/notes/by/id/", params={'group_note_id': meeting_id}, headers=headers)  

        if(res.status_code == 200):
            data = res.json()["data"]["data"]
            talking_points_=data["talking_points"]
            action_items_=data["action_items"]
            del action_items_[int(id)-1]    
        else:
            print("Couldn't fetch group data, Error code: ", res.status_code)

        updated_notes={"notes_id":meeting_id, "talking_points":talking_points_,"action_items": action_items_}

        upload = req.post(url=url+"api/v1/notes/group/note/data/update/", json=updated_notes, headers=headers)
        if(upload.status_code == 200):
            print("Upload Successful")
        else:
            print("Upload Unsuccessful", upload.status_code)

        dispatcher.utter_message("Please enter a valid ID")
        #return[SlotSet(key='id',value=None)]
        return[{"id":None}]

#Action Get New Field Values
#Action Get New Talking Point Values
class ValidateActionItemForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_actionitem_form"

    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        required_slots = ["action_item_id"]+slots_mapped_in_domain 
        return required_slots

    async def extract_action_item_id(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        last_ind=len(action_items)-1
        id=int(action_items[last_ind]['id'])+1
        dispatcher.utter_message("Action Item id updated!")

        return [{"action_item_id": id}]
        #return [SlotSet(key="action_item_id",value=id)]


class ValidateTalkingPointForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_talking_point_form"

    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        required_slots = ["talking_point_id"]+slots_mapped_in_domain 
        return required_slots

    async def extract_talking_point_id(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        last_ind=len(action_items)-1
        id=int(action_items[last_ind]['id'])+1
        dispatcher.utter_message("Talking Point id updated!")

        return [{"talking_point_id": id}]

class ActionValidateOwner(Action):
    def name(self) -> Text:
        return 'action_validate_owner'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #owner=next(tracker.get_latest_entity_values("owner"), None)
        owners=tracker.get_slot("owner")
        owners=["sanika","aayush","ayushman","neeshi","samarth","kanik","amit","ravin","tanmay"]
        matches=get_close_matches(owners,owner)
        opts="Did you mean any of these? :"
        for owner in owners:
            if owner.lower() not in owners:
                matches=get_close_matches(owners,owner)
        for match in matches:
            opts=opts+" "+str(match)
        dispatcher.utter_message(opts)
        #return [{"action_item_id": id}]
        return []
