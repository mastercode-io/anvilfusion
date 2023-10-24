import anvil.server
import anvil.tables.query as q
from anvil.server import Capability
from anvil.tables import app_tables

import functools
import re
from copy import copy
from importlib import import_module
from uuid import uuid4
from datetime import datetime

from ..datamodel.particles import ModelSearchResults
from ..datamodel import types
from . import security


CAMEL_PATTERN = re.compile(r"(?<!^)(?=[A-Z])")


def caching_query(search_function):
    """A decorator to stash the results of a data tables search."""

    @functools.wraps(search_function)
    def wrapper(
            class_name, module_name, page_length, max_depth, with_class_name, **search_args
    ):
        for arg in search_args:
            if '_model_type' in type(search_args[arg]).__dict__:
                ref_obj = search_args[arg]
                ref_row = _get_row(ref_obj.__module__, ref_obj.__class__.__name__, ref_obj.__dict__['uid'])
                search_args[arg] = ref_row
        if 'tenant_uid' not in search_args.keys():
            search_args['tenant_uid'] = anvil.server.session.get('tenant_uid', None)
        if (anvil.server.session['user_permissions'].get('super_admin', False)
                and not anvil.server.session['user_permissions'].get('locked_tenant', False)):
            search_args.pop('tenant_uid', None)
        search_query = search_args.pop('search_query', None)
        table = get_table(module_name, class_name)
        if search_query is not None:
            length = len(table.search(search_query, **search_args))
        else:
            length = len(table.search(**search_args))
        search_args['search_query'] = search_query
        if with_class_name:
            search_args["class_name"] = class_name
        rows_id = str(uuid4())
        anvil.server.session[rows_id] = search_args
        return ModelSearchResults(
            class_name,
            module_name,
            rows_id,
            page_length=page_length,
            max_depth=max_depth,
            length=length,
        )

    return wrapper


def _camel_to_snake(name):
    """Convert a CamelCase string to snake_case"""
    return CAMEL_PATTERN.sub("_", name).lower()


def get_table(module_name, class_name):
    """Return the data table for the given class name"""
    # table_name = _camel_to_snake(class_name)
    models = import_module(module_name)
    table_name = getattr(models, class_name)._table_name
    return getattr(app_tables, table_name)


def get_user_permissions():
    """Return the user permissions"""
    user_permissions = anvil.server.session['user_permissions']
    if 'administrator' not in user_permissions:
        user_permissions['administrator'] = False
    if 'super_admin' not in user_permissions:
        user_permissions['super_admin'] = False
    if 'developer' not in user_permissions:
        user_permissions['developer'] = False
    return user_permissions


def _get_row(module_name, class_name, uid, **search_args):
    """Return the data tables row for a given object instance"""
    search_args['uid'] = uid
    user_permissions = get_user_permissions()
    # if (not user_permissions['super_admin'] or
    #         (user_permissions['developer'] and 'tenant_uid' not in search_args.keys())):
    #     search_args['tenant_uid'] = anvil.server.session.get('tenant_uid', None)
    if (not user_permissions['super_admin']
            and not user_permissions.get('locked_tenant', False)
            and 'tenant_uid' not in search_args.keys()):
        search_args['tenant_uid'] = anvil.server.session.get('tenant_uid', None)
    return get_table(module_name, class_name).get(**search_args)


def _get_row_by(module_name, class_name, prop, value, **search_args):
    """Return the data tables row for a given object instance"""
    search_args[prop] = value
    user_permissions = get_user_permissions()
    # if (not user_permissions['super_admin'] or
    #         (user_permissions['developer'] and 'tenant_uid' not in search_args.keys())):
    #     search_args['tenant_uid'] = anvil.server.session.get('tenant_uid', None)
    if (not user_permissions['super_admin']
            and not user_permissions.get('locked_tenant', False)
            and 'tenant_uid' not in search_args.keys()):
        search_args['tenant_uid'] = anvil.server.session.get('tenant_uid', None)
    return get_table(module_name, class_name).get(**search_args)


