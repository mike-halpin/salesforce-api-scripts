import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from abc import ABC, abstractmethod

class SOQLStatement(ABC):
    def __init__(self, object_name, fields=[]):
        self.object_name = object_name
        self.fields = fields
        self.where_conditions = []
        self.order_by_fields = []

    def add_field(self, field):
        if field not in self.fields:
            self.fields.append(field)

    def remove_field(self, field):
        if field in self.fields:
            self.fields.remove(field)

    def add_condition(self, field, operator, value):
        self.where_conditions.append((field, operator, value))
    
    @abstractmethod
    def construct_query(self):
        pass
    
    def __str__(self):
        return self.construct_query()

class SelectSOQLStatement(SOQLStatement):
    def __init__(self, object_name, fields):
        super().__init__(object_name, fields)
        
    def add_order_by(self, field, direction='ASC'):
        self.order_by_fields.append((field, direction))

    def echo_where_clause(self):
        where_str = ''
        if self.where_conditions:
            where_str = ' AND '.join([f"{field} {operator} {value}" for field, operator, value in self.where_conditions])
            where_str = f"WHERE {where_str}"
            print(f"{where_str}")

        return where_str

    def echo_select_clause(self):
        fields_str = ''
        if self.fields:
            fields_str = ', '.join(self.fields)
            fields_str = f"SELECT {fields_str}"
            print(f"{fields_str}")

        return fields_str

    def echo_from_clause(self):
        from_clause = f"FROM {self.object_name}"
        print(f"{from_clause}")

        return from_clause

    def echo_order_by_clause(self):
        order_by_str = ''
        if self.order_by_fields:
            order_by_str = ', '.join([f"{field} {direction}" for field, direction in self.order_by_fields])
            order_by_str = f"ORDER BY {order_by_str}"
            print(f"{order_by_str}")
        return order_by_str

    def construct_query(self):
        query = f"{self.echo_select_clause()} {self.echo_from_clause()} {self.echo_where_clause()} {self.echo_order_by_clause()}"

        return query

