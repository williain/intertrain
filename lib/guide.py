#!/usr/bin/python3
import yaml,io,logging,unittest
import exercise, exceptions

class Guide(object):
    def __init__(self):
        pass

    def load_file(self, filename):
        """
        Load exercises from a file.

        Raises yaml.error.YAMLError on a parse failure
        Raises io.IOError on a bad filename or other IO error
        """
        self.load_io(io.open(filename))
        self.filename=filename

    def load_io(self, iostream):
        """
        Load exercises from a stream.
        
        Raises ParseError on a parse failure
        """
        try:
            yamlfile=yaml.safe_load(iostream)
        except yaml.error.YAMLError as e:
            raise exceptions.ParseError(e)
        self.db=self.parse(yamlfile)
        self.filename="StreamIO"

    def parse(self, yamlfile):
        self.exercises={}
        for ex_id in yamlfile:
            if not self.valid_id(ex_id):
                raise exceptions.ParseError("Exercise id '{0}' is not valid; ".
                  format(ex_id)+"Exercise ids must not contain newlines."+
                  "and must not begin with whitespace")
            ex=yamlfile[ex_id]
            try:
                name=ex.get('Name')
            except AttributeError:
                raise exceptions.ParseError("Badly formed exercise: "+ex_id)
            desc=ex.get('Description')
            tips=ex.get('Tips')

            name=self.yaml_parse_as_scalar(name)
            desc=self.yaml_parse_as_scalar(desc)
            self.exercises[ex_id]=[name, desc, tips]

    def yaml_parse_as_scalar(self, entry):
        if hasattr(entry,'keys'):
            # Dictionary-like
            raise exceptions.ParseError("Expected scalar; got "+str(entry))
        elif hasattr(entry,'append'):
            # Sequence type
            return "\n".join(entry)
        else:
            return entry

    def valid_id(self,e_id):
        return not(
          "\n" in e_id
          or e_id.startswith(' ')
          or e_id.startswith('\t')
        )

    def get_exercise_ids(self):
        """Get a list of all the exercises this guide documents"""
        return set(self.exercises.keys())

    def get_exercise(self,exercise_id):
        """
        Get a new instance of the named Exercise object
        
        Throws:
            KeyError if the named exercise_id doesn't exist.
        """
        (name, desc, tips) = self.exercises[exercise_id]
        return exercise.Exercise(name, desc, tips)

    def __contains__(self, exercise):
        if hasattr(exercise,'get_exercise_ids'):
            return exercise.get_exercise_ids().issubset(self.get_exercise_ids())
        else:
            return str(exercise) in self.get_exercise_ids()

    def __eq__(self, exercise):
        return exercise in self and self in exercise

class GuideBook(object):
    def __init__(self):
        self.guides=[]

    def get_guides(self):
        return self.guides

    def add_guide(self,guide):
        """
        Add a Guide so that any generated Routine files referencing this
        guidebook can find the exercises.
        """
        if not guide in self.guides:
            # Build a map of all exercises, pointing at the last file they
            # were defined in
            exercises={}
            for o_guide in self.get_guides():
                for exercise in o_guide.get_exercise_ids():
                    exercises[exercise]=o_guide.filename
            # From the map make a map of only the exercises duplicated in this
            # guide
            duplicates={}
            for exercise in guide.get_exercise_ids():
                if exercise in exercises.keys():
                    duplicates[exercise]=exercises[exercise]
                
            self.guides.append(guide)

            if len(duplicates)>0:
                w_exercises=duplicates.keys()
                w_files=list(duplicates.values())
                w_files.append(guide.filename)
                raise Warning(
                  "Duplicate exercise(s) '{0}' loaded from files '{1}'".
                  format("', '".join(w_exercises),"', '".join(w_files)
                  )+"; last loaded takes precedence"
                )
    
    def get_exercise(self,exercise_id):
        """
        Return a new instance of the named Exercise

        Throws:
            KeyError    If none of the guides contain the named exercise
        """
        if len(self.get_guides())==0:
            raise KeyError('No guides imported')
        for guide in reversed(self.get_guides()):
            if exercise_id in guide:
                return guide.get_exercise(exercise_id)
        raise KeyError(
          'Exercise {0} not found in any current guide'.format(exercise_id)
        )

