import numpy as np
import random
from IPython.display import clear_output
import matplotlib.pyplot as plt

import csv
import json
import math
import ast

round_count = 0
number_of_lines = 0

def createStates(speaker1,speaker2,action):
	global round_count
	round_count = round_count + 1
	decay = 0.00001
	growth = random.uniform(0, 0.5) # picking between 0 to 0.5
	noise = random.uniform(-0.1, 0.1)
	growth = growth + noise
	# print("growth: "+ str(growth))
	# print("decay rate " + str(round_count*decay))
	if action == 0 or action == 1:
		if random.uniform(0, 1) > 0.5:
			speaker2 = speaker2 + growth
		else:
			speaker1 = speaker1 + growth
	elif action == 2:
			speaker1 = speaker1 + growth
	elif action == 3:
			speaker2 = speaker2 + growth
	elif action == 5:
			speaker1 = speaker1 + growth
	elif action == 6:
			speaker2 = speaker2 + growth
	speaker2 = speaker2 - decay * round_count
	speaker1 = speaker1 - decay * round_count

	return speaker1,speaker2

from TwoMicLiveRecording import TwoMicLiveRecording as tm
from multiprocessing import Pool
import time
import sys
from RecordingTimer import noSmartDatabase as db

def actualStates():
	initial_time = time.time()
	try:
		print(time.time()-initial_time)
		agents = 1
		chunksize = 1
		pool = Pool(processes=agents)
		result= pool.map(tm.runMics, [[1,300]], chunksize)
		print(result[0])
		time.sleep(1)
	except RuntimeError:
		print ("Can't get data from the microphones right now")
		result = 3
		sys.exit(1)
	return result[0],result[0]/2

def readStates(line_index):
	try:
		f= open("SpeechDatabase.txt","r")
		lineList = f.readlines()
		f.close()
		number_of_lines = len(lineList)
		if line_index < number_of_lines:
			print(lineList[line_index])
			return (lineList[line_index])
		else:
			return
	except RuntimeError:
		print ("Can't read the file" + str (RuntimeError))
		result = 3
		sys.exit(1)

def readRealTimeStates(line_index):
	try:
		pass
	except RuntimeError:
		pass

