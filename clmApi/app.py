import flask
import os
import numpy as np
import math
from geopy.distance import great_circle
from flask import jsonify, request, json

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/greetUser', methods=['GET'])
def home():
    """
    Return greeting message to world!
    """
    return  jsonify({"success": "true", "message": "Hello world!"})

@app.route('/uploadSession', methods=['POST'])
def upload():
    """
    upload session files
    """
    #read the POST body from request 
    sessionReqObj =  request.json
    #check if empty request body
    if not sessionReqObj:
        return jsonify({"success": "false", "message": "empty request body"})
    #read the session id from the post body 
    fileId = sessionReqObj.get('id')
    #get current path, as we need to create session<<ID>>.json in current path
    currentPath = os.getcwd()
    try:
        #check if,<<ID>> must be positive int
        if(isinstance(fileId,int) and fileId > 0):
            #check if dir , sessionFiles exists if not then create
            if not os.path.exists('sessionFiles'):
                os.makedirs('sessionFiles')
            #prep the path
            sessfilePath=os.path.join(currentPath,'sessionFiles',f'session{fileId}.json')
            #open file for writing and dump the json object
            with open(sessfilePath,"w") as newSessionFile:
                json.dump(sessionReqObj,newSessionFile)
            # return success    
            return jsonify({"success": "true"})  
        else:
            #return appropriate error
            return jsonify({"success": "false", "message": "Invalid Id in request."})
    except Exception as e:
        #capture any exception
        return jsonify({"success": "false", "message": e})
   
@app.route('/sessionSpeedVariance/<int:fileId>', methods=['GET'])
def speedVariance(fileId):
    """
    Calculate the speed variance for session
    """
    try:
        #get current path
        currentPath = os.getcwd()
        #prep the session file path. This time we are get fileId from the request query string
        sessfilePath=os.path.join(currentPath,'sessionFiles',f'session{fileId}.json')
        #start reading file
        with open(sessfilePath, 'r') as sessFP_reader:
            #convert the file in content in json
            convertedJson = json.load(sessFP_reader)
            #using numPy lib for calculating the variance and format the output by rounding the data
            nArr = np.array([i["speed"] for i in convertedJson["data"]])
        return jsonify({"success": "true", "message": round(np.var(nArr),2)})
    #exception handling - file not found
    except FileNotFoundError:
        return jsonify({"success": "false", "message": 'File not found'})
    #exception handling -for empty or corrupt file
    except ValueError:
        return jsonify({"success": "false", "message": 'File content is corrupted'})    
    except Exception as e:
        return jsonify({"success": "false", "message": e})    

@app.route('/sessionDistance/<int:fileId>', methods=['GET'])
def sessionDistance(fileId):
    """
    Calculate the session distance travelled
    """
    try:
        currentPath = os.getcwd()
        sessfilePath=os.path.join(currentPath,'sessionFiles',f'session{fileId}.json')
        #read session<ID>.json file
        with open(sessfilePath, 'r') as json_reader:
            #load json from file
            convertedJson = json.load(json_reader)
            nArr = np.array([i["pos"] for i in convertedJson["data"]])
            #lamda function to calculate distance between two coordinate using geoPy 
            # library and returning in meters
            #to install geoPy use pip3 install geopy
            differenceBt2pt = lambda p1, p2: (great_circle(p1,p2).km * 1000) 
            #call lamda function over current and next row , 
            #using zip function to create tuples for great_circle function
            diffs = (differenceBt2pt(p1, p2) for p1, p2 in zip (nArr, nArr[1:]))
            #do a sum
            path=sum(diffs)
        return jsonify({"success": "true", "message": round(path,1)})
    except FileNotFoundError:
        return jsonify({"success": "false", "message": 'File not found'})
    except ValueError:
        return jsonify({"success": "false", "message": 'File content is corrupted'})
    except Exception as e:
        return jsonify({"success": "false", "message": e}) 

@app.errorhandler(500)
def error_500(exception):
    return jsonify({"error": str(exception)}), 500, {'Content-Type': 'application/json'}

@app.errorhandler(405)
def error_405(exception):
    return jsonify({"error": str(exception)}), 405, {'Content-Type': 'application/json'}


@app.errorhandler(404)
def error_404(exception):
    return jsonify({"error": str(exception)}), 404, {'Content-Type': 'application/json'}

@app.errorhandler(400)
def error_400(exception):
    return jsonify({"error": str(exception)}), 400, {'Content-Type': 'application/json'}


if __name__ == '__main__':
    app.run(host="localhost", port=3000, debug=True)