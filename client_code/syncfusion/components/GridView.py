import anvil.server
import anvil.js
from anvil.js.window import ej, jQuery

from .. import app
from ..app.constants import *
from ..orm_client.model import *
from ..orm_client import enumerations as enums
from .. import Forms

import string
import uuid
import json
import sys
from datetime import datetime

GRID_DEFAULT_FILTER_SETTINGS = {'type': 'Menu'}
GRID_DEFAULT_TOOLBAR_ITEMS = ['Add', 'Edit', 'Delete', 'Search']
GRID_DEFAULT_MODES = ['Sort', 'Filter', 'InfiniteScroll', 'Toolbar', 'Edit', 'ForeignKey']
GRID_MODE_TO_SWITCH = {
    'Sort': 'allowSorting',
    'Filter': 'allowFiltering',
    'Group': 'allowGrouping',
    'Page': 'allowPaging',
    'InfiniteScroll': 'enableInfiniteScrolling',
    'ExcelExport': 'allowExcelExport',
    'PdfExport': 'allowPdfExport',
    'Reorder': 'allowReordering',
    'Resize': 'allowResizing',
    'RowDD': 'allowRowDragAndDrop',
    'Selection': 'allowSelection',
}
GRID_DEFAULT_EDIT_SETTINGS = {
    'allowAdding': True,
    'allowEditing': True,
    'allowDeleting': True,
    'mode': 'Dialog',
    'allowEditOnDblClick': True,
    'showConfirmDialog': True,
    'showDeleteConfirmDialog': True,
    'allowScrolling': True
}
GRID_HEIGHT_OFFSET = 65
GRID_DEFAULT_COLUMN_WIDTH = 150


def get_grid_view(view_config, search_queries=None, filters=None, include_rows=False):
    cls = getattr(sys.modules[__name__], view_config['model'])
    search_queries = search_queries or []
    filters = filters or {}
    return cls.get_grid_view(view_config, search_queries, filters, include_rows)


def get_model_attribute(class_name, attr_name):
    cls = getattr(sys.modules[__name__], class_name)
    if attr_name == '_title':
        attr_name = cls._title
    attr = None
    if attr_name in cls._attributes:
        attr = cls._attributes[attr_name]
    elif attr_name in cls._computes:
        attr = cls._computes[attr_name]
    elif '.' in attr_name:
        attr_name = attr_name.split('.')
        if attr_name[0] in cls._attributes:
            attr = cls._attributes[attr_name[0]]
        elif attr_name[0] in cls._relationships:
            attr, _ = get_model_attribute(cls._relationships[attr_name[0]].class_name, '.'.join(attr_name[1:]))
    return attr, attr_name


