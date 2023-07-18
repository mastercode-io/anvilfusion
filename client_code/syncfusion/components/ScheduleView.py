import anvil.server
from anvil.tables import query as q
import anvil.js
from anvil.js.window import ej, jQuery, Date, XMLHttpRequest, Object

from .. import app
from ..app.constants import *
from ..orm_client.model import *
from .. import Forms

import string
import uuid
import json
from datetime import datetime, timedelta

PM_SCHEDULE_HEIGHT_OFFSET = 35
PM_SCHEDULE_DEFAULT_VIEWS = [
    'Agenda',
    'Day',
    'Week',
    'Month',
]
PM_SCHEDULE_DETAIL_VIEWS = [
    # 'Agenda',
    'MonthAgenda',
    'TimelineDay',
    'TimelineWeek',
    'TimelineWorkWeek',
    'TimelineMonth',
    'TimelineYear',
]
PM_SCHEDULE_CELL_TEMPLATE = '${if(type === "workCells")}<div>${pmRenderCell(resource)}</div>${/if}${if(type === ' \
                            '"monthCells")}${/if}'
PM_EVENT_VIEW_COLUMNS = [
    {'name': 'start_time'},
    {'name': 'end_time'},
    {'name': 'activity.name'},
    {'name': 'location.name'},
    {'name': 'staff.full_name'},
    {'name': 'case.case_name'},
    {'name': 'no_case'},
    {'name': 'department.full_name'},
    {'name': ''},
]


