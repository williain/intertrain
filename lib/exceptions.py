#!/usr/bin/python3
import unittest

class BaseTrainingException(Exception):
    def __init__(self,*args):
        if ".BaseTrainingException" in str(type(self)):
            raise ProtocolError("BaseTrainingException is an abstract exception")
        super().__init__(*args)

    def indented_message(self,indent="  "):
        return '\n'.join([indent+m for m in str(self).split('\n')])

class DefaultError(BaseTrainingException):
    pass

class ParseError(BaseTrainingException):
    pass

class ProtocolError(BaseTrainingException):
    pass

class TestBaseTrainingException(unittest.TestCase):
    def test_raise(self):
        try:
          raise BaseTrainingException("Not allowed")
        except ProtocolError as e:
            self.assertIn("abstract",str(e))

class TestBaseTrainingSubclass(unittest.TestCase):
    def test_raise(self):
        try:
            raise ParseError("Test message")
        except ParseError as e:
            self.assertEqual(str(e),"Test message")

        try:
            raise ParseError("Test message\non two lines")
        except ParseError as e:
            self.assertEqual(str(e),"Test message\non two lines")

    def test_indented_message(self):
        try:
            raise ProtocolError("""Test message
on more than
one line"""
            )
        except ProtocolError as e:
            self.assertEquals(e.indented_message(),"""  Test message
  on more than
  one line"""
            )
        try:
            raise ParseError("""Another message
on multiple lines"""
            )
        except ParseError as e:
            self.assertEquals(e.indented_message(indent="indent"),
              """indentAnother message
indenton multiple lines"""
            )
        try:
            raise DefaultError("Single line messages get indented too")
        except DefaultError as e:
            self.assertEquals(e.indented_message(),
              "  Single line messages get indented too"
            )

if __name__=="__main__":
    unittest.main()
