import anvil.js
import uuid
from ..tools.utils import AppEnv


class PageBase:

    def __init__(
            self,
            container_id,
            page_el_style=None,
            page_el_class=None,
            page_title_style=None,
            page_title_class=None,
            page_title=None,
            content=None,
            overflow=None,
            **kwargs
    ):
        print('PageBase')
        self.container_id = container_id or AppEnv.content_container_id
        self.container_el = None
        self.page_el = None
        self.page_el_id = f'{self.__class__.__name__}-{uuid.uuid4()}'
        self.page_el_style = page_el_style or 'margin: 10px;'
        self.page_el_class = page_el_class or ''
        self.page_title_style = page_title_style or ''
        self.page_title_class = page_title_class or 'h4'
        self.page_title = page_title or ''
        self._page_content = content or ''
        self.overflow = overflow or 'auto'
        self.visible = False


    def form_show(self, **args):
        print('PageBase.form_show')
        self.container_el = anvil.js.window.document.getElementById(self.container_id)
        self.container_el.innerHTML = f'\
            <div id="{self.page_el_id}" class="{self.page_el_class}" style="{self.page_el_style}">\
                <div id="{self.page_el_id}-title" class="{self.page_title_class}" style="{self.page_title_style}">\
                    {self.page_title}\
                </div>\
                <div id="{self.page_el_id}-content">{self._page_content}</div>\
            </div>'
        self.page_el = anvil.js.window.document.getElementById(f'{self.page_el_id}')
        self.show()


    @property
    def page_content(self):
        return self._page_content


    @page_content.setter
    def page_content(self, value):
        self._page_content = value
        if self.page_el:
            content_el = anvil.js.window.document.getElementById(f'{self.page_el_id}-content')
            content_el.innerHTML = value


    def show(self):
        print('PageBase.show')
        if not self.visible:
            self.visible = True
        if self.page_el:
            self.page_el.style.display = 'block'


    def hide(self):
        print('PageBase.hide')
        if self.visible:
            self.visible = False
        if self.page_el:
            self.page_el.style.display = 'none'


    def destroy(self):
        print('PageBase.destroy')
        self.hide()
        self.container_el.innerHTML = ''
        self._page_content = None
