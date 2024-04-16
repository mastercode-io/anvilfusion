# Form input fields and controls
import uuid

import anvil.js
from anvil import BlobMedia
from anvil.js.window import jQuery, ej, FileReader, Uint8Array, Event
from ..datamodel.types import FieldTypes
from ..datamodel.particles import ModelTypeBase
from ..tools.utils import AppEnv, DotDict, new_el_id, label_to_id
import datetime


# Implemented form input field control classes
# --------------------------------------------
# BaseInput - base input field class without JS control
# TextInput - single-line text input
# MultiLineInput - multi-line (textarea) input
# NumberInput - single-line digits only input
# DateInput - date picker input
# DateTimeInput - date-time picker input
# TimeInput - time picker input
# CheckboxInput - checkbox (boolean) field
# RadioButton - radio button selector
# DropdownInput - dropdown single/multi select input
# LookupInput - dropdown single/multi select input for lookup (related) fields
# SignatureInput - canvas draw input for ink-lke signatures
# UploadInput - file upload input
# InlineMessage - form inline message placeholder


# Base form input class
class BaseInput:

    def __init__(self,
                 name=None,
                 label=None,
                 field_type=None,
                 float_label=True,
                 shadow_label=False,
                 placeholder=None,
                 col_class=None,
                 col_style=None,
                 css_class=None,
                 value=None,
                 save=True,
                 enabled=True,
                 el_id=None,
                 container_id=None,
                 on_change=None,
                 is_dependent=False,
                 grid_field=None,
                 required=False,
                 **kwargs):
        self.name = name
        self.type = 'Input'
        self.label = label if shadow_label is False else ''
        self.field_type = field_type or FieldTypes.SINGLE_LINE
        self.shadow_label = f'<div class="da-form-input-shadow-label">{label}</div>' if shadow_label is True else ''
        self.float_label = float_label
        self.placeholder = placeholder or self.label
        self.col_class = col_class
        self.col_style = col_style
        self.css_class = css_class
        self._value = value
        self.save = save
        self.is_dependent = is_dependent
        self._enabled = enabled
        self._required = required
        self.el_id = el_id if el_id is not None else new_el_id()
        self.container_id = container_id if container_id is not None else new_el_id()
        self._html = None
        self._grid_column = None
        self.grid_field = (grid_field or self.name or self.label or '').replace('.', '__')
        self._control = None
        self.visible = False
        self.on_change = on_change

        self.grid_data = None
        self.edit_el = None

        self.html = f'\
            <div class="form-group da-form-group">\
                <input class="form-control" id="{self.el_id}" name="{self.el_id}">\
            </div>'

    @property
    def grid_column(self):
        self._grid_column = {
            'field': self.grid_field,
            'headerText': self.label,
            'type': self.field_type.GridType,
            'format': self.field_type.GridFormat,
            'textAlign': getattr(self.field_type, 'GridTextAlign', 'Left'),
            'displayAsCheckBox': self.field_type == FieldTypes.BOOLEAN,
            'edit': {
                'create': self.grid_edit_create,
                'read': self.grid_edit_read,
                'write': self.grid_edit_write,
                'destroy': self.grid_edit_destroy
            }
        }
        return self._grid_column

    @property
    def html(self):
        return self._html

    @html.setter
    def html(self, value):
        self._html = value

    @property
    def control(self):
        return self._control

    @control.setter
    def control(self, value):
        # print('set control', value, self.name, self._control)
        self._control = value
        if self._control is not None:
            self.control.change = self.change
            if self.float_label is True:
                self.control.floatLabelType = 'Always'

    @property
    def enabled(self):
        if self._control is not None:
            self._enabled = self.control.enabled
            return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value
        if self._control is not None:
            self.control.enabled = value

    @property
    def value(self):
        if self._control is not None:
            self._value = self.control.value
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        if self._control is not None:
            self.control.value = value

    @property
    def required(self):
        return self._required

    @required.setter
    def required(self, value):
        self._required = value
        if self._required and self.visible and self.label:
            label_el = anvil.js.window.document.getElementById(f'label_{self.el_id}')
            label_el.innerHTML += '<span style="color:red;!important"> *</span>'

    def create_control(self):
        pass

    def show(self):
        if not self.visible:
            anvil.js.window.document.getElementById(self.container_id).innerHTML = self.html + self.shadow_label
            if self._control is None:
                self.create_control()
            if self.control:
                self.control.appendTo(f"#{self.el_id}")
            self.value = self._value
            self.visible = True
            self.enabled = self._enabled
            self.required = self._required
            # label = anvil.js.window.document.getElementById(f'label_{self.el_id}')
            # label.innerHTML += '<span style="color:red;!important"> *</span>'

    def hide(self):
        if self.visible:
            # print('hide', self.name)
            anvil.js.window.document.getElementById(self.container_id).innerHTML = ''
            self.visible = False

    def change(self, args):
        # print('change', self.name, args)
        if self.on_change is not None:
            self.on_change(DotDict({'name': self.name, 'value': self.value if args.get('value') else None}))

    def grid_edit_create(self, args):
        self.grid_data = args.data
        self.edit_el = anvil.js.window.document.createElement('input')
        return self.edit_el

    def grid_edit_read(self, input_element, input_value):
        return self.control.value

    def grid_edit_write(self, args):
        self.create_control()
        self.control.appendTo(self.edit_el)
        if args.column.field in args.rowData:
            self.control.value = args.rowData[args.column.field]

    def grid_edit_destroy(self):
        pass

    def destroy(self):
        if self._control is not None:
            self.control.destroy()
            self._control = None


