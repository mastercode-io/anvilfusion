import anvil.js
from . import FormBase as form_base
from . import FormInputs
from ..datamodel.particles import Attribute, Relationship, types
from ..tools.utils import AppEnv
import datetime
import string


class MultiFieldInput(FormInputs.BaseInput):

    def __init__(self,
                 name=None,
                 label=None,
                 model=None,
                 fields=None,
                 schema=None,
                 orientation='rows',
                 cols=1,
                 **kwargs):
        super().__init__(**kwargs)
        self.name = name
        model_module = AppEnv.data_models
        if name and model and hasattr(model_module, model):
            self.model = getattr(model_module, model)
            self.schema = self.model._attributes[self.name].schema
        else:
            self.schema = schema if schema else {}
        if fields is None:
            schema_fields = []
            for name, field in self.schema.items():
                input_label = field.label if field.label else string.capwords(name.replace("_", " "))
                if isinstance(field, Attribute):
                    input_class = getattr(FormInputs, field.field_type.InputType)
                    schema_fields.append(input_class(name=name, label=input_label))
                elif isinstance(field, Relationship):
                    schema_fields.append(FormInputs.LookupInput(name=name, label=input_label))
            self.fields = schema_fields
        else:
            self.fields = fields
        if label == '_':
            section_label = None
        elif label:
            section_label = label
        else:
            section_label = string.capwords(self.name.replace("_", " ")) if self.name else None
        if orientation == 'rows':
            section_rows = []
            for i in range(0, len(self.fields), cols):
                section_rows.append(self.fields[i:i + cols])
            if len(section_rows[-1]) < cols:
                section_rows[-1] += [None] * (cols - len(section_rows[-1]))
            self.sections = [{
                'name': self.name,
                'label': section_label,
                # 'label_style': 'margin-top:-2px;',
                'rows': section_rows,
            }]
        else:
            section_cols = []
            rows_num = len(self.fields) // cols
            for i in range(0, cols):
                section_cols.append(self.fields[i * rows_num:(i + 1) * rows_num])
            if len(section_cols[-1]) < rows_num:
                section_cols[-1] += [None] * (rows_num - len(section_cols[-1]))
            self.sections = [{'name': self.name, 'label': section_label, 'cols': section_cols}]
        self.html, _ = form_base.FormBase.sections_content(self.sections)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value
        for field in self.fields:
            field.enabled = value

    @property
    def value(self):
        self._value = {
            field.name: field.value if not isinstance(field.value, (datetime.datetime, datetime.date))
            else field.value.isoformat()
            for field in self.fields
        }
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        if isinstance(value, dict):
            for field in self.fields:
                field.value = value.get(field.name, None)

    def show(self):
        if not self.visible:
            anvil.js.window.document.getElementById(self.container_id).innerHTML = self.html
            for field in self.fields:
                field.show()
            self.visible = True
            self.enabled = self._enabled

    def hide(self):
        if self.visible:
            for field in self.fields:
                field.hide()
            anvil.js.window.document.getElementById(self.container_id).innerHTML = ''
            self.visible = False

    def destroy(self):
        for field in self.fields:
            field.destroy()


class HyperlinkInput(MultiFieldInput):

    def __init__(self, **kwargs):

        label = kwargs.get('label', 'URL')
        schema = {
            'title': Attribute(field_type=types.FieldTypes.SINGLE_LINE),
            'link': Attribute(field_type=types.FieldTypes.SINGLE_LINE),
        }
        fields = [
            FormInputs.TextInput(name='title', label='Title'),
            FormInputs.TextInput(name='link', label='Link', placeholder='https://'),
        ]
        super().__init__(schema=schema, fields=fields, **kwargs)
