from ...components.PageBase import PageBase
from ...components.FormInputs import *
from anvil.js.window import ej
import uuid


class MigratePage(PageBase):
    def __init__(self, **kwargs):
        print('MigratePage')
        title = 'Migrate DB Schema'
        self.migrate_button = ej.buttons.Button({'content': 'Migrate DB', 'isPrimary': True, 'size': 'large'})
        self.migrate_button_id = f'migrate-button-{uuid.uuid4()}'
        self.execution_log = InlineMessage(name='execution_log')
        self.content = f'<br><div id="{self.migrate_button_id}"></div><br><br>'
        self.content += f'<div id="{self.execution_log.container_id}"></div>'

        super().__init__(page_title=title, content=self.content, **kwargs)


    def form_show(self, **args):
        print('MigratePage.form_show')
        super().form_show(**args)
        self.migrate_button.appendTo(f'#{self.migrate_button_id}')
        self.execution_log.show()
        self.execution_log.message = 'This is a test message.'
        # self.migrate_button.on_click = self.migrate_button_click
