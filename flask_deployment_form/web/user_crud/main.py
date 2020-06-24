import pymysql
#from app import app
from tables import Results, all_data, raw_data, filter_data, volt_data, status
from db_config import mysql
from flask import Flask, flash, render_template, request, redirect, send_from_directory
from flask_socketio import SocketIO
from werkzeug import generate_password_hash, check_password_hash
import socket
import evaluation
import pandas as pd
import filtercounter as fc
import memcache
import os
import time
import analysis.querydb as qdb
import createtable as ct
import dynadb.db as dbio

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)

memc = memcache.Client(['127.0.0.1:11211'], debug=1)
accelerometers=memc.get('DF_ACCELEROMETERS')
tsm_sensors = memc.get('DF_TSM_SENSORS')
logger_mobile = memc.get('DICT_LOGGER_MOBILE_SIM_NUMS')

    
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route('/new_status')
def add_status_view():
    id = request.args.get('accel_id', default='', type=int)
    print (id)
    return render_template('add.html',
        data=[{'status':'Ok', 'stat':1}, {'status':'Use with Caution', 'stat':2}, {'status':'Special Case', 'stat':3}, {'status':'Not Ok', 'stat':4}],
        name = [{'name': 'Kate Justine Flores'},{'name': 'Brainerd Cruz'},{'name': 'Kennex Razon'}],
        accel_id = id)

@app.route('/form')
def deployment_form():
    query = "SELECT site_id, site_code FROM sites order by site_code asc"
    site = qdb.get_db_dataframe(query)
    site = site.to_dict('r')
    return render_template('form.html',
                           network = [{'network': 'Globe'},{'network': 'Smart'}],
                           logger_type = [{'logger': 'masterbox'},{'logger': 'arq'},
                                          {'logger': 'router'},{'logger': 'gateway'}],
                           site = site)
  
@app.route('/addtsm', methods=['POST'])
def tsmsensor_form():
    tsm_name = request.form['input_tsm_name'].lower()
    logger_id = request.form['input_logger_id']
    site_id = request.form['input_site_id']
    date_activated = request.form['input_date_activated']
    segment_length = request.form['input_segment_length']
    number_of_segments = request.form['input_number_of_segments']
    version = request.form['input_version']
    ids = request.form.getlist('id')
    
    print (tsm_name)
    print (logger_id)
    print (site_id)
    print (date_activated)
    print (segment_length)
    print (number_of_segments)
    print (version)
    print (ids)
    
    #insert to tsm_sensors
    query = ("INSERT INTO tsm_sensors (site_id , "
             "logger_id,tsm_name, date_activated, segment_length, "
             "number_of_segments, version) Values ('{}','{}','{}','{}','{}',"
             "'{}','{}')".format(site_id, logger_id, tsm_name,
                          date_activated, segment_length, number_of_segments, version))
    print(query)
#    qdb.execute_query(query)
    tsm_id = dbio.write(query, last_insert=True, resource = "sensor_data")[0][0]
    
    node_id = 1
    #insert to deployed_node
    query = ""
    for i in ids:
        print(node_id,i)
        query = ("INSERT INTO deployed_node (dep_id , "
                    "tsm_id, node_id, n_id, version) "
                    " Values ((SELECT dep_id FROM deployment_logs "
                    "where logger_id = '{}'),'{}','{}','{}','{}');".format(logger_id, tsm_id,
                                                                      node_id, i, version))
        
        query_ac1 = ("INSERT INTO accelerometers (tsm_id , node_id, accel_number, "
                    " ts_updated,voltage_max, voltage_min, in_use) "
                    " Values ('{}', '{}','1',NOW(),"
                    "'3.47','3.14', '1');".format(tsm_id,node_id))
        query_ac2 = ("INSERT INTO accelerometers (tsm_id , node_id, accel_number, "
                    " ts_updated,voltage_max, voltage_min, in_use) "
                    " Values ('{}', '{}','2',NOW(),"
                    "'3.47','3.14', '0');".format(tsm_id,node_id))
        
        node_id += 1
        print(query)
        dbio.write(query, resource = "sensor_data")
        dbio.write(query_ac1, resource = "sensor_data")
        dbio.write(query_ac2, resource = "sensor_data")
#        query += querystr
#    qdb.execute_query(query)
#    dbio.write(query, resource = "sensor_data")
    
    flash('added successfully!')
    return redirect('/')
   

