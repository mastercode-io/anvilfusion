from anvil.js.window import ej, jQuery
from ..datamodel import types as dmtypes
from .FormBase import FormBase
from ..tools.utils import AppEnv
from ..tools import utils
import string
import uuid
import json


GRID_DEFAULT_FILTER_SETTINGS = {'type': 'Menu'}
GRID_DEFAULT_TOOLBAR_ITEMS = [
    {'id': 'delete', 'text': '', 'prefixIcon': 'e-delete', 'tooltipText': 'Delete', 'align': 'Right', 'style': 'color: #d6292c;'},
    {'id': 'search', 'text': 'Search', 'prefixIcon': 'e-search', 'tooltipText': 'Search', 'align': 'Right'},
    {'id': 'search-toggle', 'text': '', 'prefixIcon': 'e-search', 'tooltipText': 'Search', 'align': 'Right'},
    {'id': 'add', 'text': '', 'prefixIcon': 'e-add', 'tooltipText': 'Add', 'align': 'Right'}, 
    # {'text': 'Edit'}, 
    # {'text': 'Delete'}, 
]
GRID_DEFAULT_COMMAND_COLUMN = {
    'type': 'CommandColumn',
    'field': 'grid-command',
    'headerText': '',
    'width': 80,
    'visible': False,
    'commands': [
        {'type': 'Edit', 'buttonOption': {'iconCss': 'e-icons e-edit', 'cssClass': 'e-flat q-grid-command-edit',}},
        {'type': 'Delete', 'buttonOption': {'iconCss': 'e-icons e-delete', 'cssClass': 'e-flat q-grid-command-delete'}},
    ]
}
GRID_DEFAULT_MODES = ['Sort', 'Filter', 'InfiniteScroll', 'Toolbar', 'Edit', 'ForeignKey', 'Selection']
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
    'showDeleteConfirmDialog': False,
    'allowScrolling': True
}
GRID_DEFAULT_SELECTION_SETTINGS = {
    'type': 'Multiple',
    'mode': 'Row',
    'checkboxOnly': True,
    'persistSelection': True,
    'enableToggle': True,
    'checkboxWidth': 35,
}
GRID_HEIGHT_OFFSET = 25
GRID_DEFAULT_COLUMN_WIDTH = 150





def get_grid_view(view_config, search_queries=None, filters=None, include_rows=False):
    model = AppEnv.data_models
    cls = getattr(model, view_config['model'])
    search_queries = search_queries or []
    filters = filters or {}
    return cls.get_grid_view(view_config, search_queries, filters, include_rows)


def get_model_attribute(class_name, attr_name):
    model = AppEnv.data_models
    cls = getattr(model, class_name)
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


