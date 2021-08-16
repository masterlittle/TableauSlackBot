# Created by shitij at 08/07/21
# Description -
import asyncio
import contextlib
import os
from typing import List

import aiohttp.client_exceptions
from slack_bolt.app.async_app import AsyncApp
from slack_sdk.errors import SlackApiError

from app.slack_views.create_schedule_view import get_create_schedule_view
from app.controller.redash.redash import get_view_image
from app.commons.backend_list import Backends
from app.utils.log_exceptions import log_exception, log_error
from app.controller.chromedriver import driver


async def help(app, body, say, text):
    await app.client.chat_postEphemeral(text=text, channel=body['channel_id'],
                                        user=body['user_id'])


async def get_redash_image(app, body, say, text):
    filename = None
    try:
        await say("Loading image...")
        filename = await get_view_image(driver, text)
        if filename:
            await app.client.files_upload(file=filename, channels=body['channel_id'], title=text)
    finally:
        with contextlib.suppress(FileNotFoundError):
            if filename:
                os.remove(filename)


async def get_scheduled_redash_image(body, text, channel_list: List):
    app = AsyncApp()
    try:
        filename = await get_view_image(driver, text)
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
        view=get_create_schedule_view(text, Backends.redash.value))

