import unittest
import re
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ..soql_statement import SOQLStatement, SelectSOQLStatement


class TestSOQLStatement(unittest.TestCase):
    def test_add_field(self):
        statement = SelectSOQLStatement('Object', ['Field1', 'Field2'])
        statement.add_field('TEST')
        self.assertIn('TEST', statement.fields)

    def test_remove_field(self):
        statement = SelectSOQLStatement('Object', ['Field1', 'Field2'])
        statement.remove_field('Field1')
        self.assertNotIn('Field1', statement.fields)

    def test_add_condition(self):
        statement = SelectSOQLStatement('Object', ['Field1', 'Field2'])
        statement.add_condition('Field1', '=', 10)
        self.assertEqual(re.sub('%s', statement.__str__(), ''), re.sub('%s', "SELECT Field1, Field2 FROM Object WHERE Field1 = 10", ''))

    def test_construct_query_without_conditions_and_order_by(self):
        statement = SelectSOQLStatement('Object', ['Field1', 'Field2'])
        query = statement.construct_query()
        self.assertEqual(re.sub('%s', query, ''), re.sub('%s', "SELECT Field1, Field2 FROM Object", ''))

    def test_construct_query_with_conditions_and_order_by(self):
        statement = SelectSOQLStatement('Object', ['Field1', 'Field2'])
        statement.add_condition('Field1', '=', 10)
        statement.add_order_by('Field2', direction='DESC')
        query = statement.construct_query()
        expected_query = "SELECT Field1, Field2 FROM Object WHERE Field1 = 10 ORDER BY Field2 DESC"
        self.assertEqual(query, expected_query)


if __name__ == '__main__':
    unittest.main()