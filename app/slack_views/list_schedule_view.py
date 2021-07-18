# Created by shitij at 14/07/21
# Description -

def get_list_schedule_view_header(text):
    return {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f"Listing schedules for {text}"
        }
    }


def get_list_schedule_view(row, index):
    schedule_view = [
        {
            "type": "section",
            "block_id": f"section_list_schedule_{index+1}",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"{index + 1}. ⭐ \t{row.scheduled_entity_text}"
                }
            ]
        },
        {
            "type": "section",
            "block_id": f"section_scheduletime_{index+1}",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Schedule Time*\n{row.schedule_name} at {row.schedule_time}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Channel List*\n{row.target_channels}"
                }
            ]
        },
        {
            "type": "actions",
            "block_id": f"block_change_schedule_{index+1}",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Edit"
                    },
                    "style": "primary",
                    "value": f"{row.job_id}",
                    "action_id": "action_edit_schedule"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Delete"
                    },
                    "style": "danger",
                    "value": f"{row.job_id}",
                    "action_id": "action_delete_schedule"
                }
            ]
        }
    ]
    return schedule_view