@app.route('/add', methods=['POST'])
def add_logger():
    print ("add")
    site_id = request.form['input_site']
    logger_name = request.form['input_logger_name']
    date_installed = request.form['input_date_installed']
    date_activated = request.form['input_date_activated']
    location_description = request.form['input_location']
    latitude = request.form['input_latitude']
    longitude = request.form['input_longitude']
    network = request.form['input_network']
    mobile = request.form['input_mobile']
    logger_type = request.form['input_logger']
    
    personnels = request.form.getlist('input_personnels')
    
    try:
        request.form['has_tilt']
        has_tilt = 1
    except:
        has_tilt = 0
    
    try:
        request.form['has_rain']
        has_rain = 1
    except:
        has_rain = 0
    
    try:
        request.form['has_piezo']
        has_piezo = 1
    except:
        has_piezo = 0

    try:
        request.form['has_soms']
        has_soms = 1
    except:
        has_soms = 0
        
    
    print(site_id)
    print(logger_name)
    
    print(date_installed)
    print(date_activated)
    print(location_description)
    print(latitude)
    print(longitude)
    print(network)
    print(mobile)
    print(logger_type)
    
    print(has_tilt)
    print(has_rain)
    print(has_piezo)
    print(has_soms)
    print(personnels)
    persons = ''
    for i in personnels:
        persons = persons + i + ','
        print(i)
    persons = persons[0:len(persons)-1]
    print(persons)
    
    #insert data to loggers
    query = ("INSERT INTO loggers (site_id , "
             "logger_name, date_activated, latitude, "
             "longitude, model_id) Values ('{}','{}','{}','{}','{}',(SELECT model_id FROM logger_models "
             "where has_tilt = '{}' and has_rain = '{}' and has_piezo = '{}' and "
             "has_soms = '{}' and logger_type = '{}'))".format(site_id, logger_name,
                          date_activated, latitude, longitude, has_tilt, has_rain,has_piezo, has_soms, logger_type))
    print(query)
#    qdb.execute_query(query)
    logger_id_gsm = dbio.write(query, last_insert=True, resource = "sms_data")[0][0]
    logger_id_senslope = dbio.write(query, last_insert=True, resource = "sensor_data")[0][0]

    print ("logger_id gsm = ", logger_id_gsm)
    print ("logger_id senslope = ", logger_id_gsm)
    #get logger_id from senslopedb
#    query = ("SELECT logger_id FROM senslopedb.loggers"
#             " where logger_name = '{}' order by logger_id desc limit 1".format(logger_name))
#    print (query)
#    df_logger = qdb.get_db_dataframe(query)
#    logger_id = df_logger.logger_id.values[0]
#    print (logger_id)
    
    #insert data to deployment_logs
    query = ("INSERT INTO deployment_logs (logger_id , "
             "installation_date, location_description, "
             "network_type, personnel) Values ('{}','{}','{}','{}','{}')".format(logger_id_senslope, date_installed,
                 location_description, network, persons))
    print(query)
#    qdb.execute_query(query)
    dbio.write(query, resource = "sensor_data")
    
    #set gsm_id
    gsm_id = ''
    if network =='Globe':
        gsm_id = 4
    elif network == 'Smart':
        gsm_id = 5
    
    query = "select * from logger_mobile where sim_num = '{}' order by mobile_id desc limit 1".format(mobile)
    df_num_senslope = dbio.df_read(query, resource = 'sensor_data')
    df_num_gsm = dbio.df_read(query, resource = 'sms_data')
    
    query_insert = ("INSERT INTO logger_mobile (logger_id , "
                    "date_activated, sim_num, gsm_id)"
                    " Values ((SELECT logger_id FROM loggers"
                    " where logger_name = '{}' order by logger_id desc limit 1),'{}','{}','{}')".format(logger_name, date_activated,
                     mobile, gsm_id))

    #insert to senslopedb.logger_mobile
    if df_num_senslope.empty or logger_type in ('router', 'gateway'):
        dbio.write(query_insert, resource = "sensor_data")
    else:
        mobile_id = df_num_senslope.mobile_id.values[0]
        query_update = ("UPDATE logger_mobile SET `logger_id`=(SELECT logger_id FROM loggers"
                    " where logger_name = '{}' order by logger_id desc limit 1), "
                    "`date_activated` = '{}' WHERE `mobile_id`='{}'; ".format(logger_name, date_activated,mobile_id))
        dbio.write(query_update, resource = "sensor_data")
