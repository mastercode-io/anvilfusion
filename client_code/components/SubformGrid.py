import anvil.js
from .FormInputs import BaseInput
from .GridView import GridView
from ..tools.utils import AppEnv


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
                'actionComplete': self.inline_grid_action,
                # 'cellSave': '',
                'gridLines': 'Default',
                'allowScrolling': True,
                'allowTextWrap': True,
                'textWrapSettings': {'wrapMode': 'Content'},
                'width': '100%',
                'height': '100%',
            }
            grid_config['columns'].insert(
                0,
                {'field': 'uid', 'headerText': 'UID', 'visible': False, 'isPrimaryKey': True, 'width': '0px'}  # noqa
            )
            view_config['config'] = grid_config
        else:
            self.inline_input_fields = []
        for field in self.inline_input_fields:
            field.placeholder = field.grid_column['headerText']
        self.input_fields_map = {field.name: field for field in self.inline_input_fields}
        self.subform_grid_view = {'model': view_config['model'], 'columns': view_config['columns'].copy()}
        # else:
        #     grid_config = view_config
        # print('subform grid view_config', edit_mode, view_config)

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
        self.to_save = []
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
        return None

    @enabled.setter
    def enabled(self, value):
        pass

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        print('set subformgrid value', value)
        if value and value.uid:
            print('value not empty', value.uid)
            print(self.subform_grid_view)
            self._value = value
            if self.model and self.is_dependent:
                if not self.filters:
                    self.filters = {}
                if self.link_field:
                    self.filters[self.link_field] = value
                self.grid_data = self.grid_class.get_grid_view(self.subform_grid_view,
                                                               search_queries=self.search_queries,
                                                               filters=self.filters,
                                                               include_rows=False)
                self.grid.dataSource = self.grid_data
            else:
                pass
        else:
            print('no value')
            self._value = None
            self.grid_data = []
            self.grid.dataSource = self.grid_data
        if 'element' in self.grid.keys():
            self.grid.refresh()
            self.grid.dataBind()
        print('subformgrid data', self.filters, self.grid_data)
        print('subformgrid dataSource', self.grid.dataSource)

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
        print('hide subformgrid')
        if self.visible:
            self.visible = False
            if 'element' in self.grid.keys():
                self.grid.element.style.display = 'none'

    def inline_grid_action(self, args):
        print('inline_grid_action', args)
        if args.name == 'actionComplete':

            if args.requestType == 'save':
                if args.action == 'edit':
                    return
                # args.cancel = True
                print('save')
                print(args.data)
                # print(args.rowData)
                inline_controls = [args.form[el].ej2_instances[0] for el in args.form.keys()
                                   if 'ej2_instances' in args.form[el].keys() and args.form[el].ej2_instances]
                # print(inline_controls)
                row_input = {}
                for control in inline_controls:
                    field_name = control.placeholder
                    self.input_fields_map[field_name].control = control
                    field_value = self.input_fields_map[field_name].value
                    if field_name and field_value:
                        row_input[field_name] = field_value
                    # print(control, control.placeholder, control.value)
                    # print(field_name, field_value)
                # print(row_input)
                for field_name in [k for k in self.input_fields_map.keys() if k not in row_input.keys()]:
                    row_input[field_name] = args.data[field_name]
                print(row_input)
                data_row = self.grid_class(**row_input)
                print(data_row)
                row_index = args.index if hasattr(args, 'index') else args.rowIndex
                self.update_grid(data_row, False, row_index=row_index, get_relationships=True)
                # dd_el = inline_controls[1][0]
                # dd_field = self.inline_input_fields[1]
                # dd_field.control = dd_el
                # print(dd_el, dd_el.value, dd_field, dd_field.value)
                # if args.rowData.uid and 'grid' not in args.rowData.uid:
                #     instance = self.grid_class.get(args.rowData.uid)
                #     print(args.rowData.uid, instance)

            elif args.requestType == 'delete':
                print('delete')
                self.to_delete.extend([x.uid for x in self.grid.getSelectedRecords() or [] if x.uid])

    def add_edit_row(self, args=None, form_data=None):
        GridView.add_edit_row(self, args=args, form_data=self.form_data)

    def delete_selected(self, args, persist=False):
        self.to_delete.extend([x.uid for x in self.grid.getSelectedRecords() or [] if x.uid])
        GridView.delete_selected(self, args, persist=False)

    def update_grid(self, data_row, add_new, row_index=None, get_relationships=True):
        self.to_save.append(data_row)
        GridView.update_grid(self, data_row, add_new, row_index=row_index, get_relationships=True)

    def save_dependent(self, link_row=None):
        # print('save subformgrid', self.to_save, self.to_delete)
        if self.link_field and self.link_model and link_row:
            for data_row in self.to_save:
                if data_row.uid and 'grid' in data_row.uid:
                    data_row.uid = None
                data_row[self.link_field] = link_row
                data_row.save()
            for uid in self.to_delete:
                self.grid_class.get(uid).delete()
