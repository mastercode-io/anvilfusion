from ..components.PageBase import PageBase
from ..components.FormInputs import *


class MigratePage(PageBase):
    def __init__(self, **kwargs):
        print('MigratePage')
        self.content = """
                <div class="container">
                    <div class="row">
                        <div class="col-12">
                            <h4>Migration</h4>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-12">
                            <p>
                                This page is used to migrate data from the legacy system to the new system.
                            </p>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-12">
                            <div id="migrate-form"></div>
                        </div>
                    </div>
                </div>
            """
        super().__init__(content=self.content, **kwargs)