#    dbio.write(query_insert, resource = "sensor_data")
    
    #insert to comms_db.logger_mobile    
    if df_num_gsm.empty or logger_type in ('router', 'gateway'):
        dbio.write(query_insert, resource = "sms_data")
    else:
        mobile_id = df_num_gsm.mobile_id.values[0]
        query_update = ("UPDATE logger_mobile SET `logger_id`=(SELECT logger_id FROM loggers"
                    " where logger_name = '{}' order by logger_id desc limit 1), "
                    "`date_activated` = '{}' WHERE `mobile_id`='{}'; ".format(logger_name, date_activated,mobile_id))
        dbio.write(query_update, resource = "sms_data")
#    dbio.write(query_insert, resource = "sms_data")
        
    #for senslopedb.logger_mobile
#    if mobile in logger_mobile:
#        #update logger_mobile
#        mobile_id = logger_mobile[mobile]
#        query = ("UPDATE comms_db.logger_mobile SET `logger_id`=(SELECT logger_id FROM comms_db.loggers"
#                 " where logger_name = '{}' order by logger_id desc limit 1), "
#                 "`date_activated` = '{}' WHERE `mobile_id`='{}'; ".format(logger_name, date_activated,mobile_id))
#        print(query)
#        qdb.execute_query(query)
#        
#        query = ("UPDATE senslopedb.logger_mobile SET `logger_id`=(SELECT logger_id FROM senslopedb.loggers"
#                 " where logger_name = '{}' order by logger_id desc limit 1), "
#                 "`date_activated` = '{}' WHERE `mobile_id`='{}'; ".format(logger_name, date_activated,mobile_id))
#        print(query)
#        qdb.execute_query(query)
        
#    else:
#        #insert to logger_mobile
#
#            
#        query = ("INSERT INTO comms_db.logger_mobile (logger_id , "
#                 "date_activated, sim_num, gsm_id)"
#                 " Values ((SELECT logger_id FROM comms_db.loggers"
#                 " where logger_name = '{}' order by logger_id desc limit 1),'{}','{}','{}')".format(logger_name, date_activated,
#                     mobile, gsm_id))
#        print(query)
#        qdb.execute_query(query)
        
    if logger_type in ('arq','gateway'):
        ct.create_rain_table(logger_name)
    
    if has_soms == 1:
        ct.create_soms_table(logger_name)
        
    if has_piezo == 1:
        ct.create_piezo_table(logger_name)
    
    if has_tilt == 1 and logger_type != 'gateway':
        ct.create_tilt_table(logger_name)

        return render_template('form2.html',
                               logger_id = logger_id_senslope,
                               logger_name = logger_name,
                               date_activated = date_activated,
                               site_id = site_id)
    else:
        flash('added successfully!')
        return redirect('/')
  
@app.route('/')
def home():
    global df_summary, df_count, df_raw, df_filter, df_volt
    try:
        #get latest ts
#        conn = mysql.connect()
#        cursor = conn.cursor(pymysql.cursors.DictCursor)
#        cursor.execute
        query = ("SELECT * FROM deployment_logs "
                       "inner join loggers on loggers.logger_id = deployment_logs.logger_id "
                       "#inner join tsm_sensors on tsm_sensors.logger_id = deployment_logs.logger_id")
#        summary = cursor.fetchall()
        summary = qdb.get_db_dataframe(query)
#        print "###################################################"
#        print id
#        print row
        summary = summary.to_dict('r')
        table = Results(summary)
        table.border = True
        return render_template('summary.html', table=table)#rows.to_html(index=False))
    except Exception as e:
        print(e)
#    finally:
#        cursor.close() 
#        conn.close()

@app.route("/<name>" )
def show(name):
    global df_summary, df_raw, df_filter, df_volt
    
    print (name)
    
#    summary = df_summary[df_summary.tsm_name == name]
#    summary = summary.to_dict('r')
    
    raw = df_raw[df_raw.tsm_name == name]
    raw = raw.to_dict('r')
    raw = raw_data(raw)
    raw.border = True
    
    count = df_count[df_count.tsm_name == name]
    count = count.to_dict('r')
    count = all_data(count)
    count.border = True    
    
    filtered = df_filter[df_filter.tsm_name == name]
    filtered = filtered.to_dict('r')
    filtered = filter_data(raw)
    filtered.border = True
    
    volt = df_volt[df_volt.tsm_name == name]
    volt = volt.to_dict('r')
    volt = volt_data(raw)
    volt.border = True    
    
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT max(ts) as tsupdate FROM senslopedb.data_counter ")
    ts = cursor.fetchone()
    
    return render_template(
    'summary.html',
    table = count , tsupdate = ts['tsupdate'])

