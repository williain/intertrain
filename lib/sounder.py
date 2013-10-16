#!/usr/bin/python3

import os,unittest,sys
import exceptions, sounderinterface, plat

class Sounder(sounderinterface.SounderInterface):
    """
    A Sounder wrapper.  Make an instance of it and you actually get
    back an implementation of SounderInterface for your platform
    """

    def __new__(self):
        return sounderinterface.Sounders().get_sounder(os.name)

class TestSounder(unittest.TestCase):
    class DummySounder(sounderinterface.SounderInterface):
        pass

    def test_init(self):
        # Check we've at least loaded a couple of Sounders
        self.assertGreaterEqual(len(sounderinterface.Sounders().sounders),2)
        # Wipe out the sounders database
        sounderinterface.Sounders().sounders={}
        s=Sounder()

        self.assertEquals(type(s),sounderinterface.QuietSounder)

        sounderinterface.Sounders().register(os.name,TestSounder.DummySounder)
        s=Sounder()

        self.assertEquals(type(s),TestSounder.DummySounder)

if __name__=="__main__":
    unittest.main()
