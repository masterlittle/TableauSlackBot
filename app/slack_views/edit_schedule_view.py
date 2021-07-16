# Created by shitij at 14/07/21
# Description -
from app.models.db_slackbot_schedule_metadata import SlackbotScheduleMetadata


def get_edit_schedule_view(job_info: SlackbotScheduleMetadata):
    schedule_view = {
        "type": "modal",
        # View identifier
        "callback_id": "view_edit_schedule",
        "title": {"type": "plain_text", "text": "Edit Dashboard"},
        "submit": {"type": "plain_text", "text": "Submit"},
        "private_metadata": job_info.job_id,
        "blocks": [
            {
                "type": "section",
                "block_id": "url",
                "text": {"type": "mrkdwn", "text": f"{job_info.scheduled_entity_text}", "verbatim": True},
            },
            {
                "block_id": "channels",
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Pick conversations from the list"
                },
                "accessory": {
                    "action_id": "select_channels",
                    "type": "multi_conversations_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select conversations"
                    },
                    "filter": {
                        "include": ["private", "public"],
                        "exclude_bot_users": True,
                        "exclude_external_shared_channels": True
                    },
                    "max_selected_items": 10,
                    "initial_conversations": job_info.target_channels_id
                },
            },
            {
                "type": "section",
                "block_id": "time",
                "text": {
                    "type": "mrkdwn",
                    "text": "Pick a time. *[UTC]*"
                },
                "accessory": {
                    "type": "timepicker",
                    "action_id": "accessory_time",
                    "initial_time": f"{job_info.schedule_time}",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a time"
                    }
                }
            },
            {
                "type": "section",
                "block_id": "schedule",
                "text": {
                    "type": "mrkdwn",
                    "text": "Schedule Frequency"
                },
                "accessory": {
                    "type": "static_select",
                    "initial_option": {
                        "text": {
                            "type": "plain_text",
                            "text": f"{job_info.schedule_name}"
                        },
                        "value": f"{job_info.schedule_name}"
                    },
                    "placeholder": {
                        "type": "plain_text",
                        "text": "What is the schedule frequency?"
                    },
                    "action_id": "select_schedule",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "HOURLY"
                            },
                            "value": "HOURLY"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "EVERY-MINUTE"
                            },
                            "value": "EVERY-MINUTE"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "DAILY"
                            },
                            "value": "DAILY"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "WEEKLY-MONDAY"
                            },
                            "value": "WEEKLY-MONDAY"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "WEEKLY-WEDNESDAY"
                            },
                            "value": "WEEKLY-WEDNESDAY"
                        }
                    ]
                }
            }
        ]
    }
    return schedule_view
