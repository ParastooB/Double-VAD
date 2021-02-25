import configparser
import sys
import pandas as pd
import string
import psycopg2
import time
import argparse
from datetime import datetime

class Database(object):
	host = ""
	dbnam = ""
	password = ""
	user = ""
	port = ""

	def __init__(self, group_name, table_name):
		self.last = ""
		self.group_name = group_name
		self.table_name = table_name
		self.group_id = 0

	def read(self):
		config = configparser.ConfigParser()
		print(config.read('config.ini'))
		print(config.sections())

		self.host = config['AWS_db']['host'].strip("\'")
		self.dbname = config['AWS_db']['db_name'].strip("\'")
		self.password = config['AWS_db']['db_password'].strip("\'")
		self.user = config['AWS_db']['db_user'].strip("\'")
		self.port = config['AWS_db']['db_port'].strip("\'")
)
	def initilize(self):
		conn = None
		try:
			# connect to the PostgreSQL server
			print('Connecting to the PostgreSQL database...')
			conn = psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password,port=self.port,host=self.host)

			# create a cursor
			cur = conn.cursor()

			get_group_id = "SELECT * FROM %s WHERE name = \'%s\'"%("accounts_group",self.group_name)
			cur.execute(get_group_id)
			res = cur.fetchall()
			print("this is all associated with the " + self.group_name) 
			print(res)
			self.group_id = res[0][0]


			# alltables = "select * from information_schema.tables"
			agentoutput_Query = "SELECT * FROM %s WHERE group_id = %s ORDER BY id DESC LIMIT 1"%(self.table_name,self.group_id)
			cur.execute(agentoutput_Query)
			agentoutput = cur.fetchone() 

			if (agentoutput != None):
				self.last_id = agentoutput[0]
				print(self.last_id)
			else: 
				self.last_id = -1
				
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
		finally:
			if conn is not None:
				cur.close()
				conn.close()
				print('Database connection closed.')

	def connect(self):
		""" Connect to the PostgreSQL database server """
		conn = None
		try:
			# connect to the PostgreSQL server
			print('Connecting to the PostgreSQL database...')
			conn = psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password,port=self.port,host=self.host)

			# create a cursor
			cur = conn.cursor()

			alltables = "select * from information_schema.tables"
			my_query = "SELECT id,output_content,group_id FROM %s WHERE group_id = %s AND id > %s ORDER BY id ASC"%(self.table_name,self.group_id,self.last_id)
			cur.execute(my_query)
			lasts = cur.fetchall()
			print(" ----------------------------- these are all the sentences ------------------------------- ")
			print(lasts)
			print(" ------------------------------------")
			# print(self.last_id)
			if len(lasts) > 0:
				if self.last_id < lasts[0][0]:
					# print "there was a new message"
					self.last_id = lasts[0][0]
					self.last  =  lasts[0]
				print("the one I picked to response --> "+ str(self.last))
				
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
		finally:
			if conn is not None:
				cur.close()
				conn.close()
				print('Database connection closed.')

	def lastUpdate(self):
		return self.last

	def run(self,delay):
		last_id = '0'
		new = False
		try:
			while True:
				self.connect()
				print (self.lastUpdate())
				if (len(self.last) > 0):
					print("I said: " + str(last_id))
					print("I should say: "+ str(self.last[0]))
					print (int(self.lastUpdate()[0]))
					print (self.lastUpdate())

					if (int(last_id) < int(self.lastUpdate()[0])):
						print ('in if condition')
						to_say = str(self.lastUpdate()[1]['msg'])
						has_laugh = False
						if to_say.lower().find('ha ha') != -1:
							has_laugh = True
							to_say_one = to_say[:to_say.lower().find('ha ha')]
							to_say_two = to_say[to_say.lower().find('ha ha') + len('ha ha'):]
						print (self.lastUpdate()[1]['msg'])
						print (self.lastUpdate()[1]['emotion'])

				time.sleep(delay)
		except KeyboardInterrupt:
			print ("Interrupted by user, stopping Database readings")
			# Stop
			sys.exit(0)

if __name__ == '__main__':

	db = Database('Group 1','agents_agentoutput') 
	db.read()
	last_id = '0'
	db.initilize()
	db.run(5)
