import anvil.js
from anvil import BlobMedia
from anvil.js.window import jQuery, ej
# from ..tools.utils import AppEnv, DotDict, new_el_id, label_to_id
import uuid


class Tabs:
    def __init__(self,
                 container_id=None,
                 tabs_config=None,
                 selected_item=0,
                 **kwargs):

        self.container_id = container_id or f'tabs-container-{uuid.uuid4()}'
        self.tabs_id = f'tabs-control-{uuid.uuid4()}'
        self.tabs_config = tabs_config or []
        self.selected_item = selected_item
        self.tabs = None

        self.items = {}
        for tab in self.tabs_config:
            item = {
                'id': tab.get('id') or f"tab-{tab['name']}-{uuid.uuid4()}",
                'label': tab.get('label') or tab['name'],
                'content_id': tab.get('content_id', None) or f"tab-{tab['name']}-content-{uuid.uuid4()}",
                'content': tab.get('content') or '',
                'enabled': tab.get('enabled') or True
            }
            self.items[tab['name']] = item

        self.html = self.get_tabs_content()


    def get_tabs_content(self):
        html = f'<div id="{self.tabs_id}"></div>'
        for item in self.items.values():
            html += f'<div id="{item["content_id"]}">{item["content"]}</div>'
        return html


    def form_show(self):
        anvil.js.window.document.getElementById(self.container_id).innerHTML = self.html
        tabs_config = [
            {
                'id': item['id'],
                'header': {'text': item['label']},
                # 'content': f'<div id="{item["content_id"]}">{item["content"]}</div>',
                'content': f'#{item["content_id"]}',
                'cssClass': 'da-tabs-item',
                'disabled': not item['enabled'],
            }
            for item in self.items.values()
        ]
        self.tabs = ej.navigations.Tab({
            'items': tabs_config,
            'animation': {'previous': {'effect': 'None'}, 'next': {'effect': 'None'}},
            'selectedItem': self.selected_item,
        })
        self.tabs.appendTo(jQuery(f'#{self.tabs_id}')[0])
        for i in range(len(self.items.keys()) - 1, -1, -1):
            self.tabs.select(i)


    def set_tab_content(self, tab_name=None, content=''):
        tab_id = self.items[tab_name]['id']
        print('set_tab_content', tab_name, tab_id)
        for item in self.tabs.items:
            if item.id == tab_id:
                item.content = content
                break
