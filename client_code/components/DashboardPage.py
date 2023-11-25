from anvil.js.window import ej, jQuery, Event
import anvil.js
from ..tools.utils import AppEnv
from ..tools import utils
import time


class DashboardPage:
    def __init__(self, 
                 layout,
                 container_id,
                 container_style=None,
                 container_class=None,
                 title_style=None,
                 title_class=None,
                 page_title=None,
                 **properties):
        
        print('DashboardPage')
        self._element_id = utils.new_el_id()
        self.container_id = container_id or AppEnv.content_container_id
        self.container_el = jQuery(f"#{self.container_id}")[0]
        self.container_style = container_style or 'margin: 10px;'
        self.container_class = container_class or ''
        self.title_style = title_style or ''
        self.title_class = title_class or 'h4'
        self.layout = layout or {}
        self.page_title = page_title or ''
        
        self.dashboard = ej.layouts.DashboardLayout(self.layout)
        self.dashboard.change = self.dashboard_event
        self.dashboard.created = self.dashboard_event
        self.dashboard.destroyed = self.dashboard_event
        self.dashboard.drag = self.dashboard_event
        self.dashboard.dragStart = self.dashboard_event
        self.dashboard.dragStop = self.dashboard_event
        self.dashboard.resize = self.dashboard_event
        self.dashboard.resizeStart = self.dashboard_event
        self.dashboard.resizeStop = self.dashboard_event
    
    
    def form_show(self):
        # self.grid_height = self.container_el.offsetHeight - GRID_HEIGHT_OFFSET
        self.container_el.innerHTML = f'\
            <div id="da-dashboard-container" class="{self.container_class}" style="{self.container_style}">\
                <div id="{self._element_id}_header" class="{self.title_style}" style="{self.title_style}">\
                    {self.page_title}\
                </div>\
                <div id="{self._element_id}"></div>\
            </div>'

        # if self.page_title:
        #     dashboard_header = ej.navigations.AppBar({'isSticky': True, 'colorMode': 'Inherit'})
        #     dashboard_header.appendTo(f"#{self._element_id}_header")
        self.dashboard.appendTo(f"#{self._element_id}")
        self.dashboard.addEventListener('resize', self.dashboard_event)
    
    
    def destroy(self):
        self.dashboard.destroy()
        if self.container_id:
            self.container_el.innerHTML = ''


    def dashboard_event(self, args):
        print('dashboard event', args)


    def refresh(self):
        time.sleep(0.5)
        resize_event = anvil.js.new(Event, 'resize')
        anvil.js.window.dispatchEvent(resize_event)
