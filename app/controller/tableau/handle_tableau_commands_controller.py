# Created by shitij at 08/07/21
# Description -
import asyncio
import contextlib
import logging
import os
from typing import List

import aiohttp.client_exceptions
from slack_bolt.app.async_app import AsyncApp
from slack_sdk.errors import SlackApiError

from app.controller.slack_scheduler_controller import _get_list_of_records_from_db
from app.slack_views.create_schedule_view import get_create_schedule_view
from app.slack_views.list_schedule_view import get_list_schedule_view, get_list_schedule_view_header
from app.controller.tableau.tableau import get_view_image, download_view_crosstab
from app.commons.backend_list import Backends
from app.utils.log_exceptions import log_exception, log_error


async def help(app, body, say, text):
    await app.client.chat_postEphemeral(text=text, channel=body['channel_id'],
                                        user=body['user_id'])


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


async def get_tableau_image(app, body, say, text):
    try:
        await say("Loading image...")
        filename = await get_view_image(text)
        if filename:
            await app.client.files_upload(file=filename, channels=body['channel_id'], title=text)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.remove(filename)


async def download_tableau_view(app, body, say, text):
    try:
        await say("Downloading data. Please hold on...")
        filename = await download_view_crosstab(text)
        if filename:
            await app.client.files_upload(file=filename, channels=body['channel_id'], title=text)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.remove(filename)


async def get_scheduled_tableau_image(body, text, channel_list: List):
    app = AsyncApp()
    try:
        filename = await get_view_image(text)
        for channel in channel_list:
            await app.client.chat_postMessage(text=f"Scheduled report for {text} incoming", channel=channel)
            if filename:
                await app.client.files_upload(file=filename, channels=channel, filename=filename, title=text)
        os.remove(filename)
    except aiohttp.client_exceptions.InvalidURL as ie:
        log_error(ie, context=body)
        for channel in channel_list:
            await app.client.chat_postMessage(text=str(ie), channel=channel)
    except ValueError as ve:
        log_error(ve, context=body)
        for channel in channel_list:
            await app.client.chat_postMessage(text=str(ve), channel=channel)
    except aiohttp.client_exceptions.ClientResponseError as errh:
        log_exception(errh, context=body)
        for channel in channel_list:
            await app.client.chat_postMessage(text=f"An error occurred with code {errh.status}."
                                                   f" Check your url/view or try again later.", channel=channel)
    except aiohttp.client_exceptions.ClientConnectionError as errc:
        log_exception(errc, context=body)
        for channel in channel_list:
            await app.client.chat_postMessage(text=f"Error Connecting to specified url", channel=channel)
    except aiohttp.client_exceptions.ServerTimeoutError as errt:
        log_exception(errt, context=body)
        for channel in channel_list:
            await app.client.chat_postMessage(text=f"{str(errt)}", channel=channel)
    except SlackApiError as sae:
        log_error(sae, context=body)
        for channel in channel_list:
            await app.client.chat_postMessage(text=f"Error in Slack api - {str(sae.response)}", channel=channel)
    except Exception as e:
        log_exception(e, context=body)
        for channel in channel_list:
            await app.client.chat_postMessage(text=f"An error occurred while scheduling {text}. Error - *{str(e)}*",
                                              channel=channel)


async def create_schedule_view(app: AsyncApp, body, say, text):
    await app.client.views_open(
        # Pass a valid trigger_id within 3 seconds of receiving it
        trigger_id=body["trigger_id"],
        # View payload
        view=get_create_schedule_view(text, Backends.tableau.value))


async def list_schedule_reports(app: AsyncApp, body, filter_list_by: str):
    result, header_text = await _get_list_of_records_from_db(body, filter_list_by)
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