class TestGuide(unittest.TestCase):
    def setUp(self):
        self.yaml_header='''
%YAML 1.1
---'''
        stream=io.StringIO(self.yaml_header+'''
kettle_swing:
    Name: Kettlebell swing
    Description: With the legs apart and the kettlebell suspended in both hands, crouching slightly, stand as it pushes back against your thighs so it swings upin front of you, keeping your arms locked, peaking level with your shoulders.
    Tips:
        ["Keep your back straight as you crouch for this exercise, crouching with your legs so you get the maximum power from your thighs to swing the kettlebell up."]


kettle_clean_right:
    Name: Kettlebell clean to right shoulder
    Description:
        &desc_clean
        Start in a half crouch with the kettlebell suspended between the legs.  Lift the kettlebell to the shoulder as you stand and breathe in, and return it to the starting position as you breathe out.
    Tips:
        &tips_clean
        [It's simpler to start with the kettle bell on the floor ahead of you. Crouch down and grab it and swing it back between your legs as you start to stand up, so that it swings forward as you stand and you can pull your arm in to bring it to your shoulder.]

kettle_clean_left:
    Name: Kettlebell clean to left shoulder
    Description: *desc_clean
    Tips: *tips_clean

test_exercise:
    Name: Test exercise
    Description:
        Test description
    Tips:
        [&test_tip
        Test tip 1]

test_exercise_2:
    Name: Test exercise 2
    Description:
        [Test description 2,
        on two lines]
    Tips:
        [*test_tip,
        Test tip 2,
        Test tip 3]
''')
        self.g=Guide()
        self.g.load_io(stream)
        stream=io.StringIO(self.yaml_header+'''
test_exercise:
    Name: Test exercise duplicate
    Description: Test description duplicate
''')
        self.g2=Guide()
        self.g2.load_io(stream)

    def test_ids(self):
        self.assertEquals(self.g.get_exercise_ids(),
          set(['kettle_clean_left',
            'kettle_clean_right',
            'kettle_swing',
            'test_exercise',
            'test_exercise_2'
          ])
        )

    def test_bad_parse(self):
        s=io.StringIO(self.yaml_header+"""
bad_ex: foo"""
        )
        self.assertRaisesRegexp(exceptions.ParseError,"[Bb]adly formed",Guide().load_io,s)

        s=io.StringIO(self.yaml_header+"""
missing_space:
    Name: Missing space
    Description:What's wrong with this?"""
        )
        self.assertRaisesRegexp(exceptions.ParseError,"expected ':'",Guide().load_io,s)

        s=io.StringIO(self.yaml_header+"""
too_deep:
    Name:
        Description: Oops, accidentally nested"""
        )
        self.assertRaisesRegexp(exceptions.ParseError,"[Ee]xpected scalar",Guide().load_io,s)
        s=io.StringIO(self.yaml_header+"""
"   preceding spaces not allowed":
    Name: Bad spaces"""
        )
        self.assertRaisesRegexp(exceptions.ParseError,"not allowed",Guide().load_io,s)

        s=io.StringIO(self.yaml_header+"""
"included
newlines are bad too":
    Name: Bad newlines"""
        )
        self.assertRaisesRegexp(exceptions.ParseError,"not allowed",Guide().load_io,s)

    def test_bad_id(self):
        self.assertRaisesRegexp(KeyError,"test_missing",self.g.get_exercise,'test_missing')

    def test_eq(self):
        self.assertTrue(self.g2 in self.g)
        self.assertFalse(self.g in self.g2)
        self.assertNotEquals(self.g, self.g2)
        g3=self.g
        self.assertEquals(self.g, g3)

    def test_exercise_1(self):
        e=self.g.get_exercise('test_exercise')
        self.assertEquals(e.name,'Test exercise')
        self.assertEquals(e.desc,'Test description')
        self.assertEquals(e.tips,['Test tip 1'])

    def test_exercise_2(self):
        e=self.g.get_exercise('test_exercise_2')
        self.assertEquals(e.name,'Test exercise 2')
        self.assertEquals(e.desc,'Test description 2\non two lines')
        self.assertEquals(e.tips,['Test tip 1','Test tip 2','Test tip 3'])

    def test_book(self):
        b=GuideBook()
        self.assertRaises(KeyError,b.get_exercise,'test_exercise')
        b.add_guide(self.g)
        self.assertEquals(b.get_exercise('test_exercise').name,
          'Test exercise'
        )
        self.assertEquals(b.get_exercise('test_exercise_2').name,
          'Test exercise 2'
        )
        self.assertRaisesRegexp(Warning,
          "Duplicate exercise.*test_exercise",b.add_guide,self.g2
        ) # Still added the exercises; see below
        self.assertEquals(b.get_exercise('test_exercise').name,
          'Test exercise duplicate'
        )
        self.assertEquals(b.get_exercise('test_exercise_2').name,
          'Test exercise 2'
        )

    def runTest(self):
        self.test_ids()
        self.test_bad_id()
        self.test_exercise_1()
        self.test_exercise_2()
        self.test_eq()
        self.test_book()

if __name__=="__main__":
    unittest.main()
