from anvil.js.window import ej, jQuery
import anvil.server
from ..datamodel import types as dmtypes
from . import FormBase
from ..tools.utils import AppEnv, camel_to_title
import string
import uuid
import time

GRID_TOOLBAR_COMMAND_ADD = {'id': 'add', 'text': '', 'prefixIcon': 'e-add', 'tooltipText': 'Add', 'align': 'Right'}
GRID_TOOLBAR_COMMAND_DELETE = {'id': 'delete', 'text': '', 'prefixIcon': 'e-delete', 'tooltipText': 'Delete',
                               'align': 'Right', 'style': 'color: #d6292c;'}
GRID_TOOLBAR_COMMAND_SEARCH = {'id': 'search', 'text': 'Search', 'prefixIcon': 'e-search', 'tooltipText': 'Search',
                               'align': 'Right'}
GRID_TOOLBAR_COMMAND_SEARCH_TOGGLE = {'id': 'search-toggle', 'text': '', 'prefixIcon': 'e-search',
                                      'tooltipText': 'Search', 'align': 'Right'}

GRID_TOOLBAR_ITEMS = {
    'add': GRID_TOOLBAR_COMMAND_ADD,
    'delete': GRID_TOOLBAR_COMMAND_DELETE,
    'search': GRID_TOOLBAR_COMMAND_SEARCH,
    'search-toggle': GRID_TOOLBAR_COMMAND_SEARCH_TOGGLE,
}
GRID_DEFAULT_TOOLBAR_ITEMS = [
    GRID_TOOLBAR_COMMAND_DELETE,
    GRID_TOOLBAR_COMMAND_SEARCH,
    GRID_TOOLBAR_COMMAND_SEARCH_TOGGLE,
    GRID_TOOLBAR_COMMAND_ADD,
]

GRID_DEFAULT_COMMAND_COLUMN = {
    'type': 'CommandColumn',
    'field': 'grid-command',
    'headerText': '',
    'width': 80,
    'visible': False,
    'commands': [
        {'type': 'Edit', 'buttonOption': {'iconCss': 'e-icons e-edit', 'cssClass': 'e-flat q-grid-command-edit', }},
        {'type': 'Delete', 'buttonOption': {'iconCss': 'e-icons e-delete', 'cssClass': 'e-flat q-grid-command-delete'}},
    ]
}

GRID_DEFAULT_MODES = ['Sort', 'Filter', 'InfiniteScroll', 'Toolbar', 'Edit', 'ForeignKey', 'Selection', 'ContextMenu']
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

GRID_DEFAULT_FILTER_SETTINGS = {'type': 'Menu'}