def _search_rows(module_name, class_name, uids):
    """Return the data tables rows for a given list of object instances"""
    search_args = {'uid': q.any_of(*uids)}
    if (not anvil.server.session['user_permissions'].get('super_admin', False)
            and not anvil.server.session['user_permissions'].get('locked_tenant', False)
            and 'tenant_uid' not in search_args.keys()):
        search_args['tenant_uid'] = anvil.server.session.get('tenant_uid', None)
    return get_table(module_name, class_name).search(**search_args)


def _serialize_row(table, row):
    cols = table.list_columns()
    row_dict = dict(row)
    for col in cols:
        if col['type'] == 'link_single':
            row_dict[f"_{col['name']}"] = row_dict[col['name']]['uid'] if row_dict[col['name']] is not None else None
            row_dict.pop(col['name'], None)
        elif col['type'] == 'link_multiple':
            row_dict[f"_{col['name']}"] = [row['uid'] for row in row_dict[col['name']]] \
                if row_dict[col['name']] is not None else None
            row_dict.pop(col['name'], None)
        elif col['type'] == 'datetime' or col['type'] == 'date':
            row_dict[col['name']] = row_dict[col['name']].isoformat() if row_dict[col['name']] is not None else None

    return row_dict


def _audit_log(class_name, action, prev_row, new_row):
    log_uid = str(uuid4())
    current_time = datetime.now()
    current_tenant_uid = anvil.server.session.get('tenant_uid', None)
    current_user_uid = anvil.server.session.get('user_uid', None)
    record_uid = prev_row['uid'] if prev_row is not None else new_row['uid']
    log_record = {
        'table_name': class_name,
        'record_uid': record_uid,
        'action_type': action,
        'action_time': current_time,
        'action_by': current_user_uid,
        'previous_state': prev_row,
        'new_state': new_row,
        'tenant_uid': current_tenant_uid,
    }
    app_tables.app_audit_logs.add_row(uid=log_uid, **log_record)


@anvil.server.callable
def get_object(class_name, module_name, uid, max_depth=None):
    """Create a model object instance from the relevant data table row"""
    if security.has_read_permission(class_name, uid):
        module = import_module(module_name)
        cls = getattr(module, class_name)
        instance = cls._from_row(
            _get_row(module_name, class_name, uid), max_depth=max_depth
        )
        if instance is not None:
            if security.has_update_permission(class_name, uid):
                instance.update_capability = Capability([class_name, uid])
            if security.has_delete_permission(class_name, uid):
                instance.delete_capability = Capability([class_name, uid])
        return instance


@anvil.server.callable
def get_object_by(class_name, module_name, prop, value, max_depth=None):
    """Create a model object instance from the relevant data table row"""
    module = import_module(module_name)
    cls = getattr(module, class_name)
    instance = cls._from_row(
        _get_row_by(module_name, class_name, prop, value), max_depth=max_depth
    )
    if instance is not None and security.has_read_permission(class_name, instance.uid):
        if security.has_update_permission(class_name, instance.uid):
            instance.update_capability = Capability([class_name, instance.uid])
        if security.has_delete_permission(class_name, instance.uid):
            instance.delete_capability = Capability([class_name, instance.uid])
        return instance


@anvil.server.callable
def fetch_objects(class_name, module_name, rows_id, page, page_length, max_depth=None):
    """Return a list of object instances from a cached data tables search"""
    # print('Fetch objects', class_name, module_name, rows_id, page, page_length, max_depth)
    search_definition = anvil.server.session.get(rows_id, None).copy()
    if search_definition is not None:
        if (not anvil.server.session['user_permissions'].get('super_admin', False)
                and not anvil.server.session['user_permissions'].get('locked_tenant', False)
                and 'tenant_uid' not in search_definition.keys()):
            search_definition['tenant_uid'] = anvil.server.session.get('tenant_uid', None)
        else:
            search_definition.pop('tenant_uid', None)
        class_name = search_definition.pop("class_name")
        search_query = search_definition.pop("search_query", None)
        if search_query is not None:
            rows = get_table(module_name, class_name).search(search_query, **search_definition)
        else:
            rows = get_table(module_name, class_name).search(**search_definition)
    else:
        rows = []

    start = page * page_length
    end = (page + 1) * page_length
    is_last_page = end >= len(rows)
    if is_last_page:
        del anvil.server.session[rows_id]

    module = import_module(module_name)
    cls = getattr(module, class_name)
    results = (
        [
            get_object(class_name, module_name, row[cls._unique_identifier], max_depth)
            for row in rows[start:end]
        ],
        is_last_page,
    )
    return results


