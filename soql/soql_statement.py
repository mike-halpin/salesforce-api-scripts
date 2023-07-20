class SOQLStatement:
    def __init__(self, object_name, fields=[]):
        self.object_name = object_name
        self.fields = fields

    def add_field(self, field):
        if field not in self.fields:
            self.fields.append(field)

    def remove_field(self, field):
        if field in self.fields:
            self.fields.remove(field)

    def add_condition(self, field, operator, value):
        condition = f"{field} {operator} {repr(value)}"
        self.where_conditions.append(condition)


class SelectSOQLStatement(SOQLStatement):
    def __init__(self, object_name, fields):
        super().__init__(object_name)
        self.where_conditions = []
        self.order_by_fields = []

    def add_condition(self, field, operator, value):
        self.where_conditions.append((field, operator, value))

    def add_order_by(self, field, direction='ASC'):
        self.order_by_fields.append((field, direction))

    def construct_query(self):
        fields_str = ', '.join(self.fields)
        query = f"SELECT {fields_str} FROM {self.object_name}"

        if self.where_conditions:
            where_str = ' AND '.join([f"{field} {operator} {value}" for field, operator, value in self.where_conditions])
            query += f" WHERE {where_str}"

        if self.order_by_fields:
            order_by_str = ', '.join([f"{field} {direction}" for field, direction in self.order_by_fields])
            query += f" ORDER BY {order_by_str}"

        return query

