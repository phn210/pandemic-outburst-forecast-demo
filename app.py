from flask import Flask, request, jsonify, Response
from model_process.regression_model_2 import predict
from flask_cors import CORS, cross_origin
import pandas as pd
from firebase.firebase import db;
from firebase_admin import firestore
from datetime import datetime
import time
from multiprocessing import Process, Lock
import threading


app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

ENV = 'dev'

if ENV == 'dev':
    app.debug = True

@app.before_first_request
def execute_this():
    threading.Thread(target=interval).start()
    
@app.route("/realtime-data", methods=['POST', 'GET'])
def get_realtime_data():
    return "GET DATA REALTIME"
    
@app.route('/fetch-data', methods=['POST', 'GET'])
def fetch_data():
    df = pd.read_csv("data/VN-covid19.csv", on_bad_lines='skip')
        
    dates = df['ObservationDate'].tolist()
    confirmed = df['Confirmed'].tolist()
    
    for i in range(len(dates)):
        datetime_object = datetime.strptime(dates[i] + "-2021",'%d-%b-%Y').date()
        province_id = 0
        doc_ref = db.collection(u'data').document(datetime_object.__str__() + "_" + province_id.__str__())
        if doc_ref.get().exists:
            continue
        else:
            doc_ref.set({
                u'province_id' : province_id,
                u'date': datetime_object.__str__(),
                u'confirmed': confirmed[i]
            })
        
        
    return jsonify({"code": 1})

def extract_firebase_item(item):
    return item.to_dict()

def sort_key(item):
    return item['date']

@app.route("/increase-test", methods=['GET', 'POST'])
def increase_test():
    db.collection(u'interval_count').document(u'count').set({u'value' : "test"})

@app.route('/get-data', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        province_id = request.form['province_id']
        next_days_num = request.form['next_days_num']
        if not province_id: 
            return jsonify({"code": 1})
        else:
            print(province_id)
            db_ref = db.collection(u'data').where(u'province_id', u'==', int(province_id)).order_by(u'date', direction=firestore.Query.DESCENDING)
            data_items = list(map(extract_firebase_item,db_ref.get()))
            data_items.sort(key=sort_key)
            df = pd.DataFrame()
            date_data = []
            confirm_data = []
            print(data_items)
            for item in data_items:
                extract_item = item

                date_data.append(extract_item['date'])
                confirm_data.append(extract_item['confirmed'])
            df['ObservationDate'] = date_data
            df["Confirmed"] = confirm_data
            data = predict(df, int(next_days_num))
            return jsonify({
                "code": 1,
                "data": data
            })
            
    return jsonify({"code": 1})

def interval():
    time.sleep(5)
    i = 0
    while True:
        i+=1
        print(i)
        time.sleep(24* 60 * 60)
        db.collection(u'interval_count').document(u'count').set({u'value' : i})
        
def start_app():
    threading.Thread(target=app.run).start()  
    

if __name__ == '__main__':
    app.debug = True
    app.run()
    

