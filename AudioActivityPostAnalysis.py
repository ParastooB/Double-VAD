import pyaudio
import numpy as np
from functools import partial
from multiprocessing import Pool
import wave
import time
import io
import sys
import scipy.io.wavfile as wavfile
import pylab as pl
import pydub 
from pydub import AudioSegment
import os
import collections
import contextlib
import sys
import webrtcvad
from pydub.playback import play


def read_by_amplitude(self,filename,groupname,participantname):
	frames = []
	self.filename = filename
	y_rate, y = self.read(self.filename)
	data = y
	maxnp = np.max(data)


def read(f, normalized=False):
	"""MP3 to numpy array"""
	a = pydub.AudioSegment.from_file(f,"m4a")
	y = np.array(a.get_array_of_samples())
	if a.channels == 2:
		y = y.reshape((-1, 2))
	if normalized:
		return a.frame_rate, np.float32(y) / 2**15
	else:
		return a.frame_rate, y

def read_wave(path):
	"""Reads a .wav file.
	Takes the path, and returns (PCM audio data, sample rate).
	"""
	with contextlib.closing(wave.open(path, 'rb')) as wf:
		num_channels = wf.getnchannels()
		assert num_channels == 1
		sample_width = wf.getsampwidth()
		assert sample_width == 2
		sample_rate = wf.getframerate()
		assert sample_rate in (8000, 16000, 32000, 48000)
		pcm_data = wf.readframes(wf.getnframes())
		return pcm_data, sample_rate

def read_parts(path,start = 0,end = -1):
	# start and end in seconds
	global g_channels
	global g_rate
	global g_sample_Width
	aus = AudioSegment.from_file(path, "m4a")
	if end == -1:
		end = aus.duration_seconds
	start = start * 1000
	end = end * 1000
	aus2 = aus[start:end+1]
	# play(aus2)
	return aus2.raw_data, aus2.frame_rate,aus2.sample_width,aus2.channels

def read_m4a(path):
	aus = AudioSegment.from_file(path, "m4a")
	return aus.raw_data, aus.frame_rate,aus.sample_width,aus.channels

def read_m4a_portionize(path):
	aus = AudioSegment.from_file(path, "m4a")
	end = aus.duration_seconds
	start = 0
	count = 5
	results = read_parts(path,start,600) # start
	start = 601
	results = results + read_parts(path,end-601,end) # end
	if end > 1200:
		results = results + read_parts(path,start,end-601) # end
	else:
		results = results + (0,0,0,0)
	return results

def read_m4a_portionize_5min(path):
	aus = AudioSegment.from_file(path, "m4a")
	end = aus.duration_seconds
	start = 0
	stepsize = 300
	sliceend = start + stepsize
	results = []
	while sliceend <= end:
		print(start)
		print(sliceend)
		results.append(read_parts(path,start,sliceend))
		start = sliceend
		sliceend = start + stepsize
	if sliceend > stepsize:
		print(start)
		print(end)
		results.append(read_parts(path,start,end))

	return results

def write_wave(path, audio, sample_rate):
	"""Writes a .wav file.
	Takes path, PCM audio data, and sample rate.
	"""
	with contextlib.closing(wave.open(path, 'wb')) as wf:
		wf.setnchannels(1)
		wf.setsampwidth(2)
		wf.setframerate(sample_rate)
		wf.writeframes(audio)


class Frame(object):
	"""Represents a "frame" of audio data."""
	def __init__(self, bytes, timestamp, duration):
		self.bytes = bytes
		self.timestamp = timestamp
		self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
	"""Generates audio frames from PCM audio data.
	Takes the desired frame duration in milliseconds, the PCM data, and
	the sample rate.
	Yields Frames of the requested duration.
	"""
	n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
	offset = 0
	timestamp = 0.0
	duration = (float(n) / sample_rate) / 2.0
	while offset + n < len(audio):
		yield Frame(audio[offset:offset + n], timestamp, duration)
		timestamp += duration
		offset += n


