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
                print(f"\033[93mChecking if user is swiped in...\0333[0m")
                result = swipe_events.check_if_swiped_in(event, self.session, self)
                print(f"result after event_broker call: {result}")
                return result

            case EventTypes.SWIPE_IN: 
                print(f"Swipe In")
                swipe_events.swipe_in(event, self.session, self)

            # TODO IMPLEMENT
            case EventTypes.ACCEPTED_SWIPE_IN:
                print(f"Accepted Swipe In")
                event_log.log(event, self.session)
                # towerLightGreen()
                # showAttendantScreen(event)
                # showLabScreen(event)
                # expectEnter()
                
            # TODO IMPLEMENT
            case EventTypes.DENIED_SWIPE_IN:
                print(f"Denied Swipe In")
                event_log.log(event, self.session)
                # towerLightRed()

            case EventTypes.SWIPE_OUT: 
                print(f"Swipe Out")
                swipe_events.swipe_out(event, self.session, self)

            # TODO IMPLEMENT
            case EventTypes.ACCEPTED_SWIPE_OUT: 
                print(f"Accepted Swipe Out")
                event_log.log(event, self.session)
                # towerLightGreen()
                # removeAttendantScreen(event)
                # removeLabScreen(event)
                # expectExit()
        
            # TODO IMPLEMENT
            case EventTypes.DENIED_SWIPE_OUT: 
                print(f"Denied Swipe Out")
                event_log.log(event, self.session)
                # towerLightRed()

            # TODO IMPLEMENT
            case EventTypes.EXPECTED_GATE_CROSSING: 
                print(f"Expected Gate Crossing")
                event_log.log(event, self.session)

            # TODO IMPLEMENT
            case EventTypes.UNEXPECTED_GATE_CROSSING: 
                print(f"Unexpected Gate Crossing")
                event_log.log(event, self.session)
                # activateAlarm()
                # towerLightRed()

            case EventTypes.CREATE_ACCOUNT: 
                print(f"Create New Account")
                result = account_events.create(event, self.session)
                event_log.log(event, self.session)
                return result

            case EventTypes.DELETE_ACCOUNT:
                print(f"Delete Account")
                event_log.log(event, self.session)
                return account_events.delete(event, self.session)

            case EventTypes.EDIT_ACCOUNT: 
                print(f"Edit Account")
                event_log.log(event, self.session)
                return account_events.edit(event, self.session)

            case EventTypes.CREATE_NOTE: 
                print(f"Create Note")
                event_log.log(event, self.session)
                return note_events.create(event, self.session)

            case EventTypes.DELETE_NOTE: 
                print(f"Delete Note")
                event_log.log(event, self.session)
                return note_events.delete(event, self.session)

            case EventTypes.EDIT_NOTE: 
                print(f"Edit Note")
                event_log.log(event, self.session)
                return note_events.edit(event, self.session)

            # TODO IMPLEMENT
            case EventTypes.OPEN_LAB: 
                print(f"Open Lab")
                self.open_lab(event)

            # TODO IMPLEMENT
            case EventTypes.CLOSE_LAB: 
                print(f"Close Lab")
                event_log.log(event, self.session)
                self.close_lab(event)
                account_events.auto_archive_user(self.session)
                account_events.auto_delete_user(self.session)

            case EventTypes.ARCHIVE_ACCOUNT: 
                print(f"Archive User")
                event_log.log(event, self.session)
                account_events.archive_user(event, self.session)

            case EventTypes.CHANGE_USER_ROLE: 
                print(f"Archive User")
                account_events.change_user_role(event, self.session)

            case EventTypes.GET_SWIPED_IN_USERS:
                print(f"\033[93mGetting swiped-in users...\033[0m")
                result = account_events.get_swiped_in_users(self.session)
                return result
            
            case EventTypes.GET_NOTES_FOR_USER_ADMIN:
                print(f"\033[93mGetting notes for user...\033[0m")
                result = note_events.get_notes_for_user_admin(event, self.session)
                return result
            
            case EventTypes.GET_NOTES_FOR_USER_ATTENDANT:
                print(f"\033[93mGetting notes for user...\033[0m")
                result = note_events.get_notes_for_user_attendant(event, self.session)
                return result
            
            case EventTypes.GET_USERS_BY_SEARCH:
                print(f"\033[93mGetting users...\033[0m")
                result = account_events.search_users(event, self.session)
            case EventTypes.GET_NOTE_FOR_USER:
                print(f"\033[93mGetting note for user...\033[0m")
                result = note_events.get_note_for_user(event, self.session)
                return result

            case EventTypes.GET_DATA_FOR_USER:
                print(f"\033[93mGetting data for user...\033[0m")
                result = account_events.get_data_for_user(event, self.session)
                print(f"result after event_broker call: {result}")
                return result

            case EventTypes.EDIT_NOTE_FOR_USER:
                print(f"\033[93mEditing note for user...\033[0m")
                result = note_events.edit_note_for_user(event, self.session)
                print(f"result after event_broker call: {result}")
                return result

            case EventTypes.GET_PERMS_FOR_USER:
                print(f"\033[93mGetting Perms for user...\033[0m")
                result = account_events.get_perms_for_user(event, self.session)
                print(f"result after event_broker call: {result}")
                return result

            case EventTypes.CHECK_IF_WIN_EXISTS:
                print(f"\033[93mChecking if win is already in DB...\033[0m")
                result = account_events.check_if_win_exists(event, self.session)
                print(f"result after event_broker call: {result}")
                return result

            case EventTypes.GET_ALL_PERMS:
                print(f"\033[93mGetting every permission from DB...\033[0m")
                result = permission_events.get_all_perms(event, self.session)
                print(f"result after event_broker call: {result}")
                return result

            case EventTypes.GET_USERS_PAGINATED_FILTERED:
                print(f"\033[93mGetting paginated and filtered users...\033[0m")
                result = account_events.get_users_paginated_filtered(event, self.session)
                print(f"result after event_broker call: {result}")
                return result

            case EventTypes.ATTEMPT_ATTENDANT_SIGNIN:
                print(f"\033[93mAttempting attendant signin...\033[0m")
                result = account_events.attempt_attendant_signin(event, self.session)
                event_log.log(event, self.session)
                return result

            case EventTypes.ATTEMPT_ATTENDANT_SIGNOUT:
                print(f"\033[93mAttempting attendant signout...\033[0m")
                event_log.log(event, self.session)
                result = account_events.attempt_attendant_signout(event, self.session)
                return result

            case EventTypes.CHECK_IF_ACTIVE_ATTENDANT:
                print(f"\033[93mAttempting attendant signout...\033[0m")
                result = account_events.check_if_active_attendant(event, self.session)
                return result

            case EventTypes.GET_ACTIVE_ATTENDANT:
                print(f"\033[93mGetting Active Attendant...\033[0m")
                result = account_events.get_active_attendant(event, self.session)
                return result
            
            case EventTypes.SET_USER_PIN:
                print(f"\033[93mAttempting to set user pin...\033[0m")
                result = account_events.set_user_pin(event, self.session)
                return result
            
            case EventTypes.CHECK_USER_PIN:
                print(f"\033[93mAttempting to check user pin...\033[0m")
                result = account_events.check_user_pin(event, self.session)
                return result            
            case EventTypes.GET_LOGS_BY_SEARCH:
                print(f"\033[93mGetting logs...\033[0m")
                result = event_log.search_logs(event, self.session)
                return result
            case EventTypes.GET_USER:
                print(f"\033[93mGetting user...\033[0m")
                result = account_events.get_user(event, self.session)
                return result

            case _:
                print(f"Error")
