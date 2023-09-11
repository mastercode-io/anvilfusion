from anvil.js.window import ej, jQuery
# from ..datamodel import types as dmtypes
from ..tools.utils import AppEnv
from ..tools import utils


class DashboardPage:
    def __init__(self, 
                 layout,
                 container_id,
                 container_style=None,
                 container_class=None,
                 page_title=None,
                 **properties):
        
        print('DashboardPage')
        self._element_id = utils.new_el_id()
        self.container_id = container_id or AppEnv.content_container_id
        self.container_el = jQuery(f"#{self.container_id}")[0]
        self.container_style = container_style or 'margin: 10px;'
        self.container_class = container_class or ''
        self.layout = layout or {}
        self.page_title = page_title or ''
        
        self.dashboard = ej.layouts.DashboardLayout(self.layout)
    
    
    def form_show(self):
        # self.grid_height = self.container_el.offsetHeight - GRID_HEIGHT_OFFSET
        self.container_el.innerHTML = f'\
            <div id="da-dashboard-container" class="{self.container_class}" style="{self.container_style}">\
                <header id="{self._element_id}_header">{self.page_title}</header>\
                <div id="{self._element_id}"></div>\
            </div>'

        if self.page_title:
            dashboard_header = ej.navigations.AppBar({'isSticky': True, 'colorMode': 'Inherit'})
            dashboard_header.appendTo(f"#{self._element_id}_header")
        self.dashboard.appendTo(f"#{self._element_id}")
    
    
    def destroy(self):
        # self.grid.destroy()
        if self.container_id:
            self.container_el.innerHTML = ''