def vad_collector(sample_rate, frame_duration_ms,padding_duration_ms, vad, frames):
	"""Filters out non-voiced audio frames.
	Given a webrtcvad.Vad and a source of audio frames, yields only
	the voiced audio.
	Uses a padded, sliding window algorithm over the audio frames.
	When more than 90% of the frames in the window are voiced (as
	reported by the VAD), the collector triggers and begins yielding
	audio frames. Then the collector waits until 90% of the frames in
	the window are unvoiced to detrigger.
	The window is padded at the front and back to provide a small
	amount of silence or the beginnings/endings of speech around the
	voiced frames.
	Arguments:
	sample_rate - The audio sample rate, in Hz.
	frame_duration_ms - The frame duration in milliseconds.
	padding_duration_ms - The amount to pad the window, in milliseconds.
	vad - An instance of webrtcvad.Vad.
	frames - a source of audio frames (sequence or generator).
	Returns: A generator that yields PCM audio data.
	"""
	num_padding_frames = int(padding_duration_ms / frame_duration_ms)
	# We use a deque for our sliding window/ring buffer.
	ring_buffer = collections.deque(maxlen=num_padding_frames)
	# We have two states: TRIGGERED and NOTTRIGGERED. We start in the
	# NOTTRIGGERED state.
	triggered = False

	voiced_frames = []
	voiced_frames_count = 0
	for frame in frames:
		is_speech = vad.is_speech(frame.bytes, sample_rate)

		# sys.stdout.write('1' if is_speech else '0')
		if not triggered:
			ring_buffer.append((frame, is_speech))
			num_voiced = len([f for f, speech in ring_buffer if speech])
			# If we're NOTTRIGGERED and more than 90% of the frames in
			# the ring buffer are voiced frames, then enter the
			# TRIGGERED state.
			if num_voiced > 0.9 * ring_buffer.maxlen:
				triggered = True
				# sys.stdout.write('+(%s)\n' % (ring_buffer[0][0].timestamp,))
				# We want to yield all the audio we see from now until
				# we are NOTTRIGGERED, but we have to start with the
				# audio that's already in the ring buffer.
				for f, s in ring_buffer:
					voiced_frames.append(f)
				ring_buffer.clear()
		else:
			# We're in the TRIGGERED state, so collect the audio data
			# and add it to the ring buffer.
			voiced_frames.append(frame)
			ring_buffer.append((frame, is_speech))
			num_unvoiced = len([f for f, speech in ring_buffer if not speech])
			# If more than 90% of the frames in the ring buffer are
			# unvoiced, then enter NOTTRIGGERED and yield whatever
			# audio we've collected.
			if num_unvoiced > 0.9 * ring_buffer.maxlen:
				# sys.stdout.write('-(%s)\n' % (frame.timestamp + frame.duration))
				triggered = False
				yield b''.join([f.bytes for f in voiced_frames])
				ring_buffer.clear()
				voiced_frames_count = voiced_frames_count + len(voiced_frames) - 3
				voiced_frames = []
	# if triggered:
	# 	sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
	# sys.stdout.write('\n')
	# print("hello! "+str(voiced_frames_count))
	# If we have any leftover voiced audio when we run out of input,
	# yield it.
	if voiced_frames:
		yield b''.join([f.bytes for f in voiced_frames])

def get_vad_seconds(vad,audio, sample_rate, sample_width, sample_channels): 
	frames = frame_generator(30, audio, sample_rate) # generate 30 ms frames
	frames = list(frames)
	segments = vad_collector(sample_rate, 30, 200, vad, frames)
	g = 0
	for i, segment in enumerate(segments):
		sound = AudioSegment(data=segment,sample_width=sample_width,frame_rate=sample_rate,channels=sample_channels)
		g = g + sound.duration_seconds
	return g,len(frames)*30/1000

if __name__ == '__main__':
	direc = "/RawData"
	f = open("audio_analysis.txt", "a")
	f.write("%s,%s,%s,%s\n"%("groupname","user_id","talkingTime","totalTime"))
	f2 = open("audio_analysis_5min.txt", "a")
	f2.write("%s,%s,%s,%s,%s,%s,%s,%s\n"%("groupname","user_id","talkingTime(10m)","totalTime(10m)","talkingTime(-10m)","totalTime(-10m)","talkingTime(restm)","totalTime(restm)"))
	vad = webrtcvad.Vad(int(3))

	for root, dirs, files in os.walk(direc):
		for file in files:
			if file.endswith(".m4a"):
				filename = os.path.join(root, file)
				print(filename)
				parts = filename.split("/")

				audio, sample_rate, sample_width, sample_channels = read_m4a(filename)
				a,b = get_vad_seconds(vad,audio, sample_rate, sample_width, sample_channels)

				print(a,b)
				f.write("%s,%s,%s,%s\n"%(parts[6],parts[9],a,b))

				try:
					dataanalized = read_m4a_portionize_5min(filename)
					bein = 0
					start_of_line = str(parts[6])+", "+str(parts[9])
					while bein < len(dataanalized):
						a,b = get_vad_seconds(vad,dataanalized[bein][0],dataanalized[bein][1], dataanalized[bein][2], dataanalized[bein][3])
						bein = bein + 1
						start_of_line = start_of_line + ", "+ str(a)+", "+str(b)
					f2.write(start_of_line+"\n")
				except:
					print("I'm gonna have to miss file "+ parts[6] + " " + parts[9])
	f.close()
	f2.close()

