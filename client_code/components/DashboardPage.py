from anvil.js.window import ej, jQuery
# from ..datamodel import types as dmtypes
from ..tools.utils import AppEnv
from ..tools import utils


class DashboardPage:
    def __init__(self, 
                 container_id = None,
                 layout=None,
                 **properties):
        
        print('DashboardPage')
        self._element_id = utils.new_el_id()
        self.container_id = container_id or AppEnv.content_container_id
        self.layout = layout or {}
        
        self.dashboard = ej.layouts.DashboardLayout(self.layout)
    
    
    def form_show(self):
        # self.grid_height = self.container_el.offsetHeight - GRID_HEIGHT_OFFSET
        jQuery(f"#{self.container_id}")[0].innerHTML = f'\
            <div id="-dashboard-container" style="height:{self.grid_height}px;">\
                <div id="{self.grid_el_id}"></div>\
            </div>'

        self.dashboard.appendTo(f"#{self.container_id}")
    
    
    def destroy(self):
        # self.grid.destroy()
        if self.container_id:
            jQuery(f"#{self.container_id}")[0].innerHTML = ''