@anvil.server.callable
def fetch_view(class_name, module_name, columns, search_queries, filters):
    """Return a list of rows instances from a cached data tables search"""

    def parse_col_names(model, module, cols):
        if hasattr(module, model):
            cls = getattr(module, model)
        else:
            raise NameError(f'Model class {model} not found')
        dependent_cols = []
        for col in cols:
            if col in cls._computes:
                dependent_cols.extend(cls._computes[col].depends_on)
                cols.remove(col)
        cols = list(set(cols + dependent_cols))
        col_list = ['uid']
        col_dict = {}
        for col_name in cols:
            if '.' in col_name:
                split_point = col_name.index('.')
                top_name = col_name[:split_point]
                if top_name in cls._attributes:
                    col_list.append(top_name)
                elif top_name in cls._relationships:
                    top_model = cls._relationships[top_name].class_name
                    child_cols, child_dict = parse_col_names(top_model, module, [col_name[split_point + 1:]])
                    if top_name in col_dict:
                        col_dict[top_name][0].extend(child_cols)
                        col_dict[top_name][1].update(child_dict)
                    else:
                        col_dict[top_name] = [child_cols, child_dict]
            elif col_name in cls._attributes:
                col_list.append(col_name)
        col_list = list(set(col_list))
        return [col_list, col_dict]

    def build_fetch_list(fetch_list, fetch_dict):
        for key, value in fetch_dict.items():
            key_list, key_dict = value
            fetch_dict[key] = build_fetch_list(key_list, key_dict)
        return q.fetch_only(*fetch_list, **fetch_dict)

    class_module = import_module(module_name)
    cols, links = parse_col_names(class_name, class_module, columns)

    fetch_query = build_fetch_list(cols, links)
    # print('Fetch query', class_name)
    cls = getattr(class_module, class_name)
    for key in filters:
        if key in cls._relationships:
            # print('Filter', key, cls._relationships[key].class_name)
            if not isinstance(filters[key], list):
                filters[key] = [filters[key]]
            # print(filters[key])
            rel_uids = [row['uid'] for row in filters[key]]
            # print(rel_uids)
            rel_rows = [row for row in get_table(module_name, cls._relationships[key].class_name).search(uid=q.any_of(*rel_uids))]
            # print('debug 2')
            filters[key] = q.any_of(*rel_rows)
    # print('Filters', filters)
    if (not anvil.server.session['user_permissions'].get('super_admin', False)
            and not anvil.server.session['user_permissions'].get('locked_tenant', False)
            and not filters.get('tenant_uid', None)):
        filters['tenant_uid'] = anvil.server.session.get('tenant_uid', None)
        print('\nfetch view filters', filters, '\n')

    rows = get_table(module_name, class_name).search(fetch_query, *search_queries, **filters)

    return rows


@anvil.server.callable
@caching_query
def basic_search(class_name, **search_args):
    """Perform a data tables search against the relevant table for the given class"""
    # print('Basic search', class_name, search_args)
    return get_table(class_name).search(**search_args)


