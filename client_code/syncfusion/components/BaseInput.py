# Form input fields and controls
from anvil import *
import anvil.server
import anvil.media
import anvil.js
from anvil.js.window import jQuery, ej, FileReader, Uint8Array, Event

from ..app.lib import *
from ..app.constants import *
from ..orm_client.lib import *
from ..orm_client.model import *
from ..orm_client import enumerations as enums

import datetime
import time
import base64
import string
import uuid
import sys


# Implemented form input field control classes
# --------------------------------------------
# FormInput - base input field class without JS control
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


# Base form input class
class FormInput:

    def __init__(self, name=None, label=None, float_label=True, shadow_label=False, col_class=None, col_style=None,
                 value=None, save=True, enabled=True, el_id=None, container_id=None, on_change=None, **kwargs):
        self.name = name
        self.label = label if shadow_label is False else ''
        self.shadow_label = f'<div class="pm-form-input-shadow-label">{label}</div>' if shadow_label is True else ''
        self.float_label = float_label
        self.col_class = col_class
        self.col_style = col_style
        self._value = value
        self.save = save
        self._enabled = enabled
        self.el_id = el_id if el_id is not None else new_el_id()
        self.container_id = container_id if container_id is not None else new_el_id()
        self._html = None
        self._control = None
        self.visible = False
        self.on_change = on_change

        self.grid_data = None
        self.edit_el = None

        self.html = f'\
       <div class="form-group pm-form-group">\
         <input type="text" class="form-control" id="{self.el_id}" name="{self.el_id}">\
       </div>'

        self.grid_column = {
            'field': self.name, 'headerText': self.label, 'type': 'string',
            'edit': {'create': self.grid_edit_create, 'read': self.grid_edit_read, 'write': self.grid_edit_write,
                     'destroy': self.grid_edit_destroy}
        }

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
        if self._control is not None:
            self.control.value = value

    def create_control(self):
        pass

    def show(self):
        if not self.visible:
            # html = self.html + f'<div class="pm-form-input-shadow-label">{self.label}</div>'
            anvil.js.window.document.getElementById(self.container_id).innerHTML = self.html + self.shadow_label
            if self._control is None:
                self.create_control()
            self.control.appendTo(f"#{self.el_id}")
            self.value = self._value
            self.visible = True
            self.enabled = self._enabled

    def hide(self):
        if self.visible:
            anvil.js.window.document.getElementById(self.container_id).innerHTML = ''
            self.visible = False

    def change(self, args):
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


