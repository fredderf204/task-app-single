import os
import flask
import urllib.parse
from flask import request, jsonify
from werkzeug.exceptions import HTTPException

app = flask.Flask(__name__)
app.config["DEBUG"] = False

mongoacct = urllib.parse.quote_plus(os.environ.get('mongoacct'))
mongodb  = urllib.parse.quote_plus(os.environ.get('mongodb'))
mongocol  = urllib.parse.quote_plus(os.environ.get('mongocol'))
mongopwd  = urllib.parse.quote_plus(os.environ.get('mongopwd'))
mongoString = f'mongodb://{mongoacct}:{mongopwd}@{mongoacct}.documents.azure.com:10255/?ssl=true&replicaSet=globaldb'
print (mongoString)

#### Helper Functions ####
def getAllTasks(tenantp):
    from pymongo import MongoClient
    from bson.json_util import dumps
    client = MongoClient(mongoString)
    db = client[mongodb]
    col = db[mongocol]
    results = dumps(col.find( {"tenant": tenantp} ))
    return results

def getTaskByID(tenantp,docid):
    from pymongo import MongoClient
    from bson.json_util import dumps
    client = MongoClient(mongoString)
    db = client[mongodb]
    col = db[mongocol]
    from bson.objectid import ObjectId
    results = dumps(col.find_one( {"_id": ObjectId(docid)} ))
    return results

def createNewTask(tenantp,req_bodyjp):
    from pymongo import MongoClient
    from bson.json_util import dumps
    client = MongoClient(mongoString)
    db = client[mongodb]
    col = db[mongocol]
    if 'duedate' in req_bodyjp:
        duedate = str(req_bodyjp['duedate'])
    else:
        duedate = ""
    doc = {
        "completed" : False,
        "description" : req_bodyjp['description'],
        "duedate" : duedate,
        "title" : req_bodyjp['title'],
        "tenant" : tenantp,   
    }
    try:
        col.insert_one(doc).inserted_id
        return "successful"
    except Exception as e:
        errmessage = f"insert failed {e}"
        return errmessage

def updateTask(tenantp,req_bodyjp,docid):
    from pymongo import MongoClient
    from bson.json_util import dumps
    client = MongoClient(mongoString)
    db = client[mongodb]
    col = db[mongocol]
    if 'duedate' in req_bodyjp:
        duedate = str(req_bodyjp['duedate'])
    else:
        duedate = ""
    from bson.objectid import ObjectId
    try:
        col.update_one({"_id": ObjectId(docid)},{
            '$set': {
                "description" : req_bodyjp['description'],
                "duedate" : duedate,
                "title" : req_bodyjp['title'],
            }
        }, upsert=False)
        return "successful"
    except Exception as e:
        errmessage = f"insert failed {e}"
        return errmessage

def deleteTaskByID(tenantp,docid):
    from pymongo import MongoClient
    from bson.json_util import dumps
    client = MongoClient(mongoString)
    db = client[mongodb]
    col = db[mongocol]
    from bson.objectid import ObjectId
    results = col.delete_one( {"_id": ObjectId(docid)} )
    if results.deleted_count == 1:
        reply = "delete successful"
    if results.deleted_count == 0:
        reply = "no document found"
    else:
        reply = "something werid happened"
    return reply

@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify(error=str(e)), code

#### Routing ####
@app.route('/task/all', methods=['GET'])
def getTask_all():
    if request.headers['tenant']:
        tenant = request.headers.get('tenant')
        resp = getAllTasks(tenant)
        return resp, 200, {'Content-Type': 'application/json'}
    else :
        return "Error: No tenant field provided", 400, {'Content-Type': 'application/json'}

@app.route('/task', methods=['GET'])
def getTask_byid():
    if 'id' in request.args and request.headers['tenant']:
        id = request.args['id']
        tenant = request.headers.get('tenant')
        resp = getTaskByID(tenant,id)
        return resp, 200, {'Content-Type': 'application/json'}
    else:
        return "Error: No id or tenant field provided", 400, {'Content-Type': 'application/json'}

@app.route('/task', methods=['POST'])
def createTask():
    tenant = request.headers.get('tenant')
    if not tenant:
        return "Error: No tenant field provided", 400, {'Content-Type': 'application/json'}
    title = request.form.get('title')
    if not title:
        return "Error: No title field provided", 400, {'Content-Type': 'application/json'}
    description = request.form.get('description')
    if not description:
        return "Error: No description field provided", 400, {'Content-Type': 'application/json'}
    resp = createNewTask(tenant,request.form)
    return resp, 201, {'Content-Type': 'application/json'}

@app.route('/task', methods=['PUT'])
def updateTask_byid():
    tenant = request.headers.get('tenant')
    if 'id' in request.args and tenant:
        id = request.args['id']
        resp = updateTask(tenant,request.form,id)
        return resp, 200, {'Content-Type': 'application/json'}
    else:
        return "Error: No tenant or id field provided", 400, {'Content-Type': 'application/json'}

@app.route('/task', methods=['DELETE'])
def deleteTask_byid():
    tenant = request.headers.get('tenant')
    if 'id' in request.args and tenant:
        id = request.args['id']
        resp = deleteTaskByID(tenant,id)
        return resp, 200, {'Content-Type': 'application/json'}
    else:
        return "Error: No tenant or id field provided", 400, {'Content-Type': 'application/json'}

@app.route('/healthz', methods=['GET'])
def healthz():
        return "Iamok", 200, {'Content-Type': 'application/json'}

#app.run()