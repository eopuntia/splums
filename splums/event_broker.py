from events import Event
from events import EventTypes
import notecreation
import usercreation

"""This is currently just a framework for the event broker.
    Function names may be changed when they are actually developed."""
def event_broker(event: Event):
    from swipe_processor import swipe_in_process
    from swipe_processor import swipe_out_process
    match event.event_type:
        case EventTypes.SWIPE_IN: # Swipe In
            print(f"Swipe In")
            # Call swipe processor
            swipe_in_process(event)

        case EventTypes.ACCEPTED_SWIPE_IN: # Accepted Swipe In
            print(f"Accepted Swipe In")
            # Call all necessary modules
            # towerLightGreen()
            # showAttendantScreen(event)
            # showLabScreen(event)
            # updateDB(event)
            # expectEnter()
            
        case EventTypes.DENIED_SWIPE_IN: # Denied Swipe In
            print(f"Denied Swipe In")
            # Call all necessary modules
            # towerLightRed()
            # updateDB(event)

        case EventTypes.SWIPE_OUT: # Swipe Out
            print(f"Swipe Out")
            # Call swipe processor
            swipe_out_process(event)

        case EventTypes.ACCEPTED_SWIPE_OUT: # Accepted Swipe Out
            print(f"Accepted Swipe Out")
            # Call all necessary modules
            # towerLightGreen()
            # removeAttendantScreen(event)
            # removeLabScreen(event)
            # updateDB(event)
            # expectExit()
    
        case EventTypes.DENIED_SWIPE_OUT: # Denied Swipe Out
            print(f"Denied Swipe Out")
            # Call all necessary modules
            # towerLightRed()
            # updateDB(event)

        case EventTypes.EXPECTED_GATE_CROSSING: # Expected Gate Crossing
            print(f"Expected Gate Crossing")
            # Call all necessary modules
            # updateDB(event)

        case EventTypes.UNEXPECTED_GATE_CROSSING: # Unexpected Gate Crossing
            print(f"Unexpected Gate Crossing")
            # Call all necessary modules
            # activateAlarm()
            # towerLightRed()
            # updateDB(event)

        case EventTypes.CREATE_NEW_USER: # Create New User
            print(f"Create New User")
            # Call all necessary modules
            usercreation.create_user(event)
            # updateDB(event)

        case EventTypes.DELETE_USER: # Delete User
            print(f"Delete User")
            # Call all necessary modules
            usercreation.delete_user(event)
            # updateDB(event)

        case EventTypes.EDIT_USER: # Edit User
            print(f"Edit User")
            # Call all necessary modules
            usercreation.edit_user(event)
            # updateDB(event)

        case EventTypes.CREATE_NOTE: # Create Note
            print(f"Create Note")
            # Call all necessary modules
            notecreation.create_note(event)
            # updateDB(event)

        case EventTypes.EDIT_NOTE: # Edit Note
            print(f"Edit Note")
            # Call all necessary modules
            notecreation.edit_note(event)
            # updateDB(event)

        case EventTypes.DELETE_NOTE: # Delete Note
            print(f"Delete Note")
            # Call all necessary modules
            notecreation.delete_note(event)
            # updateDB(event)

        case _:
            print(f"Error")