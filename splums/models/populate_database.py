from sqlalchemy import Engine, create_engine, insert, select
from sqlalchemy.orm import sessionmaker
from models import Account, Role, Note, Account_Equipment, Equipment, Event, Event_Type, Base, Affiliation, Department

# connect to the engine.
engine = create_engine("mariadb+mariadbconnector://splums:example@127.0.0.1:3307/splums")
# setup the metadata corresponding to the base.
Base.metadata.create_all(engine)

# create a session to interact with the database engine using the ORM.
Session = sessionmaker(engine)

# using the with clause basically automatically frees the session opening when it ends.
with Session() as session:
    # it is very easy to define new records, just say the name of the class and fill in the fields.
    # these class objects are not actually added to the database yet.
    administrator = Role(name="Administrator")
    attendant = Role(name="Attendant")
    user = Role(name="User")

    undergrad = Affiliation(name="Undergrad", icon_url="./images/undergrad.png")
    graduate = Affiliation(name="Graduate", icon_url="./images/graduate.png")
    faculty = Affiliation(name="Faculty", icon_url="./images/faculty.png")
    researcher = Affiliation(name="Researcher", icon_url="./images/researcher.png")
    staff = Affiliation(name="Staff", icon_url="./images/staff.png")
    other = Affiliation(name="Other", icon_url="./images/other.png")

    chemical_paper = Department(name="Chemical and Paper Engineering")
    civil_construction = Department(name="Civil and Construction Engineering")
    computer_science = Department(name="Computer Science")
    electrical_computer = Department(name=" Electrical and Computer Engineering")
    eng_design_manufacturing_mgmt_syst = Department(name="Engineering Design, Manufacturing and Management Systems")
    indust_entreprenural_mgmt = Department(name="Industrial and Entrepreneurial Engineering and Engineering Management")
    mechanical_aero = Department(name="Mechanical and Aerospace Engineering")
    other_dep = Department(name="Other")

    # the datetime fields get populated automatically. You can see specifying the role and status relations in account.
    # what this does behind the scenes is it will populate the ID's for you. Makes it very easy. 
    renee = Account(win=212222222, role=user, affiliation=graduate, department=computer_science, display_name="rez", 
                     given_name="Renee", surname="Rickert", photo_url="./images/212222222.jpg",
                     rso="Computer Club")

    kahrl = Account(win=123412341, role=administrator, affiliation=staff, department=eng_design_manufacturing_mgmt_syst, display_name="zathras", 
                     given_name="Allin", surname="Kahrl", photo_url="./images/123412341.jpg")

    estlin = Account(win=432143214, role=attendant, affiliation=undergrad, department=electrical_computer, display_name="estlin", 
                     given_name="Estlin", surname="Mendez", photo_url="./images/432143214.jpg")

    # actually load the objects to be committed (still not in the DB, will happen after commit call.
    # important to note is that since user, active, administrator, and attendant were related in these object definitions, 
    # those objects are also implicitly added.
    session.add_all([renee, kahrl, estlin])
    session.add_all([chemical_paper, civil_construction, indust_entreprenural_mgmt, mechanical_aero, other_dep])
    session.add_all([faculty, researcher, other])



    # it is also possible to bulk add elements while declaring them at the same time.
    session.execute(
        insert(Role),
        [   {"name": "Archived"},
            {"name": "Blacklisted"},
        ],
    )
    session.execute( 
        insert(Equipment),
        [
            {"name": "drill_press", "icon_url": "./splums/images/drill_press.png"},
            {"name": "cnc_machine", "icon_url": "./splums/images/cnc_machine.png"},
            {"name": "laser_cutter", "icon_url": "./splums/images/laser_cutter.png"},
            {"name": "soldering_station", "icon_url": "./splums/images/soldering_station.png"},
        ],
    )
    session.execute( 
        insert(Event_Type),
        [
            {"name": "Authorized User Swipe"},
            {"name": "Archived User Swipe"},
            {"name": "Blacklisted User Swipe"},
            {"name": "Intrusion Detected"},
        ],
    )
    
    # example of adding account_equipment record, can also define objects in line.
    renee_welding = Account_Equipment(account=renee, equipment=Equipment(name="welding_station", icon_url="./splums/images/welding_station.png"), completed_training=False)
    session.add(renee_welding)

    # the ids for creator and subject will be populated automatically.
    note1 = Note(creator_account=kahrl, subject_account=renee, text="renee does not know how to tig weld but she can mig")
    session.add(note1)

    # it is always necessary to commit, no changes are applied until commit is applied.
    session.commit()


with Session() as session:
    # made these fields in seperate session block after the commit to show pulling data from the db.
    unauthorized = session.scalar(select(Event_Type).where(Event_Type.name=="Authorized User Swipe"))
    renee = session.scalar(select(Account).where(Account.given_name=="Renee"))

    # makes it very easy not having to worry about getting the actual ids.
    sample_event = Event(event_type=unauthorized, account=renee)

    session.add(sample_event)
    session.commit()