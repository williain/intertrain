#!/usr/bin/python3
import unittest

class BaseTrainingException(Exception):
#    def __init__(self,*args):
#        super().__init__(*args)

    def indented_message(self,indent="  "):
        return '\n'.join([indent+m for m in str(self).split('\n')])

class DefaultError(BaseTrainingException):
    pass

class ParseError(BaseTrainingException):
    pass

class ProtocolError(BaseTrainingException):
    pass

class TestBaseTrainingException(unittest.TestCase):
    def test_indented_message(self):
        try:
            raise BaseTrainingException("""Test message
on more than
one line"""
            )
        except BaseTrainingException as e:
            self.assertEquals(e.indented_message(),"""  Test message
  on more than
  one line"""
            )
        try:
            raise BaseTrainingException("""Another message
on multiple lines"""
            )
        except BaseTrainingException as e:
            self.assertEquals(e.indented_message(indent="indent"),
              """indentAnother message
indenton multiple lines"""
            )
        try:
            raise BaseTrainingException("Single line messages get indented too")
        except BaseTrainingException as e:
            self.assertEquals(e.indented_message(),
              "  Single line messages get indented too"
            )

if __name__=="__main__":
    unittest.main()
