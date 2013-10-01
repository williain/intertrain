import countdown
import time, logging, subprocess, sys

class Exercise(object):
    def __init__(self, name, desc="", tips=[], loglevel=logging.DEBUG):
        """Create a named exercise object"""
        self.lastsound=None

        self.name=name
        self.desc=desc
        if not hasattr(tips,'append'):
            # Ensure tips is a list
            tips=[str(tips)]
        self.tips=tips
        self.messagelogger=logging.getLogger('exerciseMessages')
        self.messagelogger.setLevel(loglevel)

    def prep(self, duration, rest=5, read_delay=5):
        """Set the exercise durations.  Arguments:
        duration - time to exercise for in seconds
        rest - time afterwards to allow the athlete to rest
        read_delay - time before to read and understand the instructions

        Throws: Exception for invalid input
        """
        if duration<0:
            raise Exception("Not a time traveller: Can't exercise for "+repr(duration)+" second(s)")
        if rest<0:
            raise Exception("Not a time traveller: Can't rest for "+repr(rest)+" second(s)")
        if read_delay<0:
            raise Exception("Not a time traveller: Can't let the user read for "+repr(read_delay)+" second(s)")
        self.reading=countdown.Countdown(read_delay, self.session_start)
        self.countdown=countdown.Countdown(duration, self.finish, self.tick)
        self.duration=duration
        self.rest=rest
        self.read_delay=read_delay

    def start(self):
        """Run the exercise
        
        Throws: Exception is not already prepared
        """

        if not self.duration:
            raise Exception("Can't start an exercise without first preparing it")

        self.messagelogger.info("Exercise: "+self.name+", for "+str(self.duration)+"s")
        self.messagelogger.info("Get ready...")
        self.reading.start()

    def session_start(self):
        """Called by self.reading once the read delay is over"""
        self.__play_sound('sounds/boop.ogg')
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
            self.__play_sound('sounds/beep.ogg')

    def finish(self):
        """Used by self.countdown to complete the exercise"""
        if self.messagelogger.isEnabledFor(logging.INFO):
            sys.stdout.write("\n")
        self.messagelogger.info("Finish (exercise "+self.name+"): "+str(self.rest)+"s rest")
        self.__play_sound('sounds/boop.ogg')
        rest_start=time.time()
        while time.time()-rest_start < self.rest:
            time.sleep(0.2)
        self.messagelogger.info("-"*70)

    def __clear_sound(self):
        if self.lastsound != None:
            self.lastsound.terminate()
            self.lastsound=None

    def __play_sound(self, soundfile):
        """Play a soundfile and return immediately"""
        self.__clear_sound()
        # TODO Not platform independent
        self.lastsound=subprocess.Popen(['mplayer', soundfile], stdout=open('/dev/null','w'), stderr=open('/dev/null','w'))

    def __del__(self):
        self.__clear_sound()

def Test():
    # Test default arguments
    exercise=Exercise("TEST_DEFAULT")
    exercise.prep(6)
    time_start=time.time()
    exercise.start()
    duration=time.time()-time_start
    if abs(duration-16)<0.2:
        print("TEST_DEFAULT OK: Expected duration of 16, got",duration)
    else:
        print("TEST_DEFAULT FAIL: Expected duration of 16, got",duration)
    del exercise
    
    # Test overriding defaults
    exercise=Exercise("TEST_OVERRIDE1")
    exercise.prep(15, 2, read_delay=0)
    time_start=time.time()
    exercise.start()
    duration=time.time()-time_start
    if abs(duration-17)<0.2:
        print("TEST_OVERRIDE1 OK: Expected duration of 17, got",duration)
    else:
        print("TEST_OVERRIDE1 FAIL: Expected duration of 17, got",duration)
    del exercise

    exercise=Exercise("TEST_OVERRIDE2")
    exercise.prep(5, 0, read_delay=3)
    time_start=time.time()
    exercise.start()
    duration=time.time()-time_start
    if abs(duration-8)<0.2:
        print("TEST_OVERRIDE2 OK: Expected duration of 8, got",duration)
    else:
        print("TEST_OVERRIDE2 FAIL: Expected duration of 8, got",duration)
    del exercise

    #==================================
    # Test desc and tips argments

    # Test positional arguments
    exercise=Exercise("TEST_ARGS_POS", "desc", "tips")
    if exercise.desc!="desc":
        print("TEST_ARGS_POS FAIL: Expected description of 'desc', got",str(exercise.desc))
    elif not (len(exercise.tips)==1 and exercise.tips[0]=="tips"):
        print("TEST_ARGS_POS_FAIL: Expected tips of ['tips'], got",str(exercise.tips))
    else:
        print("TEST_ARGS_POS OK")
    del exercise

    exercise=Exercise("TEST_ARGS_ALTPOS", tips="tips", desc="desc")
    if exercise.desc!="desc":
        print("TEST_ARGS_ALTPOS FAIL: Expected description of 'desc', got",str(exercise.desc))
    elif not exercise.tips==["tips"]:
        print("TEST_ARGS_ALTPOS_FAIL: Expected tips of ['tips'], got",str(exercise.tips))
    else:
        print("TEST_ARGS_ALTPOS OK")
    del exercise

    exercise=Exercise("TEST_TIPS", "desc", ["tip1", "tip2"])
    if exercise.tips==["tip1","tip2"]:
        print("TEST_TIPS OK")
    else:
        print("TEST_TIPS FAIL: Expected tips of ['tip1','tip2'], got",str(exercise.tips))

    #==================================
    # Test bad arguments
    #TODO: Check exception message/make exception types (TBD)
    exercise=Exercise("TEST_BADPREP")
    try:
        exercise.start()
        print("TEST_BADPREP FAIL: Expected exception for not prepping")
    except Exception as e:
        print("TEST_BADPREP OK: Got exception",str(e))
    finally:
        del exercise

    try:
        exercise=Exercise("TEST_BADDUR")
        exercise.prep(-1)
        print("TEST_BADDUR FAIL: Expected expected for negative duration")
    except Exception as e:
        print("TEST_BADDUR OK: Got exception",str(e))
    finally:
        del exercise

    try:
        exercise=Exercise("TEST_BADREST")
        exercise.prep(10, -2)
        print("TEST_BADREST FAIL: Expected exception for negative rest period")
    except Exception as e:
        print("TEST_BADREST OK: Got exception",str(e))
    finally:
        del exercise

    try:
        exercise=Exercise("TEST_BADDELAY")
        exercise.prep(10, read_delay=-3)
        print("TEST_BADDELAY FAIL: Expected exception for negative read delay")
    except Exception as e:
        print("TEST_BADDELAY OK: Got exception",str(e))
    finally:
        del exercise
