
import aiohttp
import aiohttp.client_exceptions
from app.controller.redash.handle_redash_commands_controller import *
from app.controller.slack_scheduler_controller import _get_list_of_records_from_db
from app.controller.tableau.handle_tableau_commands_controller import *
from app.slack_views.list_schedule_view import get_list_schedule_view, get_list_schedule_view_header
from app.utils.log_exceptions import log_error, log_exception


async def handle_instant_command(func, app, body, say, text):
    try:
        await func(app, body, say, text)
    except aiohttp.client_exceptions.InvalidURL as ie:
        log_error(ie, context=body)
        await say(f"Invalid URL - {str(ie)}")
    except ValueError as ve:
        log_error(ve, context=body)
        await say(f"Error - {str(ve)}")
    except aiohttp.client_exceptions.ClientResponseError as errh:
        log_exception(errh, context=body)
        await say(f"An error occurred with code {errh.status}. Check your url/view or try again later.")
    except aiohttp.client_exceptions.ClientConnectionError as errc:
        log_exception(errc, context=body)
        await say(f"Error Connecting to specified url")
    except asyncio.exceptions.TimeoutError as terrt:
        log_exception(terrt, context=body)
        await say(f"Request to the specified URL timed out.")
    except aiohttp.client_exceptions.ServerTimeoutError as errt:
        log_exception(errt, context=body)
        await say(f"{str(errt)}")
    except SlackApiError as sae:
        log_error(sae, context=body)
        await say(f"Error in Slack api - {str(sae.response)}")
    except Exception as e:
        log_exception(e, context=body)
        await say(f"An error occurred while getting {text}. Error - *{str(e)}*")


async def list_schedule_reports(app: AsyncApp, body, filter_list_by: str, backend_tool: str):
    result, header_text = await _get_list_of_records_from_db(body, filter_list_by, backend_tool)
    if len(result) < 1:  # For empty result
        await app.client.chat_postEphemeral(channel=body['channel_name'], user=body['user_id'],
                                            text="*No scheduled jobs found*")
    else:
        list_schedules_view = []
        for i, row in enumerate(result):
            list_schedules_view.extend(get_list_schedule_view(row, i))
        list_schedules_view.insert(0, get_list_schedule_view_header(header_text))
        await app.client.chat_postEphemeral(channel=body['channel_name'], user=body['user_id'],
                                            blocks=list_schedules_view)