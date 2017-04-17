#!/usr/bin/python2
import urllib2 as u
import geojson as g
import MySQLdb as m
import time as t
import getopt, sys
from time import sleep

MYSQL_HOSTNAME = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "toor"
MYSQL_DATABASE = "wordpress"

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

def initial_population(db, cursor):
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

def get_updatedafter(value):
    url = "https://earthquake.usgs.gov/fdsnws/event/1/count?updatedafter=" + str(value)
    data = get_data_url(url)
    return data

def check(db,c):
    c.execute("SELECT * FROM gm_eq_data ORDER BY Time DESC LIMIT 1;")
    last_entry = c.fetchone()
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&updatedafter="+ str(last_entry[6]) +"&orderby=time-asc"
    print "Updates available: {}".format(get_updatedafter(last_entry[6]))

def update(db, cursor):
    cursor.execute("SELECT * FROM gm_eq_data ORDER BY Time DESC LIMIT 1;")
    last_entry = cursor.fetchone()
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&updatedafter="+ str(last_entry[6]) +"&orderby=time-asc"
    total = get_updatedafter(last_entry[6])
    i = 0
    print "Started update job"
    print "Last entry at: " + str(last_entry[6])
    data = get_data_url(url)
    if data.metadata["count"] == 0: print "No new data available"
    try:
        count = 0
        n_updated = 0;
        n_added = 0;
        for item in data.features:
            count+=1
            cursor.execute("""SELECT COUNT(*) FROM gm_eq_data WHERE IdStr = %s;""", (item.id,))
            result = cursor.fetchone()
            progress_bar(count,total)
            if result[0] == 1:
                n_updated+=1
                values = item_tuple(item) + (item.id,)
                cursor.execute("""UPDATE gm_eq_data SET IdStr = %s, Place = %s, Lat = %s, Lng = %s, Depth = %s, Time = %s, Mag = %s WHERE IdStr = %s""", values)
            elif result[0] == 0:
                n_added+=1
                cursor.execute("""insert into gm_eq_data(IdStr, Place, Lat, Lng, Depth, Time, Mag) values (%s,%s,%s,%s,%s,%s,%s)""", item_tuple(item))
            db.commit()
        print "\nTotal updated: " + str(n_updated)
        print "Total added:   " + str(n_added)

    except(m.Error, m.Warning) as e:
        print e
        db.rollback();

def progress_bar(count,total):
     sys.stdout.write("\r")
     sys.stdout.write("[%-20s]%d%%"%('='*(count/total*20),(count/total*100)))
     sys.stdout.flush()

def help():
    print "Usage: geqdata [OPTIONS...] [FILE]..."
    print "    -h, --help       Display this help and exit."
    print "    -u, --update     Update database."
    print "    -c, --check      Check for updates to database."
    print "    -l, --log        Log to specified file"


def handle_arguments():
    try:
        opts, args = getopt.getopt(sys.argv[1:],"huclo:v",["help","update","ckeck","log","output="])
    except getopt.GetoptError as err:
        # print help information and exit
        print str(err)
        sys.exit(2)
    output = None
    verbose = False
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h","--help"):
            help()
            sys.exit()
        elif o in ("-o","--output"):
            output = a
        elif o in ("-i","--init"):
            handle_action(initial_population)
        elif o in ("-u","--update"):
            handle_action(update)
        elif o in ("-c","--check"):
            handle_action(check)
        else:
            assert False, "unhandled option"


def main():
    handle_arguments()

def handle_action(action):
    try:
        db = m.connect(host=MYSQL_HOSTNAME,user=MYSQL_USER,passwd=MYSQL_PASSWORD,db=MYSQL_DATABASE)
        c = db.cursor()
        action(db,c)
        c.close()
        db.close()
    except(m.Error, m.Warning) as e:
        print e
        sys.exit(2)

if __name__ == "__main__":
    main()
