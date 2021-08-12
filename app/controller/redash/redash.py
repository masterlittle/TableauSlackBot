import json
import os
import re
import string

import aiohttp
from app.controller.capture_screenshot import get_url_screenshot
from app.config import Settings
import asyncio
from concurrent.futures.thread import ThreadPoolExecutor

config = Settings()

REDASH_SERVER_URL = config.REDASH_SERVER_URL
REDASH_API_KEY = config.REDASH_API_KEY
REDASH_WAIT_FOR_LOAD_TIME = config.REDASH_WAIT_FOR_LOAD_TIME

FILE_DIR = "/tmp"

auth_token = None

my_timeout = aiohttp.ClientTimeout(
    total=None,  # default value is 5 minutes, set to `None` for unlimited timeout
    sock_connect=10,  # How long to wait before an open socket allowed to connect
    sock_read=10  # How long to wait with no data being read before timing out
)

client_args = dict(
    trust_env=True,
    timeout=my_timeout
)

executor = ThreadPoolExecutor(10)


async def get_dashboard(dashboard_id: str):
    async with aiohttp.ClientSession(**client_args) as session:
        url = f"{REDASH_SERVER_URL}/api/dashboards/{dashboard_id}"
        async with session.get(url, headers={'Authorization': f"Key {REDASH_API_KEY}"}) as response:
            if response.status != 200:
                response.raise_for_status()
            result = await response.text()
            return json.loads(result)


async def get_query(query_id: str):
    async with aiohttp.ClientSession(**client_args) as session:
        url = f"{REDASH_SERVER_URL}/api/queries/{query_id}"
        async with session.get(url, headers={'Authorization': f"Key {REDASH_API_KEY}"}) as response:
            if response.status != 200:
                response.raise_for_status()
            result = await response.text()
            return json.loads(result)


async def get_view_image(view_url: str):
    query_pattern = f"{REDASH_SERVER_URL}/queries/([0-9]+)(?!.*#).*$"
    chart_pattern = f"{REDASH_SERVER_URL}/queries/([0-9]+).*#([0-9]+)$"
    dashboard_pattern = f"{REDASH_SERVER_URL}/dashboard/([^?/|>]+)"

    if bool(re.search(query_pattern, view_url)):
        return await _capture_default_table(query_pattern, view_url)
    elif bool(re.search(chart_pattern, view_url)):
        return await _capture_chart(chart_pattern, view_url)
    elif bool(re.search(dashboard_pattern, view_url)):
        return await _capture_dashboard(dashboard_pattern, view_url)
    else:
        raise ValueError(f"The URL pattern {view_url} is not supported")


async def _capture_dashboard(dashboard_pattern, view_url):
    dashboard_id = re.search(dashboard_pattern, view_url).group(1)
    dashboard = await get_dashboard(dashboard_id)
    if dashboard:
        file = f"{dashboard['slug']}-dashboard-{str(dashboard['id'])}"
        file = re.sub(r'[^\w\s]', '', file)
        filename = os.path.join(FILE_DIR, f"{file}.png")
        if 'public_url' in dashboard:
            await _async_capture_screenshot(dashboard['public_url'], filename)
            return filename
        else:
            raise Exception(f"The URL {view_url} needs to be made public")
    else:
        raise Exception(f"There was a problem getting the url {view_url}")


async def _capture_chart(chart_pattern, view_url):
    regex_result = re.search(chart_pattern, view_url)
    query_id = regex_result.group(1)
    visualization_id = regex_result.group(2)
    query_data = await get_query(query_id)
    if query_data:
        visualization = tuple(viz for viz in query_data['visualizations'] if str(viz['id']) == visualization_id)
        embed_url = f"{REDASH_SERVER_URL}/embed/query/{query_id}/visualization/{visualization_id}?api_key={REDASH_API_KEY}"
        file = f"{query_data['name']}-{visualization[0]['name']}-query-{query_id}-visualization-{visualization_id}"
        file = re.sub(r'[^\w\s]', '', file)
        filename = os.path.join(FILE_DIR, f"{file}.png")
        await _async_capture_screenshot(embed_url, filename)
        return filename
    else:
        raise Exception(f"There was a problem getting the url {view_url}")


async def _capture_default_table(query_pattern, view_url):
    query_id = re.search(query_pattern, view_url).group(1)
    query_data = await get_query(query_id)
    if query_data:
        visualization_id = query_data['visualizations'][0]['id']
        embed_url = f"{REDASH_SERVER_URL}/embed/query/{query_id}/visualization/{visualization_id}?api_key={REDASH_API_KEY}"
        file = f"{query_data['name']}-{visualization_id}-query-{query_id}-visualization-{visualization_id}"
        file = re.sub(r'[^\w\s]', '', f"{file}.png")
        filename = os.path.join(FILE_DIR, file)
        await _async_capture_screenshot(embed_url, filename)
        return filename
    else:
        raise Exception(f"There was a problem getting the url {view_url}")


async def _async_capture_screenshot(url, filename):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, get_url_screenshot, url, filename, REDASH_WAIT_FOR_LOAD_TIME)
