# Application navigation
from anvil.js.window import jQuery, ej
import time
from AnvilFusion.tools.utils import AppEnv
from AnvilFusion.components.GridView import GridView
from AnvilFusion.components.FormBase import FormBase


# Sidebar control CSS
PMAPP_SIDEBAR_CSS = 'e-inherit e-caret-hide pm-sidebar-menu'
PMAPP_SIDEBAR_WIDTH = 200
PMAPP_SIDEBAR_POPUP_OFFSET = 1


# Appbar menu item list
PMAPP_APPBAR_MENU = [
    {'id': 'case_menu', 'text': 'Case Management', 'items': []},
    {'id': 'intake_menu', 'text': 'Intake', 'items': []},
    {'id': 'tools_menu', 'text': 'Tools', 'items': []},
    {'id': 'staff_menu', 'text': 'Staff', 'items': []},
    {'id': 'finance_menu', 'text': 'Finance', 'items': []},
]


# Sidebar menu item list
PMAPP_SIDEBAR_MENUS = {
    'case_menu': [
        {'nodeId': 'case_agenda', 'nodeText': 'Agenda', 'nodeChild': []},
        {'nodeId': 'case_tasks', 'nodeText': 'Tasks', 'nodeChild': []},
        {'nodeId': 'case_dashboard', 'nodeText': 'Case Dashboard', 'nodeChild': [
            {'nodeId': 'case_dashboard_events', 'nodeText': 'Events', 'nodeChild': []},
            {'nodeId': 'case_dashboard_tasks', 'nodeText': 'Tasks', 'nodeChild': []},
            {'nodeId': 'case_dashboard_documents', 'nodeText': 'Documents', 'nodeChild': []},
            {'nodeId': 'case_dashboard_time_entries', 'nodeText': 'Time Entries', 'nodeChild': []},
            {'nodeId': 'case_dashboard_expenses', 'nodeText': 'Expenses', 'nodeChild': []},
            {'nodeId': 'case_dashboard_invoices', 'nodeText': 'Invoices', 'nodeChild': []},
            {'nodeId': 'case_dashboard_payments', 'nodeText': 'Payments', 'nodeChild': []},
            {'nodeId': 'case_dashboard_contacts', 'nodeText': 'Contacts', 'nodeChild': []},
            {'nodeId': 'case_dashboard_updates', 'nodeText': 'Updates', 'nodeChild': []},
            {'nodeId': 'case_dashboard_requirements', 'nodeText': 'Requirements', 'nodeChild': []},
        ]},
        {'nodeId': 'case_reports', 'nodeText': 'Reports', 'nodeChild': [
            {'nodeId': 'case_reports_cases', 'nodeText': 'Cases', 'nodeChild': []},
            {'nodeId': 'case_reports_documents', 'nodeText': 'Documents', 'nodeChild': []},
            {'nodeId': 'case_reports_time_entries', 'nodeText': 'Time Entries', 'nodeChild': []},
            {'nodeId': 'case_reports_expenses', 'nodeText': 'Expenses', 'nodeChild': []},
            {'nodeId': 'case_reports_invoices', 'nodeText': 'Invoices', 'nodeChild': []},
            {'nodeId': 'case_reports_payments', 'nodeText': 'Payments', 'nodeChild': []},
            {'nodeId': 'case_reports_clients', 'nodeText': 'Clients', 'nodeChild': []},
            {'nodeId': 'case_reports_contacts', 'nodeText': 'Contacs', 'nodeChild': []},
            {'nodeId': 'case_reports_entities', 'nodeText': 'Entities', 'nodeChild': []},
            {'nodeId': 'case_reports_updates', 'nodeText': 'Updates', 'nodeChild': []},
            {'nodeId': 'case_reports_requirements', 'nodeText': 'Requirements', 'nodeChild': []},
        ]},
    ],
    'intake_menu': [
        {'nodeId': 'intake_leads', 'nodeText': 'Leads', 'nodeChild': []},
        {'nodeId': 'intake_lead_analytics', 'nodeText': 'Lead Analytics', 'nodeChild': []},
    ],
    'tools_menu': [
        {'nodeId': 'tools_date_calculator', 'nodeText': 'Date Calculator', 'nodeChild': []},
        {'nodeId': 'tools_probation_calculator', 'nodeText': 'Probation Calculator', 'nodeChild': []},
        {'nodeId': 'tools_settlement_calculator', 'nodeText': 'Settlement Calculator', 'nodeChild': []},
        {'nodeId': 'tools_statute_search', 'nodeText': 'Statute Search', 'nodeChild': []},
        {'nodeId': 'tools_warrant_search', 'nodeText': 'Warrant Search', 'nodeChild': []},
        {'nodeId': 'tools_analytics', 'nodeText': 'Analytics', 'nodeChild': []},
        {'nodeId': 'tools_admin', 'nodeText': 'System Admin', 'nodeChild': [
            {'nodeId': 'tools_admin_activity', 'nodeText': 'Activity', 'nodeChild': []},
            {'nodeId': 'tools_admin_bank_account_type', 'nodeText': 'Bank Account Type', 'nodeChild': []},
            {'nodeId': 'tools_admin_branch', 'nodeText': 'Branch', 'nodeChild': []},
            {'nodeId': 'tools_admin_case_stage', 'nodeText': 'Case Stage', 'nodeChild': []},
            {'nodeId': 'tools_admin_case_status', 'nodeText': 'Case Status', 'nodeChild': []},
            {'nodeId': 'tools_admin_case_workflow', 'nodeText': 'Case Worflow', 'nodeChild': []},
            {'nodeId': 'tools_admin_case_workflow_item', 'nodeText': 'Case Worflow Items', 'nodeChild': []},
            {'nodeId': 'tools_admin_cause_of_action', 'nodeText': 'Cause of Action', 'nodeChild': []},
            {'nodeId': 'tools_admin_contact_group', 'nodeText': 'Contact Group', 'nodeChild': []},
            {'nodeId': 'tools_admin_contact_role', 'nodeText': 'Contact Role', 'nodeChild': []},
            {'nodeId': 'tools_admin_entity_type', 'nodeText': 'Entity Type', 'nodeChild': []},
            {'nodeId': 'tools_admin_fee_type', 'nodeText': 'Fee Type', 'nodeChild': []},
            {'nodeId': 'tools_admin_lead_source', 'nodeText': 'Lead Source', 'nodeChild': []},
            {'nodeId': 'tools_admin_practice_area', 'nodeText': 'Practice Area', 'nodeChild': []},
            {'nodeId': 'tools_admin_type_of_action', 'nodeText': 'Type of Action', 'nodeChild': []},
            {'nodeId': 'tools_admin_staff_group', 'nodeText': 'Staff Group', 'nodeChild': []},
            {'nodeId': 'tools_admin_staff_pay_type', 'nodeText': 'Staff Pay Type', 'nodeChild': []},
            # {'nodeId': 'tools_admin_', 'nodeText': '', 'nodeChild': []},
        ]},
    ],
    'staff_menu': [
        {'nodeId': 'staff_my_timesheets', 'nodeText': 'My Timesheets', 'nodeChild': []},
        {'nodeId': 'staff_my_reimbursement', 'nodeText': 'My Reimbursement Requests', 'nodeChild': []},
        {'nodeId': 'staff_my_timeoff', 'nodeText': 'My Time-Off Requests', 'nodeChild': []},
        {'nodeId': 'staff_my_incentives', 'nodeText': 'My Performance Incentives', 'nodeChild': []},
        {'nodeId': 'staff_directory', 'nodeText': 'Staff Directory', 'nodeChild': []},
    ],
    'finance_menu': [
        {'nodeId': 'finance_checks', 'nodeText': 'Checks', 'nodeChild': []},
        {'nodeId': 'finance_payments', 'nodeText': 'Payments', 'nodeChild': []},
        {'nodeId': 'finance_ledger', 'nodeText': 'Master Ledger', 'nodeChild': []},
        {'nodeId': 'finance_bank_accounts', 'nodeText': 'Bank Accounts', 'nodeChild': []},
        {'nodeId': 'finance_incentives', 'nodeText': 'Performance Incentives', 'nodeChild': []},
        {'nodeId': 'finance_timeoff', 'nodeText': 'Time-Off Requests', 'nodeChild': []},
        {'nodeId': 'finance_reimbursement', 'nodeText': 'Reimbursement Requests', 'nodeChild': []},
        {'nodeId': 'finance_timesheets', 'nodeText': 'Timesheets', 'nodeChild': []},
        {'nodeId': 'finance_payrolls', 'nodeText': 'Payrolls', 'nodeChild': []},
    ],
}


