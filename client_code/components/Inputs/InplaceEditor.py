from ..FormInputs import BaseInput
import anvil.js
from anvil.js.window import ej


class InplaceEditor(BaseInput):
    def __init__(self,
                 input_type=None,
                 edit_mode='Inline',
                 **kwargs):
        super().__init__(**kwargs)

        self.input_type = input_type
        self.edit_mode = edit_mode
        self.html = f'<div id="{self.el_id}"></div>'

    def create_control(self):
        self.control = ej.inplaceeditor.InPlaceEditor({
            # 'enableEditMode': True,
            'mode': self.edit_mode,
            'value': self._value,
            'type': self.input_type,
            'save': self.submit,
        })

    def submit(self, **event_args):
        # self._value = self.control.model.value
        print('InplaceEditor submit', event_args, self.value)
