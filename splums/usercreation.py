import cam
import datetime


def create_user():

    bronco_id= input("Type the user's bronco id: ")
    name = input("Type the user's first and last name: ")
    photo_url = cam.take_picture(name)
    user_type_id = int(input("What type of user is this\n(1): Administrator\n(2): Attendant\n(3): Student\n(4): Blacklisted\n"))


create_user()