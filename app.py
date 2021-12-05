from flask import Flask, request, jsonify, Response
from model_process.regression_model_2 import predict
from flask_cors import CORS, cross_origin
import pandas as pd
from firebase.firebase import db;
from firebase_admin import firestore
from datetime import datetime
import time
import threading
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

ENV = 'dev'

if ENV == 'dev':
    app.debug = True

@app.before_first_request
def execute_this():
    threading.Thread(target=interval).start()

def get_realtime_data():
    provinces = db.collection(u'provinces').get()
    province_map = {
        u'Cả nước' : 0
    }
    
    for province in provinces:
        extract_province = province.to_dict()
        province_map[extract_province['label']] = extract_province['value']
    
    URL = "https://vi.wikipedia.org/wiki/B%E1%BA%A3n_m%E1%BA%ABu:D%E1%BB%AF_li%E1%BB%87u_%C4%91%E1%BA%A1i_d%E1%BB%8Bch_COVID-19_t%E1%BA%A1i_Vi%E1%BB%87t_Nam"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find_all(class_="tpl-blanktable")[0]
   
    trs = table.find_all("tr", class_= None)
    tr_top = table.find_all("tr", class_="sorttop")[0]
    
    tds_of_tf_top = tr_top.find_all("td")
    top_infected_case = int(tds_of_tf_top[1]["data-sort-value"])
    top_case_of_death = int(tds_of_tf_top[2]["data-sort-value"])
    top_new_cases = int(tds_of_tf_top[3]["data-sort-value"])
    top_total_vaccinations = int(tds_of_tf_top[4]["data-sort-value"])
    top_nose_1 = int(tds_of_tf_top[5]["data-sort-value"])
    # tds_of_tf_top[6]["data-sort-value"]
    top_nose_2 = int(tds_of_tf_top[7]["data-sort-value"])
    # tds_of_tf_top[8]["data-sort-value"]
    top_num_of_dose_delivery = int(tds_of_tf_top[9]["data-sort-value"])
    top_population = int(tds_of_tf_top[10]["data-sort-value"])
    top_num_of_dose_per_100 = float(tds_of_tf_top[11]["data-sort-value"])
    
    datetime_object_string = datetime.today().strftime('%Y-%m-%d')
    top_province_id = 0
    top_doc_ref = db.collection(u'data').document(datetime_object_string + "_" + top_province_id.__str__())
    if top_doc_ref.get().exists == False:
        top_doc_ref.set({
            u'province_id' : top_province_id,
            u'date': datetime_object_string,
            u'confirmed': top_infected_case,
            u'case_of_deatch': top_case_of_death,
            u'new_cases': top_new_cases,
            u'total_vaccinations': top_total_vaccinations,
            u'nose_1': top_nose_1,
            u'nose_2': top_nose_2,
            u'num_of_dose_delivery': top_num_of_dose_delivery,
            u'population': top_population,
            u'num_of_dose_per_100': top_num_of_dose_per_100
        })
    
    for tr in trs:
        tds = tr.find_all("td")
        print("=================")
        print(tds[0].text)
        infected_case = int(tds[1]["data-sort-value"])
        case_of_death = int(tds[2]["data-sort-value"])
        new_cases = int(tds[3]["data-sort-value"])
        total_vaccinations = int(tds[4]["data-sort-value"])
        nose_1 = int(tds[5]["data-sort-value"])
        # tds[6]["data-sort-value"]
        nose_2 = int(tds[7]["data-sort-value"])
        # tds[8]["data-sort-value"]
        num_of_dose_delivery = int(tds[9]["data-sort-value"])
        population = int(tds[10]["data-sort-value"])
        num_of_dose_per_100 = float(tds[11]["data-sort-value"])
        province_id = province_map[tds[0].text]
        doc_ref = db.collection(u'data').document(datetime_object_string + "_" + province_id.__str__())
        if doc_ref.get().exists == False:
            doc_ref.set({
                u'province_id' : province_id,
                u'date': datetime_object_string,
                u'confirmed': infected_case,
                u'case_of_deatch': case_of_death,
                u'new_cases': new_cases,
                u'total_vaccinations': total_vaccinations,
                u'nose_1': nose_1,
                u'nose_2': nose_2,
                u'num_of_dose_delivery': num_of_dose_delivery,
                u'population': population,
                u'num_of_dose_per_100': num_of_dose_per_100
            })
       
    date_ref =  db.collection(u'crawl_date').document(datetime_object_string)
    if date_ref.get().exists == False:
        db.collection(u'crawl_date').document(datetime_object_string).set({u'value': True})
    
# @app.route('/fetch-data', methods=['POST', 'GET'])
# def fetch_data():
#     df = pd.read_csv("data/VN-covid19.csv", on_bad_lines='skip')
        
#     dates = df['ObservationDate'].tolist()
#     confirmed = df['Confirmed'].tolist()
    
#     for i in range(len(dates)):
#         datetime_object = datetime.strptime(dates[i] + "-2021",'%d-%b-%Y').date()
#         province_id = 0
#         doc_ref = db.collection(u'data').document(datetime_object.__str__() + "_" + province_id.__str__())
#         if doc_ref.get().exists:
#             continue
#         else:
#             doc_ref.set({
#                 u'province_id' : province_id,
#                 u'date': datetime_object.__str__(),
#                 u'confirmed': confirmed[i]
#             })
        
        
#     return jsonify({"code": 1})

# @app.route('/fetch-province', methods=['GET', 'POST'])
# def get_province():
#     URL = "https://vi.wikipedia.org/wiki/B%E1%BA%A3n_m%E1%BA%ABu:D%E1%BB%AF_li%E1%BB%87u_%C4%91%E1%BA%A1i_d%E1%BB%8Bch_COVID-19_t%E1%BA%A1i_Vi%E1%BB%87t_Nam"
#     page = requests.get(URL)
#     soup = BeautifulSoup(page.content, "html.parser")
#     table = soup.find_all(class_="tpl-blanktable")[0]
   
#     trs = table.find_all("tr", class_= None)
#     tr_top = table.find_all("tr", class_="sorttop")[0]
    
#     i = 0
    
#     db.collection(u'provinces').document(tr_top.text).set({u'value': i, u'label': tr_top.text})
#     i += 1
    
#     for tr in trs:
#         tds = tr.find_all("td")
#         print(tds[0].text)
#         db.collection(u'provinces').document(tds[0].text).set({u'value': i, u'label': tds[0].text})
#         i += 1

#     return "DONE"

def extract_firebase_item(item):
    return item.to_dict()

def sort_key(item):
    return item['date']

@app.route("/get-province", methods=['GET', 'POST'])
def get_province():
    provinces = db.collection(u'provinces').get()
    return jsonify(list(map(extract_firebase_item, provinces)))

@app.route('/get-data', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        province_id = request.form['province_id']
        next_days_num = request.form['next_days_num']
        if not province_id: 
            return jsonify({"code": 1})
        else:
            db_ref = db.collection(u'data').where(u'province_id', u'==', int(province_id)).order_by(u'date', direction=firestore.Query.DESCENDING)
            data_items = list(map(extract_firebase_item,db_ref.get()))
            data_items.sort(key=sort_key)
            df = pd.DataFrame()
            date_data = []
            confirm_data = []
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
        get_realtime_data()
        time.sleep(24* 60 * 60)
        
def start_app():
    threading.Thread(target=app.run).start()  
    

if __name__ == '__main__':
    app.debug = True
    app.run()
    

