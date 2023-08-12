from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
import mysql.connector

def create_app():
    db = MongoClient('mongo-service', 27017).flask

    app = Flask(__name__)

    @app.route('/')
    def home():
        return render_template('home.html')
    
    @app.route('/about')
    def about():
        return render_template('about.html')
    
    @app.route('/labs', methods = ["GET", "POST", "DELETE"])
    def labs():
        if request.method == "GET":
            lab_list = db.labs.find()
            return render_template('labs.html', lab_list=lab_list)
        if request.method == "POST":
            new_lab = dict(request.form)
            db.labs.insert_one(new_lab)
            return redirect('/labs')

    @app.get('/labs/<lab_id>')
    def get_lab(lab_id):
        selected_lab = db.labs.find_one({'_id': ObjectId(lab_id)})
        return render_template('lab.html', selected_lab=selected_lab)
    
    @app.post('/labs/<lab_id>')
    def post_lab(lab_id):
        selected_lab = db.labs.find_one({'_id': ObjectId(lab_id)})
        if request.form.get('_action') == 'EDIT':
            return render_template('update-a-lab.html', selected_lab = selected_lab)
        if request.form.get('_method') == 'DELETE':
            db.labs.delete_one({'_id': ObjectId(lab_id)})
            return redirect('/labs')
        
        if request.form.get('_method') == 'PUT':
            selected_lab = db.labs.find_one({'_id': ObjectId(lab_id)})
            db.labs.update_one({'_id': ObjectId(lab_id)}, {'$set': request.form})
            return redirect('/labs')

    @app.route('/labs/add-a-new-lab')
    def add_new_lab():
        return render_template('add-a-new-lab.html')
    
    @app.route('/devices/new')
    def new_device():
        return render_template('/devices/new.html')
    
    
    
    @app.route('/devices', methods= ['GET', 'POST'])
    def devices():
        try: 
            conn = mysql.connector.connect(user = 'root', password = 'cisco123', host = 'mysql-service', database = 'devcor2023')
            c = conn.cursor()
            query = 'CREATE DATABASE IF NOT EXISTS devcor2023'
            c.execute(query)
            conn.commit()
            query = 'CREATE TABLE IF NOT EXISTS devices (id INT AUTO_INCREMENT, hostname VARCHAR(20), ip VARCHAR(20), status VARCHAR(10), PRIMARY KEY (id)) ;'
            c.execute(query)
            conn.commit()

            if request.method == 'GET':
                query = "SELECT id, hostname, ip, status FROM devices"
                c.execute(query)
                device_list = [{'id': id, 'hostname': hostname, 'ip': ip, 'status': status} for (id, hostname, ip, status) in c]
                return render_template('/devices/devices.html', device_list = device_list)
            if request.method == 'POST':
                new_device =request.form.get('hostname'), request.form.get('ip'), request.form.get('status')
                conn = mysql.connector.connect(user = 'root', password = 'cisco123', host='mysql-service', database='devcor2023')
                c = conn.cursor()
                query = f"INSERT INTO devices (hostname, ip, status) VALUES {new_device} ;"
                c.execute(query)
                conn.commit()
                c.close()
                conn.close()
                return redirect('/devices')
        except Exception as e:
            return render_template('/error.html', error = e)
    
    @app.route('/devices/<id>', methods = ['POST'])
    def device(id):
        try:
            conn = mysql.connector.connect(user='root', password='cisco123', host='mysql-service', database='devcor2023')
            c = conn.cursor()
        except Exception as e:
            return render_template('/error.html', error = e)
        
        try:
            if request.method == 'POST' and request.form.get('_method') == 'DELETE':    
                query = f"DELETE FROM devices WHERE id={id}"
                c.execute(query)
                conn.commit()
                c.close()
                conn.close()
                return redirect('/devices')
        except Exception as e:
            return render_template('/error.html', error = e)

        try:
            if request.method == 'POST':
                query = f"UPDATE devices SET hostname='{request.form.get('hostname')}', ip='{request.form.get('ip')}', status='{request.form.get('status')}' WHERE id={id} ;"
                c.execute(query)
                conn.commit()
                c.close()
                conn.close()
                return redirect('/devices')
        except Exception as e:
            return render_template('/error.html', error = e)

    @app.route('/devices/<id>/update')
    def update_device_form(id):
        try:
            conn = mysql.connector.connect(user = 'root', password = 'cisco123', host = 'mysql-service', database = 'devcor2023')
            c = conn.cursor()
            query = f"SELECT hostname, ip, status FROM devices WHERE id = {id}"
            c.execute(query)
            device = [{'hostname': hostname, 'ip': ip, 'status': status} for hostname, ip, status in c][0]
            c.close()
            conn.close()
            return render_template('/devices/update.html', device = device, id=id)
        except Exception as e:
            return render_template('/error.html', error = e)
    return app