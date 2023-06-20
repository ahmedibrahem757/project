import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import keras
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense
from keras.utils import to_categorical
from sklearn import metrics
from flask import Flask
import tensorflow as tfbase
app = Flask(__name__)
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

@app.route('/process_data')
def process_data():
    # Get data from Firebase
    # Use a service account.
    cred = credentials.Certificate('./project.json')

    # check if the app has already been initialized
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    
    
    #read
    
    users_ref = db.collection('Data')
    docs = users_ref.stream()
    data_list = []
    for doc in docs:
        doc_data = doc.to_dict()
        data_list.append(doc_data)
        print(data_list)

    # create a new list with only the values from each dictionary
    values_list = [list(data_dict.values()) for data_dict in data_list]

    # convert
    my_array = np.array(values_list)

    #PREDICT
    from tensorflow.keras.models import load_model

    model = tf.keras.models.load_model('model.h5')
    
    results = []

    for i in range(len(my_array)):
        result = np.argmax(model.predict(my_array[i]))
        results.append(result)
    #convert
    results_array = np.array(results)
    output = results_array.T
    
    #element_counts
    element_counts = {}
    for element in output:
        if element in element_counts:
            element_counts[element] += 1
        else:
            element_counts[element] = 1

    # Find the maximum count
    max_count = max(element_counts.values())

    # Create a new array with only the most common elements
    output_array = [element for element in output if element_counts[element] == max_count]

    #///////////////////////////

    dic = {
        0:' أشعر ',
        1:' أنا ',
        2:' مرحبا ',
        3:' لاحقا ',
        4:' كيف حالك ',
        5:' بخير ',
        6:' اليوم ',
        7:' انا سعيد بلقائك ',
        8:' حزين ',
        9:' اراك ',
        10:' اتصل بي ',
        11:' احبك ',
        12:' مبروك ',
        13:' ساعدني  ',
        15:'  اكرهك ',
        14:' اكيد  ',
        16:' جعان  ',
        17:' وداعا  ',
        18:'  سعيد ',
        19:' شكرا  ',
    }

    sentence = ''
    prev_element = None
    for element in output_array:
        if element != prev_element:
            sentence += dic[element]
            prev_element = element

    #create k,v

    my_dict = {'output': [sentence]}
    data = [my_dict]
    
    #output to firebase
    for record in data:
        # convert any list values to strings
        for key, value in record.items():
            if isinstance(value, list):
                record[key] = ', '.join(value)

        # set the document in Firestore
        doc_ref = db.collection(u'Out').document(record['output'])
        doc_ref.set(record)
    return my_dict  


    #/////////////////////////////////////////////////////////////
if __name__ == '__main__':
    app.run(debug=True, port=9000)
