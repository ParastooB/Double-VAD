import pyaudio
import numpy as np
from functools import partial
from multiprocessing import Pool
import wave
import time

class TwoMicLiveRecording (object):

	def __init__(self,inputs):
		self.CHUNK = 2**11
		self.RATE = 44100

		self.p=pyaudio.PyAudio()
		self.voice_segments = 0
		self.index = inputs[0]
		self.speakingPeak = inputs[1]
		self.totalTime = int(1*44100/1024)
		

	def getPercentage(self):
		# mic1id = -1
		# mic2id = -1
		info = self.p.get_host_api_info_by_index(0)
		numdevices = info.get('deviceCount')
		for i in range(0, numdevices):
			print(self.p.get_device_info_by_host_api_device_index(0, i))
			if (self.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
				if (self.index == 1 and self.p.get_device_info_by_host_api_device_index(0, i).get('name')) == "sysdefault":
				# "sysdefault":
				# "Microphone (Realtek Audio)"
					micid = i
					print ("Input (soundcard) Device id ", i, " - ", self.p.get_device_info_by_host_api_device_index(0, i).get('name'))
					print("1 is working NOW -----------------------------///////////////////////")
					# self.index = mic1id
				elif (self.index == 2 and self.p.get_device_info_by_host_api_device_index(0, i).get('name')) == "USB Audio Device: - (hw:1,0)":
				# "USB Audio Device: - (hw:1,0)":el
				# "Microphone (USB Audio Device)"
					micid = i
					print ("Input (usb) Device id ", i, " - ", self.p.get_device_info_by_host_api_device_index(0, i).get('name'))
					print("2 is working NOW -----------------------------///////////////////////")
					# self.index = mic2id
				else:
					print("~.~.~.~.~.~.~.~.~ "+"~.~ "+str(self.index)+": "+self.p.get_device_info_by_host_api_device_index(0, i).get('name'))
					micid = 7
					# self.index = mic2id


		print("Before index is "+str(self.index))
		try:
			print("micid is "+str(micid))
			self.micName = self.p.get_device_info_by_host_api_device_index(0, micid).get('name')
		except:
			print("micid is "+"-1-1-1")
		# self.index = micid
		# print("Now index is "+str(self.index))

		frames = []
		try:
			stream=self.p.open(format=pyaudio.paInt16,channels=1,rate=self.RATE,input=True,
					  frames_per_buffer=self.CHUNK,input_device_index=micid)
		except:
			print("for some reason the MIC IS NOT WORKING! " + str(micid) + ": "+\
				self.p.get_device_info_by_host_api_device_index(0, micid).get('name'))
		for i in range(self.totalTime): #go for a few seconds
			data = np.fromstring(stream.read(self.CHUNK,exception_on_overflow=False),dtype=np.int16)
			peak=np.average(np.abs(data))*2
			# bars = bars="/#/#/"*int(self.speakingPeak*peak/2**16)
			if self.index == 1:
				bars=" * * "*int(self.speakingPeak*peak/2**16)
			if self.index == 2:
				bars=" # # "*int(self.speakingPeak*peak/2**16)
			frames.append(data)
			if len(bars)>0:
				self.voice_segments = self.voice_segments + 1
			print("%d: %04d - %05d %s"%(self.index,i,peak,bars))
		

		stream.stop_stream()
		stream.close()

		wf = wave.open("speaker_index"+str(self.index)+".wav", 'wb')
		wf.setnchannels(1)
		wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
		wf.setframerate(self.RATE)
		wf.writeframes(b''.join(str(frames)))
		wf.close()
		self.p.terminate()



		# if self.voice_segments == 0:
		# 	result = 0
		# else:
		# 	result = self.voice_segments/self.totalTime
		# print("This %s mic has been used %f%%"%(self.micName,result))
		# return (result)
		return(self.voice_segments)


	def runMics(self,dataset):
		tm = TwoMicLiveRecording(dataset)
		return tm.getPercentage()


if __name__ == '__main__':
	tm = TwoMicLiveRecording([2,300])
	tm.runMics([2,300])

	# usb_mic = letssee(7,500)
	# default_mic = letssee(8,20)
	# print("%f%%"%(usb_mic.getPercentage()))
	# print("%f%%"%(default_mic.getPercentage()))

	# # dataset = [[1,300],[2,300]]
	# # agents = 2 
	# agents = 1
	# chunksize = 1
	# # try:
	# with Pool(processes=agents) as pool:
	# 	result= pool.map(TwoMicLiveRecording, dataset, chunksize)
	# # except:
	# # 	print("something went wrong, no idea what.")
	# 	# print(result)
	# print("working for now")