@app.route('/loading')
def update_datacounter():
    try:  

            
        fc.main()
#        time.sleep(10)

        flash('data counter updated successfully!')
        return redirect('/')
#        else:
#            return 'Error while updating status'
    except Exception as e:
        print(e)
#    finally:
#        cursor.close() 
#        conn.close()

@app.route('/status')
def view_status():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        query = ("SELECT stat_id, accelerometer_status.accel_id, tsm_name, "
                       "node_id, accel_number, ts_flag, date_identified, status, "
                       "IF(status=1,'Ok', IF(status=2,'Use with Caution', "
                       "IF(status=3,'Special Case', IF(status=4,'Not Ok', NULL)))) "
                       "as accel_status, remarks FROM accelerometer_status "
                       "inner join accelerometers on "
                       "accelerometer_status.accel_id = accelerometers.accel_id "
                       "inner join tsm_sensors on accelerometers.tsm_id = tsm_sensors.tsm_id "
                       "order by tsm_name, node_id, accel_number")
#        rows = cursor.fetchall()
        
        rows = qdb.get_db_dataframe(query)
        rows = rows.to_dict('r')
        
        table = status(rows)
        table.border = True
        return render_template('summary.html', table=table, tsupdate='')
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close()

@app.route('/edit/<int:id>')
def edit_view(id):
    print (int(id))
    try:
#        conn = mysql.connect()
#        cursor = conn.cursor(pymysql.cursors.DictCursor)
        query = "SELECT * FROM accelerometer_status WHERE stat_id={}".format(id)
#        row = cursor.fetchone()
        row = qdb.get_db_dataframe(query)
#        print "###################################################"
#        print id
#        print row
        row = row.to_dict('r')[0]
        if row:
            print ("nagana")
            print(row)
            return render_template('edit.html', row=row,
                                   data=[{'status':'Ok', 'stat':1}, {'status':'Use with Caution', 'stat':2}, {'status':'Special Case', 'stat':3}, {'status':'Not Ok', 'stat':4}],
                                   name = [{'name': 'Kate Justine Flores'},{'name': 'Brainerd Cruz'},{'name': 'Kennex Razon'}])
        else:
            return 'Error loading #{id}'.format(id=id)
    except Exception as e:
        print(e)
#    finally:
#        cursor.close()
#        conn.close()

@app.route('/update', methods=['POST'])
def update_status():
    try:  
        accel_id = request.form['input_accel_id']
        date_identified = request.form['input_date_identified']
        status = request.form['input_status']
        remarks = request.form['input_remarks']
        flagger = request.form['input_flagger']
        stat_id = request.form['id']
        # validate the received values
        if accel_id and date_identified and status and flagger and request.method == 'POST':
            #do not save password as a plain text
#            _hashed_password = generate_password_hash(_password)
            # save edits
#            sql = "UPDATE tbl_user SET user_name=%s, user_email=%s, user_password=%s WHERE user_id=%s"
            sql = ("UPDATE accelerometer_status SET accel_id = '{}', "
                   "ts_flag = NOW(), date_identified = '{}', flagger='{}', "
                   "status='{}', remarks='{}' WHERE stat_id = '{}'".format(accel_id, date_identified, flagger, status, remarks, stat_id))
#            conn = mysql.connect()
#            cursor = conn.cursor()
#            cursor.execute(sql, data)
#            conn.commit()
            qdb.execute_query(sql)
            flash('Status updated successfully!')
            return redirect('/')
        else:
            return 'Error while updating status'
    except Exception as e:
        print(e)
#    finally:
#        cursor.close() 
#        conn.close()
  
@app.route('/delete/<int:id>')
def delete_status(id):
    try:
#        conn = mysql.connect()
#        cursor = conn.cursor()
        sql = "DELETE FROM accelerometer_status WHERE stat_id={}".format(id)
        qdb.execute_query(sql)
        flash('User deleted successfully!')
        return redirect('/')
    except Exception as e:
        print(e)
#    finally:
#        cursor.close() 
#        conn.close()
  
if __name__ == "__main__":
#    ip = socket.gethostbyname(socket.gethostname())
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    print(ip)
    socketio.run(app, host= ip, port=3000)
    app.run(debug=True)