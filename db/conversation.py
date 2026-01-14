import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any


from pymongo import DESCENDING
from db.mongo import get_collection

conv = get_collection("conversations")
conv.create_index([("last_conv", DESCENDING)], unique=True)


def now_utc():
    return datetime.now(timezone.utc)

def create_new_conversation_id():
    return str(uuid.uuid4())

def create_new_conversation(title=None,role=None,content=None):
    conv_id = create_new_conversation_id()
    ts = now_utc()
    doc = {
        "_id": conv_id,
        "title": title or "Untitled Conversation",
        "messages": [],
        "last_conv": ts,
    }
    if role and content:
        doc["messages"].append({"role": role, "content": content, "ts": ts})
    conv.insert_one(doc)
    return conv_id

def add_message(conv_id, role, content):
    ts = now_utc()
    res = conv.update_one({"_id": conv_id}, {
            "$push": {"messages": {"role": role, "content": content, "ts": ts}},
            "$set": {"last_interacted": ts},
        },)
    return res.matched_count == 1

def get_conversation(conv_id):
    ts = now_utc()
    doc = conv.find_one_and_update({"_id": conv_id}, {"$set": {"last_conv": ts}},
                                   return_document=True, )
    return doc

def get_all_conversations():
    cursor = conv.find({},{"title":1}).sort("_id",DESCENDING)
    return {doc["_id"]:doc["title"] for doc in cursor}



#For a new conversation (with the first message):
# conve_id = create_new_conversation(title="Intro to Deep Learning", role="user", content="What is DL?")
# add_message(conve_id, "assistant", "Answer for DL query")
# print(get_conversation(conve_id))
# print(get_all_conversations())



