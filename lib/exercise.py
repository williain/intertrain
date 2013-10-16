#!/usr/bin/python3

import countdown,exceptions,sounder
import time, logging, sys, unittest

class Exercise(object):
    def __init__(self, name, desc="", tips=[]):
        """Create a named exercise object"""
        self.name=name
        self.desc=desc
        if not hasattr(tips,'append'):
            # Ensure tips is a list
            tips=[str(tips)]
        self.tips=tips
        self.messagelogger=logging.getLogger(__name__)
        self.sounder=sounder.Sounder()

    def prep(self, duration, rest=5, read_delay=5):
        """Set the exercise durations.  Arguments:
        duration - time to exercise for in seconds
        rest - time afterwards to allow the athlete to rest
        read_delay - time before to read and understand the instructions

        Throws: Exception for invalid input
        """
        if duration<0:
            raise exceptions.ParseError(
              "Not a time traveller: Can't exercise for {0} second(s)".
              format(repr(duration))
            )
        if rest<0:
            raise exceptions.ParseError(
              "Not a time traveller: Can't rest for {0} second(s)".
              format(repr(rest))
            )
        if read_delay<0:
            raise exceptions.ParseError(
              "Not a time traveller: Can't let the user read for {0} second(s)".
              format(repr(read_delay))
            )
        self.reading=countdown.Countdown(read_delay, self.session_start)
        self.countdown=countdown.Countdown(duration, self.finish, self.tick)
        self.duration=duration
        self.rest=rest
        self.read_delay=read_delay

    def get_total_duration(self):
        return self.read_delay+self.duration+self.rest

    def start(self):
        """Run the exercise
        
        Throws: Exception is not already prepared
        """

        if not hasattr(self,'duration'):
            raise exceptions.ProtocolError(
              "Can't start an exercise without first preparing it"
            )

        self.messagelogger.info("Exercise: "+self.name+", for "+str(self.duration)+"s")
        self.messagelogger.info("Get ready...")
        self.reading.start()

    def session_start(self):
        """Called by self.reading once the read delay is over"""
        self.sounder.play('sounds/boop.ogg')
        self.messagelogger.info("Start exercise")
        self.countdown.start()

    def tick(self,clock):
        """Used by self.countdown to inform the athlete of progress
        Prints dots if INFO logging is enabled
        Logs the last ten seconds at DEBUG level
        Provides an audible indicator for the last five seconds (it beeps)

        """
        if self.messagelogger.isEnabledFor(logging.INFO):
            sys.stdout.write(".")
            sys.stdout.flush()
        time_left=self.duration-clock
        if time_left<10:
            self.messagelogger.debug(str(time_left)+"...")
        if time_left<5 and time_left>0:
            self.sounder.play('sounds/beep.ogg')

    def finish(self):
        """Used by self.countdown to complete the exercise"""
        if self.messagelogger.isEnabledFor(logging.INFO):
            sys.stdout.write("\n")
        self.messagelogger.info("Finish (exercise "+self.name+"): "+str(self.rest)+"s rest")
        self.sounder.play('sounds/boop.ogg')
        rest_start=time.time()
        while time.time()-rest_start < self.rest:
            time.sleep(0.2)
        self.messagelogger.info("-"*70)

    def __del__(self):
        self.sounder.stop()

import sounderinterface 

