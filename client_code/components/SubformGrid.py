import anvil.js
from anvil.js.window import ej, jQuery
from .FormInputs import BaseInput, LookupInput
from .GridView import GridView
from ..tools.utils import AppEnv
import uuid


class SubformGrid(BaseInput, GridView):
    def __init__(self,
                 name=None,
                 label=None,
                 container_id=None,
                 form_container_id=None,
                 form_data=None,
                 model=None,
                 link_model=None,
                 link_field=None,
                 is_dependent=False,
                 schema=None,
                 data=None,
                 view_config=None,
                 edit_mode='dialog',
                 **kwargs):

        BaseInput.__init__(
            self, name=name,
            label=label,
            container_id=container_id,
            **kwargs)

        if view_config is None:
            view_config = {}

        if edit_mode == 'inline':
            self.inline_input_fields = view_config.get('inline_edit_fields', [])
            grid_config = {
                'toolbar': ['Add', 'Edit', 'Delete', 'Update', 'Cancel'],
                'editSettings': {
                    'allowEditing': True,
                    'allowAdding': True,
                    'allowDeleting': True,
                    'showConfirmDialog': True,
                    'showDeleteConfirmDialog': True,
                    'mode': 'Normal',
                    'newRowPosition': 'Bottom'
                },
                'columns': [field.grid_column for field in self.inline_input_fields],
                'dataSource': [],
                'actionBegin': self.inline_grid_action,
                'actionComplete': self.inline_grid_action,
                # 'cellSave': '',
                'gridLines': 'Default',
                'allowScrolling': True,
                'width': '100%',
                'height': '100%',
            }
            if view_config.get('content_wrap', True):
                grid_config['allowTextWrap'] = True
                grid_config['textWrapSettings'] = {'wrapMode': 'Content'}
            else:
                grid_config['allowTextWrap'] = False
                grid_config['textWrapSettings'] = {'wrapMode': 'Header'}

            if model is not None:
                grid_config['columns'][0:0] = [
                    {'field': 'uid', 'headerText': 'UID', 'visible': False, 'isPrimaryKey': True, 'width': '0px'},  # noqa
                    {'field': 'row', 'headerText': 'Row', 'visible': False, 'width': '0px'}
                ]
            view_config['config'] = grid_config
        else:
            self.inline_input_fields = []
        for field in self.inline_input_fields:
            field.placeholder = field.grid_field
        self.input_fields_map = {field.placeholder: field for field in self.inline_input_fields}
        self.subform_grid_view = {'model': view_config.get('model', None),
                                  'columns': view_config.get('columns', []).copy()}

        GridView.__init__(
            self, model=model, title=label,
            container_id=self.el_id,
            form_container_id=form_container_id,
            view_config=view_config,
            persist=False,
            edit_mode=edit_mode,
            **kwargs)

        self.link_model = link_model
        self.link_field = link_field
        self.data = data
        self.html = f'<div><p>Subform Grid</p></div><div id="{self.el_id}"></div>'
        self.form_data = form_data
        self.is_dependent = True if link_model and link_field else is_dependent
        self.to_save = {}
        self.to_delete = []
        self._value = None
        # print('subform grid', self.container_id)

    @property
    def control(self):
        return self._control

    @control.setter
    def control(self, value):
        self._control = value

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value
        if self._enabled:
            self.grid.editSettings.allowEditing = True
            self.grid.editSettings.allowAdding = True
            self.grid.editSettings.allowDeleting = True
        else:
            self.grid.editSettings.allowEditing = False
            self.grid.editSettings.allowAdding = False
            self.grid.editSettings.allowDeleting = False


    @property
    def value(self):
        if self.is_dependent:
            return self._value
        else:
            self._value = []
            for row in self.grid.dataSource:
                self._value.append(dict(row))
            print('get subformgrid value', self._value)
            return self._value

    @value.setter
    def value(self, value):
        print('set subformgrid value', value)
        if value and value.uid:
            print('value not empty', value.uid)
            # print(self.subform_grid_view)
            self._value = value
            if self.model and self.is_dependent:
                if not self.filters:
                    self.filters = {}
                if self.link_field:
                    self.filters[self.link_field] = value
                self.grid_data = self.grid_class.get_grid_view(self.subform_grid_view,
                                                               search_queries=self.search_queries,
                                                               filters=self.filters,
                                                               include_rows=True)
                for grid_row in self.grid_data:
                    grid_row['row'] = dict(grid_row['row'])
                self.grid.dataSource = self.grid_data
                # print('subformgrid data', self.filters, self.grid_data)
        elif value:
            self.grid_data = value
            self.grid.dataSource = self.grid_data
        else:
            print('no value')
            self._value = None
            self.grid_data = []
            self.grid.dataSource = self.grid_data
        if 'element' in self.grid.keys():
            self.grid.refresh()
            self.grid.dataBind()
        # print('subformgrid data', self.filters, self.grid_data)
        # print('subformgrid dataSource', self.grid.dataSource)

    def show(self):
        print('show subformgrid')
        if not self.visible:
            self.visible = True
            if 'element' in self.grid.keys():
                self.grid.element.style.display = 'block'
                self.grid.refresh()
            else:
                GridView.form_show(self, get_data=False)


    def hide(self):
        self.visible = False
        if 'element' in self.grid.keys():
            self.grid.element.style.display = 'none'

    def inline_grid_action(self, args):
        if not self.model:
            return

        if args.name == 'actionComplete' and args.requestType == 'save':
            if not hasattr(args, 'index') and not hasattr(args, 'rowIndex'):
                return
            print('inline_grid_action\n', args)
            row_index = args.index if hasattr(args, 'index') else args.rowIndex
            inline_controls = [args.form[el].ej2_instances[0] for el in args.form.keys()
                               if 'ej2_instances' in args.form[el].keys() and args.form[el].ej2_instances]
            row_input = {'uid': args.data['uid']}
            for control in inline_controls:
                grid_field = control.placeholder
                input_field = self.input_fields_map[grid_field]
                input_field.control = control
                field_value = input_field.value
                if grid_field and field_value:
                    print('get input value')
                    print(grid_field, field_value)
                    row_input[input_field.name] = field_value
            for grid_field in [k for k in self.input_fields_map.keys()
                               if self.input_fields_map[k].name not in row_input.keys()]:
                row_input[self.input_fields_map[grid_field].name] = args.data[grid_field]
            if row_input['uid'] is None or 'grid' in row_input['uid']:
                data_row = self.grid_class(**row_input)
            else:
                data_row = self.grid_class.get(row_input['uid'])
                data_row.update(row_input)
            self.update_grid(data_row, False, row_index=row_index, get_relationships=True)

        if args.name == 'actionComplete' and args.requestType == 'delete':
            if args.data[0]['uid'] and 'grid' not in args.data[0]['uid']:
                self.to_delete.append(args.data[0]['uid'])
            self.to_save.pop(args.data[0]['uid'], None)

    def add_edit_row(self, args=None, **kwargs):
        if args is not None and args.rowData.uid:
            data_row = self.to_save.get(args.rowData.uid, None)
        else:
            data_row = None
        GridView.add_edit_row(self, args=args, form_data=self.form_data, data_row=data_row)

    def delete_selected(self, args, persist=False):
        self.to_delete.extend([x.uid for x in self.grid.getSelectedRecords() or [] if x.uid])
        GridView.delete_selected(self, args, persist=False)

    def update_grid(self, data_row, add_new, row_index=None, get_relationships=True):
        if data_row.uid is None:
            data_row.uid = f"grid_{uuid.uuid4()}"
        self.to_save[data_row.uid] = data_row
        GridView.update_grid(self, data_row, add_new, row_index=row_index, get_relationships=True)

    def save_dependent(self, link_row=None):
        print('save subformgrid')
        # print('SAVE\n', self.to_save)
        # print('DELETE\n', self.to_delete)
        if self.link_field and self.link_model and link_row:
            for data_row in self.to_save.values():
                if data_row.uid and 'grid' in data_row.uid:
                    data_row.uid = None
                data_row[self.link_field] = link_row
                # print('data_row', data_row['uid'], data_row['name'], data_row)
                data_row.save()
            for uid in self.to_delete:
                self.grid_class.get(uid).delete()
