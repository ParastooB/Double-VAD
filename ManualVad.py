import psycopg2
import datetime
import tkinter as tk
import configparser
import argparse

class SpeakerTimer(tk.Frame):

	def __init__(self, parent,group):
		tk.Frame.__init__(self, parent)
		self.parent = parent
		self.counter0 = 0 
		self.counter1 = 0 
		self.counter2 = 0 
		self.id = 1
		self.pasue1 = True
		self.pasue2 = True
		self.user_ids = []
		self.zero_count = 0
		self.group_name = group
		self.read()
		self.initialize_users()
		self.initialize_user_interface()

	def read(self):
		config = configparser.ConfigParser()
		print(config.read('config.ini'))
		print(config.sections())
		local = False
		if local:
			self.host = config['AWS_db']['local_host'].strip("\'")
			self.db_name = config['AWS_db']['local_db_name'].strip("\'")
			self.db_password = config['AWS_db']['local_db_password'].strip("\'")
			self.db_user = config['AWS_db']['local_db_user'].strip("\'")
			self.db_port = config['AWS_db']['local_db_port'].strip("\'")
		else:
			self.host = config['AWS_db']['remote_host'].strip("\'")
			self.db_name = config['AWS_db']['remote_db_name'].strip("\'")
			self.db_password = config['AWS_db']['remote_db_password'].strip("\'")
			self.db_user = config['AWS_db']['remote_db_user'].strip("\'")
			self.db_port = config['AWS_db']['remote_db_port'].strip("\'")

	def initialize_users(self):
		conn = None
		group_table_name = "accounts_group"
		table_name = "accounts_profile"
		group_name = self.group_name
		user_name_table = "auth_user"
		try:
			# connect to the PostgreSQL server
			print('Connecting to the PostgreSQL database...')
			conn = psycopg2.connect(dbname=self.db_name, user=self.db_user, password=self.db_password,port=self.db_port,host=self.host)

			# create a cursor
			cur = conn.cursor()

			get_group_id = "SELECT * FROM %s WHERE name = \'%s\'"%(group_table_name,group_name)
			cur.execute(get_group_id)
			res = cur.fetchall()
			print("this is all associated with the " + group_name) 
			print(res)
			group_id = res[0][0]


			# alltables = "select * from information_schema.tables"
			get_group_users = "SELECT * FROM %s WHERE group_id = %s"%(table_name,group_id)
			cur.execute(get_group_users)
			users_ids = cur.fetchall() 

			if (get_group_users != None):
				for i in users_ids:
					# self.user_ids.append(i)
					i = list(i)
					get_usernames = "SELECT * FROM %s WHERE id = %s"%(user_name_table,i[5])
					cur.execute(get_usernames)
					users_name = cur.fetchone()
					i.append(users_name[4])
					self.user_ids.append(i)
			else: 
				print("the group is somehow empty!")
			print(self.user_ids)
				
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
		finally:
			if conn is not None:
				cur.close()
				conn.close()
				print('Database connection closed.')

	def initialize_user_interface(self):
		self.parent.geometry("800x600")
		self.parent.title("Counting Seconds")
		# self.button=tk.Button(self.parent,text="Enter", command=self.PassCheck)
		# self.button.pack()
		self.label = tk.Label(self.parent, fg="dark green")
		self.label1 = tk.Label(self.parent, fg="dark blue")
		self.label2 = tk.Label(self.parent, fg="dark red")
		# self.label=tk.Label(self.parent,text="Please a password")
		# self.label.pack()
		self.label.pack()
		self.label1.pack()
		self.label2.pack()

		self.counter_label()
		speaker_1 = self.user_ids[0][6]
		speaker_2 = self.user_ids[1][6]
		self.button1 = tk.Button(root, text=speaker_1 + ' start', height = 5, width=100, command=self.counter_label1)
		self.button2 = tk.Button(root, text=speaker_1 + ' end', height = 5, width=100, command=self.end_speaker1)
		self.button3 = tk.Button(root, text=speaker_2 + ' start', height = 5, width=100, command=self.counter_label2)
		self.button4 = tk.Button(root, text=speaker_2 + ' end', height = 5, width=100, command=self.end_speaker2)
		self.button5 = tk.Button(root, text='End All', height = 5, width=100, command=self.close_all)
		self.button1.pack()
		self.button2.pack()
		self.button3.pack()
		self.button4.pack()
		self.button5.pack()


	# def PassCheck(self):
	#    password = self.entry.get()
	#    if len(password)>=9 and len(password)<=12:
	#       self.label.config(text="Password is correct")
	#    else:
	#       self.label.config(text="Password is incorrect")


	def counter_label(self):
		self.counter0 = 0
		def count():
			self.counter0 += 1
			if self.counter0 == 10:
				if self.counter1 != 0 or self.counter2 != 0:
					self.write_in_db(self.counter0,self.counter1,self.counter2)
					self.zero_count = 0
				else:
					# self.write_in_db(self.counter0,self.counter1,self.counter2)
					if self.read_db() == None:
						self.write_in_db(self.counter0,self.counter1,self.counter2)
						self.zero_count = 1+ self.zero_count
					else:
						idd, a, b = self.read_db()
						print("-------------------------")
						print(a)
						print(b)
						print(idd)
						if a == "0" and b == "0":
							self.delete_from_db(idd)
							self.write_in_db(self.counter0,self.counter1,self.counter2)
							self.zero_count = 1+ self.zero_count
						else:
							self.write_in_db(self.counter0,self.counter1,self.counter2)
							self.zero_count = 0
				self.counter0 = 0
				self.counter1 = 0 
				self.counter2 = 0 
			self.label.config(text=str(self.counter0))
			self.label.after(1000, count)
		count()


	def counter_label1(self):
		self.pasue1 = False
		# self.counter1 = 0
		def count():
			if not self.pasue1:
				self.counter1 += 1
				self.label1.config(text=str(self.counter1))
				self.label1.after(1000, count)
		count()


	def counter_label2(self):
		# self.counter2 = 0
		self.pasue2 = False
		def count():
			# global counter2
			if not self.pasue2:
				self.counter2 += 1
				self.label2.config(text=str(self.counter2))
				self.label2.after(1000, count)
		count()

	def end_speaker1(self):
		self.pasue1 = True

	def end_speaker2(self):
		self.pasue2 = True

	def close_all(self):
		self.write_in_db(self.counter0,self.counter1,self.counter2)
		self.destroy
		self.quit()
		# self.parent.destroy

	def delete_from_db(self,deleteID):
		print("deleting id %s"%(deleteID))
		connection = psycopg2.connect(user=self.db_user,
			password=self.db_password,
			host=self.host,
			port=self.db_port,
			database=self.db_name)
		cursor = connection.cursor()

		postgres_delete_query = "DELETE FROM actions_audiolog WHERE id = %s" %(deleteID)
		cursor.execute(postgres_delete_query)
		connection.commit()
		cursor.close()
		connection.close()

	def write_in_db(self,num1,num2,num3):
		try:
			connection = psycopg2.connect(user=self.db_user,
				password=self.db_password,
				host=self.host,
				port=self.db_port,
				database=self.db_name)
			cursor = connection.cursor()

			postgres_insert_query = """ INSERT INTO actions_audiolog (duration,user1_duration,user2_duration,group_id,user1_id,user2_id, zero_count, created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
			# record_to_insert = (self.id, num1, num2, num3,datetime.datetime.now().isoformat())
			print(type(self.user_ids[0][4]))
			print(self.user_ids[0][5])
			print(self.user_ids[1][5])
			record_to_insert = (num1, num2, num3,self.user_ids[0][4],self.user_ids[0][5],self.user_ids[1][5],self.zero_count, datetime.datetime.now().isoformat())
			cursor.execute(postgres_insert_query, record_to_insert)

			connection.commit()
			count = cursor.rowcount
			print (count, "Record inserted successfully into mobile table")

		except (Exception, psycopg2.Error) as error :
			if(connection):
				print("Failed to insert record into table", error)

		finally:
			#closing database connection.
			if(connection):
				cursor.close()
				connection.close()
				print("PostgreSQL connection is closed")
				self.id = self.id+1

	def read_db(self):
		connection = ""
		try:
			connection = psycopg2.connect(user=self.db_user,
				password=self.db_password,
				host=self.host,
				port=self.db_port,
				database=self.db_name)
			cursor = connection.cursor()
		except:
			print("Can't even connect to database")

		try:
			my_query = "SELECT id,duration,user1_duration,user2_duration FROM actions_audiolog ORDER BY id DESC LIMIT 1"
			cursor.execute(my_query)
			last = cursor.fetchone()
			print(" ----------------------------- these are all the sentences -------------------------------")
			print(last)
			print(" -----------------------------------------------------------------------------------------")

		except (Exception, psycopg2.Error) as error :
			if(connection):
				print("Failed to read record from table", error)

		finally:
			#closing database connection.
			if(connection):
				cursor.close()
				connection.close()
				print("PostgreSQL connection is closed")
				if last == None:
					return None
				return last[0],last[2],last[3]

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--gr", type=str, default='Test1', help="Group assigned")
	args = parser.parse_args()

	print(args.gr)
	root = tk.Tk()
	run = SpeakerTimer(root,args.gr)
	root.mainloop()