# Navigation items/actions
PMAPP_NAV_ITEMS = {
    # 'case_agenda': {'model': '', 'type': 'page|view|form', 'action': 'open|popup', 'props': {}},
    'case_tasks': {'model': 'Task', 'type': 'view', 'action': 'open', 'config': 'TaskView', 'props': {}},
    'case_dashboard': {'model': 'CaseDashboard', 'type': 'page', 'action': 'open',
                       'subcomponent': 'case_dashboard_events', 'props': {}},
    'case_dashboard_events': {'class': 'EventScheduleView', 'type': 'custom', 'action': 'open', 'props': {}},
    'case_dashboard_tasks': {'model': 'Task', 'type': 'view', 'action': 'open', 'config': 'TaskView', 'props': {}},
    # 'case_dashboard_documents': {'model': '', 'type': 'page|view|form', 'action': 'open|popup', 'props': {}},
    'case_dashboard_time_entries': {'model': 'TimeEntry', 'type': 'view', 'action': 'open', 'config': 'TimeEntryView',
                                    'props': {}},
    'case_dashboard_expenses': {'model': 'Expense', 'type': 'view', 'action': 'open', 'config': 'ExpenseView',
                                'props': {}},
    'case_dashboard_invoices': {'model': 'Invoice', 'type': 'view', 'action': 'open', 'config': 'InvoiceView',
                                'props': {}},
    'case_dashboard_payments': {'model': 'Payment', 'type': 'view', 'action': 'open', 'config': 'PaymentView',
                                'props': {}},
    'case_dashboard_contacts': {'model': 'CaseContact', 'type': 'view', 'action': 'open', 'props': {}},
    # 'case_dashboard_updates': {'model': '', 'type': 'page|view|form', 'action': 'open|popup', 'props': {}},
    # 'case_dashboard_requirements': {'model': '', 'type': 'page|view|form', 'action': 'open|popup', 'props': {}},
    'case_reports_cases': {'model': 'Case', 'type': 'view', 'action': 'open', 'config': 'CaseView', 'props': {}},
    # 'case_reports_documents': {'model': '', 'type': 'view', 'action': 'open', 'props': {}},
    'case_reports_time_entries': {'model': 'TimeEntry', 'type': 'view', 'action': 'open', 'config': 'TimeEntryView',
                                  'props': {}},
    'case_reports_expenses': {'model': 'Expense', 'type': 'view', 'action': 'open', 'config': 'ExpenseView',
                              'props': {}},
    'case_reports_invoices': {'model': 'Invoice', 'type': 'view', 'action': 'open', 'config': 'InvoiceView',
                              'props': {}},
    'case_reports_payments': {'model': 'Payment', 'type': 'view', 'action': 'open', 'config': 'PaymentView',
                              'props': {}},
    'case_reports_clients': {'model': 'Client', 'type': 'view', 'action': 'open', 'config': 'ClientView', 'props': {}},
    'case_reports_contacts': {'model': 'Contact', 'type': 'view', 'action': 'open', 'config': 'ContactView',
                              'props': {}},
    'case_reports_entities': {'model': 'Entity', 'type': 'view', 'action': 'open', 'config': 'EntityView', 'props': {}},
    # 'case_reports_updates': {'model': '', 'type': 'page', 'action': 'open', 'props': {}},
    # 'case_reports_requirements': {'model': '', 'type': 'page', 'action': 'open', 'props': {}},

    'intake_leads': {'model': 'Lead', 'type': 'view', 'action': 'open', 'props': {}},
    # 'intake_lead_analytics': {'model': '', 'type': 'page|view|form', 'action': 'open|popup', 'props': {}},

    # 'tools_date_calculator': {'model': '', 'type': 'view', 'action': 'open', 'props': {}},
    # 'tools_probation_calculator': {'model': '', 'type': 'view', 'action': 'open', 'props': {}},
    # 'tools_settlement_calculator': {'model': '', 'type': 'view', 'action': 'open', 'props': {}},
    # 'tools_statute_search': {'model': '', 'type': 'view', 'action': 'open', 'props': {}},
    # 'tools_warrant_search': {'model': '', 'type': 'view', 'action': 'open', 'props': {}},
    # 'tools_analytics': {'model': '', 'type': 'view', 'action': 'open', 'props': {}},
    'tools_admin_activity': {'model': 'Activity', 'type': 'view', 'action': 'open', 'props': {}},
    'tools_admin_bank_account_type': {'model': 'BankAccountType', 'type': 'view', 'action': 'open', 'props': {}},
    'tools_admin_branch': {'model': 'Branch', 'type': 'view', 'action': 'open', 'props': {}},
    'tools_admin_case_stage': {'model': 'CaseStage', 'type': 'view', 'action': 'open', 'props': {}},
    'tools_admin_case_status': {'model': 'CaseStatus', 'type': 'view', 'action': 'open', 'props': {}},
    'tools_admin_case_workflow': {'model': 'CaseWorkflow', 'type': 'view', 'action': 'open', 'props': {}},
    'tools_admin_case_workflow_item': {'model': 'CaseWorkflowItem', 'type': 'view', 'action': 'open', 
                                  'config': 'CaseWorkflowItemView', 'props': {}},
    'tools_admin_cause_of_action': {'model': 'CauseOfAction', 'type': 'view', 'action': 'open',
                                    'config': 'CauseOfActionView', 'props': {}},
    'tools_admin_contact_group': {'model': 'ContactGroup', 'type': 'view', 'action': 'open', 'props': {}},
    'tools_admin_contact_role': {'model': 'ContactRole', 'type': 'view', 'action': 'open', 'props': {}},
    'tools_admin_entity_type': {'model': 'EntityType', 'type': 'view', 'action': 'open', 'props': {}},
    'tools_admin_fee_type': {'model': 'FeeType', 'type': 'view', 'action': 'open', 'props': {}},
    'tools_admin_lead_source': {'model': 'LeadSource', 'type': 'view', 'action': 'open', 'props': {}},
    'tools_admin_practice_area': {'model': 'PracticeArea', 'type': 'view', 'action': 'open', 'props': {}},
    'tools_admin_type_of_action': {'model': 'TypeOfAction', 'type': 'view', 'action': 'open', 'props': {}},
    'tools_admin_staff_group': {'model': 'StaffGroup', 'type': 'view', 'action': 'open', 'props': {}},
    'tools_admin_staff_pay_type': {'model': 'StaffPayType', 'type': 'view', 'action': 'open', 'props': {}},

    'staff_my_timesheets': {'model': 'Timesheet', 'type': 'view', 'action': 'open', 'config': 'TimesheetView',
                            'props': {}},
    # 'staff_my_reimbursement': {'model': '', 'type': 'view', 'action': 'open', 'props': {}},
    # 'staff_my_timeoff': {'model': '', 'type': 'view', 'action': 'open', 'props': {}},
    # 'staff_my_incentives': {'model': '', 'type': 'view', 'action': 'open', 'props': {}},
    'staff_directory': {'model': 'Staff', 'type': 'view', 'action': 'open', 'config': 'StaffView', 'props': {}},

    'finance_checks': {'model': 'Check', 'type': 'view', 'action': 'open', 'config': 'CheckView', 'props': {}},
    'finance_payments': {'model': 'Payment', 'type': 'view', 'action': 'open', 'config': 'PaymentView', 'props': {}},
    'finance_ledger': {'model': 'Ledger', 'type': 'view', 'action': 'open', 'props': {}},
    'finance_bank_accounts': {'model': 'BankAccount', 'type': 'view', 'action': 'open', 'config': 'BankAccountView',
                              'props': {}},
    # 'finance_incentives': {'model': '', 'type': 'view', 'action': 'open', 'props': {}},
    # 'finance_timeoff': {'model': '', 'type': 'view', 'action': 'open', 'props': {}},
    # 'finance_reimbursement': {'model': '', 'type': 'view', 'action': 'open', 'props': {}},
    'finance_timesheets': {'model': 'Timesheet', 'type': 'view', 'action': 'open', 'config': 'TimesheetView',
                           'props': {}},
    # 'finance_payrolls': {'model': '', 'type': 'view', 'action': 'open', 'props': {}},
}