class QLearning():
	def __init__ (self,state_size,action_size):
		self.state_size = state_size
		self.action_size = action_size
		self.rewards =[]
		self.times = []
		self.epochs = []
		self.ratios = []
		self.interval = 10 #s
		self.current_line = 0
		self.Q = np.zeros((self.state_size, self.action_size))

	def learn(self,lr,gamma,epsilon,states,actions,dataIneed):
		# for i in range(1, 10):
		i = 0
		print("------------------------------- new epoch ------------------------------------")
		done = False
		speaker1 = 0
		speaker2 = 0
		state_id = random.randint(0, len(states)-2)
		# Set the percent you want to explore
		set_of_actions_chosen =[]

		js = []

		j = 0
		while not done:
			j = j+1
			js.append(j)
			if random.uniform(0, 1) < epsilon:
				"""
				Explore: select a random action
				"""
				action_id = random.randint(0, len(actions)-1)
				# print("action explore "+str(action_id))
			else:
				"""
				Exploit: select the action with max value (future reward)
				"""
				action_id = np.argmax(self.Q[state_id])
				# print("action exploit "+str(action_id))

			set_of_actions_chosen.append(actions[action_id])

			# try:
			# speaker1,speaker2 = createStates(speaker1,speaker2,action_id)
			# dataIneed = readStates(self.current_line)
			# dataIneed = input("put the times in format of x y\n")
			if dataIneed == "done":
				done = True
			else:
				speaker1,speaker2 = (dataIneed).split(" ")
				print("observations "+ str(speaker1)+ " " + str(speaker2))
				speaker1 = int(speaker1)
				speaker2 = int(speaker2)
				talking_time = speaker1 + speaker2
				if speaker2 == 0:
					ratio = 20
				else:
					ratio = speaker1/speaker2
					# talking_time = float(input("How long kids spent talking from 10s?"))
					# ratio = float(input("What is the ratio of speaker 1 talking to speaker 2?"))
				# except:
				# 	print("wrong format!")

				self.times.append(talking_time)
				self.ratios.append(ratio)

				print("set of actions so far "+ str(set_of_actions_chosen))
				time.sleep(2)
				# rewards are distance
				# we want reward to be 0
				# that's why I negatived them, so the biggest value possible is 0
				r1 = -1 * ((1-(talking_time/self.interval))**2)
				if ratio > 1:
					ratio_r = 1/ratio
				else:
					ratio_r = ratio
				r2 = -1 * ((1-ratio_r)**2)
				print("This is r1 "+str(r1)+" and this is r2 "+str(r2))

				reward = -1 *((r1**2)+(r2**2))

				# the done parameter depends on the study
				# if reward > -0.01 or talking_time > 60:
				# 	done = True
				if j > 0:
					done = True

				# self.current_line = self.current_line + 1
				# done = (readStates(self.current_line) == None)

				self.rewards.append(reward)
				self.epochs.append(i)

				# IS THIS IDEA CORRECT?
				# encourages more talking then encourages equal talking
				
				if ratio > 1:
					next_state_id = 1
				elif ratio < 1:
					next_state_id = 2
				else:
					if talking_time/self.interval < 1:
						next_state_id = 0
					else:
						next_state_id = 3

				# Update q values
				self.Q[state_id, action_id] = self.Q[state_id, action_id] + lr * (reward + gamma * np.max(self.Q[next_state_id, :]) - self.Q[state_id, action_id])
				state_id = next_state_id
				# print(Q)


			# plt.subplot(3, 1, 1)

			# plt.plot(self.times)
			# plt.title('Total reward, the talking time and the ratios')
			# plt.ylabel('Total Talking Time')

			# plt.subplot(3, 1, 2)
			# plt.plot(self.ratios)
			# plt.ylabel('Speaker 1 to 2')

			# plt.subplot(3, 1, 3)
			# plt.plot(self.rewards)
			# plt.xlabel('time (s)')
			# plt.ylabel('Total Reward')

			# plt.waitforbuttonpress()
			# plt.show(block=False)
			# plt.close() 

		# return [js,self.rewards,self.times,self.ratios]
		return action_id

	def plots(arr1,arr2,title, axis1, axis2, legs,image):
		font = {'family' : 'DejaVu Sans','weight' : 'bold','size'   : 16}
		plt.rc('font', **font)

		plt.plot(arr1,arr2,ms= 10)
		plt.grid()
		plt.title(title)
		plt.ylabel(axis1)
		plt.xlabel(axis2)
		plt.legend(legs)
		plt.show()
		# plt.savefig(image)

	def duplicates(lst, item):
		return [i for i, x in enumerate(lst) if x == item]

	def pickRandom(list_of_actions, memory_of_action):
		action_probability = []
		for i in range(0,len(list_of_actions)):
			action = list_of_actions[i]
			probs = duplicates(memory_of_action,action)
			if probs == []:
				action_probability[i] = len(memory_of_action)
			else:
				action_probability[i] = sum(probs)
		picked_action = np.random.choice(len(list_of_actions), 1, p=action_probability)
		return picked_action


if __name__ == '__main__': # necessary to avoid creating multiple processes
	state_size = 4 
	action_size = 7
	lr = 0.6 # how much stick to new data
	gamma = 0.2 # discount
	epsilon = 0.5 # exploration vs exploit

	states = ["s1","s2","s3","s4"]
	actions = ["a1","a2","a3","a4","a5","a6","a7"]
	# ask both
	# ask none
	# ask 1
	# ask 2
	# action_names = ["Ask question both", "Statement both", "Ask questions s1", "Ask questions s2", "Nothing", "Ask s1 -reassurance", "Ask s2 -reassurance"]
	action_names = ["ask both", "ask none", "ask 1", "ask 2"]

	myQLearning = QLearning(state_size,action_size)
	# [epochs,rewards,times,ratios] = myQLearning.learn(lr,gamma,epsilon,states,action_names,"0 0")
	action = myQLearning.learn(lr,gamma,epsilon,states,action_names,"0 0")
	print("This is the final action: "+str(action))
	# plots(epochs,times,"Reward over time", "Total time spend speaking", "time (s)",('discount rate 0.1'),"gamma.png")
	# plots(epochs,rewards,"Rewards over time", "Reward", "time (s)",('discount rate 0.1'),"gamma.png")
	# plots(epochs,ratios,"Reward over time", "Ratios", "time (s)",('discount rate 0.1'),"gamma.png")