class EventScheduleView:
    def __init__(self,
                 container_id=None,
                 model=None,
                 title=None,
                 ):
        print('EventScheduleView')

        self.db_data = None
        self.schedule_el_id = None
        self.schedule_height = None
        self.container_id = container_id
        self.container_el = None
        self.events = None

        event_fields = {
            'id': {'name': 'uid'},
            'subject': {'name': 'subject', 'title': 'Event'},
            'startTime': {'name': 'start_time', 'title': 'Start Time'},
            'endTime': {'name': 'end_time', 'title': 'End Time'},
            'description': {'name': 'description', 'title': 'Description'},
            'location': {'name': 'location', 'title': 'Location'},
        }

        self.data_adaptor = ej.data.CustomDataAdaptor()
        self.data_adaptor.options.getData = self.data_adaptor_get_data
        self.data_adaptor.options.addRecord = self.data_adaptor_record
        self.data_adaptor.options.updateRecord = self.data_adaptor_record
        self.data_adaptor.options.deleteRecord = self.data_adaptor_record
        self.data_adaptor.options.butchUpdate = self.data_adaptor_record
        self.data_manager = ej.data.DataManager({
            'url': '_/theme/data-adaptor.json',
            'adaptor': self.data_adaptor,
        })

        schedule_config = {
            'height': '100%',
            'currentView': 'Agenda',
            'views': PM_SCHEDULE_DEFAULT_VIEWS,
            'selectedDate': Date.now(),
            'eventSettings': {
                'dataSource': self.data_manager,
                # 'dataSource': self.events,
                'fields': event_fields,
            },
            'popupOpen': self.popup_open,
            'actionBegin': self.action_begin,
            'actionComplete': self.action_complete,
            'hover': self.hover_event,
            'cssClass': 'pm-schedule-cell-width pm-schedule-cell-height e-hide-spinner',
            # 'cellTemplate': PM_SCHEDULE_CELL_TEMPLATE,
            'renderCell': self.render_cell,
        }

        self.schedule = ej.schedule.Schedule(schedule_config)
        # anvil.js.window.pmRenderCell = self.render_cell

    # get events and bind them to the view
    def form_show(self, **event_args):
        self.schedule_el_id = uuid.uuid4()
        self.container_el = jQuery(f"#{self.container_id}")[0]
        self.schedule_height = self.container_el.offsetHeight - PM_SCHEDULE_HEIGHT_OFFSET
        self.container_el.innerHTML = f'\
       <div class="pm-scheduleview-container" style="height:{self.schedule_height}px;">\
         <div class="pm-gridview-title">Agenda</div>\
         <div id="{self.schedule_el_id}"></div>\
       </div>'
        self.schedule.appendTo(jQuery(f"#{self.schedule_el_id}")[0])
        # self.get_events()
        # self.schedule.eventSettings.dataSource = self.events

    def destroy(self):
        self.schedule.destroy()
        if self.container_el is not None:
            self.container_el.innerHTML = ''

    def popup_open(self, args):
        # print('popup', args.type)
        if (args.type == 'QuickInfo' and 'subject' not in args.data.keys()) or args.type == 'Editor':
            args.cancel = True
            if args.type == 'Editor':
                # print(args.data)
                event_uid = args.data.get('uid', None)
                if event_uid:
                    action = 'edit'
                    event = Event.get(event_uid)
                else:
                    action = 'add'
                    start_time = app.lib.datetime_js_to_py(args.data.start_time)
                    end_time = start_time + timedelta(hours=1)
                    event = Event(start_time=start_time, end_time=end_time)
                editor = Forms.EventForm(data=event, action=action, target=self.container_id,
                                         update_source=self.update_schedule)
                editor.form_show()
        elif args.type == 'QuickInfo':
            # print('POPUP', args.data)
            args.data['location'] = 'LOCATION'

    def update_schedule(self, event):
        self.schedule.refreshEvents()

    def action_begin(self, args):
        print('Begin', args.requestType)

        # change event
        if args.requestType == 'eventChange':
            changed_event = args.data
            # event = self.db_data[changed_event.uid]
            event = Event.get(changed_event.uid)
            event['start_time'] = app.lib.datetime_js_to_py(changed_event.start_time)
            event['end_time'] = app.lib.datetime_js_to_py(changed_event.end_time)
            event.save()
            self.schedule.refreshEvents()

        # delete event(s)
        if args.requestType == 'eventRemove':
            for removed in args.data:
                # event = self.db_data[removed.uid]
                event = Event.get(removed.uid)
                event.delete()
            self.schedule.refreshEvents()

    def action_complete(self, args):
        print('Complete', args.requestType)

    def hover_event(self, args):
        if self.schedule.currentView not in PM_SCHEDULE_DETAIL_VIEWS:
            event = self.schedule.getEventDetails(args.element)
            if event:
                event['location'] = 'OVERRIDE'
                self.schedule.openQuickInfoPopup(event)
                # for k in event.keys():
                #  print(k, event[k])
            else:
                self.schedule.closeQuickInfoPopup()

    def render_cell(self, args):
        # for k in args.keys():
        #   print(k, args[k])
        if args.elementType == 'workCells' or args.elementType == 'monthCells':
            # print('element', args.element)
            # for k in args.element.keys():
            #   print(k, args[k])
            event = self.schedule.getEventDetails(args.element)
            # if event:
            # print('event', event)

    def get_events(self, start_time, end_time):
        query = {'start_time': q.all_of(q.greater_than(start_time), q.less_than(end_time))}
        event_cols = [
            {'name': 'uid'},
            {'name': 'start_time'},
            {'name': 'end_time'},
            {'name': 'activity.name'},
            {'name': 'case.case_name'},
            {'name': 'location.name'},
            {'name': 'department.full_name'},
            {'name': 'staff.full_name'},
        ]
        self.events = Event.get_grid_view(view_config={'columns': event_cols}, filters=query)
        for event in self.events:
            event['subject'] = event['activity']
            if event['case']:
                event['subject'] = f"{event['case']}: {event['subject']}"
                event['location'] = f"{event['location']} / {event['department']}<br>{event['staff']}"
            else:
                event['location'] += f"<br>{event['staff']}"
        self.events = ej.base.extend([], self.events, None, True)
        print('Events #', len(self.events))
        for event in self.events:
            print(event['subject'], event['location'])

    def data_adaptor_get_data(self, query):
        print('getData')
        print(query)

        query_data = json.loads(query.data)
        start_time = datetime.fromisoformat(query_data['StartDate'][:10])
        end_time = datetime.fromisoformat(query_data['EndDate'][:10])
        self.get_events(start_time, end_time)

        # construct HTTP request for data adaptor
        request = XMLHttpRequest()
        request.open('GET', '_/theme/data-adaptor.json', False)
        request.setRequestHeader('Content-Type', 'application/json; charset=utf-8')
        request.send({})
        query['httpRequest'] = request

        # call back to pass data back to adaptor
        query.onSuccess(self.events, query)

    def data_adaptor_record(self, query):
        print('record', query)