class Button(BaseInput):
    def __init__(self, is_primary=True, content=None, icon=None, action=None, **kwargs):
        super().__init__(**kwargs)
        self.type = 'Button'
        self.content = content
        self.icon = icon
        self.action = action
        self.is_primary = is_primary
        self.html = f'<div id="{self.el_id}" name="{self.el_id}">{self.content}</div>'
        self.save = False

    def create_control(self):
        self.control = ej.buttons.Button({
            'content': self.content,
            'iconCss': f'fa-solid fa-{self.icon}' if self.icon else '',
            'cssClass': self.css_class or '',
            'isPrimary': True if self.is_primary else False,
        })

    # def show(self):
    #     super().show()
        # self.control.element.onclick = self.action
    #     if not self.visible:
    #         if self._control is None:
    #             anvil.js.window.document.getElementById(self.container_id).innerHTML = self.html
    #             self.create_control()
    #             self.control.appendTo(f"#{self.el_id}")
    #         else:
    #             anvil.js.window.document.getElementById(self.container_id).style.display = 'inline-flex'
    #         self.value = self._value
    #         self.visible = True
    #
    # def hide(self):
    #     if self.visible:
    #         self.visible = False
    #         anvil.js.window.document.getElementById(self.container_id).style.display = 'none'

    def destroy(self):
        pass

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value
        if self._control is not None:
            self.control.content = value

    @property
    def enabled(self):
        if self._control is not None:
            self._enabled = not self.control.disbled
            return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = not value if value else False
        if self._control is not None:
            self.control.disabled = not self._enabled

    @property
    def required(self):
        return None

    @required.setter
    def required(self, value):
        self._value = value

    def show(self):
        super().show()
        self.control.element.onclick = self.action


class DropdownButton(Button):
    def __init__(self, options=None, **kwargs):
        super().__init__(**kwargs)
        self.type = 'Input'
        self.options = options
        # self.html = f'<div id="{self.el_id}" name="{self.el_id}">{self.content}</div>'

    def create_control(self):
        self.control = ej.splitbuttons.DropDownButton({
            'content': self.content,
            'iconCss': f'fa-solid fa-{self.icon}' if self.icon else '',
            'cssClass': self.css_class or '',
            'isPrimary': True if self.is_primary else False,
            'items': [{'id': label_to_id(option), 'text': option} for option in self.options],
            'select': self.action,
        })


