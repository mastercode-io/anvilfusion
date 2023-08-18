import anvil.js
from .FormInputs import BaseInput
from .GridView import GridView


class SubformGrid(BaseInput, GridView):
    def __init__(self, 
                 name=None,
                 label=None,
                 container_id=None, 
                 model=None, 
                 link_model=None, 
                 link_field=None, 
                 data=None,
                 **kwargs):
        
        BaseInput.__init__(self, name=name, label=label, container_id=container_id, **kwargs)
        GridView.__init__(self, model=model, container_id=self.el_id, **kwargs)
        self.html = f'<div id="{self.el_id}"></div>'

        
    @property
    def control(self):
        return self._control

    @control.setter
    def control(self, value):
        self._control = value


    @property
    def enabled(self):
        pass

    @enabled.setter
    def enabled(self, value):
        pass


    @property
    def value(self):
        pass

    @value.setter
    def value(self, value):
        pass


    def show(self):
        if not self.visible:
            anvil.js.window.document.getElementById(self.container_id).innerHTML = self.html + self.shadow_label
            if self.grid:
                self.grid.appendTo(f"#{self.el_id}")
            self.visible = True


