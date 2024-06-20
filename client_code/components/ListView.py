import anvil.js
from anvil.js.window import ej, jQuery
from ..datamodel import ModelTypeBase
from .FormInputs import BaseInput
from ..tools.utils import AppEnv


# UI component based on SyncFusion ListBox control
class ListView(BaseInput):
    def __init__(self,
                 text_field=None,
                 value_field=None,
                 header=None,
                 container_class='',
                 view_class='',
                 model=None,
                 options=None,
                 compute_option=None,
                 select='single',
                 select_all=False,
                 edit_form=None,
                 **kwargs):
        super().__init__(**kwargs)

        self.select = 'Multiple' if select == 'multi' else 'Single'
        self.select_all = select_all
        self.header = header
        self.float_label = False
        self.container_class = container_class
        self.view_class = view_class
        self.model = model
        self.text_field = text_field or 'text'
        self.value_field = value_field or 'value'
        self.compute_option = compute_option
        self.options = options
        self.edit_form = edit_form
        self.fields = {'text': text_field, 'value': value_field}

        self.html = f'<div class="{self.container_class}">'
        if self.label:
            self.html += f'<label id="label_{self.el_id}" class="da-form-input-label">{self.label or ""}</label>'
        self.html += f'<div class="{self.view_class}" id="{self.el_id}" name="{self.el_id}"></div></div>'



    @property
    def options(self):
        return self._options


    @options.setter
    def options(self, value):
        if not value:
            options = []
        else:
            if not isinstance(value, list):
                value = [*value]
            if isinstance(value[0], str):
                options = [{self.text_field: option, self.value_field: option} for option in value]
            else:
                model_field = self.text_field.replace('.', '__') if self.model else self.text_field
                options = [
                    {
                        self.text_field: self.compute_option(option)
                        if self.compute_option and callable(self.compute_option)
                        else option.get(model_field, ''),
                        self.value_field: option[self.value_field],
                    } for option in value
                ]
        # for option in value:
        #     data_row = option if (isinstance(option, ModelTypeBase)) else option.get('row', option)
        #     if self.compute_option and callable(self.compute_option):
        #         name = self.compute_option(data_row)
        #     else:
        #         name = self.get_field_value(data_row, self.display_field)
        #     uid = data_row['uid']
        #     options.append({'name': name, 'uid': uid})
        # print('options', options)
        # if isinstance(options, list) and options != [] and isinstance(options[0], str):
        #     self._options = [{'text': option, 'value': option} for option in options]
        # else:
        print('ListView options', options)
        self._options = options
        if self._control is not None:
            self.control.dataSource = options

    def get_field_value(self, data, field):
        field_name = field.split('.', 1)
        if len(field_name) > 1:
            return self.get_field_value(data[field_name[0]], field_name[1])
        else:
            return data[field_name[0]]

    def show(self):
        super().show()
        if self._control is not None:
            self.control.dataSource = self.options

    def form_show(self):
        self.show()

    def create_control(self, **kwargs):
        listview_config = {
            'dataSource': self.options,
            'fields': self.fields,
            'cssClass': 'e-list-template',
        }
        if self.header:
            listview_config['headerTitle'] = self.header
            listview_config['showHeader'] = True
        selection_settings = {'mode': self.select}
        if self.select_all:
            selection_settings['showSelectAll'] = True
            selection_settings['showCheckbox'] = True
        listview_config['selectionSettings'] = selection_settings
        listview_config['template'] = f'<div class="e-list-wrapper ">\
                                            <div class="e-list-content">${{name}}\
                                                <div id="${{{self.value_field}}}-edit-button" class="da-listview-item-button"></div>\
                                            </div>\
                                        </div>'
        listview_config['actionComplete'] = self.render_edit_button

        self.control = ej.lists.ListView(listview_config)

    def render_edit_button(self, args):
        print('render_edit_button', args)

        for item in args.data:
            edit_button = ej.buttons.Button({
                'iconCss': f'fa-solid fa-pencil',
                'cssClass': 'e-flat e-small e-icon-btn',
            }, f'#{item[self.value_field]}-edit-button')
            edit_button.element.onclick = lambda click_args: self.edit_item(item, click_args)

    def edit_item(self, item, args):
        print('edit_item', item, args)
        args.cancel = True
        if callable(self.edit_form):
            self.edit_form(item)