GRID_HEIGHT_OFFSET = 25
GRID_DEFAULT_COLUMN_WIDTH = 150
GRID_DEFAULT_CUSTOM_ATTRIBUTES = {'class': 'align-top'}


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
                 form_container_id=None,
                 title=None,
                 model=None,
                 view_name=None,
                 view_config=None,
                 search_queries=None,
                 filters=None,
                 grid_modes=None,
                 toolbar_items=None,
                 toolbar_actions=None,
                 context_menu_items=None,
                 persist=True,
                 edit_mode='dialog',
                 add_edit_form=None,
                 content_wrap=True,
                 data=None,
                 ):

        self.grid_config = {}
        self.grid_height = None
        self.grid_el_id = None
        self.container_id = container_id or AppEnv.content_container_id
        self.form_container_id = form_container_id or container_id
        self.container_el = None
        self.search_queries = search_queries
        self.filters = filters
        self.persist = persist
        self.form_class = None
        self.edit_mode = edit_mode
        self.confirm_dialog = None
        self.show_confirm_dialog = True
        self.toolbar_items = []
        self.context_menu_actions = {}
        self.grid_data = data or []
        self.grid_el_id = uuid.uuid4()

        print('GridView', view_name, model)

        self.view_config = {}
        if view_config:
            self.view_config = view_config
        else:
            view_obj = None
            if view_name:
                view_obj = AppEnv.data_models.AppGridView.get_by('name', view_name)
            elif model:
                view_obj = AppEnv.data_models.AppGridView.get_by('model', model)
            if view_obj:
                # print('view_obj', view_obj)
                self.view_config = view_obj['config'] or {}
                self.view_config['model'] = model or view_obj['model']
                self.view_config['columns'] = view_obj['columns'] or []

        self.model = self.view_config.get('model', model)
        self.grid_class = getattr(AppEnv.data_models, self.model or 'None', None)

        # print('edit mode', self.edit_mode, self.view_config)
        if self.edit_mode == 'inline':
            # print('inline edit')
            # print(self.view_config['config'])
            # self.gird_config = self.view_config['config'].copy()
            # self.grid_config['dataSource'] = self.grid_data
            self.view_config['config']['datasource'] = self.grid_data
            # print('inline grid')
            # print(self.view_config['config'])
            self.grid = ej.grids.Grid(self.view_config['config'])
            return

        if add_edit_form:
            if isinstance(add_edit_form, str):
                self.form_class = getattr(AppEnv.forms, add_edit_form, None)
            else:
                self.form_class = add_edit_form
        if not self.form_class:
            self.form_class = getattr(AppEnv.forms, f"{self.model}Form", None) or FormBase.FormBase
        if not self.view_config or 'columns' not in self.view_config:
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
        print('grid model', model, self.model)
        print('form class', self.form_class)

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
                if column['name'] == '_spacer':
                    grid_column = {
                        'headerText': '',
                        'template': '<div class="a-grid-spacer"></div>',
                        'textAlign': 'Left',
                        'customAttributes': {'class': 'align-top'},
                        'width': column.get('width', None) or GRID_DEFAULT_COLUMN_WIDTH,
                    }
                else:
                    # print('column', column['name'])
                    col_attr, _ = get_model_attribute(self.model, column['name'])
                    if '.' in column['name']:
                        if col_attr.field_type == dmtypes.FieldTypes.OBJECT and col_attr.schema:
                            col_attr = col_attr.schema[column['name'].split('.')[1]]
                            # print('object', column['name'], col_attr)
                    # print(column)
                    grid_column = {
                        # 'field': column['name'].split('.')[0] if '.' in column['name'] else column['name'],
                        'field': column['name'].replace('.', '__'),
                        'headerText': column.get('label', column['name']),
                        'type': col_attr.field_type.GridType,
                        'format': column.get('format', None) or col_attr.field_type.GridFormat,
                        'displayAsCheckBox': col_attr.field_type == dmtypes.FieldTypes.BOOLEAN,
                        'textAlign': 'Left',
                        'customAttributes': column.get('custom_attributes', GRID_DEFAULT_CUSTOM_ATTRIBUTES.copy()),
                        'disableHtmlEncode': column.get('disable_html_encode', True),
                        'width': column.get('width', None) or GRID_DEFAULT_COLUMN_WIDTH,
                        'visible': column.get('visible', True),
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
        self.grid_title = title or camel_to_title(self.grid_class._plural_name)
        self.grid_config = {
            'columns': self.grid_view['config']['columns'],
            'dataSource': self.grid_data,
        }

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
        if self.grid_view['config'].get('content_wrap', True):
            self.grid_config['allowTextWrap'] = True
            self.grid_config['textWrapSettings'] = {'wrapMode': 'Content'}
        else:
            self.grid_config['allowTextWrap'] = False
            self.grid_config['textWrapSettings'] = {'wrapMode': 'Header'}
        if 'Toolbar' in self.grid_view['config']['modes']:
            tb_items = []
            self.toolbar_actions = {}
            if isinstance(toolbar_actions, list):
                for action_item in toolbar_actions:
                    self.toolbar_actions[action_item['name']] = action_item
                    toolbar_item = {
                        'id': action_item['name'],
                        'type': action_item['input'].type,
                        'template': f'<div id="{action_item["input"].container_id}"></div>',
                        'align': 'Left',
                    }
                    if action_item['input'].type == 'Input':
                        action_item['input'].create_control()
                        toolbar_item['template'] = action_item['input'].control
                    tb_items.append(toolbar_item)
                print('toolbar_actions', tb_items)
            # for item_id in self.toolbar_actions.keys():
            #     toolbar_item = {
            #         'id': item_id,
            #         'type': self.toolbar_actions[item_id].get('type', 'Button'),
            #         'text': self.toolbar_actions[item_id].get('label', ''),
            #         'tooltipText': self.toolbar_actions[item_id].get('tooltip', ''),
            #         'prefixIcon': self.toolbar_actions[item_id].get('icon', ''),
            #         'template': f'<div id="{self.grid_el_id}-action-{item_id}"></div>',
            #         'align': 'Left',
            #     }
            tb_items.extend(
                toolbar_items or
                self.grid_view['config'].get('toolbar', AppEnv.grid_settings.get('toolbar_items')) or
                GRID_DEFAULT_TOOLBAR_ITEMS
            )
            self.toolbar_items = tb_items.copy()
        else:
            self.toolbar_items = []
        print('toolbar_items', self.toolbar_items)
        self.grid_config['toolbar'] = self.toolbar_items
        self.grid_config['toolbarClick'] = self.toolbar_click
        self.grid_config['toolbar'].insert(
            0,
            {'id': 'title', 'template': f'<div class="da-grid-view-title">{self.grid_title}</div>', 'align': 'Left'},
            # type: ignore
        )
        if 'Filter' in self.grid_view['config']['modes']:
            self.grid_config['filterSettings'] = GRID_DEFAULT_FILTER_SETTINGS
        if 'Selection' in self.grid_view['config']['modes']:
            self.grid_config['selectionSettings'] = GRID_DEFAULT_SELECTION_SETTINGS
            self.grid_config['columns'].insert(0,
                                               {'type': 'checkbox', 'lockColumn': True,  # type: ignore
                                                'width': GRID_DEFAULT_SELECTION_SETTINGS['checkboxWidth']}
                                               )
            self.grid_config['rowSelected'] = self.row_selected
            self.grid_config['rowDeselected'] = self.row_deselected
        self.grid_config['showColumnMenu'] = True
        # self.grid_config['allowTextWrap'] = True
        if context_menu_items:
            self.grid_config['contextMenuItems'] = []
            for item in context_menu_items:
                self.context_menu_actions[item['id']] = item.get('action', None)
                self.grid_config['contextMenuItems'].append(
                    {'text': item['label'], 'target': '.e-content', 'id': item['id']}  # type: ignore
                )
            self.grid_config['contextMenuClick'] = self.context_menu_click
        # self.grid_config['enableStickyHeader'] = True
        self.grid_config['width'] = '100%'
        self.grid_config['height'] = '100%'

        # attach grid event handlers
        self.grid_config['actionBegin'] = self.grid_action_handler
        self.grid_config['actionComplete'] = self.grid_action_handler
        self.grid_config['queryCellInfo'] = self.query_cell_info
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
    def form_show(self, get_data=True, **args):
        print('show grid')
        # try:
        # print('\nGrid data source\n', self.grid.dataSource, '\n')
        self.container_el = jQuery(f"#{self.container_id}")[0]
        self.grid_height = self.container_el.offsetHeight - GRID_HEIGHT_OFFSET
        if self.grid_height < 0:
            self.grid_height = None
        print('grid height', self.grid_height, self.container_el.offsetHeight, GRID_HEIGHT_OFFSET)
        print('container_el', self.container_el.id)
        if self.grid_height:
            self.container_el.innerHTML = f'\
                <div id="da-grid-container" style="height:{self.grid_height}px;">\
                    <div id="{self.grid_el_id}"></div>\
                </div>'
        else:
            self.container_el.innerHTML = f'\
                <div id="da-grid-container">\
                    <div id="{self.grid_el_id}"></div>\
                </div>'
        self.grid.appendTo(jQuery(f"#{self.grid_el_id}")[0])
        if self.grid_height is None:
            print('grid height', self.grid.height, self.container_el.offsetHeight)
            grid_container = self.container_el.querySelector('#da-grid-container')
            grid_container.style.height = f'{self.container_el.offsetHeight}px'
            # jQuery(f"#da-grid-container")[0].style.height = f'{self.container_el.offsetHeight}px'
            # print(jQuery(f"#da-grid-container")[0].style.height)
        # print('grid height', self.grid.height, self.container_el.offsetHeight)
        # print(self.grid_el_id, anvil.js.window.document.getElementById(self.grid_el_id))
        # self.grid.appendTo(anvil.js.window.document.getElementById(f"#{self.grid_el_id}"))

        if not self.edit_mode == 'inline':
            for item in self.toolbar_items:
                item_title = item.get('tooltipText', item.get('text', ''))
                item_css_class = item.get('cssClass')
                item_style = item.get('style')
                button = self.grid.element.querySelector(f'.e-toolbar .e-toolbar-item[title="{item_title}"] button')
                if item_css_class:
                    item_css_class = item_css_class.split(' ')
                    for cls in item_css_class:
                        button.classList.add(cls)
                    for text in button.children:
                        for cls in item_css_class:
                            text.classList.add(cls)
                if item_style:
                    button.style = item_style
                    for text in button.children:
                        text.style = item_style
                if item.get('id') == 'search-toggle':
                    self.grid.element.querySelector(
                        f'#{self.container_id} .e-toolbar .e-toolbar-item.e-search-wrapper[title="Search"]').style.display = 'none'
                elif item.get('id') == 'delete':
                    self.grid.element.querySelector(
                        f'#{self.container_id} .e-toolbar .e-toolbar-item[title="Delete"]').style.display = 'none'

        print('debug B')
        # print('toolbar_actions', self.toolbar_actions)
        # for action_item in self.toolbar_actions:
        #     if self.toolbar_actions[action_item]['input'].type != 'Input':
        #         self.toolbar_actions[action_item]['input'].show()
        #         if self.toolbar_actions[action_item]['selected_records']:
        #             self.toolbar_actions[action_item]['input'].hide()
        # for item_id in self.toolbar_actions.keys():
        #     item_button = ej.buttons.Button({
        #         'content': self.toolbar_actions[item_id].get('label', ''),
        #         'iconCss': self.toolbar_actions[item_id].get('icon', ''),
        #         'cssClass': self.toolbar_actions[item_id].get('css_class', 'e-outline'),
        #     })
        #     # item_button.appendTo(jQuery(f'#{self.grid_el_id}-action-{item_id}')[0])
        #     self.toolbar_actions[item_id]['control'].appendTo(jQuery(f'#{self.grid_el_id}-action-{item_id}')[0])
        #     self.grid.element.querySelector(f'[id="{self.grid_el_id}-action-{item_id}"]').style.display = 'none'

        print('debug C')
        if not self.grid_data and get_data:
            print('get grid data', self.filters, self.search_queries)
            self.grid_data = self.grid_class.get_grid_view(self.view_config,
                                                           search_queries=self.search_queries,
                                                           filters=self.filters,
                                                           include_rows=False)
            # self.grid_data = anvil.server.call('fetch_view',
            #                                    self.grid_class.__name__,
            #                                    self.grid_class.__module__,
            #                                    [col['name'] for col in self.view_config['columns']],
            #                                    self.search_queries or [],
            #                                    self.filters or {})
            self.grid['dataSource'] = self.grid_data
            # print(self.grid_data)
            # print(self.grid_config['columns'])
        # for k in self.grid.keys():
        #     print(k, self.grid[k])
        print('show grid done')
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
        print('toolbar_click', args.item.id, args.cancel)
        if args.item.id == 'add':
            args.cancel = True
            self.add_edit_row(args=None)
        elif args.item.id == 'search-toggle':
            print('toggle search')
            self.grid.element.querySelector(
                f'.e-toolbar .e-toolbar-item button[id="search-toggle"]').parentElement.style.display = 'none'
            self.grid.element.querySelector(
                f'.e-toolbar .e-toolbar-item.e-search-wrapper[title="Search"]').style.display = 'inline-flex'
        elif args.item.id == 'search':
            pass
        elif args.item.id == 'delete' and self.grid.getSelectedRecords():
            args.cancel = True
            self.confirm_delete(args)
        elif (args.item.id in self.toolbar_actions and self.toolbar_actions[args.item.id]['toolbar_click'] and
              callable(self.toolbar_actions[args.item.id]['input'].action)):
            print('toolbar item', args.item.id)
            args.cancel = True
            # self.toolbar_actions[args.item.id]['input'].action(args)

    def context_menu_click(self, args):
        if args.item.id in self.context_menu_actions and callable(self.context_menu_actions[args.item.id]):
            self.context_menu_actions[args.item.id](args)

    def row_selected(self, args):
        # for item in self.grid.toolbarModule.toolbar.properties.items:
        #     if item.properties.id in self.toolbar_actions.keys():
        #         self.grid.element.querySelector(
        #             f'[id="{self.grid_el_id}-action-{item.properties.id}"]'
        #         ).style.display = 'inline-flex'
        for action_item in self.toolbar_actions:
            if self.toolbar_actions[action_item]['selected_records']:
                self.toolbar_actions[action_item]['input'].show()
        self.grid.element.querySelector(f'.e-toolbar .e-toolbar-item[title="Delete"]').style.display = 'inline-flex'

    def row_deselected(self, args):
        # print('row_deselected', args)
        if not self.grid.getSelectedRecords():
            # for item in self.grid.toolbarModule.toolbar.properties.items:
            #     if item.properties.id in self.toolbar_actions.keys():
            #         self.grid.element.querySelector(
            #             f'[id="{self.grid_el_id}-action-{item.properties.id}"]'
            #         ).style.display = 'none'
            for action_item in self.toolbar_actions:
                if self.toolbar_actions[action_item]['selected_records']:
                    self.toolbar_actions[action_item]['input'].hide()
            self.grid.element.querySelector(f'.e-toolbar .e-toolbar-item[title="Delete"]').style.display = 'none'

    def record_click(self, args):
        if args.target.id in self.row_actions:
            print(args.rowIndex, args.rowData)

    def grid_action_handler(self, args):
        # print('grid_action_handler', args)
        if args.requestType in ('beginEdit', 'add') and args.type == 'actionComplete':

            if args.requestType in ('beginEdit', 'add') and 'dialog' in args:
                args.dialog.close()
                self.add_edit_row(args)

        elif args.requestType == 'delete' and args.type == 'actionBegin' and self.show_confirm_dialog:
            if not self.confirm_dialog:
                self.confirm_delete(args)

    def add_edit_row(self, args=None, form_data=None, data_row=None):
        # print('add_edit_row', args, form_data)
        if args is not None and args.requestType == 'beginEdit':
            form_action = 'edit'
            if args.rowData.uid and 'grid' not in args.rowData.uid and not data_row:
                instance = self.grid_class.get(args.rowData.uid)
                print(args.rowData.uid, instance)
            elif data_row:
                instance = data_row
            else:
                props = args.rowData
                # props.pop('uid', None)
                instance = self.grid_class(**props)
        else:
            form_action = 'add'
            instance = self.grid_class(**form_data) if form_data else None
        print(form_action, form_data, self.persist)
        self.form_class(model=self.model,
                        data=instance,
                        action=form_action,
                        update_source=self.update_grid,
                        source=self,
                        target=self.form_container_id,
                        persist=self.persist,
                        ).form_show()

    def confirm_delete(self, args):
        args.cancel = True
        self.confirm_dialog = ej.popups.DialogUtility.confirm({
            'title': 'Confirm Delete',
            'content': 'Are you sure you want to delete selected record(s)?',
            'okButton': {'text': 'Yes', 'click': self.delete_selected},
            'cancelButton': {'text': 'Cancel'},
            'showCloseIcon': True,
        })

    def delete_selected(self, args, persist=True):
        print('delete_selected')
        self.show_confirm_dialog = False
        if self.confirm_dialog:
            self.confirm_dialog.hide()
            self.confirm_dialog.destroy()
            self.confirm_dialog = None

        selected_rows = self.grid.getSelectedRecords() or []
        for grid_row in selected_rows:
            print('Delete row', grid_row)
            self.grid.dataSource.remove(grid_row)
        for row in self.grid.getSelectedRows():
            self.grid.deleteRow(row)
        self.grid.refresh()
        self.show_confirm_dialog = True

        if persist:
            print('persist delete')
            for grid_row in selected_rows:
                if grid_row.uid and 'grid' not in grid_row.uid:
                    db_row = self.grid_class.get(grid_row.uid) if grid_row.uid else None
                    if db_row is not None:
                        db_row.delete()

    def update_grid(self, data_row, add_new, row_index=None, get_relationships=False):
        if data_row.uid is None:
            data_row.uid = f"grid_{uuid.uuid4()}"
        grid_row = data_row.get_row_view(
            self.view_config['columns'],
            include_row=False,
            get_relationships=get_relationships,
        )
        if add_new:
            self.grid.addRecord(grid_row)
        else:
            if row_index is None:
                row_index = self.grid.getRowIndexByPrimaryKey(grid_row['uid'])
            # print('updateRow', row_index, grid_row)
            # print('dataSource', type(self.grid.dataSource), self.grid.dataSource)
            self.grid.updateRow(row_index, grid_row)
            self.grid.dataSource[row_index] = grid_row
            # else:
            #     self.grid.updateRow(self.grid.getRowIndexByPrimaryKey(grid_row['uid']), grid_row)
        # self.grid.refresh()
        # print('updated grid', self.grid.dataSource)