# Single line text input
class TextInput(FormInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.html = f'\
       <div class="form-group pm-form-group">\
         <input type="text" class="form-control" id="{self.el_id}" name="{self.el_id}">\
       </div>'

    def create_control(self):
        self.control = ej.inputs.TextBox({'placeholder': self.label})


# Multi line text input
class MultiLineInput(TextInput):
    def __init__(self, rows=2, **kwargs):
        super().__init__(**kwargs)

        self.html = f'\
      <div class="form-group pm-form-group">\
        <textarea class="form-control" id="{self.el_id}" name="{self.el_id}" rows="{rows}"></textarea>\
      </div>'


# Number input
class NumberInput(FormInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.grid_column['type'] = 'number'
        self.grid_column['textAlign'] = 'Right'
        self.grid_column['format'] = 'C2'

    def create_control(self):
        self.control = ej.inputs.NumericTextBox({'placeholder': self.label, 'showSpinButton': False})


# Date picker input
class DateInput(FormInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.grid_column['type'] = 'date'
        self.grid_column['format'] = {'type': 'date', 'format': 'dd/MM/yyyy'}

    def create_control(self):
        self.control = ej.calendars.DatePicker({'placeholder': self.label})

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
class DateTimeInput(FormInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.grid_column['type'] = 'dateTime'
        self.grid_column['format'] = {'type': 'dateTime', 'format': 'dd/MM/yyyy hh:mm a'}

    def create_control(self):
        self.control = ej.calendars.DateTimePicker({'placeholder': self.label})

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
class TimeInput(FormInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.grid_column['type'] = 'dateTime'
        self.grid_column['format'] = {'type': 'dateTime', 'format': 'hh:mm a'}

    def create_control(self):
        self.control = ej.calendars.TimePicker({'placeholder': self.label})

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
class CheckboxInput(FormInput):
    def __init__(self, label_position='After', **kwargs):
        self.label_position = label_position
        super().__init__(**kwargs)

        self.html = f'\
      <div class="form-group pm-form-group">\
        <input type="checkbox" class="form-control pm-checkbox-input" id="{self.el_id}" name="{self.el_id}">\
      </div>'

        self.grid_column['type'] = 'boolean'
        self.grid_column['displayAsCheckBox'] = True

    def create_control(self):
        self.control = ej.buttons.CheckBox({
            'label': self.label,
            'labelPosition': self.label_position,
            'cssClass': 'pm-checkbox-input',
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

    def grid_edit_read(self, input_element, input_value):
        return self.control.checked


# Radio button input
class RadioButtonInput(FormInput):
    def __init__(self, options=None, direction='horizontal', **kwargs):
        self.options = [] if options is None else options
        self.direction = direction
        super().__init__(**kwargs)

        # create html
        spacer = '<br>' if self.direction == 'vertical' else '&nbsp;&nbsp'
        html_string = f'<div class="form-group pm-form-group pm-radiobutton-input">'
        for option in self.options:
            el_id = new_el_id()
            html_string += f'<input type="radio" class="form-control" id="{el_id}">{spacer}'
            option['el_id'] = el_id
        html_string += f'</div>'
        self.html = html_string

    def create_control(self):
        # create input controls
        for option in self.options:
            radio_button = ej.buttons.RadioButton({
                'name': self.name,
                'value': option['value'],
                'label': option['label'] if 'label' in option else option['value'],
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
class DropdownInput(FormInput):
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
                'placeholder': self.label,
                'showClearButton': True,
                'fields': self.fields,
                'dataSource': self.options,
                'allowFiltering': True,
            })
        elif self.select == 'multi':
            self.control = ej.dropdowns.MultiSelect({
                'placeholder': self.label,
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
        self._options = options
        if self._control is not None:
            self.control.dataSource = options


# Lookup input (reference field)
class LookupInput(DropdownInput):
    def __init__(self, model=None, text_field=None, compute_option=None, data=None, add_item_label='Add Item',
                 add_item_form=None, add_item_model=None, **kwargs):
        self.model = model
        self.text_field = text_field
        self.compute_option = compute_option
        self.add_item_label = add_item_label
        self.add_item_form = add_item_form
        self.add_item_model = add_item_model
        self.add_item_popup = None
        options = None
        if self.model:
            if self.model in enums.Models:
                options = enums.Models[self.model].options
            elif not data:
                cols = [self.text_field] if isinstance(self.text_field, str) else self.text_field
                data = getattr(sys.modules[__name__], self.model).get_grid_view(
                    view_config={'columns': [{'name': col} for col in cols]})
        if data:
            options = [
                {
                    'name': self.compute_option(option) if self.compute_option and callable(self.compute_option)
                    else option[self.text_field.split('.', 1)[0]], 'uid': option['uid']
                } for option in data
            ]
            # 'row': option['row']} for option in data]
        super().__init__(options=options, **kwargs)

    def create_control(self):
        super().create_control()
        if self.add_item_form is not None or self.add_item_model is not None:
            self.add_el_id = new_el_id()
            self.control.footerTemplate = f'<button class="e-control e-btn e-lib e-flat" type="button" ' \
                                          f'id="{self.add_el_id}">+ {self.add_item_label}</button>'
            self.control.open = self.control_open
            self.control.close = self.control_close

    @property
    def value(self):
        if self._control and self.control.value is not None:
            if self.select == 'single':
                # self._value = self.control.getDataByValue(self.control.value)['uid']
                self._value = self.control.getDataByValue(self.control.value)
            else:
                # self._value = [self.control.getDataByValue(item)['uid'] for item in self.control.value]
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
            # if self.name == 'fee_type':
            #     print(self.control.dataSource)
            # self.control.dataBind()

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
                    props = {'action': 'add', 'modal': True, 'update_source': self.new_item}
                    if self.add_item_model is not None:
                        props['model'] = self.add_item_model
                    self.add_item_popup = self.add_item_form(**props)
                self.add_item_popup.form_show()

    def new_item(self, item):
        self.control.addItem(
            {
                'text': self.compute_option(item) if self.compute_option and callable(self.compute_option)
                else item[self.text_field],
                'value': item.uid,
                'row': item
            }, 0
        )
        if self.select == 'single':
            self.control.index = 0
        elif self.value:
            self.control.value.append(item.uid)
        else:
            self.control.value = [item.uid]


# Signature input
class SignatureInput(FormInput):
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
        self.control = ej.inputs.Signature({'placeholder': self.label})

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
class FileUploadInput(FormInput):
    def __init__(self, width=None, height=None, **kwargs):
        super().__init__(**kwargs)

        self.html = f'\
       <div class="form-group pm-form-group">\
         <h6>{self.label}</h6>\
         <input type="file" class="form-control" id="{self.el_id}" name="{self.el_id}">\
       </div>'

    def create_control(self):
        self.control = ej.inputs.Uploader({'placeholder': self.label})

    @property
    def value(self):
        if self._control:
            file_data = self.control.getFilesData()[0].rawFile
            file_content = anvil.js.window.Uint8Array(file_data.arrayBuffer())
            self._value = anvil.BlobMedia(name=file_data.name, content_type=file_data.type, content=file_content)
            return self._value

    @value.setter
    def value(self, value):
        self._value = value
        if self._control is not None and value is not None:
            self.control.load(value)


# Form inline message area
class InlineMessage(FormInput):
    def __init__(self, message=None, **kwargs):
        super().__init__(**kwargs)

        self.html = f'<div id="{self.el_id}"></div>'
        self.message = message
        self.save = False

    @property
    def value(self):
        self._value = self.message
        return self._value

    @value.setter
    def value(self, value):
        self.message = value
        anvil.js.window.document.getElementById(self.el_id).innerHTML = self.message

    def show(self):
        if not self.visible:
            anvil.js.window.document.getElementById(self.container_id).innerHTML = self.html
            anvil.js.window.document.getElementById(self.el_id).innerHTML = self.message
            self.visible = True
