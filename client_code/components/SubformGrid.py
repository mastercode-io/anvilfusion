import anvil.js
from .FormInputs import BaseInput
from .GridView import GridView


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
                 data=None,
                 **kwargs):
        
        BaseInput.__init__(
            self, name=name, 
            label=label, 
            container_id=container_id, 
            **kwargs)
        GridView.__init__(
            self, model=model, title=label, 
            container_id=self.el_id, 
            form_container_id=form_container_id,
            save=False, 
            **kwargs)
        self.html = f'<div id="{self.el_id}"></div>'
        self.form_data = form_data
        self.is_subfrom = True
        print('subform grid', self.container_id)

        
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
        print('show subformgrid')
        if not self.visible:
            self.visible = True
            if 'element' in self.grid.keys():
                self.grid.element.style.display = 'block'
            else:
                print('show subform grid', self.container_id, self.el_id, self.html, self.grid)
                GridView.form_show(self)
            
            
    def hide(self):
        print('hide subformgrid')
        if self.visible:
            self.visible = False
            if 'element' in self.grid.keys():
                self.grid.element.style.display = 'none'
                
                
    def add_edit_row(self, args):
        return GridView.add_edit_row(self, args=args, form_data=self.form_data)
