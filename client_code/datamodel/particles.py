import sys
import anvil.server
import anvil.js
import datetime
from . import types
from ..tools.utils import AppEnv, get_plural_name, get_table_name


SYSTEM_TENANT_UID = '00000000-0000-0000-0000-000000000000'


class Attribute:
    """A class to represent an attribute of a model object class.
    Attributes are persisted as columns on the class's relevant data table
    """

    def __init__(self, 
                 field_type=types.FieldTypes.SINGLE_LINE,
                 label=None,
                 schema=None,
                 required=False,
                 default=None,
                 is_uid=False,
                 is_unique=False,
                 ):
        self.field_type = field_type
        self.label = label
        self.schema = schema
        self.required = required
        self.default = default
        self.is_uid = is_uid
        self.is_unique = is_unique

    def props(self):
        return {'field_type': self.field_type, 'required': self.required,
                'default': self.default, 'is_uid': self.is_uid, 'schema': self.schema}


class AttributeValue:
    """A class to represent the instance value of an attribute."""

    def __init__(self, name, value, title=None):
        self.name = name
        self.value = value
        self.title = title or name.title()

    def to_dict(self):
        return {"name": self.name, "value": self.value, "title": self.title}


class Relationship:
    """A class to represent a relationship between two model object classes.
    These are persisted as data tables linked columns.
    """

    def __init__(
            self, class_name, required=False, with_many=False, cross_reference=None
    ):
        self.field_type = types.FieldTypes.RELATIONSHIP
        self.class_name = class_name
        self.required = required
        self.default = None
        if with_many:
            self.default = []
        self.with_many = with_many
        self.cross_reference = cross_reference

    @property
    def cls(self):
        try:
            return getattr(sys.modules[self.__module__], self.class_name)
        except AttributeError:
            return getattr(sys.modules[self.__module__[:self.__module__.rfind(".")]], self.class_name)


class Computed:
    """A class to represent the computed property of a model object."""

    def __init__(self, depends_on, compute_func, field_type=types.FieldTypes.SINGLE_LINE):
        self.required = False
        self.field_type = field_type
        self._depends_on = depends_on
        self._compute_func = compute_func

    @property
    def depends_on(self):
        return self._depends_on

    def compute(self, cls, args, grid_view=False):
        value = getattr(cls, self._compute_func)(args)
        if grid_view and isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
            value = anvil.js.window.Date(int(value.strftime('%s')) * 1000)
        return value


class ModelSearchResultsIterator:
    """A paging iterator over the results of a search cached on the server"""

    def __init__(self, class_name, module_name, rows_id, page_length, page, max_depth=None, background_task_id=None):
        self.class_name = class_name
        self.module_name = module_name
        self.rows_id = rows_id
        self.page_length = page_length
        self.next_page = page
        self.page = page
        self.is_last_page = False
        self.max_depth = max_depth
        self.background_task_id = background_task_id
        self.iterator = iter([])

    def __next__(self):
        try:
            return next(self.iterator)
        except StopIteration:
            if self.is_last_page or self.next_page > self.page:
                raise
            results, self.is_last_page = anvil.server.call(
                "fetch_objects",
                self.class_name,
                self.module_name,
                self.rows_id,
                self.next_page,
                self.page_length,
                self.max_depth,
                self.background_task_id,
            )
            self.iterator = iter(results)
            self.next_page += 1
            return self.__next__()


@anvil.server.serializable_type
class ModelSearchResults:
    """A class to provide lazy loading of search results"""

    def __init__(
            self, class_name, module_name, rows_id, page_length, page, max_depth, length, background_task_id=None
    ):
        self.class_name = class_name
        self.module_name = module_name
        self.rows_id = rows_id
        self.page_length = page_length or length
        self.page = page
        self.max_depth = max_depth
        self._length = length
        self.count = length
        self.total_pages = length // page_length + 1 if length % page_length else length // page_length
        self.background_task_id = background_task_id
        # print('ModelSearchResults', self.background_task_id)

    def __len__(self):
        return self._length

    def __iter__(self):
        return ModelSearchResultsIterator(
            self.class_name,
            self.module_name,
            self.rows_id,
            self.page_length,
            self.page,
            self.max_depth,
            self.background_task_id,
        )


def attribute_props(self, name):
    """A factory function to pass Attribute properties"""
    attr = getattr(self, name, None)
    return attr.props()


