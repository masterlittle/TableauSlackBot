from enum import Enum
from app.controller.tableau.handle_tableau_commands_controller import get_tableau_image, create_schedule_view,\
    list_schedule_reports, help


class TableauCommands(Enum):
    list_schedules = {"func": list_schedule_reports, "doc": "`list_schedules` \n>List the schedules that have been "
                                                           "setup. "
                                                           "Usage - `<bot> list_schedules channel`. If you do not put "
                                                           "anything after list_schedules, it will show you schedules "
                                                           "for your user by default."}
    schedule = {"func": create_schedule_view, "doc": "`schedule` \n>Schedule your Tableau view URL. Usage - `<bot> "
                                                     "schedule <URL>`"}
    image = {"func": get_tableau_image, "doc": "`image` \n>Get the Tableau image for a particular view URL. Usage - "
                                               "`<bot> image "
                                               "<URL>`"}
    help = {"func": help, "doc": f"*List of available commands* -"
                                 f" \n - {list_schedules['doc']}"
                                 f" \n - {schedule['doc']}"
                                 f" \n - {image['doc']}"}
