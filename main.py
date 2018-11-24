import time
import random
import string
import os
import json
from threading import Thread
from requests import get
from flask import Flask, Response, request, jsonify


app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

def givetime():
    for i in range(10):
        yield "data: "+ str(i) +"\n\n"
        time.sleep(1)
    
@app.route("/subscribe")
def dosub():
    print("yey")
    r = Response(givetime(), mimetype='text/event-stream')
    r.headers.add("Access-Control-Allow-Origin", "*")
    return r

@app.route("/primaryKeyParse", methods=['POST'])
def primaryKeyParse():
    formdata = request.form.to_dict()
    targetFolder = generate_random_name()
    
    r = jsonify({"status" : "OK", "targetFolder" : targetFolder, "total": int(formdata['to']) - int(formdata['from']) + 1})
    r.headers.add("Access-Control-Allow-Origin", "*")
    #  start scrape in another thread
    t = Thread(target=scrape, args=(formdata, targetFolder))
    t.start()

    return r

@app.route("/checkProgress/<targetfolder>/<total>", methods=['GET'])
def progressCheck(targetfolder, total):
    r = Response(doCount(targetfolder, total), mimetype='text/event-stream')
    r.headers.add("Access-Control-Allow-Origin", "*")
    return r

    
def doCount(targetfolder, total):
    try:
        progress = len(os.listdir("data/" + targetfolder)) / int(total)
    except FileNotFoundError:
        print("Error")
        yield "data: {}\n\n".format("error")
    else: 
        while(progress != 1):
            print(progress)
            progress = len(os.listdir("data/" + targetfolder)) / int(total)
            time.sleep(1)
            yield "data: {}\n\n".format(int(progress * 100))



def scrape(formdata, targetFolder):
    folderpath = "data/" + targetFolder
    os.mkdir(folderpath)
    for item in range(int(formdata['from']), int(formdata['to'])):
        result = get(formdata['url'].format(item))
        with open(folderpath + "/" + str(item) + ".html", 'wb') as fout:
            fout.write(result.content)

def generate_random_name(strlen=10):
    name = "".join([string.hexdigits[random.randrange(0, len(string.hexdigits))] for item in range(strlen)])
    return name

if __name__ == '__main__':
    app.run()