@anvil.server.callable
def save_object(instance, audit):
    """Persist an instance to the database by adding or updating a row"""
    class_name = type(instance).__name__
    # table = get_table(class_name)
    table = getattr(app_tables, instance._table_name)
    # print('Save object', class_name, instance, instance._table_name)

    attributes = {
        name: getattr(instance, name)
        for name, attribute in instance._attributes.items()
    }
    single_relationships = {
        name: _get_row(
            relationship.cls.__module__,
            relationship.cls.__name__,
            getattr(instance, name)['uid'],
        )
        for name, relationship in instance._relationships.items()
        if not relationship.with_many and getattr(instance, name) is not None
    }
    multi_relationships = {
        name: list(
            _search_rows(
                relationship.cls.__module__,
                relationship.cls.__name__,
                [
                    member['uid']
                    for member in getattr(instance, name)
                    if member is not None
                ],
            )
        )
        for name, relationship in instance._relationships.items()
        if relationship.with_many and getattr(instance, name) is not None
    }

    members = {**attributes, **single_relationships, **multi_relationships}
    cross_references = [
        {"name": name, "relationship": relationship}
        for name, relationship in instance._relationships.items()
        if relationship.cross_reference is not None
    ]

    has_permission = False
    current_time = datetime.now()
    current_tenant_uid = anvil.server.session.get('tenant_uid', None)
    current_user_uid = anvil.server.session.get('user_uid', None)
    prev_row = None
    new_row = None
    if instance.uid is not None:
        if getattr(instance, "update_capability") is not None:
            Capability.require(instance.update_capability, [class_name, instance.uid])
            has_permission = True
            row = table.get(uid=instance.uid)
            prev_row = _serialize_row(table, row)
            # if instance._model_type == types.ModelTypes.DATA:
            system_attributes = {
                'updated_time': current_time,
                'updated_by': current_user_uid
            }
            if getattr(instance, 'tenant_uid', False):
                system_attributes['tenant_uid'] = instance.tenant_uid
            row.update(**members, **system_attributes)
            new_row = _serialize_row(table, row)
        else:
            raise ValueError("You do not have permission to update this object")
    else:
        if security.has_create_permission(class_name):
            has_permission = True
            uid = str(uuid4())
            instance = copy(instance)
            instance.uid = uid
            # if instance._model_type == types.ModelTypes.DATA:
            # print('tenant_uid in instance?', getattr(instance, 'tenant_uid', None))
            system_attributes = {
                'tenant_uid': getattr(instance, 'tenant_uid', None) or current_tenant_uid,
                'created_time': current_time,
                'created_by': current_user_uid,
                'updated_time': current_time,
                'updated_by': current_user_uid
            }
            # print('system attributes', system_attributes)
            # else:
            #     system_attributes = {}
            row = table.add_row(uid=uid, **members, **system_attributes)
            new_row = _serialize_row(table, row)
            if security.has_update_permission(class_name, uid):
                instance.update_capability = Capability([class_name, uid])
            if security.has_delete_permission(class_name, uid):
                instance.delete_capability = Capability([class_name, uid])
        else:
            raise ValueError("You do not have permission to save this object")

    if audit and new_row is not None:
        action = 'add' if prev_row is None else 'update'
        _audit_log(class_name, action, prev_row, new_row)

    if has_permission:
        # Very simple cross-reference update
        for xref in cross_references:

            # We only update the 'many' side of a cross-reference
            if not xref["relationship"].with_many:
                xref_row = single_relationships[xref["name"]]
                column_name = xref["relationship"].cross_reference

                # We simply ensure that the 'one' side is included in the 'many' side.
                # We don't clean up any possibly redundant entries on the 'many' side.
                if row not in xref_row[column_name]:
                    xref_row[column_name] += [row]

    return instance


@anvil.server.callable
def delete_object(instance, audit):
    """Delete the data tables row for the given model instance"""
    class_name = type(instance).__name__
    Capability.require(instance.delete_capability, [class_name, instance.uid])
    # table = get_table(type(instance).__name__)
    # row = table.get(uid=instance.uid)
    table = getattr(app_tables, instance._table_name)
    row = table.get(uid=instance.uid)
    prev_row = _serialize_row(table, row)
    new_row = {}
    row.delete()
    if audit:
        _audit_log(class_name, 'delete', prev_row, new_row)
