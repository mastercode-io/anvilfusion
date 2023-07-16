from .utils import Enumeration

# Model types
MODEL_TYPES = {
    'system': 'system',
    'data': 'data',
}
ModelTypes = Enumeration(MODEL_TYPES)


# Field types
FIELD_TYPES = {
    'uid': {
        'ColumnType': 'string',
        'InputType': 'TextInput',
        'GridType': 'string',
        'GridFormat': '',
    },
    'single_line': {
        'ColumnType': 'string',
        'InputType': 'TextInput',
        'GridType': 'string',
        'GridFormat': '',
    },
    'multi_line': {
        'ColumnType': 'string',
        'InputType': 'MultiLineInput',
        'GridType': 'string',
        'GridFormat': '',
    },
    'number': {
        'ColumnType': 'number',
        'InputType': 'NumberInput',
        'GridType': 'number',
        'GridFormat': '',
    },
    'decimal': {
        'ColumnType': 'number',
        'InputType': 'NumberInput',
        'GridType': 'number',
        'GridFormat': 'N2',
    },
    'currency': {
        'ColumnType': 'number',
        'InputType': 'NumberInput',
        'GridType': 'number',
        'GridFormat': 'C2',
    },
    'date': {
        'ColumnType': 'date',
        'InputType': 'DateInput',
        'GridType': 'date',
        'GridFormat': 'dd/MM/yyyy',
    },
    'datetime': {
        'ColumnType': 'datetime',
        'InputType': 'DateTimeInput',
        'GridType': 'datetime',
        'GridFormat': 'dd/MM/yyyy hh:mm',
    },
    'time': {
        'ColumnType': 'datetime',
        'InputType': 'TimeInput',
        'GridType': 'datetime',
        'GridFormat': 'hh:mm',
    },
    'boolean': {
        'ColumnType': 'boolean',
        'InputType': 'CheckboxInput',
        'GridType': 'boolean',
        'GridFormat': '',
    },
    'email': {
        'ColumnType': 'string',
        'InputType': 'TextInput',
        'GridType': 'string',
        'GridFormat': '',
    },
    'address': {
        'ColumnType': 'simpleObject',
        'InputType': 'AddressInput',
        'GridType': 'string',
        'GridFormat': '',
    },
    'hyperlink': {
        'ColumnType': 'simpleObject',
        'InputType': 'HyperlinkInput',
        'GridType': 'string',
        'GridFormat': '',
    },
    'signature': {
        'ColumnType': 'string',
        'InputType': 'SignatureInput',
        'GridType': 'string',
        'GridFormat': '',
    },
    'object': {
        'ColumnType': 'simpleObject',
        'InputType': 'MultiLineInput',
        'GridType': 'string',
        'GridFormat': '',
    },
    'media': {
        'ColumnType': 'media',
        'InputType': 'FileUploadInput',
        'GridType': 'media',
        'GridFormat': '',
    },
    'file_upload': {
        'ColumnType': 'simpleObject',
        'InputType': 'FileUploadInput',
        'GridType': 'string',
        'GridFormat': '',
    },
    'enum_single': {
        'ColumnType': 'string',
        'InputType': 'DropdownInput',
        'GridType': 'string',
        'GridFormat': '',
    },
    'enum_multi': {
        'ColumnType': 'simpleObject',
        'InputType': 'DropdownInput',
        'GridType': 'string',
        'GridFormat': '',
    },
    'relationship': {
        'ColumnType': 'link',
        'InputType': 'DropdownInput',
        'GridType': 'string',
        'GridFormat': '',
    },
}
FieldTypes = Enumeration(FIELD_TYPES)
