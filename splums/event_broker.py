from events import Event
from events import EventTypes

"""This is currently just a framework for the event broker.
    Function names may be changed when they are actually developed."""
def event_broker(event: Event):
    match event.event_type:
        case EventTypes.SWIPE_IN: # Swipe In
            print("Swipe In")
            # Call swipe processor
            from swipe_processor import swipe_in_process
            swipe_in_process(event)

        case EventTypes.ACCEPTED_SWIPE_IN: # Accepted Swipe In
            print("Accepted Swipe In")
            # Call all necessary modules
            # towerLightGreen()
            # showAttendantScreen(event)
            # showLabScreen(event)
            # updateDB(event)
            # expectEnter()
            
        case EventTypes.DENIED_SWIPE_IN: # Denied Swipe In
            print("Denied Swipe In")
            # Call all necessary modules
            # towerLightRed()
            # updateDB(event)

        case EventTypes.SWIPE_OUT: # Swipe Out
            print("Swipe Out")
            # Call swipe processor
            from swipe_processor import swipe_out_process
            swipe_out_process(event)

        case EventTypes.ACCEPTED_SWIPE_OUT: # Accepted Swipe Out
            print("Accepted Swipe Out")
            # Call all necessary modules
            # towerLightGreen()
            # removeAttendantScreen(event)
            # removeLabScreen(event)
            # updateDB(event)
            # expectExit()
    
        case EventTypes.DENIED_SWIPE_OUT: # Denied Swipe Out
            print("Denied Swipe Out")
            # Call all necessary modules
            # towerLightRed()
            # updateDB(event)

        case EventTypes.EXPECTED_GATE_CROSSING: # Expected Gate Crossing
            print("Expected Gate Crossing")
            # Call all necessary modules
            # updateDB(event)

        case EventTypes.UNEXPECTED_GATE_CROSSING: # Unexpected Gate Crossing
            print("Unexpected Gate Crossing")
            # Call all necessary modules
            # activateAlarm()
            # towerLightRed()
            # updateDB(event)

        case EventTypes.CREATE_NEW_USER: # Create New User
            print("Create New User")
            # Call all necessary modules
            import usercreation
            usercreation.create_user(event)
            # updateDB(event)

        case EventTypes.DELETE_USER: # Delete User
            print("Delete User")
            # Call all necessary modules
            import usercreation
            usercreation.delete_user(event)
            # updateDB(event)

        case EventTypes.EDIT_USER: # Edit User
            print("Edit User")
            # Call all necessary modules
            import usercreation
            usercreation.edit_user(event)
            # updateDB(event)

        case EventTypes.CREATE_NOTE: # Create Note
            print("Create Note")
            # Call all necessary modules
            import notecreation
            notecreation.create_note(event)
            # updateDB(event)

        case EventTypes.EDIT_NOTE: # Edit Note
            print("Edit Note")
            # Call all necessary modules
            import notecreation
            notecreation.edit_note(event)
            # updateDB(event)

        case EventTypes.DELETE_NOTE: # Delete Note
            print("Delete Note")
            # Call all necessary modules
            import notecreation
            notecreation.delete_note(event)
            # updateDB(event)

        case EventTypes.OPEN_LAB: # Open Lab
            print("Open Lab")
            # Call all necessary modules
            # editNote(event)
            # updateDB(event)

        case EventTypes.CLOSE_LAB: # Close Lab
            print("Close Lab")
            # Call all necessary modules
            # editNote(event)
            # updateDB(event)

        case EventTypes.ARCHIVE_USER: # Archive User
            print("Archive User")
            # Call all necessary modules
            # editNote(event)
            # updateDB(event)

        case _:
            print("Error")