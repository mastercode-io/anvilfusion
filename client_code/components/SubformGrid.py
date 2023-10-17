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
                 is_dependent=False,
                 schema=None,
                 data=None,
                 view_config=None,
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
            view_config=view_config,
            persist=False, 
            **kwargs)
        self.link_model = link_model
        self.link_field = link_field
        self.data = data
        self.html = f'<div id="{self.el_id}"></div>'
        self.form_data = form_data
        self.is_dependent = True if link_model and link_field else is_dependent
        self.to_save = []
        self.to_delete = []
        # print('subform grid', self.container_id)

        
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
        return self._value

    @value.setter
    def value(self, value):
        print('set subformgrid value', value)
        if value and value.uid:
            self._value = value
            if self.model and self.is_dependent:
                if not self.filters:
                    self.filters = {}
                if self.link_field:
                    self.filters[self.link_field] = value
                self.grid_data = self.grid_class.get_grid_view(self.view_config,
                                                               search_queries=self.search_queries,
                                                               filters=self.filters,
                                                               include_rows=False)
                self.grid.dataSource = self.grid_data
            else:
                pass
        else:
            self._value = None
            self.grid_data = []
            self.grid.dataSource = self.grid_data
        if 'element' in self.grid.keys():
            self.grid.refresh()
        print('subformgrid data', self.filters, self.grid_data)


    def show(self):
        print('show subformgrid')
        if not self.visible:
            self.visible = True
            if 'element' in self.grid.keys():
                self.grid.element.style.display = 'block'
            else:
                GridView.form_show(self, get_data=False)
            
            
    def hide(self):
        print('hide subformgrid')
        if self.visible:
            self.visible = False
            if 'element' in self.grid.keys():
                self.grid.element.style.display = 'none'
                
                
    def add_edit_row(self, args=None, form_data=None):
        GridView.add_edit_row(self, args=args, form_data=self.form_data)
    
    
    def delete_selected(self, args, persist=False):
        self.to_delete.extend([x.uid for x in self.grid.getSelectedRecords() or [] if x.uid])
        GridView.delete_selected(self, args, persist=False)


    def update_grid(self, data_row, add_new, get_relationships=True):
        self.to_save.append(data_row)
        GridView.update_grid(self, data_row, add_new, get_relationships=True)
    
    
    def save_dependent(self, link_row=None):
        # print('save subformgrid', self.to_save, self.to_delete)
        if self.link_field and self.link_model and link_row:
            for data_row in self.to_save:
                if data_row.uid and 'grid' in data_row.uid:
                    data_row.uid = None
                data_row[self.link_field] = link_row
                data_row.save()
            for uid in self.to_delete:
                self.grid_class.get(uid).delete()
