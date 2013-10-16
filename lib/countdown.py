#!/usr/bin/python3

import time, os, logging

class AbortCountdownException(Exception):
	pass

class Countdown(object):
	def __init__(self, duration, finish_func, tick_func = False):
		self.logger = logging.getLogger(__name__)
		self.duration = duration
		self.func_tick = tick_func
		self.func_finish = finish_func
		self.logger.info("Countdown object created, duration %d",duration)

	def start(self):
		self.logger.info("Countdown started, duration %d",self.duration)
		self.started = time.time()

		clock = 0
		try:
			while clock < int(self.duration):
				while time.time() < self.started + clock + 1:
					time.sleep(0.1)
				clock = int(time.time()-self.started+0.5)
				self.logger.debug("Tick %d",clock)
				if self.func_tick:
					self.func_tick(clock)

			if int(self.duration) < self.duration:
				self.logger.debug("Counting down for remaining subsecond")
				while time.time() < self.started + self.duration:
					time.sleep(0.05)
			self.logger.info("Countdown finished (duration %d)",self.duration)
			self.func_finish()
		except AbortCountdownException as e:
			# Tick function aborted the countdown.  Return now, do not pass go
			self.logger.info("Countdown aborted (was duration %d)",self.duration)

def Test():
	logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
	logging.getLogger(__name__).setLevel(logging.INFO)
	ok = False
	def finish():
		nonlocal ok
		ok = True

	timer=Countdown(5, finish)

	started=time.time()
	timer.start()
	duration=time.time()-started

	if ok == True:
		print("TEST1 OK")
	else:
		print("TEST1 FAILED: Did not finish")

	if abs(duration-5)>0.1:
		print("TEST2 failed: Expected duration of 5, got",duration)
	else:
		print("TEST2 OK: Expected duration of 5, got",duration)

	ok = True
	def tick(t):
		if t>=2: raise AbortCountdownException("Test stop")
	def finish():
		Test.ok = False
	timer=Countdown(3, finish, tick)
	
	started=time.time()
	timer.start()
	duration=time.time()-started

	if ok == True:
		print("TEST3 OK")
	else:
		print("TEST3 FAILED: Excpected abort, but finished instead")

	if abs(duration-2)>0.1:
		print("TEST4 FAIL: Expected duration of 2, got",duration)
	else:
		print("TEST4 OK: Expected duration of 2, got",duration)

if __name__=="__main__":
    Test()
