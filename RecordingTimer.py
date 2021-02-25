import sched, time
from TwoMicLiveRecording import TwoMicLiveRecording as tm
from multiprocessing import Pool
import sys
import os

class noSmartDatabase():
	table = [];

	def add2table(tuple):
		noSmartDatabase.table.append(tuple)

	def readTable(index):
		return noSmartDatabase.table[index]

	def printall():
		print(noSmartDatabase.table)

if __name__ == '__main__':
	initial_time = time.time()	
	agents = 2
	chunksize = 1
	pool = Pool(processes=agents)
	result= pool.map(tm.runMics, [[1,300], chunksize
	check = True
	round_count = 0
	while check:
		try:
			agents = 1
			chunksize = 1
			pool = Pool(processes=agents)
			os.system('cat /proc/asound/modules')
			result= pool.map(tm.runMics, [[1,80],[2,300]], chunksize)
			noSmartDatabase.add2table(str(result[0])+" "+str(result[1]))
			file = "data/"+"SpeechData"+str(round_count)+".txt"
			print(file)
			f = open(file,"w+")
			f.write("%d %d\n" % (result[0],result[1]))
			f.close() 
			time.sleep(1)
		except KeyboardInterrupt:
			check = False
			print ("Interrupted by user")
			# f.close() 
			sys.exit(1)
		except RuntimeError:
			print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
				   "Please check your script arguments. Run with -h option for help.")
			# f.close() 
			sys.exit(1)
		round_count = round_count+ 1
		time.sleep(2)