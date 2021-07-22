from enum import Enum
from app.controller.tableau.handle_tableau_commands_controller import get_tableau_image, create_schedule_view, help, download_tableau_view
from app.controller.base_handle_commands_controller import list_schedule_reports


class TableauCommands(Enum):
    list_schedules = {"func": list_schedule_reports, "doc": "`list_schedules` \n>List the schedules that have been "
                                                           "setup. "
                                                           "Usage - `<bot> list_schedules channel`. If you do not put "
                                                           "anything after list_schedules, it will show you schedules "
                                                           "for your user by default."}
    schedule = {"func": create_schedule_view, "doc": "`schedule` \n>Schedule your Tableau view URL. Usage - `<bot> "
                                                     "schedule <URL>`"}
    image = {"func": get_tableau_image, "doc": "`image` \n>Get the Tableau image for a particular view URL. Usage - "
                                               "`<bot> image <URL>`"}
    download = {"func": download_tableau_view, "doc": "`download` \n>Download the Tableau crossdata for a particular"
                                                      " view URL. Usage - `<bot> download <URL>`"}

    help = {"func": help, "doc": f"*List of available commands* -"
                                 f" \n - {list_schedules['doc']}"
                                 f" \n - {schedule['doc']}"
                                 f" \n - {download['doc']}"
                                 f" \n - {image['doc']}"}
