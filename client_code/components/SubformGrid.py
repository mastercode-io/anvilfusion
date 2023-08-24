import anvil.js
from .FormInputs import BaseInput
from .GridView import GridView
from ..tools.utils import AppEnv


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
            persist=False, 
            **kwargs)
        self.link_model = link_model
        self.link_field = link_field
        self.data = data
        self.html = f'<div id="{self.el_id}"></div>'
        self.form_data = form_data
        self.is_dependent = True if link_model and link_field else False
        self.to_save = []
        self.to_delete = []
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
        GridView.add_edit_row(self, args=args, form_data=self.form_data)
    
    
    def delete_selected(self, args):
        self.to_delete.extend([x.uid for x in self.grid.getSelectedRecords() or [] if x.uid])
        GridView.delete_selected(self, args, persist=False)


    def update_grid(self, data_row, add_new):
        self.to_save.append(data_row)
        GridView.update_grid(self, data_row, add_new, get_relationships=True)
    
    
    def save(self, link_row=None):
        print('save subformgrid', self.to_save, self.to_delete)
        if self.link_field and self.link_model and link_row:
            for data_row in self.to_save:
                data_row[self.link_field] = link_row
                data_row.save()
            for uid in self.to_delete:
                self.grid_class.get(uid).delete()