def attribute_value(self, name, title=None):
    """A factory function to generate AttributeValue instances"""
    value = getattr(self, name, None)
    return AttributeValue(name=name, value=value, title=title)


def _constructor(attributes, relationships, computes, system_attributes):
    """A function to return the __init__ function for the eventual model class"""
    # We're just merging dicts here but skulpt doesn't support the ** operator
    members = attributes.copy()
    members.update(relationships)
    members.update(computes)
    members.update(system_attributes)

    def init(self, **kwargs):
        self.uid = kwargs.pop("uid", None)

        # Check that we've received arguments for all required members
        required_args = [name for name, member in members.items() if hasattr(member, 'required') and member.required]
        for name in required_args:
            if name not in kwargs:
                raise ValueError(f"No argument provided for required {name}")

        # Check that the arguments received match the model and set the instance attributes if so
        for name, value in kwargs.items():
            if name not in members:
                raise ValueError(
                    f"{type(self).__name__}.__init__ received an invalid argument: '{name}'"
                )
            else:
                setattr(self, name, value)

        # Set the default instance attributes for optional members missing from the arguments
        for name, member in members.items():
            if name not in kwargs:
                value = member.default if hasattr(member, 'default') else None
                setattr(self, name, value)

        # Compute the values of any computed members and set the instance attributes
        for name, computed in computes.items():
            args = {dep: getattr(self, dep) for dep in computed.depends_on}
            setattr(self, name, computed.compute(self.__class__, args))

    return init


# Base class for model types to give it a common type name
class ModelTypeBase:
    pass


def _equivalence(self, other):
    """A function to assert equivalence between client and server side copies of model
    instances"""
    return type(self) == type(other) and self.uid == other.uid


def _getitem(self, key):
    """A function to provide dict like indexing"""
    return getattr(self, key, None)


def _setitem(self, key, value):
    setattr(self, key, value)


def _update(self, attrs):
    for key, value in attrs.items():
        setattr(self, key, value)


def _from_row(unique_identifier, attributes, relationships, computes, system_attributes):
    """A factory function to generate a model instance from a data tables row."""

    @classmethod
    def instance_from_row(cls, row, cross_references=None, max_depth=None, depth=0):
        if anvil.server.context.type == "client":
            raise TypeError(
                "_from_row is a server side function and cannot be called from client code"
            )

        if row is None:
            return None

        if cross_references is None:
            cross_references = set()

        attrs = dict(row)
        attrs = {
            key: value
            for key, value in attrs.items()
            if key in attributes or key in system_attributes or key == "uid"
        }
        if "uid" not in attrs:
            attrs["uid"] = attrs[unique_identifier]

        for name, relationship in relationships.items():
            xref = None
            attrs[name] = None

            if relationship.cross_reference is not None:
                xref = (cls.__name__, attrs["uid"], name)

            if xref is not None and xref in cross_references:
                break

            if xref is not None:
                cross_references.add(xref)

            if max_depth is None or depth < max_depth:
                if not relationship.with_many:
                    attrs[name] = relationship.cls._from_row(
                        row[name], cross_references, max_depth, depth + 1
                    )
                else:
                    attrs[name] = []
                    if row[name]:
                        attrs[name] = [
                            relationship.cls._from_row(
                                member, cross_references, max_depth, depth + 1
                            )
                            for member in row[name]
                        ]

        for name, computed in computes.items():
            args = {dep: attrs[dep] for dep in computed.depends_on}
            attrs[name] = computed.compute(cls, args)

        return cls(**attrs)

    return instance_from_row


@classmethod
def _get(cls, uid, max_depth=None):
    """Provide a method to fetch an object from the server"""
    # print('get context', anvil.server.context)
    return anvil.server.call(
        "get_object",
        cls.__name__,
        cls.__module__,
        uid,
        max_depth,
        background_task_id=getattr(anvil.server.context, 'background_task_id', None),
    )
    # return anvil.server.call("get_object", cls.__name__, AppEnv.data_models.__name__, uid, max_depth)


@classmethod
def _get_by(cls, prop, value, max_depth=None):
    """Provide a method to fetch an object from the server"""
    # print('get_by context', anvil.server.context)
    return anvil.server.call(
        "get_object_by",
        cls.__name__,
        cls.__module__,
        prop,
        value,
        max_depth,
        background_task_id=getattr(anvil.server.context, 'background_task_id', None),
    )
    # return anvil.server.call("get_object_by", cls.__name__, AppEnv.data_models.__name__, prop, value, max_depth)


