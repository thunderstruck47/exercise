#!/usr/bin/python2
import urllib2 as u
import geojson as g
import MySQLdb as m

def get_data():
	response = u.urlopen("https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2014-01-01&endtime=2014-01-02&minmagnitude=4")
	data = g.loads(response.read())
	return data
	# data.features[0].geometry

db = m.connect(host="localhost",user="root",passwd="toor",db="wordpress")
cursor = db.cursor()

#Drop if exists
try:
	cursor.execute("DROP TABLE gm_eq_data")
	db.commit()
except:
	db.rollback()

#Create table
try:
	cursor.execute("CREATE TABLE gm_eq_data( ID INT NOT NULL AUTO_INCREMENT PRIMARY KEY, Name VARCHAR(255), Lat DOUBLE, Lng DOUBLE);")
	db.commit()
except:
	db.rollback()

#Populate table
data = get_data()
#print data
for item in data.features:
	try:
		print item.properties["title"],item.geometry.coordinates[1],item.geometry.coordinates[0]
		cursor.execute("""insert into gm_eq_data(Name, Lat, Lng) values (%s,%s,%s)""", (item.properties["title"],item.geometry.coordinates[1],item.geometry.coordinates[0]))
		db.commit()
	except:
		print "ROLL"
		db.rollback()
db.close();
