import requests
import sqlite3
import json

#to start osrm osrm-routed ../maps/new-york-latest.osrm


def routing(lon0,lat0,lon1,lat1):
	"""wrapper for doing routing with OSRM"""
	req = "http://0.0.0.0:5000/route/v1/table/%s,%s;%s,%s"%(lon0,lat0,lon1,lat1)
	osrm_raw = requests.get(req)
	orsm =json.loads(osrm_raw.text)
	return orsm['routes'][0]['duration']


def proc_edges(db, farms=False, constores = True):
	"""use this to create edges between procs, farms and stores
	set the flag to switch between farms and stores. stores by default"""

	table = 'ps_edges'
	query1 = 'SELECT * FROM ps_list' if constores else 'SELECT * FROM ps_list2' #leaving the option to have all stores
	query2 = 'INSERT INTO ps_edges VALUES (?,?,?);'
	query3 = 'SELECT * FROM ps_edges WHERE procid = ? AND storeid = ?'
	
	if (farms):
		table = 'fp_edges'
		query1 = 'SELECT * FROM farm_proc_bands;'
		query2 = 'INSERT INTO fp_edges VALUES (?,?,?);'
		query3 = 'SELECT * FROM fp_edges WHERE procid = ? AND farmid = ?'

	conn1 = sqlite3.connect(db, isolation_level = 'DEFERRED') #probably not secure, but ya know
	conn2 = sqlite3.connect(db, isolation_level = 'DEFERRED')
	c1 = conn1.cursor()
	c2 = conn2.cursor()

	for row in c1.execute(query1):
		c2.execute(query3,(row[0],row[3],))
		result = c2.fetchone()
		if(result == None): #ensure this edge doesn't already exist
			duration = routing(row[2],row[1],row[5],row[4])
			c2.execute(query2, (row[3],row[0],duration,))
	conn2.commit()
	return


if __name__ == "__main__":
	#proc_edges("db/test.db")
	#proc_edges("db/test.db", farms = True )
	fp_edges("db/test.db")