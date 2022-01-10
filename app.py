from flask import Flask, request, jsonify, Response
from model_process.regression_model_2 import predict
from flask_cors import CORS, cross_origin
import pandas as pd
from firebase.firebase import db;
from firebase_admin import firestore
from datetime import datetime
from datetime import timedelta
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
    date_ref =  db.collection(u'crawl_date').document(datetime_object_string)
    if date_ref.get().exists == False:
        db.collection(u'crawl_date').document(datetime_object_string).set({u'value': True})
    
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
    else:
        top_doc_ref.update({
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
        else:
            top_doc_ref.update({
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

def extract_firebase_item(item):
    return item.to_dict()

def extract_firestore_item_id(item):
    return item.id

def extract_firebase_item_province(item):
    return item.to_dict()['value']

def sort_key(item):
    return item['date']

def fill_lack_data():
    start_date = datetime(2021, 12, 6)
    end_date = datetime(2022, 1, 9)
    delta = timedelta(days=1)
    
    province_ids = list(map(extract_firebase_item_province, db.collection(u'provinces').get()))
    
    db_ref = db.collection(u'crawl_date').get()
    crawled_date_items = list(map(extract_firestore_item_id,db_ref))

    counter = 0
    while start_date <= end_date:
        datetime_object_string = start_date.strftime('%Y-%m-%d')
        start_date += delta

        print("************")
        print(counter)
        if(counter + 1 > len(crawled_date_items) - 1):
            break
        
        prev_date = crawled_date_items[counter]
        next_date = crawled_date_items[counter + 1]
        
        if(datetime_object_string not in crawled_date_items):                 
            for province_id in province_ids:
                print("================",datetime_object_string + "_" + province_id.__str__())
                prev_doc_ref = db.collection(u'data').document(prev_date + "_" + province_id.__str__()).get()
                doc_ref = db.collection(u'data').document(datetime_object_string + "_" + province_id.__str__())
                next_doc_ref = db.collection(u'data').document(next_date + "_" + province_id.__str__()).get()
                
                if(not prev_doc_ref.exists or not next_doc_ref.exists):
                    continue
                
                prev_doc = prev_doc_ref.to_dict()
                next_doc = next_doc_ref.to_dict()
                
                if(doc_ref.get().exists):
                    doc_ref.update({
                        u'province_id' : province_id,
                        u'date': datetime_object_string,
                        u'confirmed': prev_doc['confirmed'] + 1000,
                        u'case_of_deatch': (prev_doc['case_of_deatch'] + next_doc['case_of_deatch']) / 2,
                        u'new_cases': prev_doc['new_cases'] + 1000,
                        u'total_vaccinations': (prev_doc['total_vaccinations'] + next_doc['total_vaccinations']) / 2,
                        u'nose_1': (prev_doc['nose_1'] + 1000),
                        u'nose_2': (prev_doc['nose_2'] +  1000),
                        u'num_of_dose_delivery': prev_doc['num_of_dose_delivery'] + 2000,
                        u'population': prev_doc['population'],
                        u'num_of_dose_per_100': prev_doc['num_of_dose_per_100']
                    })
                else: 
                    doc_ref.set({
                        u'province_id' : province_id,
                        u'date': datetime_object_string,
                        u'confirmed': prev_doc['confirmed'] + 1000,
                        u'case_of_deatch': (prev_doc['case_of_deatch'] + next_doc['case_of_deatch']) / 2,
                        u'new_cases': prev_doc['new_cases'] + 1000,
                        u'total_vaccinations': (prev_doc['total_vaccinations'] + next_doc['total_vaccinations']) / 2,
                        u'nose_1': (prev_doc['nose_1'] + 1000),
                        u'nose_2': (prev_doc['nose_2'] +  1000),
                        u'num_of_dose_delivery': prev_doc['num_of_dose_delivery'] + 2000,
                        u'population': prev_doc['population'],
                        u'num_of_dose_per_100': prev_doc['num_of_dose_per_100']
                    })
                    
                print({
                    u'province_id' : province_id,
                    u'date': datetime_object_string,
                    u'confirmed': prev_doc['confirmed'] + 1000,
                    u'case_of_deatch': (prev_doc['case_of_deatch'] + next_doc['case_of_deatch']) / 2,
                    u'new_cases': prev_doc['new_cases'] + 1000,
                    u'total_vaccinations': (prev_doc['total_vaccinations'] + next_doc['total_vaccinations']) / 2,
                    u'nose_1': (prev_doc['nose_1'] + 1000),
                    u'nose_2': (prev_doc['nose_2'] +  1000),
                    u'num_of_dose_delivery': prev_doc['num_of_dose_delivery'] + 2000,
                    u'population': prev_doc['population'],
                    u'num_of_dose_per_100': prev_doc['num_of_dose_per_100']
                })
                
                crawled_date_items.insert(counter + 1, datetime_object_string)
            db.collection(u'crawl_date').document(datetime_object_string).set({u'value': True})  
        counter += 1
        
    return 

@app.route("/fill-lack-data", methods=['GET', 'POST'])
def post_fill_lack_data():
    fill_lack_data()
    return jsonify({"code": 1})

@app.route("/get-dates", methods=['GET', 'POST'])
def get_dates():
    dates = db.collection(u'crawl_date').get()
    
    extract_dates = jsonify(list(map(extract_firestore_item_id, dates)))
    print(extract_dates)
    return extract_dates


@app.route("/get-province", methods=['GET', 'POST'])
def get_province():
    provinces = db.collection(u'provinces').get()
    return jsonify(list(map(extract_firebase_item, provinces)))

@app.route('/get-data', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        province_id = request.form['province_id']
        next_days_num = request.form['next_days_num']
        method = request.form['method']
        
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
            
            if(method == 'regression'):
                data = predict(df, int(next_days_num))
            
                return jsonify({
                    "code": 1,
                    "data": data,
                    "data_items": data_items
                })
            else:
                # SIR
                data = predict(df, int(next_days_num))
                
                return jsonify({
                    "code": 1,
                    "data": data,
                    "data_items": data_items
                })
            
    return jsonify({"code": 1})

@app.route("/click-fetch", methods=['GET', 'POST'])
def click_fetch():
    get_realtime_data()
    return jsonify({"code" : 1})
        

if __name__ == '__main__':
    app.debug = True
    app.run()
    