@classmethod
def _search(
        cls,
        page_length=100,
        page=1,
        max_depth=None,
        server_function=None,
        with_class_name=True,
        **search_args,
):
    """Provides a method to retrieve a set of model instances from the server"""
    _server_function = server_function or "basic_search"
    results = anvil.server.call(
        _server_function,
        cls.__name__,
        cls.__module__,
        page_length,
        page,
        max_depth,
        with_class_name,
        background_task_id=getattr(anvil.server.context, 'background_task_id', None),
        **search_args,
    )
    return results


def get_col_value(cls, data, col, get_relationships=False):
    if '.' not in col:
        if col not in cls._computes:
            value = data[col] if not isinstance(data, list) else [row[col] for row in data]
        else:
            value = cls._computes[col].compute(cls, data, grid_view=True) if not isinstance(data, list) \
                else [cls._computes[col].compute(cls, x, grid_view=True) for x in data]
        if isinstance(value, list):
            # print(col, value)
            value = ', '.join([str(v) for v in value] if value and isinstance(value[0], dict) else value)

        parent = col
    else:
        parent, col = col.split('.', 1)
        value = data[parent]
        if value is not None:
            if parent in cls._attributes:
                value = data[parent][col]
                parent = f'{parent}.{col}'
            else:
                rel = getattr(sys.modules[cls.__module__], cls._relationships[parent].class_name)
                # rel = getattr(sys.modules[AppEnv.data_models.__name__], cls._relationships[parent].class_name)
                if get_relationships:
                    if cls._relationships[parent].with_many:
                        rel_value = [rel.get(x['uid']) for x in data[parent]]
                    else:
                        rel_value = rel.get(data[parent]['uid'])
                    data[parent] = rel_value
                value, _ = get_col_value(rel, data[parent], col)
                parent = f'{parent}.{col}'

    if isinstance(value, (datetime.date, datetime.datetime)):
        value = anvil.js.window.Date(int(value.strftime('%s')) * 1000)
    elif isinstance(value, dict) and '.' not in parent:
        value = ', '.join([str(value[k]) for k in value.keys() if value[k]])
    value = value or ''
    return value, parent.replace('.', '__')


def _get_row_view(self, columns, include_row=True, get_relationships=False):
    row_view = {'uid': self.uid if self.uid else ''}
    for col in columns:
        if not col.get('no_data', False):
            value, field = get_col_value(self.__class__, self, col['name'], get_relationships=get_relationships)
            row_view[field] = value
    if include_row:
        row_view['row'] = self.get(self.uid) if self.uid else None
    return row_view


@classmethod
def _get_grid_view(cls, view_config, search_queries=None, filters=None, include_rows=False):
    """Provides a method to retrieve a set of model instances from the server"""
    stime = datetime.datetime.now()
    results = anvil.server.call('get_grid_view', cls, view_config, search_queries, filters, include_rows)
    etime = datetime.datetime.now()
    # print('get_grid_view', cls.__name__, (etime - stime))
    return results


@classmethod
def _get_json_view(cls, view_config, search_queries=None, filters=None, include_rows=False):
    """Provides a method to retrieve a set of model instances from the server"""
    results = anvil.server.call('get_grid_view',
                                cls, view_config, search_queries, filters, include_rows, json=True)
    return results


@classmethod
def _get_json_schema(cls):
    json_schema = {}
    fields = []
    for name in cls._attributes.keys():
        fields.append(name)
    json_schema['fields'] = fields
    relationships = {}
    for name, relationship in cls._relationships.items():
        relationships[name] = relationship.cls.get_json_schema()
    json_schema['relationships'] = relationships
    return json_schema


