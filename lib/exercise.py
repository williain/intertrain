import countdown
import time, logging, subprocess, sys

class Exercise(object):
	def __init__(self, exercise, duration, rest=5, read_delay=5, loglevel=logging.DEBUG):
		self.lastsound=None
		if duration<0:
			raise Exception("Not a time traveller: Can't exercise for "+repr(duration)+" second(s)")
		if rest<0:
			raise Exception("Not a time traveller: Can't rest for "+repr(rest)+" second(s)")
		if read_delay<0:
			raise Exception("Not a time traveller: Can't let the user read for "+repr(read_delay)+" second(s)")

		self.reading=countdown.Countdown(read_delay, self.session_start)
		self.countdown=countdown.Countdown(duration, self.finish, self.tick)
		self.exercise=exercise
		self.duration=duration
		self.rest=rest
		self.read_delay=read_delay
		self.messagelogger=logging.getLogger('exerciseMessages')
		self.messagelogger.setLevel(loglevel)

	def __del__(self):
		self.__clear_sound()

	def __clear_sound(self):
		if self.lastsound != None:
			self.lastsound.terminate()
			self.lastsound=None

	def __play_sound(self, soundfile):
		self.__clear_sound()
		# TODO Not platform independent
		self.lastsound=subprocess.Popen(['mplayer', soundfile], stdout=open('/dev/null','w'), stderr=open('/dev/null','w'))

	def start(self):
		self.messagelogger.info("Exercise: "+self.exercise+", for "+str(self.duration)+"s")
		self.messagelogger.info("Get ready...")
		self.reading.start()

	def session_start(self):
		self.__play_sound('sounds/boop.ogg')
		self.messagelogger.info("Start exercise")
		self.countdown.start()

	def tick(self,clock):
		if self.messagelogger.isEnabledFor(logging.INFO):
			sys.stdout.write(".")
			sys.stdout.flush()
		time_left=self.duration-clock
		if time_left<10:
			self.messagelogger.debug(str(time_left)+"...")
		if time_left<5 and time_left>0:
			self.__play_sound('sounds/beep.ogg')

	def finish(self):
		if self.messagelogger.isEnabledFor(logging.INFO):
			sys.stdout.write("\n")
		self.messagelogger.info("Finish (exercise "+self.exercise+"): "+str(self.rest)+"s rest")
		self.__play_sound('sounds/boop.ogg')
		rest_start=time.time()
		while time.time()-rest_start < self.rest:
			time.sleep(0.2)
		self.messagelogger.info("-"*70)

def Test():
	# Test default arguments
	exercise=Exercise("test_default", 6)
	time_start=time.time()
	exercise.start()
	duration=time.time()-time_start
	if abs(duration-16)<0.2:
		print("TEST_DEFAULT OK: Expected duration of 16, got",duration)
	else:
		print("TEST_DEFAULT FAIL: Expected duration of 16, got",duration)
	del exercise
	
	# Test overriding defaults
	exercise=Exercise("test_override1", 15, 2, read_delay=0)
	time_start=time.time()
	exercise.start()
	duration=time.time()-time_start
	if abs(duration-17)<0.2:
		print("TEST_OVERRIDE1: Expected duration of 17, got",duration)
	else:
		print("TEST_OVERRIDE1: Expected duration of 17, got",duration)
	del exercise

	exercise=Exercise("test_override2", 5, 0, read_delay=3)
	time_start=time.time()
	exercise.start()
	duration=time.time()-time_start
	if abs(duration-8)<0.2:
		print("TEST_OVERRIDE2 OK: Expected duration of 8, got",duration)
	else:
		print("TEST_OVERRIDE2 FAIL: Expected duration of 8, got",duration)
	del exercise	

	#TODO: Check exception message/make exception types (TBD)
	try:
		exercise=Exercise("TEST_EXCEPT1", -1)
		print("TEST_EXCEPT1 FAIL: Exception expected")
		del exercse
	except Exception as e:
		print("TEST_EXCEPT1 OK: Got exception",str(e))

	try:
		exercise=Exercise("test_except2", 10, -2)
		print("TEST_EXCEPT2 FAIL: Exception expected")
		del exercise
	except Exception as e:
		print("TEST_EXCEPT2 OK: Got exception",str(e))

	try:
		exercise=Exercise("test_except3", 10, read_delay=-3)
		print("TEST_EXCEPT3 FAIL: Exception expected")
		del exercise
	except Exception as e:
		print("TEST_EXCEPT3 OK: Got exception",str(e))
