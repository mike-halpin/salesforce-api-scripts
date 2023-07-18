from simple_salesforce import format_soql

def get_last_created_with_field(object_name, field_name):
    query_string = f'SELECT CreatedDate, {field_name} FROM {object_name} WHERE {field_name} != null ORDER BY CreatedDate DESC LIMIT 1'
    return format_soql(query_string)

def get_count_of_field_value(object_name, field_name):
    query_string = f'SELECT FieldName, COUNT(Id) FROM {object_name} GROUP BY {field_name} ORDER BY COUNT(Id)'
    return format_soql(query_string)

def get_count_of_fields_values(object_name, field_names):
    query_string = f'SELECT {", ".join([f"COUNT({field_name})" for field_name in field_names])} FROM {object_name}'
    return format_soql(query_string)

def get_most_common_values(object_name, field_name, groups_to_count=3):
    query_string = f'SELECT {field_name}, COUNT(Id) FROM {object_name} GROUP BY {field_name} ORDER BY COUNT(Id) DESC LIMIT {groups_to_count}'
    return format_soql(query_string)