class HiddenInput(BaseInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.html = f'<input type="hidden" id="{self.el_id}" name="{self.el_id}">'

    def create_control(self):
        pass

    def show(self):
        pass

    def hide(self):
        pass

    def destroy(self):
        pass

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


# Single line text input
class TextInput(BaseInput):
    def __init__(self, input_type='text', **kwargs):
        super().__init__(**kwargs)
        self.input_type = input_type
        self.element = None

        self.html = f'\
            <div class="form-group pm-form-group">\
                <input type="text" class="form-control" id="{self.el_id}" name="{self.el_id}">\
            </div>'

    def create_control(self):
        self.control = ej.inputs.TextBox({
            'placeholder': self.placeholder,
            'type': self.input_type,
        })

    def show(self):
        super().show()
        if self.input_type == 'tel':
            self.element = anvil.js.window.document.getElementById(self.el_id)
            self.control.addEventListener('input', self.format_phone_number)

    # @staticmethod
    def format_phone_number(self, args):
        input_value = "".join(filter(str.isdigit, self.element.value))
        print(input_value)
        if input_value:
            print('debug')
            input_value = input_value[:10]
            formatted_value = ""
            if len(input_value) > 0:
                formatted_value = "(" + input_value[:3]
            if len(input_value) > 3:
                formatted_value += ") " + input_value[3:6]
            if len(input_value) > 6:
                formatted_value += "-" + input_value[6:]
            self.element.value = formatted_value
        else:
            self.element.value = input_value


# Multi line text input
class MultiLineInput(BaseInput):
    def __init__(self, rows=2, **kwargs):
        super().__init__(**kwargs)

        self.html = f'\
            <div class="form-group pm-form-group">\
                <textarea class="form-control" id="{self.el_id}" name="{self.el_id}" rows="{rows}"></textarea>\
            </div>'

    def create_control(self):
        self.control = ej.inputs.TextBox({'placeholder': self.placeholder})


# Number input
class NumberInput(BaseInput):
    def __init__(self, number_format=None, **kwargs):
        super().__init__(**kwargs)
        self.number_format = number_format
        self.grid_column['type'] = 'number'
        self.grid_column['textAlign'] = 'Right'
        self.grid_column['format'] = 'C2'

    def create_control(self):
        self.control = ej.inputs.NumericTextBox({
            'placeholder': self.placeholder,
            'showSpinButton': False,
            'format': self.number_format,
        })


# Date picker input
class DateInput(BaseInput):
    def __init__(self, string_format=None, **kwargs):
        super().__init__(**kwargs)
        self.string_format = string_format or 'dd-MM-yyyy'
        self.grid_column['type'] = 'date'
        self.grid_column['format'] = {'type': 'date', 'format': 'dd-MM-yyyy'}

    def create_control(self):
        self.control = ej.calendars.DatePicker({'placeholder': self.placeholder, 'format': self.string_format})

    @property
    def value(self):
        if self._control is not None and self.control.value is not None:
            epoch = self.control.value.getTime()
            self._value = datetime.date.fromtimestamp(epoch / 1000)
        return self._value

    @value.setter
    def value(self, value):
        if value is None:
            self._value = None
            if self._control is not None:
                self.control.value = None
        else:
            if isinstance(value, datetime.date):
                self._value = value
            else:
                self._value = datetime.date.fromisoformat(value) if isinstance(value, str) \
                    else datetime.date.fromtimestamp(value.getTime() / 1000)
            if self._control is not None:
                dt = datetime.datetime.combine(self._value, datetime.datetime.min.time())
                epoch = int(dt.strftime('%s')) * 1000
                self.control.value = anvil.js.window.Date(epoch)

    @property
    def serialized(self):
        return self.value.isoformat() if self._value is not None else None


# Date-Time picker input
class DateTimeInput(BaseInput):
    def __init__(self, string_format=None, **kwargs):
        super().__init__(**kwargs)
        self.string_format = string_format or 'dd-MM-yyyy hh:mm a'
        self.grid_column['type'] = 'dateTime'
        self.grid_column['format'] = {'type': 'dateTime', 'format': 'dd-MM-yyyy hh:mm a'}

    def create_control(self):
        self.control = ej.calendars.DateTimePicker({'placeholder': self.placeholder, 'format': self.string_format})

    @property
    def value(self):
        if self._control is not None and self.control.value is not None:
            epoch = self.control.value.getTime()
            self._value = datetime.datetime.fromtimestamp(epoch / 1000)
        return self._value

    @value.setter
    def value(self, value):
        if value is None:
            self._value = None
            if self._control is not None:
                self.control.value = None
        else:
            if isinstance(value, datetime.datetime):
                self._value = value
            else:
                self._value = datetime.datetime.fromisoformat(value) if isinstance(value, str) \
                    else datetime.datetime.fromtimestamp(value.getTime() / 1000)
            if self._control is not None and value is not None:
                epoch = int(self._value.strftime('%s')) * 1000
                self.control.value = anvil.js.window.Date(epoch)

    @property
    def serialized(self):
        return self.value.isoformat() if self._value is not None else None


# Time picker input
class TimeInput(BaseInput):
    def __init__(self, string_format=None, **kwargs):
        super().__init__(**kwargs)

        self.grid_column['type'] = 'dateTime'
        self.grid_column['format'] = {'type': 'dateTime', 'format': 'hh:mm a'}

    def create_control(self):
        self.control = ej.calendars.TimePicker({'placeholder': self.placeholder, 'format': 'hh:mm a'})

    @property
    def value(self):
        if self._control is not None and self.control.value is not None:
            hours = self.control.value.getHours()
            minutes = self.control.value.getMinutes()
            self._value = datetime.datetime(1970, 1, 1, hours, minutes)
        return self._value

    @value.setter
    def value(self, value):
        if value is None:
            self._value = None
            if self._control is not None:
                self.control.value = None
        else:
            if isinstance(value, datetime.datetime):
                self._value = value
            else:
                self._value = datetime.datetime.fromisoformat(value) if isinstance(value, str) \
                    else datetime.datetime.fromtimestamp(value.getTime() / 1000)
            if self._control is not None and value is not None:
                epoch = int(self._value.strftime('%s')) * 1000
                self.control.value = anvil.js.window.Date(epoch)

    @property
    def serialized(self):
        return self.value.isoformat() if self._value is not None else None


# Checkbox input
class CheckboxInput(BaseInput):
    def __init__(self, label_position='After', **kwargs):
        self.label_position = label_position
        super().__init__(**kwargs)

        self.html = f'\
      <div class="form-group pm-form-group">\
        <input type="checkbox" class="form-control da-checkbox-input" id="{self.el_id}" name="{self.el_id}">\
      </div>'

        self.grid_column['type'] = 'boolean'
        self.grid_column['displayAsCheckBox'] = True

    def create_control(self):
        self.control = ej.buttons.CheckBox({
            'label': self.label,
            'labelPosition': self.label_position,
            'cssClass': self.css_class or 'da-checkbox-input',
        })

    @property
    def value(self):
        if self._control:
            self._value = self.control.checked
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        if self._control:
            self.control.checked = self._value

    @property
    def enabled(self):
        if self._control is not None:
            self._enabled = not self.control.disbled
            return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value
        if self._control is not None:
            self.control.disabled = not value

    def grid_edit_read(self, input_element, input_value):
        return self.control.checked


# Radio button input
class RadioButtonInput(BaseInput):
    def __init__(self, options=None, direction='horizontal', **kwargs):
        self.options = []
        self.direction = direction
        super().__init__(**kwargs)

        # create html
        spacer = '<br>' if self.direction == 'vertical' else '&nbsp;&nbsp'
        html_string = f'<div id="{self.el_id}" class="form-group pm-form-group pm-radiobutton-input">'
        if self.label:
            html_string += (f'<div class="e-float-text e-label-top" '
                            f'style="color:rgba(var(--color-sf-outline));font-size:11px;margin-bottom:10px;">'
                            f'{self.label}</div>')
        for option in options:
            el_id = new_el_id()
            html_string += f'<input type="radio" class="form-control" id="{el_id}">{spacer}'
            if isinstance(option, str):
                option = {'value': option, 'label': option}
            option['el_id'] = el_id
            self.options.append(option)
        html_string += f'</div>'
        self.html = html_string

    def create_control(self):
        # create input controls
        for option in self.options:
            radio_button = ej.buttons.RadioButton({
                'name': self.name,
                'value': option['value'],
                'label': option.get('label', option['value']),
                'change': self.change,
            })
            option['control'] = radio_button
        self.value = self._value

    @property
    def value(self):
        for option in self.options:
            if 'control' in option and option['control'].checked is True:
                self._value = option['control'].properties['value']
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        for option in self.options:
            if 'control' in option and option['value'] == self._value:
                option['control'].checked = True

    def show(self):
        if not self.visible:
            anvil.js.window.document.getElementById(self.container_id).innerHTML = self.html
            self.create_control()
            for option in self.options:
                option['control'].appendTo(f'#{option["el_id"]}')
            self.value = self._value
            self.visible = True


# Dropdown input
class DropdownInput(BaseInput):
    def __init__(self, text_field='name', value_field='uid', select='single', options=None, **kwargs):
        self.select = select
        self.add_el_id = None
        self.value_field = value_field
        if isinstance(options, list) and options != [] and isinstance(options[0], str):
            self.fields = {'text': 'text', 'value': 'value'}
            self._options = [{'text': option, 'value': option} for option in options]
        else:
            self.fields = {'text': text_field, 'value': value_field}
            self._options = options
        super().__init__(**kwargs)

    def create_control(self):
        if self.select == 'single':
            self.control = ej.dropdowns.DropDownList({
                'placeholder': self.placeholder,
                'cssClass': self.css_class,
                'showClearButton': True,
                'fields': self.fields,
                'dataSource': self.options,
                'allowFiltering': True,
            })
        elif self.select == 'multi':
            self.control = ej.dropdowns.MultiSelect({
                'placeholder': self.placeholder,
                'cssClass': self.css_class,
                'showClearButton': True,
                'fields': self.fields,
                'dataSource': self.options,
                'showDropDownIcon': True,
                'allowFiltering': True,
            })

    @property
    def value(self):
        if self._control and self.control.value is not None:
            self._value = self.control.value
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        if self._control is not None:
            self.control.value = value

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        if isinstance(options, list) and options != [] and isinstance(options[0], str):
            self._options = [{'text': option, 'value': option} for option in options]
        else:
            self._options = options
        if self._control is not None:
            self.control.dataSource = options


# Lookup input (dropdown with options from a model)
class LookupInput(DropdownInput):
    def __init__(self, model=None, text_field=None, compute_option=None,
                 data=None, get_data=True, filters=None, search_queries=None,
                 add_item_label=None, add_item_form=None, add_item_model=None, add_item_data=None,
                 add_item=False, inline_grid=False,
                 **kwargs):
        self.model = model
        self.text_field = text_field or getattr(AppEnv.data_models, self.model)._title
        self.compute_option = compute_option
        self.add_item = add_item
        self.add_item_label = add_item_label or 'Add Item'
        self.add_item_form = add_item_form
        self.add_item_model = add_item_model or model
        self.add_item_data = add_item_data
        self.add_item_popup = None
        options = None
        if self.model:
            if AppEnv.enum_models and self.model in AppEnv.enum_models:
                options = AppEnv.enum_models[self.model].options
            elif not data and get_data:
                cols = [self.text_field] if isinstance(self.text_field, str) else self.text_field
                data = getattr(AppEnv.data_models, self.model).get_grid_view(
                    view_config={'columns': [{'name': col} for col in cols]},
                    filters=filters, search_queries=search_queries)
        if data:
            # print('lookup data', data)
            options = [
                {
                    'name': self.compute_option(option) if self.compute_option and callable(self.compute_option)
                    else option.get(self.text_field.replace('.', '__'), ''),
                    'uid': option['uid'],
                } for option in data
            ]
        value_field = 'uid' if not inline_grid else 'name'
        super().__init__(options=options, value_field=value_field, **kwargs)

    def create_control(self):
        super().create_control()
        if self.add_item:
            self.add_el_id = new_el_id()
            self.control.footerTemplate = f'<button class="e-control e-btn e-lib e-flat" type="button" ' \
                                          f'id="{self.add_el_id}">+ {self.add_item_label}</button>'
            self.control.open = self.control_open
            self.control.close = self.control_close

    @property
    def data(self):
        return super().options

    @data.setter
    def data(self, data):
        if data:
            self.options = self.get_options(data)
        else:
            self.options = None

    def get_options(self, data):
        options = []
        for option in data:
            data_row = option if (isinstance(option, ModelTypeBase)) else option.get('row', option)
            if self.compute_option and callable(self.compute_option):
                name = self.compute_option(data_row)
            else:
                name = self.get_field_value(data_row, self.text_field)
            uid = data_row['uid']
            options.append({'name': name, 'uid': uid})
        return options

    def get_field_value(self, data, field):
        # print('get field value', data, field)
        field_name = field.split('.', 1)
        if len(field_name) > 1:
            return self.get_field_value(data[field_name[0]], field_name[1])
        else:
            return data[field_name[0]]

    @property
    def value(self):
        if self._control and self.control.value is not None:
            if self.select == 'single':
                self._value = self.control.getDataByValue(self.control.value)
            else:
                self._value = [self.control.getDataByValue(item) for item in self.control.value]
        return self._value

    @value.setter
    def value(self, value):
        if self._control is not None:
            if value:
                if self.select == 'single':
                    self.control.value = value['uid']
                else:
                    self.control.value = [item['uid'] for item in value]
            else:
                self.control.value = None

    def control_open(self, args):
        if self.add_item_form is not None:
            anvil.js.window.document.addEventListener('click', self.add_item)

    def control_close(self, args):
        if self.add_item_form is not None:
            anvil.js.window.document.removeEventListener('click', self.add_item)

    def add_item(self, event):
        if event.target and event.target.id == self.add_el_id:
            if self.add_item_form is not None:
                if self.add_item_popup is None:
                    props = {
                        'action': 'add',
                        'modal': True,
                        'data': self.add_item_data,
                        'update_source': self.new_item,
                    }
                    if self.add_item_model is not None:
                        props['model'] = self.add_item_model
                    self.add_item_popup = self.add_item_form(**props)
                self.add_item_popup.form_show()

    def new_item(self, item, action):
        print('new item', item, action)
        if item:
            self.control.addItem(
                {
                    'name': self.compute_option(item) if self.compute_option and callable(self.compute_option)
                    else item[self.text_field],
                    'uid': item.uid,
                    # 'row': item
                }, 0
            )
            if self.select == 'single':
                self.control.index = 0
            elif self.value:
                self.control.value.append(item.uid)
            else:
                self.control.value = [item.uid]


# Signature input
class SignatureInput(BaseInput):
    def __init__(self, width=None, height=None, **kwargs):
        self.width = width
        self.height = height
        super().__init__(**kwargs)

        canvas_height = f'height:{self.height};' if self.height is not None else ''
        canvas_width = f'width:{self.width};' if self.width is not None else ''
        self.html = f'<div id="parent-{self.el_id}">\
      <div class="form-group pm-form-group" style="{canvas_height}{canvas_width}">{self.label}<br>\
        <canvas class="form-control" style="height:100%;width:100%;" id="{self.el_id}" name="{self.el_id}"></canvas>\
      </div></div>'

    def create_control(self):
        self.control = ej.inputs.Signature({'placeholder': self.placeholder})

    @property
    def value(self):
        if self._control:
            self._value = self.control.getSignature({})
            return self._value

    @value.setter
    def value(self, value):
        self._value = value
        if self._control is not None and value is not None:
            self.control.load(value)


# File Upload input
class FileUploadInput(BaseInput):
    def __init__(self, width=None, height=None, multiple=False, required=False, storage_config=None, **kwargs):
        super().__init__(**kwargs)
        self.multiple = multiple
        self.storage_config = storage_config
        self._value = []

        self.html = f'\
           <div class="form-group pm-form-group">\
             <h6>{self.label}</h6>\
             <input type="file" class="form-control" id="{self.el_id}" name="{self.el_id}">\
             <div id="{self.el_id}-required" class="e-error" style="display:none;">* Select file(s) to upload</div>\
           </div>'

    def create_control(self):
        self.control = ej.inputs.Uploader({
            'multiple': self.multiple,
            'selected': self.upload_files,
            'removing': self.remove_upload,
            'buttons': {
                'browse': 'Select File(s)',
                'clear': 'Clear All',
                'upload': 'Upload All',
            },
            # 'autoUpload': False,
            # 'asyncSettings': {
            #     'saveUrl': self.upload_files,
            #     'removeUrl': self.remove_upload,
            # }
        })
        # print('upload', self.control.change)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value or []

    def upload_files(self, args):
        if args:
            print('uploading file(s)', self.storage_config)
            anvil.js.window.document.getElementById(f'{self.el_id}-required').style.display = 'none'
            if self.storage_config and self.storage_config.get('type') == 'aws_s3':
                s3_bucket = self.storage_config.get('bucket', AppEnv.aws_config.get('s3_bucket'))
                key_prefix = self.storage_config.get('key_prefix', 'files')
                for file in args.filesData:
                    print(file.name, file.type, file.size, file.size)
                    file_key = (f"tenants/{AppEnv.logged_user['tenant_uid']}/{key_prefix}/"
                                f"{uuid.uuid4()}/{file.name}")
                    if AppEnv.aws_s3.upload_file(file_key, file.rawFile, bucket=s3_bucket):
                        print('uploaded file', file_key)
                        self._value.append({
                            'name': file.name,
                            'size': file.size,
                            'type': file.type,
                            'storage': {
                                'type': 'aws_s3',
                                'bucket': s3_bucket,
                                'key': file_key,
                            },
                        })
                    else:
                        self.control.remove(file)
                        # self.remove_upload({'filesData': [file]})
            else:
                self._value = args.filesData if self.multiple else args.filesData[0]
                super().change({'value': self._value})
        # print('upload complete', self._value)

    def remove_upload(self, args):
        print('removing', args)
        if self.storage_config and self.storage_config.get('type') == 'aws_s3':
            for file in self._value:
                if file['name'] == args['filesData'][0].name:
                    AppEnv.aws_s3.delete_files([file['storage']['key']], bucket=file['storage']['bucket'])
                    self._value.remove(file)
                    break
        print('remove complete', self._value)

    def show_required(self):
        anvil.js.window.document.getElementById(f'{self.el_id}-required').style.display = 'block'


# Form inline message area
class InlineMessage(BaseInput):
    def __init__(self, content=None, label_css=None, **kwargs):
        super().__init__(**kwargs)

        # self.html = f'<div id="{self.el_id}"></div>'
        if not self.css_class:
            self.css_class = 'da-form-input-message'
        label_css = label_css or 'da-form-input-label'
        self.html = '<div class="form-group da-form-group">'
        if self.label:
            self.html += f'<label id="label_{self.el_id}" class="{label_css}">{self.label or ""}</label>'
        self.html += f'<div id="{self.el_id}" name="{self.el_id}" class="{self.css_class}">{content or ""}</div></div>'
        self._content = content or ''
        self._message_type = None
        self.save = False

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, content):
        self._content = content or ''
        el = anvil.js.window.document.getElementById(self.el_id)
        if el:
            el.innerHTML = self._content

    @property
    def message_type(self):
        return self._message_type

    @message_type.setter
    def message_type(self, value):
        self._message_type = value
        if self.visible:
            if self._message_type is not None:
                anvil.js.window.document.getElementById(self.el_id).className = self._message_type
            else:
                anvil.js.window.document.getElementById(self.el_id).className = ''

    def show(self):
        if not self.visible:
            anvil.js.window.document.getElementById(self.container_id).innerHTML = self.html
            anvil.js.window.document.getElementById(self.el_id).innerHTML = self._content
            self.visible = True
