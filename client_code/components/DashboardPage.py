from anvil.js.window import ej, jQuery
# from ..datamodel import types as dmtypes
from ..tools.utils import AppEnv
from ..tools import utils


class DashboardPage:
    def __init__(self, 
                 container_id,
                 layout,
                 **properties):
        
        print('DashboardPage')
        self._element_id = utils.new_el_id()
        self.container_id = container_id or AppEnv.content_container_id
        self.container_el = jQuery(f"#{self.container_id}")[0]
        self.layout = layout or {}
        
        self.dashboard = ej.layouts.DashboardLayout(self.layout)
    
    
    def form_show(self):
        # self.grid_height = self.container_el.offsetHeight - GRID_HEIGHT_OFFSET
        self.container_el.innerHTML = f'\
            <div id="da-dashboard-container" style="height:100%;width:100%;">\
                <div id="{self._element_id}"></div>\
            </div>'

        self.dashboard.appendTo(f"#{self._element_id}")
    
    
    def destroy(self):
        # self.grid.destroy()
        if self.container_id:
            self.container_el.innerHTML = ''