class TestExercise(unittest.TestCase):
    mock=True
    quiet=True
    time=0

    class MockCountdown(countdown.Countdown):
        def start(self):
            if TestExercise.mock:
                # Don't actually countdown - just add the time
                TestExercise.time+=self.duration
                self.func_finish()
            else:
                super().start()

    class MockExercise(Exercise):
        def __init__(self,*args):
            super().__init__(*args)
            if TestExercise.quiet:
                self.sounder=sounderinterface.QuietSounder()

        def start(self):
            TestExercise.time=0
            # Plug in our MockCountdown object, to allow mocking
            self.reading=TestExercise.MockCountdown(
              self.reading.duration, self.reading.func_finish
            )
            self.countdown=TestExercise.MockCountdown(
              self.countdown.duration,
              self.countdown.func_finish,
              self.countdown.func_tick
            )
            super().start()

        def finish(self):
            if TestExercise.mock:
                TestExercise.time+=self.rest
            else:
                super().finish()
            
    def test_init_args(self):
        exercise=Exercise("TEST_ARGS_POS", "desc", "tips")
        self.assertEqual(exercise.desc,"desc")
        self.assertEqual(exercise.tips,["tips"])
        del exercise

        exercise=Exercise("TEST_ARGS_ALTPOS", tips="tips", desc="desc")
        self.assertEqual(exercise.desc,"desc")
        self.assertEqual(exercise.tips,["tips"])
        del exercise

        exercise=Exercise("TEST_TIPS", "desc", ["tip1", "tip2"])
        self.assertEqual(exercise.tips,["tip1","tip2"])

    def test_prep_bad(self):
        exercise=Exercise("TEST_PREP_BAD")
        self.assertRaisesRegexp(exceptions.ProtocolError,"without first prep",
          exercise.start
        )
        del exercise

        exercise=Exercise("TEST_PREP_BADDUR")
        self.assertRaisesRegexp(exceptions.ParseError,"[Cc]an't exercise for",
          exercise.prep,-1
        )
        del exercise

        exercise=Exercise("TEST_PREP_BADREST")
        self.assertRaisesRegexp(exceptions.ParseError,"[Cc]an't rest for",
          exercise.prep,10, -2
        )
        del exercise

        exercise=Exercise("TEST_PREP_BADDELAY")
        self.assertRaisesRegexp(exceptions.ParseError,"[Cc]an't .*read for",
          exercise.prep,10, read_delay=-3
        )
        del exercise

    def test_prep(self):
        exercise=Exercise("TEST_PREP_DEFAULT")
        exercise.prep(2)
        self.assertEquals(exercise.duration,2)
        self.assertEquals(exercise.rest,5)
        self.assertEquals(exercise.read_delay,5)
        exercise=Exercise("TEST_PREP_OVERRIDE")
        exercise.prep(3,2,1)
        self.assertEquals(exercise.duration,3)
        self.assertEquals(exercise.rest,2)
        self.assertEquals(exercise.read_delay,1)

    def test_start(self):
        # Test default arguments
        exercise=TestExercise.MockExercise("TEST_START_DEFAULT")
        exercise.prep(1)
        duration=self.__timed_run(exercise)
        self.__assert_time(duration, 11)
        del exercise
    
    def test_start_override(self):
        # Test overriding defaults
        exercise=TestExercise.MockExercise("TEST_OVERRIDE1")
        exercise.prep(4, 1, 0)
        duration=self.__timed_run(exercise)
        self.__assert_time(duration,5)
        del exercise

        exercise=TestExercise.MockExercise("TEST_OVERRIDE2")
        exercise.prep(2, 0, read_delay=2)
        duration=self.__timed_run(exercise)
        self.__assert_time(duration,4)
        del exercise

    def __timed_run(self,exercise):
        time_start=time.time()
        exercise.start()
        duration=time.time()-time_start
        if self.mock:
            duration=TestExercise.time
        return duration

    def __assert_time(self,time,expected_time):
        if self.mock:
            self.assertEqual(time,expected_time)
        else:
            self.assertLess(abs(time-expected_time),0.2)

    def test_get_total_duration(self):
        exercise=Exercise("TEST_TOTAL_DUR")
        exercise.prep(86)
        self.assertEqual(exercise.get_total_duration(),96)
        del exercise
        exercise=Exercise("TEST_TOTAL_DUR_OVERRIDE")
        exercise.prep(35,rest=32,read_delay=53)
        self.assertEqual(exercise.get_total_duration(),120)

if __name__=='__main__':
    logging.basicConfig(format='.')
    logging.getLogger('countdown').setLevel(logging.ERROR)
    logging.getLogger(__name__).setLevel(logging.ERROR)
    unittest.main()
