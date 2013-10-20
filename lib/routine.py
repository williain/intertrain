#!/usr/bin/python3
import io, unittest, collections
import guide, exceptions

class Routine(object):
    """An exercise routine - a list of Exercises that have been prepped with
    the appropriate durations, so that they can be run in series."""

    def __init__(self,guidebook=None):
        """
        Create an exercise routine.

        Optional parameters:
            guidebook   A guidebook which contains the definitions of all
                        the exercises you can add

            If not specified, this class creates its own GuideBook, which you
            can get using get_guidebook and add guides to after the fact.
        """
        self.name=None
        self.desc=None
        self.exercises=[]
        self.guidebook=guidebook
        if self.guidebook==None:
            self.guidebook=guide.GuideBook()

    def get_guidebook(self):
        """Return the live guidebook - please handle with care"""
        return self.guidebook

    def set_name(self,name):
        self.name=name

    def set_description(self,desc):
        self.desc=desc

    def get_name(self):
        return self.name

    def get_description(self):
        return self.desc

    def add_exercise(self,ex_id, duration, rest, read_delay):
        """
        Add a named exercise.

        Parameters:
        ex_id        The id of the exercise to add
        duration     How long to run the exercise for as part of the routine
        rest         The rest period for after the exercise
        read_delay   The read delay, allowing athletes chance to read the
                       instructions before beginning

        Throws:
        KeyError     If the id isn't recognised - it's not defined in any Guides
        """
        ex=self.get_guidebook().get_exercise(ex_id)
        ex.prep(duration, rest, read_delay)
        self.exercises.append(ex)
    
    def get_total_time(self):
        """Sum the total times for all of the exercises"""
        totals=[exercise.get_total_time() for exercise in self.exercises]
        return sum(totals)

    def start(self):
        """Run all the exercises"""
        for exercise in self.exercises:
            exercise.start()
            
