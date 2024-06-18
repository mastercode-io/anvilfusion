import anvil.js
from anvil.js.window import ej
from .FormInputs import BaseInput


# UI component based on SyncFusion ListBox control
class ListView(BaseInput):
    def __init__(self,
                 text_field='name',
                 value_field='uid',
                 header=None,
                 data=None,
                 options=None,
                 select='single',
                 select_all=False,
                 **kwargs):
        super().__init__(**kwargs)

        self.select = 'Multiple' if select == 'multi' else 'Single'
        self.select_all = select_all
        self.header = header
        self.float_label = False
        self.html = f'<div class="{self.container_class}">'
        if self.label:
            self.html += f'<label id="label_{self.el_id}" class="da-form-input-label">{self.label or ""}</label>'
        self.html += f'<div class="form-control da-form-group" id="{self.el_id}" name="{self.el_id}"></div></div>'

        self.value_field = value_field
        self.text_field = text_field
        if isinstance(options, list) and options != [] and isinstance(options[0], str):
            self.value_field = 'value'
            self.text_field = 'text'
            self.fields = {'text': 'text', 'value': 'value'}
            self._options = [{'text': option, 'value': option} for option in options]
        else:
            self.fields = {'text': text_field, 'value': value_field}
            self._options = options

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

    def create_control(self, **kwargs):
        listview_config = {
            'dataSource': self.options,
            'fields': self.fields,
        }
        if self.header:
            listview_config['headerTitle'] = self.header
            listview_config['showHeader'] = True
        selection_settings = {'mode': self.select}
        if self.select_all:
            selection_settings['showSelectAll'] = True
            selection_settings['showCheckbox'] = True
        listview_config['selectionSettings'] = selection_settings

        self.control = ej.lists.ListView(listview_config)