class BaseGridView:
    def __init__(self,
                 container_id=None,
                 title=None,
                 model=None,
                 view_name=None,
                 view_config=None,
                 search_queries=None,
                 filters=None,
                 ):

        self.grid_height = None
        self.grid_el_id = None
        self.container_id = container_id
        self.container_el = None
        self.model = model
        self.search_queries = search_queries
        self.filters = filters

        print('BaseGridView', view_name)
        if view_name or view_config:
            if view_config is not None:
                self.view_config = view_config
            else:
                view_obj = appGridViews.get_by('name', view_name)
                self.view_config = json.loads(view_obj['config'].replace("'", "\""))
            self.model = self.view_config['model']
            self.grid_class = getattr(sys.modules[__name__], self.model)
        else:
            self.grid_class = getattr(sys.modules[__name__], self.model)
            self.view_config = {'model': self.model}
            view_columns = []
            model_members = self.grid_class._attributes.copy()
            model_members.update(self.grid_class._computes)
            for attr_name, attr in model_members.items():
                view_columns.append({
                    'name': attr_name,
                    'label': string.capwords(attr_name.replace("_", " ")),
                })
            for attr_name, attr in self.grid_class._relationships.items():
                title_attr, title_name = get_model_attribute(attr.class_name, '_title')
                view_columns.append({
                    'name': f"{attr_name}.{title_name}",
                    'label': string.capwords(attr_name.replace("_", " ")),
                })
            self.view_config['columns'] = view_columns

        grid_columns = [{'field': 'uid', 'headerText': 'UID', 'visible': False, 'isPrimaryKey': True, 'width': '0px'}]
        self.row_actions = {}
        for column in self.view_config['columns']:
            if column.get('row_action', False):
                continue
            # {commands: [{buttonOption:{content: 'Details', click: onClick, cssClass: details-icon}}],
            # headerText: 'Customer Details'}
            # grid_column = {
            #     'headerText': '',
            #     'template': f"<div id=\"row_action_{column['name']}\"></div>",
            #     'textAlign': 'Left',
            #     'customAttributes': {'class': 'align-top'},
            #     'width': column.get('width', None) or GRID_DEFAULT_COLUMN_WIDTH,
            # }
            # self.row_actions[f"row_action_{column['name']}"] = column['row_action']
            # else:
            else:
                # print('column', column['name'])
                col_attr, _ = get_model_attribute(self.model, column['name'])
                grid_column = {
                    'field': column['name'].split('.')[0] if '.' in column['name'] else column['name'],
                    'headerText': column['label'],
                    'type': col_attr.field_type.GridType,
                    'format': column.get('format', None) or col_attr.field_type.GridFormat,
                    'displayAsCheckBox': col_attr.field_type == enums.FieldTypes.BOOLEAN,
                    'textAlign': 'Left',
                    'customAttributes': {'class': 'align-top'},
                    'width': column.get('width', None) or GRID_DEFAULT_COLUMN_WIDTH,
                    # 'valueAccessor': self.format_value,
                    # 'formatter': self.get_value,
                    # def get_value(column, data):
                    #   return '<span style="color:' + (data['Verified'] ? 'green' : 'red') +
                    #   '"><i>' + data['Verified'] + '</i><span>';
                }
            grid_columns.append(grid_column)
        self.grid_view = {'config': self.view_config.copy()}
        self.grid_view['config']['columns'] = grid_columns

        # configure Grid control
        self.grid_title = title if title is not None else app.lib.camel_to_title(self.model)
        self.grid_config = {}
        self.grid_data = []
        self.db_data = {}
        self.grid_config['columns'] = self.grid_view['config']['columns']
        self.grid_config['dataSource'] = self.grid_data

        # configure grid settings
        if 'modes' not in self.grid_view['config']:
            self.grid_view['config']['modes'] = GRID_DEFAULT_MODES
        for grid_mode in self.grid_view['config']['modes']:
            ej.grids.Grid.Inject(ej.grids[grid_mode])
            if grid_mode in GRID_MODE_TO_SWITCH and GRID_MODE_TO_SWITCH[grid_mode]:
                self.grid_config[GRID_MODE_TO_SWITCH[grid_mode]] = True
        if 'Page' in self.grid_view['config']['modes']:
            self.grid_config['allowPaging'] = True
            self.grid_config['pageSettings'] = {'pageSize': self.grid_view['config']['pageSize']}
        else:
            self.grid_config['pageSettings'] = {'pageSize': 1000000}
        if 'Edit' in self.grid_view['config']['modes']:
            self.grid_config['editSettings'] = self.grid_view['config'].get('editSettings', GRID_DEFAULT_EDIT_SETTINGS)
        if 'Toolbar' in self.grid_view['config']['modes']:
            self.grid_config['toolbar'] = self.grid_view['config'].get('toolbar', GRID_DEFAULT_TOOLBAR_ITEMS)
        if 'Filter' in self.grid_view['config']['modes']:
            self.grid_config['filterSettings'] = GRID_DEFAULT_FILTER_SETTINGS
        self.grid_config['showColumnMenu'] = True
        self.grid_config['allowTextWrap'] = True
        # self.grid_config['enableStickyHeader'] = True
        self.grid_config['width'] = '100%'
        self.grid_config['height'] = '100%'

        # attach grid event handlers
        self.grid_config['actionBegin'] = self.grid_action_handler
        self.grid_config['actionComplete'] = self.grid_action_handler
        # self.grid_config['queryCellInfo'] = self.query_cell_info
        # self.grid_config['recordClick'] = self.record_click
        # self.grid_config['rowSelecting'] = lambda args: print('rowSelecting', args)
        # self.grid_config['rowSelected'] = lambda args: print('rowSelected', args)

        # create Grid control
        self.grid = ej.grids.Grid(self.grid_config)
        # print('\nGrid config\n', json.dumps(self.grid_config), '\n')

    @staticmethod
    def format_value(col, row, cell):
        return row[col] or ''

    # get Grid data and refresh the view
    def form_show(self, **args):
        print('show grid')
        # try:
        self.grid_data = self.grid_class.get_grid_view(self.view_config,
                                                       search_queries=self.search_queries,
                                                       filters=self.filters,
                                                       include_rows=False)
        self.grid['dataSource'] = self.grid_data
        # print('\nGrid data source\n', self.grid.dataSource, '\n')
        self.grid_el_id = uuid.uuid4()
        self.container_el = jQuery(f"#{self.container_id}")[0]
        self.grid_height = self.container_el.offsetHeight - GRID_HEIGHT_OFFSET
        self.container_el.innerHTML = f'\
               <div id="pm-grid-container" style="height:{self.grid_height}px;">\
                 <div class="pm-gridview-title">{self.grid_title}</div>\
                 <div id="{self.grid_el_id}"></div>\
               </div>'
        self.grid.appendTo(jQuery(f"#{self.grid_el_id}")[0])

        # except Exception as e:
        #     print('Error in Grid form_show', e)

    def destroy(self):
        self.grid.destroy()
        if self.container_el is not None:
            self.container_el.innerHTML = ''

    def query_cell_info(self, args):
        for name, props in self.row_actions.items():
            el = args.cell.querySelector(f"#{name}")
            if props['type'] == 'button':
                button = ej.buttons.Button({'content': props['content']})
                button.appendTo(el)

    def record_click(self, args):
        if args.target.id in self.row_actions:
            print(args.rowIndex, args.rowData)

    def grid_action_handler(self, args):
        # print('grid_action_handler', args)
        if args.requestType in ('beginEdit', 'add', 'delete') and args.type == 'actionComplete':
            # print('\nactionComplete\n', args, '\n')

            if args.requestType in ('beginEdit', 'add'):
                args.dialog.close()
                if args.requestType == 'beginEdit':
                    form_action = 'edit'
                    form_data = self.grid_class.get(args.rowData.uid)
                else:
                    form_action = 'add'
                    form_data = None
                    print('Add row')
                if hasattr(sys.modules[f"{APP_NAME}.Forms"], f"{self.model}Form"):
                    print('Dialog form: ', f"Forms.{self.model}Form")
                    edit_form_class = getattr(sys.modules[f"{APP_NAME}.Forms"], f"{self.model}Form")
                    form_dialog = edit_form_class(data=form_data, action=form_action, update_source=self.update_grid,
                                                  target=self.container_id)
                else:
                    form_dialog = Forms.BaseForm(model=self.model, data=form_data, action=form_action,
                                                 update_source=self.update_grid, target=self.container_id)
                form_dialog.form_show()

            elif args.requestType == 'delete':
                # print('\nDelete row(s)\n', args.data, '\n')
                for gird_row in args.data:
                    db_row = self.grid_class.get(gird_row.uid)
                    if db_row is not None:
                        db_row.delete()

            else:
                print('\nUnknown requestType\n', args.requestType, '\n')

    def update_grid(self, data_row, add_new):
        grid_row = data_row.get_row_view(self.view_config['columns'], include_row=False)
        if add_new:
            self.grid.addRecord(grid_row)
        else:
            self.grid.setRowData(grid_row['uid'], grid_row)
