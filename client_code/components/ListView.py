import anvil.js
from anvil.js.window import ej
from .FormInputs import BaseInput


# UI component based on SyncFusion ListView control
class ListView(BaseInput):
    def __init__(self, name=None, label=None, items=None, **kwargs):
        super().__init__(name=name, label=label, **kwargs)
        self.items = items or []
        self.items_id = f'listview-{self.name}'
        self.items_html = self.get_items_html()
        self.html = self.get_html()

    def get_items_html(self):
        html = ''
        for item in self.items:
            html += f'<div class="list-item">{item}</div>'
        return html

    def get_html(self):
        return f'<div id="{self.items_id}">{self.items_html}</div>'

    def form_show(self):
        anvil.js.window.document.getElementById(self.container_id).innerHTML = self.html
        ej.lists.ListView({
            'dataSource': self.items,
            'headerTitle': self.label,
            'showHeader': True,
            'showHeaderBackButton': True,
            'headerBackButtonText': 'Back',
            'showHeaderTitle': True,
            'headerTitleText': self.label,
            'enableHeaderTitle': True,
            'enableHeaderBackButton': True,
        }).appendTo(f'#{self.items_id}')