def _to_json_dict(self, json_schema=None, integration_uid=None):
    json_dict = {'uid': self.uid}
    if not json_schema:
        json_schema = self.get_json_schema()
    for field in json_schema.get('fields', []):
        value = getattr(self, field, None)
        if value is not None:
            if isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
                value = value.isoformat()
            elif (isinstance(value, list) and
                  (isinstance(value[0], datetime.datetime) or isinstance(value[0], datetime.date))):
                value = [v.isoformat() for v in value]
        json_dict[field] = value
    for relationship in json_schema.get('relationships', {}).keys():
        rel_instance = getattr(self, relationship, None)
        if isinstance(rel_instance, list):
            json_dict[relationship] = [
                rel.to_json_dict(json_schema['relationships'].get(relationship, None), integration_uid)
                for rel in rel_instance
            ]
        elif rel_instance:
            # print('rel_instance', rel_instance, relationship, json_schema['relationships'].get(relationship, None))
            json_dict[relationship] = rel_instance.to_json_dict(
                json_schema['relationships'].get(relationship, None),
                integration_uid
            )
        else:
            json_dict[relationship] = None
    if 'remote_links' in json_dict:
        link_id = json_dict['remote_links'].get(integration_uid, None)
        if link_id:
            json_dict['link_id'] = link_id
        json_dict.pop('remote_links', None)
    return json_dict


def _save(self, audit=True):
    """Provides a method to persist an instance to the database"""
    instance = anvil.server.call(
        "save_object",
        self,
        audit,
        background_task_id=getattr(anvil.server.context, 'background_task_id', None),
    )
    if self.uid is None:
        self.uid = instance.uid
    return instance


def _delete(self, audit=True):
    """Provides a method to delete an instance from the database"""
    anvil.server.call("delete_object", self, audit)


def _validate(self):
    """Provides a method to validate an instance"""
    return True, None


def model_type(cls):
    """A decorator to provide a usable model class"""
    class_members = {
        key: value for key, value in cls.__dict__.items() if not key.startswith("__")
    }
    attributes = {
        key: value
        for key, value in class_members.items()
        if isinstance(value, Attribute)
    }
    unique_identifier = "uid"
    unique_identifiers = [key for key, value in attributes.items() if value.is_uid]
    if unique_identifiers:
        if len(unique_identifiers) > 1:
            raise AttributeError("Multiple unique identifiers defined")
        else:
            unique_identifier = unique_identifiers[0]
    
    _singular_name = class_members.get('_singular_name', cls.__name__)
    _plural_name = class_members.get('_plural_name', get_plural_name(_singular_name))
    _table_name = class_members.get('_table_name', get_table_name(_plural_name))
    _title = class_members.get('_title', attributes.get('name', next(iter(attributes.values()), _singular_name)))

    relationships = {
        key: value
        for key, value in class_members.items()
        if isinstance(value, Relationship)
    }
    for relationship in relationships.values():
        relationship.__module__ = cls.__module__
        # relationship.__module__ = AppEnv.data_models.__name__

    computes = {
        key: value
        for key, value in class_members.items()
        if isinstance(value, Computed)
    }

    methods = {key: value for key, value in class_members.items() if callable(value)}
    class_attributes = {
        key: value
        for key, value in class_members.items()
        if not isinstance(value, (Attribute, Relationship, Computed))
    }

    class_properties = {
        key: value
        for key, value in class_members.items()
        if isinstance(value, property)
    }

    system_attributes = {
        'tenant_uid': None,
        'created_time': None,
        'created_by': None,
        'updated_time': None,
        'updated_by': None,
    }

    members = {
        "__module__": cls.__module__,
        "__init__": _constructor(attributes, relationships, computes, system_attributes),
        "__eq__": _equivalence,
        "__getitem__": _getitem,
        "__setitem__": _setitem,
        "_attributes": attributes,
        "_relationships": relationships,
        "_computes": computes,
        "_properties": class_properties,
        "_from_row": _from_row(unique_identifier, attributes, relationships, computes, system_attributes),
        "_unique_identifier": unique_identifier,
        "_system_attributes": system_attributes,
        "_model_type": class_members.get('_model_type', types.ModelTypes.DATA),
        "_singular_name": _singular_name,
        "_plural_name": _plural_name,
        "_table_name": _table_name,
        "_title": _title,
        "update_capability": None,
        "delete_capability": None,
        "search_capability": None,
        "attribute_props": attribute_props,
        "attribute_value": attribute_value,
        "get": _get,
        "get_by": _get_by,
        "search": _search,
        "get_grid_view": _get_grid_view,
        "get_row_view": _get_row_view,
        "get_json_view": _get_json_view,
        "get_json_schema": _get_json_schema,
        "to_json_dict": _to_json_dict,
        "validate": _validate,
        "update": _update,
        "save": _save,
        "expunge": _delete,
        "delete": _delete,
    }
    members.update(methods)
    members.update(class_attributes)

    model = type(cls.__name__, (ModelTypeBase,), members)
    return anvil.server.portable_class(model)
