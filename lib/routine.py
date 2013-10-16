#!/usr/bin/python3
import io, unittest, collections
import guide, exceptions

class Routine(object):
    """An exercise routine - a list of Exercises that have been prepped with
    the appropriate durations, so that they can be run in series."""

    class Defaults(object):
        desc={
          'rest':'rest period',
          'read_delay':'read delay',
          'name':'name',
          'description':'description'
        }

        def __init__(self):
            self.settings={}
            for setting in self.desc:
                self.settings[setting]=None

        def get_description(self, setting):
            return self.desc[setting]

        def set(self,setting, value):
            self.desc[setting] # Check the setting name is valid
            self.settings[setting]=value

        def get(self,setting):
            return self.settings[setting]
            
    def __init__(self,rest=None,read_delay=None,guidebook=None):
        """
        Create an exercise routine.

        Optional parameters:
            rest        The default rest period, after each exercise
            read_delay  The default read delay, giving athletes time to read
                        and understand the instructions for the exercise
                        they're about to do.

            If either of these parameters is not set, either here, or via the
            appropriate setters, any Exercise objects added must be fully
            prepped.

            guidebook   A guidebook which contains the definitions of all
                        the exercises you can add

            If not specified, this class creates its own GuideBook, which you
            can get using get_guidebook and add guides to after the fact.
        """
        self.defaults=Routine.Defaults()
        self.defaults.set("rest",rest)
        self.defaults.set("read_delay",read_delay)
        self.exercises=[]
        if guidebook==None:
            self.guidebook=guide.GuideBook()

    def set_default(self, setting, value_str):
        """
        Raises ParseError if value_str isn't a string representing an integer
        """
        try:
            if setting=="rest" or setting=="read_delay":
                self.defaults.set(setting, self.__to_int(value_str))
            else:
                self.defaults.set(setting, value_str)
        except (KeyError,exceptions.ParseError) as e:
            raise exceptions.ParseError(
              "{0} is not a valid {1}:\n{2}".format(
                repr(value_str),self.defaults.get_description(setting),e.indented_message()
              )
            )

    def get_guidebook(self):
        """Return the live guidebook - please handle with care"""
        return self.guidebook

    def add_exercise(self,ex_id, duration, rest=None, read_delay=None):
        """
        Add a named exercise.

        Parameters:
        ex_id        The id of the exercise to add
        duration     How long to run the exercise for as part of the routine
        rest         OPTIONAL The rest period for after the exercise
        read_delay   OPTIONAL The read delay, allowing athletes chance to read
                       the instructions before beginning

        Throws:
        KeyError     If the id isn't recognised - it's not defined in any Guides
        DefaultError If either or both of rest and read_delay isn't specified,
                       and neither have they been defined as defaults
        """
        ex=self.get_guidebook().get_exercise(ex_id)
        if rest==None:
            rest=self.defaults.get('rest')
            if rest==None:
                raise exceptions.DefaultError(
                  "If a default rest period hasn't been set, you must supply an explicit one"
                )
        if read_delay==None:
            read_delay=self.defaults.get('read_delay')
            if read_delay==None:
                raise exceptions.DefaultError(
                  "If a default read_delay hasn't been set, you must supply an explicit one"
                )
        ex.prep(duration, rest, read_delay)
        self.exercises.append(ex)

    def load_file(self, filename):
        """
        Load the routine file specified.
        """
        self.load_io(io.open(filename))

    def __to_int(self, string):
        """
        Either returns the string as an integer, or raises ParseError
        """
        try:
            a=int(string,base=10)
        except (TypeError, ValueError):
            raise exceptions.ParseError(
              "{0} is not a valid integer".format(repr(string))
            )
        return a


    def __wrap_to_int(self, string, meaning):
        """
        Either returns the string as an integer, or raises ParserError
        using 'meaning' as part of the message
        """
        try:
            return self.__to_int(string)
        except exceptions.ParseError as e:
            raise exceptions.ParseError(
              "{0} is not a valid {1}:\n{2}".format(
                repr(string),meaning,e.indented_message()
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

    def load_io(self,file_io):
        """Load a specification from a definition in stream io"""
        in_setting=False
        for line in file_io.readlines():
            # Eat the indent - not important to this file format
            line=line.strip()
            if len(line)==0:
                if in_setting:
                    # Ended a multi-line setting
                    in_setting=False
                    try:
                        self.set_default(setting,value)
                    except exceptions.ParseError:
                        raise exceptions.ParseError(
                          "Unrecognised setting '{0}'\n  Line:{1}".format(
                          setting,line)
                        )
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
                    setting=setline[:setline.index('\x0b')]
                    try:
                        self.defaults.get_description(setting)
                    except exceptions.ParseError:
                        raise exceptions.ParseError(
                          "Unrecognised setting '{0}'\n  Line:{1}".format(
                            setting, line
                          )
                        )
                    in_setting=True
                    value=""
                else:
                    # Single line setting
                    (setting,value)=setline.split('\x0b')
                    setting=setting.lower().strip()
                    try:
                        self.set_default(setting,value)
                    except KeyError:
                        raise exceptions.ParseError(
                          "Unrecognised setting '{0}'\n  Line:{1}".format(
                            setting,line
                          )
                        )
                continue
            exline=self.__unescape(line,',')
            if '\x0b' in exline:
                # Exercise
                (args)=exline.split('\x0b')
                ex_id=args[0]
                duration=self.__wrap_to_int(args[1],'duration')
                rest=None
                read_delay=None
                if len(args)>=3:
                    rest=self.__wrap_to_int(args[2],'rest period')
                if len(args)==4:
                    read_delay=self.__wrap_to_int(args[3],'read delay')
                elif len(args)>4:
                    raise exceptions.ParseError(
                      "Unrecognised exercise in routine file ({0}):\n  {1}".
                        format('too many commas',line)
                    )
                self.add_exercise(ex_id,duration,rest,read_delay)
            else:
                raise exceptions.ParseError(
                  "Unrecognised line in routine file: {0}".
                  format(line)
                )

    def start(self):
        """Run all the exercises"""
        for exercise in self.exercises:
            exercise.start()
            
import exercise

class TestRoutine(unittest.TestCase):
    def test_load_file_good(self):
        r=self.__make_routine("""
            # Settings
            rest=7
            read_delay=10
            name=Test routine
            description=Test description
            # Exercises
            exercise1,5
            exercise2,8
        """, [self.__simple_guide(), self.__simple_guide2()]
        )
        exs=r.exercises
        ex_names=sorted(map(lambda x:x.name,exs))
        self.assertEquals(ex_names,["Test Exercise 1","Test Exercise 2"])
        self.assertEquals(exs[0].duration,5)
        self.assertEquals(exs[1].rest,7)
        self.assertEquals(exs[1].read_delay,10)
        self.assertEquals(r.defaults.get('name'),"Test routine")
        self.assertEquals(r.defaults.get('description'),"Test description")
        r=self.__make_routine("""
            name=
              Multiline
              name

            # Don't need a description (or a name, even)
            # Test that you can omit rest and read_delay settings if you specify them for each exercise 
            exercise1,5,2,8
            exercise2,4,3,1
        """, [self.__simple_guide(), self.__simple_guide2()]
        )
        self.assertEquals(r.exercises[0].read_delay,8)
        self.assertEquals(r.exercises[1].rest,3)
        self.assertEquals(r.defaults.get('name'),"Multiline name")

    def test_get_guidebook(self):
        r=Routine()
        g=self.__simple_guide()
        r.get_guidebook().add_guide(g)
        # Add an exercise to the guide, after having loaded it
        g.exercises['exercise3']=['name','desc',['tips']]
        # Ensure we can refer to this new exercise in the precreated routine
        r.load_io(io.StringIO("""
            exercise3,1,2,3
        """))
        r=Routine()
        g=self.__simple_guide2()
        r.get_guidebook().add_guide(g)
        # Delete the exercise we're about to refer to - hee hee!
        del g.exercises['exercise2']
        self.assertRaises(KeyError,r.load_io,io.StringIO("""
            exercise2,4,5,6
        """))

    def test_load_file_missing_settings(self):
        self.assertRaisesRegexp(exceptions.DefaultError,"default read_delay",
          self.__make_routine,"""
            rest=5
            # No default read delay
            exercise1,5,2
          """,[self.__simple_guide()]
        )
        self.assertRaisesRegexp(exceptions.DefaultError,"default rest",
          self.__make_routine,"""
            read_delay=8
            # No default rest period
            exercise1,6
          """,[self.__simple_guide()]
        )

    def test_load_file_bad(self):
        self.assertRaisesRegexp(exceptions.ParseError,"[Uu]nrecognised line",
          self.__make_routine,"""
            rest=4
            read_delay=3
            exercise1
          """,[self.__simple_guide()]
        )
        self.assertRaisesRegexp(exceptions.ParseError,
          "'not a number'.*valid rest",
          self.__make_routine,"""
            rest=not a number
            read_delay=48
            exercise1,6
          """,[self.__simple_guide()]
        )
        self.assertRaisesRegexp(exceptions.ParseError,
          "'also not a number'.*valid read delay",
          self.__make_routine,"""
            rest=68
            read_delay=also not a number
            exercise1,2
          """,[self.__simple_guide()]
        )
        self.assertRaisesRegexp(exceptions.ParseError,
          "'still not a number'.*valid duration",
          self.__make_routine,"""
            rest=42
            read_delay=21
            exercise1,still not a number
          """,[self.__simple_guide()]
        )
        self.assertRaisesRegexp(exceptions.ParseError,
          "'bad rest'.*valid rest",
          self.__make_routine,"""
            rest=24
            read_delay=28
            exercise1,65,bad rest
          """,[self.__simple_guide()]
        )
        self.assertRaisesRegexp(exceptions.ParseError,
          "'bad read delay'.*valid read delay",
          self.__make_routine,"""
            rest=39
            read_delay=84
            exercise1,38,4223,bad read delay
          """,[self.__simple_guide()]
        )
        self.assertRaisesRegexp(exceptions.ParseError,
          "Unrecognised setting.*'bad setting'",
          self.__make_routine,"""
            rest=4
            bad setting=87
          """,[self.__simple_guide()]
        )
        self.assertRaisesRegexp(exceptions.ParseError,
          "too many commas",
          self.__make_routine,"""
            rest=245
            read_delay=2495
            exercise1,32,51,15,15,extra_parm
          """,[self.__simple_guide()]
        )

    def test_load_file_missing_exercise(self):
        self.assertRaisesRegexp(KeyError,"not found",
          self.__make_routine,"""
            rest=4
            read_delay=8
            missing_exercise,2
          """,[self.__simple_guide()]
        )

    def __make_routine(self, filestring, guides):
        r=Routine()
        for guide in guides:
            r.get_guidebook().add_guide(guide)
        s=io.StringIO(filestring)
        r.load_io(s)
        return r
        
    def __simple_guide(self):
        stream=io.StringIO("""\
exercise1:
    Name: Test Exercise 1
    Description: Test description 1
""")
        g=guide.Guide()
        g.load_io(stream)
        return g

    def __simple_guide2(self):
        stream=io.StringIO("""\
exercise2:
    Name: Test Exercise 2
    Description: Test description 2
""")
        g=guide.Guide()
        g.load_io(stream)
        return g

if __name__=="__main__":
    unittest.main()
