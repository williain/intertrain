#!/usr/bin/python3

import time, os, logging, unittest

class AbortCountdownException(Exception):
    pass

class Countdown(object):
    def __init__(self, duration, finish_func, tick_func = False,interval=1):
        self.logger = logging.getLogger(__name__)
        self.duration = duration
        self.func_tick = tick_func
        self.func_finish = finish_func
        self.interval = interval
        self.logger.info("Countdown object created, duration {0}".format(
          duration
        ))

    def start(self):
        self.logger.info("Countdown started, duration {0}".format(
          self.duration
        ))
        self.started = time.time()

        clock = 0
        try:
            while clock < int(self.duration)-self.interval/2:
                while time.time() < self.started + clock + 1:
                    time.sleep(self.interval/10)
                clock = int(time.time()-self.started)
                self.logger.debug("Tick {0}".format(clock))
                if self.func_tick:
                    self.func_tick(clock)

            if int(self.duration) < self.duration:
                self.logger.debug("Counting down for remaining subsecond")
                while time.time() < self.started + self.duration:
                    time.sleep(self.interval/20)
            self.logger.info("Countdown finished (duration {0})".format(
              self.duration
            ))
            self.func_finish()
        except AbortCountdownException as e:
            # Tick function aborted the countdown.  Return now, do not pass go
            self.logger.info("Countdown aborted (was duration {0})".format(
              self.duration
            ))

class TestCountdown(unittest.TestCase):
    def test_start(self):
        finished = False
        def finish():
            nonlocal finished
            finished = True

        dur=0.8
        interval=0.2
        timer=Countdown(dur, finish, interval=interval)

        started=time.time()
        timer.start()
        duration=time.time()-started

        self.assertTrue(finished)
        self.assertLess(abs(duration-dur),interval/2)

        finished = False
        def tick(t):
            nonlocal abort
            if t>=abort: raise AbortCountdownException("Test stop")
        def finish():
            nonlocal finished
            finished = True
        dur=1.5
        abort=1
        interval=0.5
        timer=Countdown(dur, finish, tick, interval=interval)
        
        started=time.time()
        self.assertRaises(AbortCountdownException, timer.start())
        duration=time.time()-started

        self.assertFalse(finished)
        self.assertLess(abs(duration-abort),interval/2)
        
        dur=0.8
        abort=0.8
        interval=0.1
        finished=False
        timer=Countdown(dur, finish, tick, interval=interval)
        started=time.time()
        timer.start()
        duration=time.time()-started

        self.assertTrue(finished)
        self.assertLess(abs(duration-dur),interval/2)

if __name__=="__main__":
#    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
    logging.getLogger(__name__).setLevel(logging.ERROR)
    unittest.main()