class GridView:
    def __init__(self,
                 container_id=None,
                 popup_container_id=None,
                 title=None,
                 model=None,
                 view_name=None,
                 view_config=None,
                 search_queries=None,
                 filters=None,
                 grid_modes=None,
                 toolbar_items=None,
                 save=True,
                 ):

        self.grid_height = None
        self.grid_el_id = None
        self.container_id = container_id
        self.popup_container_id = popup_container_id or container_id
        self.container_el = None
        self.model = model
        self.search_queries = search_queries
        self.filters = filters
        self.save = save
        self.confirm_dialog = None
        print('grid model', model, self.model)
        
        # depenencies
        self.app_model = AppEnv.data_models
        self.app_forms = AppEnv.forms

        print('GridView', view_name)
        if view_name or view_config:
            if view_config is not None:
                self.view_config = view_config
            else:
                view_obj = self.app_model.appGridViews.get_by('name', view_name)
                self.view_config = json.loads(view_obj['config'].replace("'", "\""))
            self.model = self.view_config['model']
            self.grid_class = getattr(self.app_model, self.model)
        else:
            # self.model = 'CaseWorkflowItem'
            self.grid_class = getattr(self.app_model, self.model)
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
                col_attr, _ = get_model_attribute(self.model, column['name'])
                grid_column = {
                    'field': column['name'].split('.')[0] if '.' in column['name'] else column['name'],
                    'headerText': column['label'],
                    'type': col_attr.field_type.GridType,
                    'format': column.get('format', None) or col_attr.field_type.GridFormat,
                    'displayAsCheckBox': col_attr.field_type == dmtypes.FieldTypes.BOOLEAN,
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
        self.grid_title = title if title is not None else utils.camel_to_title(self.model)
        self.grid_config = {}
        self.grid_data = []
        self.db_data = {}
        self.grid_config['columns'] = self.grid_view['config']['columns']
        self.grid_config['dataSource'] = self.grid_data

        # configure grid settings
        if 'modes' not in self.grid_view['config']:
            self.grid_view['config']['modes'] = grid_modes or AppEnv.grid_settings.get('modes', GRID_DEFAULT_MODES)
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
            toolbar_items = toolbar_items or \
                self.grid_view['config'].get('toolbar', AppEnv.grid_settings.get('toolbar_items')) or \
                GRID_DEFAULT_TOOLBAR_ITEMS
            self.toolbar_items = toolbar_items.copy()
        else:
            self.toolbar_items = []
        self.grid_config['toolbar'] = self.toolbar_items
        self.grid_config['toolbarClick'] = self.toolbar_click
        self.grid_config['toolbar'].insert(0, {'id': 'title', 
                                                'template': f'<div class="h4 a-grid-view-title">{self.grid_title}</div>', 
                                                'align': 'Left'}
                                            )
        if 'Filter' in self.grid_view['config']['modes']:
            self.grid_config['filterSettings'] = GRID_DEFAULT_FILTER_SETTINGS
        if 'Selection' in self.grid_view['config']['modes']:
            self.grid_config['selectionSettings'] = GRID_DEFAULT_SELECTION_SETTINGS
            # command_column = GRID_DEFAULT_COMMAND_COLUMN.copy()
            # self.grid_config['columns'].insert(0, command_column)
            self.grid_config['columns'].insert(0, 
                                               {'type': 'checkbox', 'lockColumn': True,
                                                'width': GRID_DEFAULT_SELECTION_SETTINGS['checkboxWidth']})
            self.grid_config['rowSelected'] = self.row_selected
            self.grid_config['rowDeselected'] = self.row_deselected
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
        # self.container_el.innerHTML = f'\
        #        <div id="pm-grid-container" style="height:{self.grid_height}px;">\
        #          <div class="pm-gridview-title">{self.grid_title}</div>\
        #          <div id="{self.grid_el_id}"></div>\
        #        </div>'
        self.container_el.innerHTML = f'\
               <div id="pm-grid-container" style="height:{self.grid_height}px;">\
                 <div id="{self.grid_el_id}"></div>\
               </div>'
        self.grid.appendTo(jQuery(f"#{self.grid_el_id}")[0])

        for item in self.toolbar_items:
            item_title = item.get('tooltipText', item.get('text', ''))
            item_css_class = item.get('cssClass')
            item_style = item.get('style')
            button = self.grid.element.querySelector(f'.e-toolbar .e-toolbar-item[title="{item_title}"] button')
            if item_css_class:
                button.classList.add(item_css_class)
                for text in button.children:
                    text.classList.add(item_css_class)
            if item_style:
                button.style = item_style
                for text in button.children:
                    text.style = item_style
            if item.get('id') == 'search-toggle':
                self.grid.element.querySelector(f'#{self.container_id} .e-toolbar .e-toolbar-item.e-search-wrapper[title="Search"]').style.display = 'none'
            elif item.get('id') == 'delete':
                self.grid.element.querySelector(f'#{self.container_id} .e-toolbar .e-toolbar-item[title="Delete"]').style.display = 'none'
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


    def toolbar_click(self, args):
        print('toolbar_click', args.item, args.cancel)
        if args.item.id == 'add':
            args.cancel = True
            self.add_edit_row()
        elif args.item.id == 'search-toggle':
            print('toggle search')
            self.grid.element.querySelector(f'.e-toolbar .e-toolbar-item button[id="search-toggle"]').parentElement.style.display = 'none'
            self.grid.element.querySelector(f'.e-toolbar .e-toolbar-item.e-search-wrapper[title="Search"]').style.display = 'inline-flex'
        elif args.item.id == 'search':
            pass
        elif args.item.id == 'delete' and self.grid.getSelectedRecords():
            self.confirm_delete(args)


    def row_selected(self, args):
        print('row_selected')
        self.grid.element.querySelector(f'.e-toolbar .e-toolbar-item[title="Delete"]').style.display = 'inline-flex'
    
    
    def row_deselected(self, args):
        print('row_deselected', self.grid.getSelectedRecords())
        if not self.grid.getSelectedRecords():
            self.grid.element.querySelector(f'.e-toolbar .e-toolbar-item[title="Delete"]').style.display = 'none'
    
    
    def record_click(self, args):
        if args.target.id in self.row_actions:
            print(args.rowIndex, args.rowData)


    def grid_action_handler(self, args):
        # print('grid_action_handler', args)
        if args.requestType in ('beginEdit', 'add') and args.type == 'actionComplete':

            if args.requestType in ('beginEdit', 'add'):
                args.dialog.close()
                self.add_edit_row(args)

        elif args.requestType == 'delete' and args.type == 'actionBegin':
            if not self.confirm_dialog:
                self.confirm_delete(args)

        # else:
        #     print('\nUnknown requestType\n', args.requestType, '\n')

                            
    def add_edit_row(self, args=None):
        print('add_edit_row', args)
        if args is not None and args.requestType == 'beginEdit':
            form_action = 'edit'
            if args.rowData.uid:
                form_data = self.grid_class.get(args.rowData.uid)
            else:
                form_data = self.grid_class(args.rowData)
        else:
            form_action = 'add'
            form_data = None
            print('Add row')
        if hasattr(self.app_forms, f"{self.model}Form"):
            print('Dialog form: ', f"Forms.{self.model}Form")
            edit_form_class = getattr(self.app_forms, f"{self.model}Form")
            form_dialog = edit_form_class(data=form_data, 
                                          action=form_action, 
                                          update_source=self.update_grid,
                                          target=self.popup_container_id,
                                          save=self.save,
                                          )
        else:
            form_dialog = FormBase(model=self.model, 
                                   data=form_data, 
                                   action=form_action, 
                                   update_source=self.update_grid, 
                                   target=self.popup_container_id,
                                   save=self.save,
                                   )
        form_dialog.form_show()
        
        
    def confirm_delete(self, args):
        args.cancel = True
        self.confirm_dialog = ej.popups.DialogUtility.confirm({
            'title': 'Confirm Delete',
            'content': 'Are you sure you want to delete selected record(s)?',
            'okButton': {'text': 'Yes', 'click': self.delete_selected},
            'cancelButton': {'text': 'Cancel'},
            'showCloseIcon': True,
            })
    
    
    def delete_selected(self, args):
        print('delete_selected')
        for grid_row in self.grid.getSelectedRecords() or []:
            print('Delete row', grid_row)
            db_row = self.grid_class.get(grid_row.uid) if grid_row.uid else None
            if db_row is not None:
                db_row.delete()
            if grid_row.uid:
                print('uid', grid_row.uid)
                self.grid.deleteRecord('uid', grid_row)
            else:
                print('no uid')
                self.grid.daraSource.remove(grid_row)
                self.grid.refresh()
        if self.confirm_dialog:
            self.confirm_dialog.hide()
            self.confirm_dialog.destroy()
            self.confirm_dialog = None
        # self.grid.refresh()


    def update_grid(self, data_row, add_new):
        grid_row = data_row.get_row_view(self.view_config['columns'], include_row=False)
        if add_new:
            self.grid.addRecord(grid_row)
        else:
            self.grid.setRowData(grid_row['uid'], grid_row)
