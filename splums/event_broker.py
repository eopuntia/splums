from events import Event

"""This is currently just a framework for the event broker.
    Function names may be changed when they are actually developed."""
def event_broker(event):
    match event.event_type:
        case 0: # Swipe In
            print(f"Swipe In")
            # Call swipe processor
            # swipeInProcess(event)
        case 1: # Accepted Swipe In
            print(f"Accepted Swipe In")
            # Call all necessary modules
            # towerLightGreen()
            # showAttendantScreen(event)
            # showLabScreen(event)
            # updateDB(event)
            # expectEnter()
            
        case 2: # Denied Swipe In
            print(f"Denied Swipe In")
            # Call all necessary modules
            # towerLightRed()
            # updateDB(event)

        case 3: # Swipe Out
            print(f"Swipe Out")
            # Call swipe processor
            # swipeOutProcess(event)

        case 4: # Accepted Swipe Out
            print(f"Accepted Swipe Out")
            # Call all necessary modules
            # towerLightGreen()
            # removeAttendantScreen(event)
            # removeLabScreen(event)
            # updateDB(event)
            # expectExit()
            
        case 5: # Denied Swipe Out
            print(f"Denied Swipe Out")
            # Call all necessary modules
            # towerLightRed()
            # updateDB(event)

        case 6: # Expected Gate Crossing
            print(f"Expected Gate Crossing")
            # Call all necessary modules
            # updateDB(event)

        case 7: # Unexpected Gate Crossing
            print(f"Unexpected Gate Crossing")
            # Call all necessary modules
            # activateAlarm()
            # towerLightRed()
            # updateDB(event)

        case 8: # Create New User
            print(f"Create New User")
            # Call all necessary modules
            # createUser(event)
            # updateDB(event)

        case 9: # Delete User
            print(f"Delete User")
            # Call all necessary modules
            # deleteUser(event)
            # updateDB(event)

        case 10: # Edit User
            print(f"Edit User")
            # Call all necessary modules
            # editUser(event)
            # updateDB(event)

        case 11: # Create Note
            print(f"Create Note")
            # Call all necessary modules
            # createNote(event)
            # updateDB(event)

        case 12: # Edit Note
            print(f"Edit Note")
            # Call all necessary modules
            # editNote(event)
            # updateDB(event)

        case 13: # Delete Note
            print(f"Delete Note")
            # Call all necessary modules
            # deleteNote(event)
            # updateDB(event)

        case _:
            print(f"Error")