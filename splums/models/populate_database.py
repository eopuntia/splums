from sqlalchemy import Engine, create_engine, insert, select
from sqlalchemy.orm import sessionmaker
from models import Account, Role, Account_Equipment, Equipment, Event, Event_Type, Base, Affiliation, Department


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
    administrator = Role(name="administrator")
    attendant = Role(name="attendant")
    user = Role(name="user")
    pending = Role(name="pending")

    undergrad = Affiliation(name="Undergrad", icon_url="./images/undergrad.png")
    graduate = Affiliation(name="Graduate", icon_url="./images/graduate.png")
    faculty = Affiliation(name="Faculty", icon_url="./images/faculty.png")
    researcher = Affiliation(name="Researcher", icon_url="./images/researcher.png")
    staff = Affiliation(name="Staff", icon_url="./images/staff.png")
    other = Affiliation(name="Other", icon_url="./images/other.png")

    computer_science = Department(name="cs")
    eng_design_manufacturing_mgmt_syst = Department(name="edmms")
    electrical_computer = Department(name="ece")
    chemical_paper = Department(name="cpe")
    civil_construction = Department(name="cce")
    indust_entreprenural_mgmt = Department(name="ieeem")
    mechanical_aero = Department(name="mae")
    ceas = Department(name="ceas")
    pilot = Department(name="pcpp")
    other_dep = Department(name="other")

    undergrad = Affiliation(name="undergrad", icon_url="./images/undergrad.png")
    graduate = Affiliation(name="graduate", icon_url="./images/graduate.png")
    faculty = Affiliation(name="faculty", icon_url="./images/faculty.png")
    researcher = Affiliation(name="researcher", icon_url="./images/researcher.png")
    staff = Affiliation(name="staff", icon_url="./images/staff.png")
    other = Affiliation(name="other", icon_url="./images/affiliation_other.png")

    # the datetime fields get populated automatically. You can see specifying the role and status relations in account.
    # what this does behind the scenes is it will populate the ID's for you. Makes it very easy. 
    renee = Account(win=212222222, role=user, affiliation=graduate, department=computer_science, display_name="rez", 
                     given_name="Renee", surname="Rickert", photo_url="./images/212222222.jpg",
                     rso="Computer Club", public_note='', private_note='')

    kahrl = Account(win=123412341, role=administrator, affiliation=staff, department=eng_design_manufacturing_mgmt_syst, display_name="zathras",
                     given_name="Allin", surname="Kahrl", photo_url="./images/default_pic.jpg", public_note='', private_note='')

    estlin = Account(win=432143214, role=attendant, affiliation=undergrad, department=electrical_computer, display_name="estlin", public_note='', private_note='',
                     given_name="Estlin", surname="Mendez", photo_url="./images/default_pic.jpg")

    # actually load the objects to be committed (still not in the DB, will happen after commit call.
    # important to note is that since user, active, administrator, and attendant were related in these object definitions, 
    # those objects are also implicitly added.
    session.add_all([faculty, researcher, other, pending])
    session.add_all([renee, kahrl, estlin])
    session.add_all([chemical_paper, civil_construction, indust_entreprenural_mgmt, mechanical_aero, other_dep, pilot, ceas])



    # it is also possible to bulk add elements while declaring them at the same time.
    session.execute(
        insert(Role),
        [   {"name": "archived"},
            {"name": "blacklisted"},
        ],
    )
    session.execute( 
        insert(Equipment),
        [
            {"name": "SMAW_(arc)", "icon_url": "./splums/images/smaw_arc.png"},
            {"name": "GTAW_(MIG)", "icon_url": "./splums/images/gtaw_mig.png"},
            {"name": "GTAW_(TIG)", "icon_url": "./splums/images/gtaw_tig.png"},
            {"name": "Gas_Welding", "icon_url": "./splums/images/gas_welding.png"},
            {"name": "Offhand_Grinding_(Offset,_Belt,_and_Tool)", "icon_url": "./splums/images/offhand_grinding.png"},
            {"name": "Finish_Grinding_(Surface_and_Cylindrical)", "icon_url": "./splums/images/finish_grinding.png"},
            {"name": "Drill_Presses", "icon_url": "./splums/images/drill_presses.png"},
            {"name": "Manual_Milling", "icon_url": "./splums/images/manual_milling.png"},
            {"name": "Manual_Turning", "icon_url": "./splums/images/manual_turning.png"},
            {"name": "CNC_Milling", "icon_url": "./splums/images/cnc_milling.png"},
            {"name": "CNC_Turning", "icon_url": "./splums/images/cnc_turning.png"},
            {"name": "Arbor_Press", "icon_url": "./splums/images/arbor_press.png"},
            {"name": "Paint_Booth", "icon_url": "./splums/images/paint_booth.png"},
            {"name": "Soldering", "icon_url": "./splums/images/soldering.png"},
            {"name": "Table_Saw", "icon_url": "./splums/images/table_saw.png"},
            {"name": "Bandsaws", "icon_url": "./splums/images/bandsaws.png"},
            {"name": "Blast_Cabinet", "icon_url": "./splums/images/blast_cabinet"},
            {"name": "Gas_Cylinder_Handling", "icon_url": "./splums/images/gas_cylinder_handling.png"},
            {"name": "Flammable_Liquid_Handling", "icon_url": "./splums/images/flammable_liquid_handling.png"},
            {"name": "Lithium_Battery_Handling", "icon_url": "./splums/images/lithium_battery_handling.png"},
            {"name": "Respirators", "icon_url": "./splums/images/respirators.png"},
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


    # it is always necessary to commit, no changes are applied until commit is applied.
    session.commit()


with Session() as session:
    # made these fields in seperate session block after the commit to show pulling data from the db.
    unauthorized = session.scalar(select(Event_Type).where(Event_Type.name=="Authorized User Swipe"))
    renee = session.scalar(select(Account).where(Account.given_name=="Renee"))
    renee.public_note = "renee can wig but not mig"

    # makes it very easy not having to worry about getting the actual ids.
    sample_event = Event(event_type=unauthorized, account=renee)

    session.add(sample_event)
    session.commit()
