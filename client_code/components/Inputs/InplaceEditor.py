from ..FormInputs import BaseInput
import anvil.js
from anvil.js.window import ej


class InplaceEditor(BaseInput):
    def __init__(self,
                 input_type='Text',
                 input_control_id=None,
                 edit_mode='Inline',
                 **kwargs):
        super().__init__(**kwargs)

        self.input_type = input_type
        self.input_control_id = input_control_id
        self.edit_mode = edit_mode
        self.html = f'<div id="{self.el_id}"></div>'

    def create_control(self):
        control_config = {
            'mode': self.edit_mode,
            'value': self.value,
        }
        if self.input_control_id is not None:
            control_config['template'] = f'#{self.input_control_id}'
        else:
            control_config['type'] = self.input_type
        print('InplaceEditor config', control_config)
        self.control = ej.inplaceeditor.InPlaceEditor(control_config)

    def submit(self, **event_args):
        # self._value = self.control.model.value
        print('InplaceEditor submit', event_args, self.value)
