import datetime
import os
import re

import aiohttp
import xmltodict

from app.config import Settings

config = Settings()

TABLEAU_SERVER_URL = config.TABLEAU_SERVER_URL
TABLEAU_PERSONAL_ACCESS_TOKEN_NAME = config.TABLEAU_PERSONAL_ACCESS_TOKEN_NAME
TABLEAU_PERSONAL_ACCESS_TOKEN_SECRET = config.TABLEAU_PERSONAL_ACCESS_TOKEN_SECRET
TABLEAU_CONTENT_URL = config.TABLEAU_CONTENT_URL
TABLEAU_SERVER_API_VERSION = config.TABLEAU_SERVER_API_VERSION
TABLEAU_SERVER_IMAGE_API_TIMEOUT = config.TABLEAU_SERVER_IMAGE_API_TIMEOUT

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


async def get_tableau_auth_token(session):
    url = f"{TABLEAU_SERVER_URL}/api/{TABLEAU_SERVER_API_VERSION}/auth/signin"
    auth_data = f"""
    <tsRequest>
        <credentials personalAccessTokenName="{TABLEAU_PERSONAL_ACCESS_TOKEN_NAME}"
                 personalAccessTokenSecret="{TABLEAU_PERSONAL_ACCESS_TOKEN_SECRET}">
        <site contentUrl="{TABLEAU_CONTENT_URL}" />
        </credentials>
   </tsRequest>"""

    async with session.post(url, data=auth_data, timeout=TABLEAU_SERVER_IMAGE_API_TIMEOUT) as response:
        if response.status != 200:
            response.raise_for_status()
        res = xmltodict.parse(await response.text())
        auth_token = res['tsResponse']['credentials']['@token']
        site_id = res['tsResponse']['credentials']['site']['@id']
        return auth_token, site_id


async def get_view_info(session, auth_token, site_id, view_name: str, workbook_name: str):
    url = f"{TABLEAU_SERVER_URL}/api/{TABLEAU_SERVER_API_VERSION}/sites/{site_id}/views?filter=viewUrlName:eq:{view_name}"
    async with session.get(url, headers={'X-Tableau-Auth': auth_token}, timeout=TABLEAU_SERVER_IMAGE_API_TIMEOUT) as response:
        if response.status != 200:
            response.raise_for_status()
        view_dict = xmltodict.parse(await response.text())
        if not view_dict['tsResponse']['views']:
            raise Exception(f"The specified view {view_name} could not be found")
        if isinstance(view_dict['tsResponse']['views']['view'], list):
            # To check for multiple views of same name across workbooks
            all_views = view_dict['tsResponse']['views']['view']
            for view in all_views:
                if workbook_name in view['@contentUrl']:
                    return view['@id']
        else:
            view_id = view_dict['tsResponse']['views']['view']['@id']
        return view_id


async def get_view_image(view_url: str):
    workbook_name, view_name = await get_view_name(view_url)
    if not view_name or not workbook_name:
        raise ValueError(f"Please check the URL {view_url} and try again.")
    else:
        async with aiohttp.ClientSession(**client_args) as session:
            auth_token, site_id = await get_tableau_auth_token(session)
            view_id = await get_view_info(session, auth_token, site_id, view_name, workbook_name)

            async with session.get(
                    f'{TABLEAU_SERVER_URL}/api/{TABLEAU_SERVER_API_VERSION}/sites/{site_id}/views/{view_id}/image?maxAge=15',
                    timeout=TABLEAU_SERVER_IMAGE_API_TIMEOUT,
                    headers={'X-Tableau-Auth': auth_token}) as response:
                if response.status != 200:
                    response.raise_for_status()
                filename = os.path.join(FILE_DIR, f'{view_name}.png')
                if response.content:
                    with open(filename, 'wb') as f:
                        f.write(await response.content.read())
                        return filename
                else:
                    raise Exception("Report could not be generated")


async def get_view_name(view_url: str):
    pattern = "^.*views/(.*)/(.*)\?.*$"
    a = re.search(pattern, view_url)
    if a:
        workbook_name = a.group(1)
        view_name = a.group(2)
        return workbook_name, view_name
    else:
        raise ValueError(f"Please check the URL {view_url} and try again.")
