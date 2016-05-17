#!/usr/bin/python

from flask import Flask, request, jsonify
import db_model
from datetime import datetime, timedelta

#import importlib.machinery
#db_model = importlib.machinery.SourceFileLoader('db_model', '../').load_module()

app = Flask(__name__)
app.config.update({'DEBUG': True})


db_model.init_db()

@app.route('/sensors/<sensor_name>')
def hello(sensor_name):
    start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d %H:%M:%S') if 'start_date' in request.args else None

    print('Received date: ', start_date)

    end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d %H:%M:%S') if 'end_date' in request.args else None

    res = db_model.get_sensor_data(name=sensor_name, start=start_date, end=end_date)
    
    return jsonify({'data': [e.to_dict() for e in res]})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