class RoutineFile(object):
    desc={
      'rest':'rest period',
      'read_delay':'read delay',
      'name':'set_name()',
      'description':'set_description()'
    }

    def __init__(self):
        self.settings={}
        self.clear_settings()
        self.guidebook=guide.GuideBook()

    def set_default(self, setting, value_str):
        """
        Raises ParseError if value_str isn't a string representing an integer
        """
        if not setting in self.desc or self.desc[setting].endswith('()'):
            raise exceptions.ParseError("{0} is not a valid setting".format(
              repr(setting)
            ))
        else:
            self.settings[setting]=self.__to_int(
              value_str,self.desc[setting]
            )

    def add_guide(self, g):
        """
        Add a guide or guides to any routines created in future

        Throws:
            ProtocolError - if the argument you give it is neither a Guide
                              object or a list of Guides.
        """
        if isinstance(g,guide.Guide):
            self.guidebook.add_guide(g)
        else:
            try:
                for gd in g:
                    self.add_guide(gd)
            except:
                raise exceptions.ProtocolError("Invalid argument to add_guide")

    def load_file(self, filename):
        """
        Load the routine file specified.
        The file will be loaded using any pre-existing default settings
        """
        routine=Routine(guidebook=self.guidebook)
        return self.load_file_into(routine, filename)

    def load_file_into(self, routine, filename):
        """
        Load the specified file into a pre-prepared Routine object.
        The file will be loaded using any pre-existing default settings
        """
        with io.open(filename) as filehandle:
            return self.load_io_into(routine, filehandle)

    def load_io(self,file_io):
        """
        Load the provided file object into a new Routine object.
        The data will be loaded using any pre-existing default settings
        """
        routine=Routine(guidebook=self.guidebook)
        return self.load_io_into(routine,file_io)

    def load_io_into(self,routine,file_io):
        """
        Load a specification from a file object into a pre-prepared Routine
        object. The data will be loaded using any pre-existing default settings
        """
        in_setting=False
        for line in file_io.readlines():
            # Eat the indent - not important to this file format
            line=line.strip()
            if len(line)==0:
                if in_setting:
                    # Ended a multi-line setting
                    in_setting=False
                    try:
                        self.__set_setting(setting,value,routine)
                    except exceptions.ParseError as e:
                        raise exceptions.ParseError("{0}\n  Line:{1}".format(
                          str(e),setting_line
                        ))
                continue
            if line[0]=="#":
                # Comment
                continue
            if in_setting:
                if len(value)>0:
                    value+=' '
                value+=line
                continue
            setline=self.__unescape(line,'=')
            if '\x0b' in setline:
                if setline.endswith('\x0b'):
                    # Multi-line setting
                    setting=setline[:setline.index('\x0b')].lower().strip()
                    if not setting in self.desc:
                        raise exceptions.ParseError(
                          "Unrecognised setting {0}\n  Line:{1}".format(
                            repr(setting), line
                          )
                        )
                    in_setting=True
                    setting_line=line
                    value=""
                else:
                    # Single line setting
                    (setting,value)=setline.split('\x0b')
                    setting=setting.lower().strip()
                    try:
                        self.__set_setting(setting,value,routine)
                    except exceptions.ParseError as e:
                        raise exceptions.ParseError("{0}\n  Line:{1}".format(
                            str(e),line
                          )
                        )
                continue
            exline=self.__unescape(line,',')
            if '\x0b' in exline:
                # Exercise
                (args)=exline.split('\x0b')
                try:
                    self.__add_exercise(routine,args)
                except exceptions.ParseError as e:
                    raise exceptions.ParseError(
                      "{0}:\n  {1}".format(str(e),line)
                    )
            else:
                raise exceptions.ParseError(
                  "Unrecognised line in routine file: {0}".
                  format(line)
                )
        return routine

    def clear_settings(self):
        """
        Unset all of the settings - must be done between subsequent load* calls
        """
        for setting in self.desc:
            if not self.desc[setting].endswith('()'):
                self.settings[setting]=None

    def __add_exercise(self,routine,args):
        """
        Add a named exercise.

        Parameters:
        routine      The routine object to add the exercise to the instructions
                       before beginning
        args         The arguments taken from a routine file including the
                       exercise id, duration, rest and read delay

        Throws:
        DefaultError If either or both of rest and read_delay isn't specified,
                       and neither have they been defined as defaults
        ParseError   If any of the parameters which should be ints aren't
        """
        ex_id=args[0]
        vals=[self.__to_int(args[1],'duration')]
        parms=('rest','read_delay') # Routine.add_exercise parameter order
        for i in range(len(parms)):
            if len(args)>i+2:
                val=self.__to_int(args[i+2],self.desc[parms[i]])
            else:
                val=self.settings[parms[i]]
                if val==None:
                    raise exceptions.DefaultError("""If a default {0} hasn't
been set, you must supply an explicit one""".format(parms[i])
                    )
            vals.append(val)
        if len(args)>len(parms)+2:
            raise exceptions.ParseError(
              "Unrecognised exercise in routine file (too many arguments)"
            )
        routine.add_exercise(ex_id,*vals)

    def __to_int(self, string, meaning):
        """
        Either returns the string as an integer, or raises ParserError
        using 'meaning' as part of the message
        """
        try:
            return int(string,base=10)
        except (TypeError, ValueError) as e:
            raise exceptions.ParseError(
              "{0} is not a valid {1}: not a valid integer".format(
                repr(string),meaning
              )
            )
           
    def __unescape(self,text,char):
        escaped=False
        textout=""
        for c in text:
            if c=='\\' and not escaped:
                escaped=True
            elif c==char and not escaped:
                textout+='\x0b' # Unprintable bell
            else:
                textout+=c
        return textout

    def __set_setting(self,setting,value,routine):
        if not setting in self.desc:
            raise exceptions.ParseError(
              "Unrecognised setting {0}".format(repr(setting))
            )
        if self.desc[setting].endswith('()'):
            function=self.desc[setting][:-2]
            # Call function(value)
            routine.__getattribute__(function)(value) 
        else:
            self.set_default(setting,value)

#####################################################################
# Test code

import exercise

