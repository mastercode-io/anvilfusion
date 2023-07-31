import anvil.js
import string

from .FormBase import FormBase
from . import FormInputs
from ..datamodel.particles import Attribute, Relationship
from ..tools.dependency_cache import DependencyCache


class MultiInput(FormInputs.BaseInput):

    def __init__(self,
                 name=None,
                 label=None,
                 model=None,
                 subfields=None,
                 schema=None,
                 orientation='rows',
                 cols=1,
                 **kwargs):
        super().__init__(**kwargs)
        self.name = name
        model_module = DependencyCache.get_dependency('data_models')
        if name and model and hasattr(model_module, model):
            self.model = getattr(model_module, model)
            self.schema = self.model._attributes[self.name].schema
        else:
            self.schema = schema if schema else {}
        if subfields is None:
            schema_fields = []
            for name, field in self.schema.items():
                input_label = field.label if field.label else string.capwords(name.replace("_", " "))
                if isinstance(field, Attribute):
                    input_class = getattr(FormInputs, field.field_type.InputType)
                    schema_fields.append(input_class(name=name, label=input_label))
                elif isinstance(field, Relationship):
                    schema_fields.append(FormInputs.LookupInput(name=name, label=input_label))
            self.subfields = schema_fields
        else:
            self.subfields = subfields
        if label:
            section_label = label
        else:
            section_label = string.capwords(self.name.replace("_", " ")) if self.name else None
        if orientation == 'rows':
            section_rows = []
            for i in range(0, len(self.subfields), cols):
                section_rows.append(self.subfields[i:i + cols])
            if len(section_rows[-1]) < cols:
                section_rows[-1] += [None] * (cols - len(section_rows[-1]))
            self.sections = [{'name': self.name, 'label': section_label, 'rows': section_rows}]
        else:
            section_cols = []
            rows_num = len(self.subfields) // cols
            for i in range(0, cols):
                section_cols.append(self.subfields[i * rows_num:(i + 1) * rows_num])
            if len(section_cols[-1]) < rows_num:
                section_cols[-1] += [None] * (rows_num - len(section_cols[-1]))
            self.sections = [{'name': self.name, 'label': section_label, 'cols': section_cols}]
        self.html, _ = FormBase.sections_content(self.sections)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value
        for subfield in self.subfields:
            subfield.enabled = value

    @property
    def value(self):
        # self._value = DotDict({subfield.name: subfield.value for subfield in self.subfields})
        self._value = {
            subfield.name: subfield.value if not isinstance(subfield.value, (datetime.datetime, datetime.date))
            else subfield.value.isoformat()
            for subfield in self.subfields
        }
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        if isinstance(value, dict):
            for subfield in self.subfields:
                subfield.value = value.get(subfield.name, None)

    def show(self):
        if not self.visible:
            anvil.js.window.document.getElementById(self.container_id).innerHTML = self.html
            for subfield in self.subfields:
                subfield.show()
            self.visible = True
            self.enabled = self._enabled

    def hide(self):
        if self.visible:
            for subfield in self.subfields:
                subfield.hide()
            anvil.js.window.document.getElementById(self.container_id).innerHTML = ''
            self.visible = False
