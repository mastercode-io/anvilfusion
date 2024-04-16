from ...components.PageBase import PageBase
from ...components.FormInputs import *
from ...datamodel.migrate import migrate_db_schema
from anvil.js.window import ej
import uuid


class MigratePage(PageBase):
    def __init__(self, **kwargs):
        print('MigratePage')
        title = 'Migrate DB Schema'
        self.migrate_button = ej.buttons.Button({
            'content': 'Migrate DB',
            'isPrimary': True,
            'size': 'large',
        })
        self.migrate_button_id = f'migrate-button-{uuid.uuid4()}'
        self.execution_log = InlineMessage(name='execution_log')
        self.content = f'<br><div id="{self.migrate_button_id}"></div><br><br>'
        self.content += f'<div id="{self.execution_log.container_id}" style="overflow-y: scroll; height: 100%;"></div>'

        super().__init__(page_title=title, content=self.content, overflow='auto', **kwargs)


    def form_show(self, **args):
        print('MigratePage.form_show')
        super().form_show(**args)
        # anvil.js.window.document.getElementById(self.container_id).style.overflow = 'hidden'
        self.migrate_button.appendTo(f'#{self.migrate_button_id}')
        self.migrate_button.addEventListener('onclick', self.migrate_button_action)
        self.migrate_button.element.onclick = self.migrate_button_action
        self.execution_log.show()
        self.execution_log.content = 'Click <b>Migrate DB</b> to start migration'


    def migrate_button_action(self, args):
        print('MigratePage.migrate_button_action')
        self.execution_log.message = 'Starting migration...<br><br>'
        migrate_db_schema(logger=self.log_message)
        self.execution_log.content = '<br>Migration complete.'


    def log_message(self, message):
        self.execution_log.content += str(message) + '<br>'