class TestRoutine(unittest.TestCase):
    countstart=0

    def test_init(self):
        r=Routine()
        g=guide.GuideBook()
        r=Routine(g)

    def test_get_guidebook(self):
        g=TestRoutine.simple_guide()
        r=Routine(g)
        self.assertEqual(r.get_guidebook(),g)
        r=Routine()
        r.get_guidebook().add_guide(g)
        # Add an exercise to the guide, after having loaded it
        g.exercises['exercise3']=['name','desc',['tips']]
        # Ensure we can refer to this new exercise in the precreated routine
        RoutineFile().load_io_into(r,io.StringIO("""
            exercise3,1,2,3
        """))
        r=Routine()
        g=TestRoutine.simple_guide2()
        r.get_guidebook().add_guide(g)
        # Delete the exercise we're about to refer to - hee hee!
        del g.exercises['exercise2']
        self.assertRaises(KeyError,RoutineFile().load_io_into,r,io.StringIO("""
            exercise2,4,5,6
        """))

    def test_set_get(self):
        r=Routine()
        r.set_name("Test name")
        self.assertEquals(r.get_name(),"Test name")
        r.set_description("Test description")
        self.assertEquals(r.get_description(),"Test description")

    def test_add_exercise(self):
        r=Routine()
        r.get_guidebook().add_guide(TestRoutine.simple_guide())
        r.get_guidebook().add_guide(TestRoutine.simple_guide2())
        r.add_exercise("exercise1",45,25,64)
        self.assertEqual(len(r.exercises),1)
        self.assertEquals(r.exercises[0].name,"Test Exercise 1")
        self.assertEquals(r.exercises[0].desc,"Test description 1")
        self.assertEquals(r.exercises[0].duration,45)
        self.assertEquals(r.exercises[0].rest,25)
        self.assertEquals(r.exercises[0].read_delay,64)
        r.add_exercise("exercise2",53,24,66)
        self.assertEquals(len(r.exercises),2)
        self.assertEquals(r.exercises[1].name,"Test Exercise 2")
        self.assertEquals(r.exercises[1].duration,53)
        self.assertEquals(r.exercises[1].read_delay,66)
        self.assertRaises(KeyError,r.add_exercise,"exercise3",1,3,4)

    def test_get_total_time(self):
        r=Routine()
        r.get_guidebook().add_guide(TestRoutine.simple_guide2())
        r.add_exercise("exercise2",52,22,12)
        self.assertEqual(r.get_total_time(),52+22+12)
        r.add_exercise("exercise2",32,67,2400)
        self.assertEqual(r.get_total_time(),52+22+12+32+67+2400)

    def test_start(self):
        class DummyExercise(exercise.Exercise):
            def start(self):
                TestRoutine.countstart+=1
        class GuideMock(guide.Guide):
            def get_exercise(self,*args):
                return DummyExercise()
            def get_exercise_ids(self):
                return ["dummy exercise","another dummy","a third dummy"]

        g=guide.GuideBook()
        g.add_guide(GuideMock())
        r=Routine(g)
        r.add_exercise("dummy exercise",1,2,3)
        TestRoutine.countstart=0
        r.start()
        self.assertEquals(TestRoutine.countstart,1)
        r.add_exercise("another dummy",2346,23,2)
        r.add_exercise("a third dummy",5,4,3)
        TestRoutine.countstart=0
        r.start()
        self.assertEquals(TestRoutine.countstart,3)

    def simple_guide():
        stream=io.StringIO("""\
exercise1:
    Name: Test Exercise 1
    Description: Test description 1
""")
        g=guide.Guide()
        g.load_io(stream)
        return g

    def simple_guide2():
        stream=io.StringIO("""\
exercise2:
    Name: Test Exercise 2
    Description: Test description 2
""")
        g=guide.Guide()
        g.load_io(stream)
        return g

