from anvil.js.window import ej, jQuery
from ..datamodel import types as dmtypes
from . import FormBase as fbase
from ..tools.utils import AppEnv
from ..tools import utils
import string
import uuid
import json


class DashboardPage:
    def __init__(self, 
                 container_id = None,
                 layout=None,
                 **properties):
        
        print('DashboardPage')
        self.container_id = container_id or AppEnv.content_container_id
        self.layout = layout or {}
        
        self.dashboard = ej.layouts.DashboardLayout(self.layout)
    
    
    def form_show(self):
        self.dashboard.appendTo(f"#{self.container_id}")
    
    
    def destroy(self):
        # self.grid.destroy()
        if self.container_id:
            jQuery(f"#{self.container_id}")[0].innerHTML = ''
