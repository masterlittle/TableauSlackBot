from enum import Enum
from app.controller.redash.handle_redash_commands_controller import get_redash_image, create_schedule_view, \
    list_schedule_reports, help


class RedashCommands(Enum):
    list_schedules = {"func": list_schedule_reports, "doc": "`list_schedules` \n>List the schedules that have been "
                                                            "setup. "
                                                            "Usage - `<bot> list_schedules channel`. If you do not put "
                                                            "anything after list_schedules, it will show you schedules "
                                                            "for your user by default."}
    schedule = {"func": create_schedule_view, "doc": "`schedule` \n>Schedule your Redash view URL. Usage - `<bot> "
                                                     "schedule <URL>`"}
    image = {"func": get_redash_image, "doc": "`image` \n>Get the Redash image for a particular view URL. Usage - "
                                              "`<bot> image "
                                              "<URL>`"}
    help = {"func": help, "doc": f"*List of available commands* -"
                                 f" \n - {list_schedules['doc']}"
                                 f" \n - {schedule['doc']}"
                                 f" \n - {image['doc']}"}