class TestRoutineFile(unittest.TestCase):
    def test_load_io_good(self):
        r=self.__make_routine("""
            # Settings
            rest=7
            read_delay=10
            name=Test routine
            description=Test description
            # Exercises
            exercise1,5
            exercise2,8
        """, [TestRoutine.simple_guide(), TestRoutine.simple_guide2()]
        )
        exs=r.exercises
        ex_names=sorted(map(lambda x:x.name,exs))
        self.assertEquals(ex_names,["Test Exercise 1","Test Exercise 2"])
        self.assertEquals(exs[0].duration,5)
        self.assertEquals(exs[1].rest,7)
        self.assertEquals(exs[1].read_delay,10)
        self.assertEquals(r.get_name(),"Test routine")
        self.assertEquals(r.get_description(),"Test description")
        r=self.__make_routine("""
            name=
              Multiline
              name

            # Don't need a description (or a name, even)

            # Test that you can omit rest and read_delay settings if you
            # specify them for each exercise 
            exercise1,5,2,8
            exercise2,4,3,1
        """, [TestRoutine.simple_guide(), TestRoutine.simple_guide2()]
        )
        self.assertEquals(r.exercises[0].read_delay,8)
        self.assertEquals(r.exercises[1].rest,3)
        self.assertEquals(r.get_name(),"Multiline name")

    def test_load_io_missing_settings(self):
        self.assertRaisesRegexp(exceptions.DefaultError,"default read_delay",
          self.__make_routine,"""
            rest=5
            # No default read delay
            exercise1,5,2
          """,TestRoutine.simple_guide()
        )
        self.assertRaisesRegexp(exceptions.DefaultError,"default rest",
          self.__make_routine,"""
            read_delay=8
            # No default rest period
            exercise1,6
          """,TestRoutine.simple_guide()
        )

    def test_load_io_bad(self):
        self.assertRaisesRegexp(exceptions.ParseError,"[Uu]nrecognised line",
          self.__make_routine,"""
            rest=4
            read_delay=3
            exercise1
          """,TestRoutine.simple_guide()
        )
        self.assertRaisesRegexp(exceptions.ParseError,
          "'not a number'.*valid rest",
          self.__make_routine,"""
            rest=not a number
            read_delay=48
            exercise1,6
          """,TestRoutine.simple_guide()
        )
        self.assertRaisesRegexp(exceptions.ParseError,
          "'also not a number'.*valid read delay",
          self.__make_routine,"""
            rest=68
            read_delay=also not a number
            exercise1,2
          """,TestRoutine.simple_guide()
        )
        self.assertRaisesRegexp(exceptions.ParseError,
          "'still not a number'.*valid duration",
          self.__make_routine,"""
            rest=42
            read_delay=21
            exercise1,still not a number
          """,TestRoutine.simple_guide()
        )
        self.assertRaisesRegexp(exceptions.ParseError,
          "'bad rest'.*valid rest",
          self.__make_routine,"""
            rest=24
            read_delay=28
            exercise1,65,bad rest
          """,TestRoutine.simple_guide()
        )
        self.assertRaisesRegexp(exceptions.ParseError,
          "'bad read delay'.*valid read delay",
          self.__make_routine,"""
            rest=39
            read_delay=84
            exercise1,38,4223,bad read delay
          """,TestRoutine.simple_guide()
        )
        self.assertRaisesRegexp(exceptions.ParseError,
          "'bad setting'",
          self.__make_routine,"""
            rest=4
            bad setting=87
          """,TestRoutine.simple_guide()
        )
        self.assertRaisesRegexp(exceptions.ParseError,
          "too many arguments",
          self.__make_routine,"""
            rest=245
            read_delay=2495
            exercise1,32,51,15,15,extra_parm
          """,TestRoutine.simple_guide()
        )

    def test_load_io_missing_exercise(self):
        self.assertRaisesRegexp(KeyError,"not found",
          self.__make_routine,"""
            rest=4
            read_delay=8
            missing_exercise,2
          """,TestRoutine.simple_guide()
        )

    def test_set_default(self):
        rf=RoutineFile()
        rf.set_default("read_delay","103")
        rf.add_guide(TestRoutine.simple_guide())
        r=rf.load_io(io.StringIO("""
          exercise1,265,6
        """))
        self.assertEqual(r.exercises[0].read_delay,103)
        self.assertRaises(exceptions.ParseError,
          rf.set_default,"rest","bad integer"
        )
        self.assertRaises(exceptions.ParseError,
          rf.set_default,"not a setting",4
        )
        
        rf.set_default("rest","13045")
        r=rf.load_io_into(r,io.StringIO("""
          exercise1,245
        """))
        self.assertEqual(r.exercises[1].rest,13045)
        self.assertEqual(r.exercises[1].read_delay,103)

    def test_clear_settings(self):
        rf=RoutineFile()
        rf.set_default("rest","1283")
        rf.set_default("read_delay","148")
        rf.add_guide(TestRoutine.simple_guide())
        s=io.StringIO("""
          exercise1,23
        """)
        r=rf.load_io(s)
        self.assertEqual(r.exercises[0].rest,1283)
        self.assertEqual(r.exercises[0].read_delay,148)
        rf.clear_settings()
        s.seek(0) # Reset s to the start
        self.assertRaises(exceptions.DefaultError, rf.load_io, s)

    def __make_routine(self, filestring, guides):
        rf=RoutineFile()
        rf.add_guide(guides)
        s=io.StringIO(filestring)
        return rf.load_io(s)
        
if __name__=="__main__":
    unittest.main()
