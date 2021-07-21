# Vizack

Vizack aims to bring the power of data tools (primarily visualisation tools) to Slack to streamline the process of using data and gaining insights straight from a single source
, without moving through systems. This also opens up new avenues to chain workflows by leveraging
the power of Slack API for a lot of other usecases.

## Current backend tools and features supported
- **Tableau**
  - Get an image of a view into a Slack channel.
  - Download crosstab data for a view into a slack channel.
  - Schedule a view to be sent to multiple channels at various frequencies.
  - List the schedules that have been set up and filter by your user or channel.  
- **Redash**
    - Get an image of a view into a Slack channel.
    - Schedule a view to be sent to multiple channels at various frequencies.
    - List the schedules that have been set up and filter by your user or channel.
    - All queries/charts/dashboards supported, even with parameters in their URL.
    
## How to install 
 - Visit https://api.slack.com/apps and create a new app using the `app.manifest` file included in this
   repository as a sample file. You need to give your bot name, and the URL of the webhook service
   which we will be setting up.
 - Install poetry package manager using ```pip3 install poetry```
 - Install python dependencies (ideally within a virtual environment) ```poetry install```  
 - Edit your .env file and fill in the requisite variables. A sample .env file has been provided 
   in the repository. All optional and required variables have been marked and can be found in config.py with the config 
   file having some sane defaults where applicable.
   

 - **The bot name in the Slack app manifest, and the bot name in your .env file should match**
 - **Similarly, the backend url in the Slack app manifest, and the url for the backend deployment should match. 
   For local deployments consider using ngrok to create a public url.**
   

 - Run the command ```uvicorn app.main:app --reload```  

## How to use
 - Install your bot in the Slack workspace.
 - Add the bot to the channel of your choice, either private or public. Use the command `@botname`
 - Use command `/<bot-name>-tableau help` or `/<bot-name>-redash help` to see all the commands and how to use them.
   - eg: `/bot-tableau image https://tableau.server.com/#/views/workbook/view?:iid=1`
    
## Tips and things to remember
 
 - Tableau:
   - The image and download options cache the files for 15 minutes, to prevent heavy processing load on the servers .
    Downloads will timeout after 30 seconds for the same reason.
   - Authentication to Tableau needs a personal access token. Direct username/password are not supported.
   - The timings for schedules are in UTC.
 - Redash:
   - The image download happens after some time which is configurable using REDASH_WAIT_FOR_LOAD_TIME env variable.
     This is to wait for the dashboard to refresh/load.
   - To get an image of a dashboard, you need to make it *public*. Please verify this as it may be a security risk.
    
## Technologies/Libraries used
  - FastApi
  - Bolt for Python
  - Selenium python
  - Asyncio
  - aiohttp

## Disclaimer
For all backend tools, please verify within your org if needed, about privacy, security and licensing concerns beforehand.


