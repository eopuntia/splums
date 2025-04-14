from events import Event
from events import EventTypes
from sqlalchemy import select
import note_events, account_events, swipe_events, event_log, permission_events
from models.models import Account, Role

class EventBroker:
    def __init__(self, session):
        self.session = session

    def process_event(self, event):
        match event.event_type:
            case EventTypes.CHECK_IF_SWIPED_IN:
                result = swipe_events.check_if_swiped_in(event, self.session, self)
                return result

            case EventTypes.SWIPE_IN: 
                swipe_events.swipe_in(event, self.session, self)

            # TODO IMPLEMENT
            case EventTypes.ACCEPTED_SWIPE_IN:
                event_log.log(event, self.session)
                # towerLightGreen()
                # showAttendantScreen(event)
                # showLabScreen(event)
                # expectEnter()
                
            # TODO IMPLEMENT
            case EventTypes.DENIED_SWIPE_IN:
                event_log.log(event, self.session)
                # towerLightRed()

            case EventTypes.SWIPE_OUT: 
                swipe_events.swipe_out(event, self.session, self)

            # TODO IMPLEMENT
            case EventTypes.ACCEPTED_SWIPE_OUT: 
                event_log.log(event, self.session)
                # towerLightGreen()
                # removeAttendantScreen(event)
                # removeLabScreen(event)
                # expectExit()
        
            # TODO IMPLEMENT
            case EventTypes.DENIED_SWIPE_OUT: 
                event_log.log(event, self.session)
                # towerLightRed()

            # TODO IMPLEMENT
            case EventTypes.EXPECTED_GATE_CROSSING: 
                event_log.log(event, self.session)

            # TODO IMPLEMENT
            case EventTypes.UNEXPECTED_GATE_CROSSING: 
                event_log.log(event, self.session)
                # activateAlarm()
                # towerLightRed()

            case EventTypes.CREATE_ACCOUNT: 
                result = account_events.create(event, self.session)
                event_log.log(event, self.session)
                return result

            case EventTypes.DELETE_ACCOUNT:
                event_log.log(event, self.session)
                return account_events.delete(event, self.session)

            case EventTypes.EDIT_ACCOUNT: 
                event_log.log(event, self.session)
                return account_events.edit(event, self.session)

            case EventTypes.CREATE_NOTE: 
                event_log.log(event, self.session)
                return note_events.create(event, self.session)

            case EventTypes.DELETE_NOTE: 
                event_log.log(event, self.session)
                return note_events.delete(event, self.session)

            case EventTypes.EDIT_NOTE: 
                event_log.log(event, self.session)
                return note_events.edit(event, self.session)

            # TODO IMPLEMENT
            case EventTypes.OPEN_LAB: 
                self.open_lab(event)

            # TODO IMPLEMENT
            case EventTypes.CLOSE_LAB: 
                event_log.log(event, self.session)
                self.close_lab(event)
                account_events.auto_archive_user(self.session)
                account_events.auto_delete_user(self.session)

            case EventTypes.ARCHIVE_ACCOUNT: 
                event_log.log(event, self.session)
                account_events.archive_user(event, self.session)

            case EventTypes.CHANGE_USER_ROLE: 
                account_events.change_user_role(event, self.session)

            case EventTypes.GET_SWIPED_IN_USERS:
                result = account_events.get_swiped_in_users(self.session)
                return result
            
            case EventTypes.GET_NOTES_FOR_USER_ADMIN:
                result = note_events.get_notes_for_user_admin(event, self.session)
                return result
            
            case EventTypes.GET_NOTES_FOR_USER_ATTENDANT:
                result = note_events.get_notes_for_user_attendant(event, self.session)
                return result
            
            case EventTypes.GET_USERS_BY_SEARCH:
                result = account_events.search_users(event, self.session)
            case EventTypes.GET_NOTE_FOR_USER:
                result = note_events.get_note_for_user(event, self.session)
                return result

            case EventTypes.GET_DATA_FOR_USER:
                result = account_events.get_data_for_user(event, self.session)
                return result

            case EventTypes.EDIT_NOTE_FOR_USER:
                result = note_events.edit_note_for_user(event, self.session)
                return result

            case EventTypes.GET_PERMS_FOR_USER:
                result = account_events.get_perms_for_user(event, self.session)
                return result

            case EventTypes.CHECK_IF_WIN_EXISTS:
                result = account_events.check_if_win_exists(event, self.session)
                return result

            case EventTypes.GET_ALL_PERMS:
                result = permission_events.get_all_perms(event, self.session)
                return result

            case EventTypes.GET_USERS_PAGINATED_FILTERED:
                result = account_events.get_users_paginated_filtered(event, self.session)
                return result

            case EventTypes.ATTEMPT_ATTENDANT_SIGNIN:
                result = account_events.attempt_attendant_signin(event, self.session)
                event_log.log(event, self.session)
                return result

            case EventTypes.ATTEMPT_ATTENDANT_SIGNOUT:
                event_log.log(event, self.session)
                result = account_events.attempt_attendant_signout(event, self.session)
                return result

            case EventTypes.CHECK_IF_ACTIVE_ATTENDANT:
                result = account_events.check_if_active_attendant(event, self.session)
                return result

            case EventTypes.GET_ACTIVE_ATTENDANT:
                result = account_events.get_active_attendant(event, self.session)
                return result
            
            case EventTypes.SET_USER_PIN:
                result = account_events.set_user_pin(event, self.session)
                return result
            
            case EventTypes.CHECK_USER_PIN:
                result = account_events.check_user_pin(event, self.session)
                return result            
            case EventTypes.GET_LOGS_BY_SEARCH:
                result = event_log.search_logs(event, self.session)
                return result
            case EventTypes.GET_USER:
                result = account_events.get_user(event, self.session)
                return result

            case _:
                print(f"Error")