# Appbar navigation class
class AppbarMenu:
    def __init__(self, container_el, sidebar, menu_items):
        self.container_el = container_el
        self.sidebar = sidebar
        self.menu_items = menu_items
        self.selected_el = None

        self.menu = ej.navigations.Menu({
            'cssClass': 'e-inherit',
            'items': self.menu_items,
            'select': self.menu_select
        })

    def show(self):
        self.menu.appendTo(jQuery(f"#{self.container_el}")[0])

    def menu_select(self, args):
        if self.selected_el is not None:
            self.selected_el.classList.remove('pm-appbar-menu-selected')
        self.selected_el = args.element
        self.selected_el.classList.add('pm-appbar-menu-selected')
        menu_id = args.item.properties.id
        print(menu_id)
        self.sidebar.show_menu(menu_id)


# Sidebar navigation class
class Sidebar:
    def __init__(self,
                 target_el,
                 container_el,
                 content_id,
                 sidebar_width=PMAPP_SIDEBAR_WIDTH,
                 sections=PMAPP_SIDEBAR_MENUS,
                 nav_items=PMAPP_NAV_ITEMS,
                 **properties):

        self.target_el = target_el
        self.container_el = container_el
        self.content_id = content_id
        self.nav_target_id = None
        self.content_control = None
        self.nav_items = nav_items

        # Init sidebar menu controls
        self.control = self.sidebar = ej.navigations.Sidebar({
            'width': sidebar_width,
            'target': self.target_el,
            'mediaQuery': '(min-width: 600px)',
            'isOpen': True,
            'animate': False,
        })

        self.menu = ej.navigations.TreeView({
            'fields': {
                'cssClass': PMAPP_SIDEBAR_CSS,
                'dataSource': '',
                'id': 'nodeId',
                'text': 'nodeText',
                'child': 'nodeChild'
            },
            'expandOn': 'Click',
            'nodeSelected': self.menu_select,
        })

    # Show sidebar menu
    def show(self):
        self.menu.appendTo(jQuery(f"#{self.container_el}-menu")[0])
        self.control.appendTo(jQuery(f"#{self.container_el}")[0])

    # Sidebar toggle
    def toggle(self, args):
        self.control.toggle()

    def show_menu(self, menu_id):
        self.menu.fields.dataSource = PMAPP_SIDEBAR_MENUS[menu_id]

    def menu_select(self, args, subcomponent=None):
        if subcomponent is None:
            if 'e-level-1' in list(args.node.classList):
                print('Accordion')
                self.menu.collapseAll()
                self.menu.expandAll([args.node])
                self.nav_target_id = None

            menu_item_id = args.nodeData.id
            print(menu_item_id)
            component = PMAPP_NAV_ITEMS[menu_item_id] if menu_item_id in PMAPP_NAV_ITEMS else None
        else:
            component = PMAPP_NAV_ITEMS[subcomponent]
        if component is None:
            return

        if self.content_control is not None and self.nav_target_id is None:
            self.content_control.destroy()

        nav_container_id = self.content_id if self.nav_target_id is None else self.nav_target_id
        if component['type'] == 'custom':
            try:
                view_class = getattr(AppEnv.views, component['class'])
                self.content_control = view_class(container_id=nav_container_id)
            except Exception as e:
                print(e)

        if component['type'] == 'view':
            if 'config' in component:
                self.content_control = GridView(view_name=component['config'], container_id=nav_container_id)
            elif hasattr(AppEnv.views, f"{component['model']}View"):
                view_class = getattr(AppEnv.views, f"{component['model']}View")
                self.content_control = view_class(container_id=nav_container_id)
            else:
                self.content_control = GridView(model=component['model'], container_id=nav_container_id)

        elif component['type'] == 'form':
            try:
                form_class = getattr(AppEnv.forms, f"{component['model']}Form")
                self.content_control = form_class(target=nav_container_id)
            except Exception as e:
                print(e.args)
                self.content_control = FormBase(model=component['model'], target=nav_container_id)

        elif component['type'] == 'page':
            try:
                page_class = getattr(AppEnv.pages, f"{component['model']}Page")
                self.content_control = page_class(container_id=nav_container_id)
            except Exception as e:
                print(e.args)
                # self.content_control = Pages.BaseForm(model=component['model'], target=self.content_id)

        if hasattr(self.content_control, 'target_id'):
            self.nav_target_id = self.content_control.target_id

        # try:
        self.content_control.form_show()
        # except Exception as e:
        #     print(e)
        if self.control.isOpen:
            self.control.toggle()
            self.control.toggle()

        if 'subcomponent' in component:
            time.sleep(0.5)
            self.menu_select(None, subcomponent=component['subcomponent'])
            

PMAPP_APPBAR_ADD_ITEM = {
    'Add Time Entry': {'model': 'TimeEntry', 'type': 'form'},
    'Add Event': {'model': 'Event', 'type': 'form'},
    'Add Task': {'model': 'Task', 'type': 'form'},
    'Add Document': {'model': 'Document', 'type': 'form'},
    'Add Expense': {'model': 'Expense', 'type': 'form'},
    'Add Contact': {'model': 'Contact', 'type': 'form'},
    'Add Lead': {'model': 'Lead', 'type': 'form'},
    'Add Case': {'model': 'Case', 'type': 'form'},
    'Add Invoice': {'model': 'Invoice', 'type': 'form'},
    'Add Update': {'model': 'Update', 'type': 'form'},
}

            
def add_item_select(args, content_el_id):
    print('Add item selected')
    item = PMAPP_APPBAR_ADD_ITEM.get(args.item.text)
    if item and item['type'] == 'form':
        try:
            form_class = getattr(AppEnv.forms, f"{item['model']}Form")
            form_control = form_class(target=content_el_id)
        except Exception as e:
            print(e.args)
            form_control = FormBase(model=item['model'], target=content_el_id)
        form_control.form_show()
