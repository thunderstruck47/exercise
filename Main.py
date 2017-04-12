#!/usr/bin/python2
import urllib2 as u
import geojson as g
import MySQLdb as m
import time as t

def get_data(start_time, end_time):
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=" + start_time +"&endtime=" + end_time + "&orderby=time-asc"
    response = u.urlopen(url)
    data = g.loads(response.read())
    return data

def get_data_url(url):
    response = u.urlopen(url)
    data = g.loads(response.read())
    return data

def get_date_input(text):
    date_entry = input(text)
    year,month,day = map(int,date_entry.split('-'))
    if (year>=1999 and month<=12 and month>0): return date_entry

def initial_population():
    db = m.connect(host="localhost",user="root",passwd="toor",db="wordpress")
    cursor = db.cursor()

    #Drop if exists
    try:
        cursor.execute("DROP TABLE gm_eq_data")
        db.commit()
    except(m.Error, m.Warning) as e:
        print e
        db.rollback()

    #Create table
    try:
        cursor.execute("CREATE TABLE gm_eq_data(ID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,IdStr VARCHAR(45), Place VARCHAR(255), Lat DOUBLE, Lng DOUBLE, Depth DOUBLE, Time TIMESTAMP, Mag DOUBLE);")
        db.commit()
    except(m.Error, m.Warning) as e:
        print e
        db.rollback()
    
    #Populate table
    data = get_data('2017-03-01', '2017-04-10')
    append_data(db,cursor,data)

def item_tuple(item):
    ID = item.id
    place = item.properties["place"]
    lat = item.geometry.coordinates[1]
    lng = item.geometry.coordinates[0]
    depth = item.geometry.coordinates[2]
    time = t.strftime('%Y-%m-%d %H:%M:%S',t.gmtime(item.properties["time"]/1000))
    mag = item.properties["mag"]
    return (ID,place,lat,lng,depth,time,mag)    

def append_data(db, cursor, data):
    for item in data.features:
        try:
            ID = item.id
            place = item.properties["place"]
            lat = item.geometry.coordinates[1]
            lng = item.geometry.coordinates[0]
            depth = item.geometry.coordinates[2]
            time = t.strftime('%Y-%m-%d %H:%M:%S',t.gmtime(item.properties["time"]/1000))
            mag = item.properties["mag"]
            print ID, place, lat, lng, depth, time, mag
            cursor.execute("""insert into gm_eq_data(IdStr, Place, Lat, Lng, Depth, Time, Mag) values (%s,%s,%s,%s,%s,%s,%s)""", (ID,place,lat,lng,depth,time,mag))
            db.commit()
        except(m.Error, m.Warning) as e:
            print e
            db.rollback()

def update(db,cursor):
    cursor.execute("SELECT * FROM gm_eq_data ORDER BY Time DESC LIMIT 1;")
    last_entry = cursor.fetchone()
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&updatedafter="+ str(last_entry[6]) +"&orderby=time-asc"
    print last_entry, url
    
    data = get_data_url(url)
    if data.metadata["count"] == 0: print "No new data available"
    try:
        n_updated = 0;
        n_added = 0;
        for item in data.features:
            cursor.execute("""SELECT COUNT(*) FROM gm_eq_data WHERE IdStr = %s;""", (item.id,))
            result = cursor.fetchone()
            if result[0] == 1:
                n_updated+=1
                values = item_tuple(item) + (item.id,)
                cursor.execute("""UPDATE gm_eq_data SET IdStr = %s, Place = %s, Lat = %s, Lng = %s, Depth = %s, Time = %s, Mag = %s WHERE IdStr = %s""", values)
                db.commit()
            elif result[0] == 0:
                n_added+=1
                try:
                    cursor.execute("""insert into gm_eq_data(IdStr, Place, Lat, Lng, Depth, Time, Mag) values (%s,%s,%s,%s,%s,%s,%s)""", item_tuple(item))
                    db.commit()
                except(m.Error, m.Warning) as e:
                    print e
                    db.rollback()
        print "Total updated: " + n_updated, "Total added" + n_added

    except(m.Error, m.Warning) as e:
        print e
        db.rollback();

#initial_population()
db = m.connect(host="localhost", user="root", passwd="toor", db="wordpress")
cursor = db.cursor()
update(db,cursor)
db.close()
