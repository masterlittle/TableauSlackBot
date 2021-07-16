from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler

from app.controller.tableau.tableau_commands import TableauCommands
from app.config import Settings
from app.controller.tableau.handle_tableau_commands_controller import get_scheduled_tableau_image
from app.controller.slack_scheduler_controller import action_submit_remove_scheduled_report, action_view_edit_schedule, \
    action_submit_edit_scheduled_report, action_submit_schedule_report

app = AsyncApp()
app_handler = AsyncSlackRequestHandler(app)
bot_name = Settings().BOT_NAME


@app.action("select_channels")
async def handle_some_action(ack, body, logger):
    await ack()


@app.action("select_schedule")
async def handle_some_action(ack, body, logger):
    await ack()
    logger.info(body)


@app.action("action_delete_schedule")
async def delete_schedule(ack, body, logger):
    await ack()
    await action_submit_remove_scheduled_report(app, body)


@app.action("action_edit_schedule")
async def edit_scheduled(ack, body, logger):
    await ack()
    await action_view_edit_schedule(app, body)


@app.view("view_create_schedule")
async def handle_create_schedule_view_events(ack, body, logger):
    await ack()
    await action_submit_schedule_report(body, get_scheduled_tableau_image)


@app.view("view_edit_schedule")
async def handle_edit_schedule_view_events(ack, body, logger):
    await ack()
    await action_submit_edit_scheduled_report(body)


@app.command(f"/{bot_name}-tableau")
async def handle_tableau_slash_commands(ack, say, body):
    await ack()
    if 'text' in body:
        params = body['text'].split(' ')
        if len(params) > 0:
            subcommand = str.strip(params[0])

            if subcommand == TableauCommands.image.name:
                if len(params) > 1:
                    url = str.strip(params[1])
                    await TableauCommands.image.value["func"](app, body, say, url)
                else:
                    await say(TableauCommands.image.value["doc"])

            elif subcommand == TableauCommands.schedule.name:
                if len(params) > 1:
                    url = str.strip(params[1])
                    await TableauCommands.schedule.value["func"](app, body, say, url)
                else:
                    await say(TableauCommands.schedule.value["doc"])

            elif subcommand == TableauCommands.list.name:
                await say(TableauCommands.list.value["doc"])

            elif subcommand == TableauCommands.list_schedules.name:
                filter_schedule_by = 'user'
                if len(params) > 1:
                    filter_schedule_by = str.strip(params[1])
                if filter_schedule_by not in ['user', 'channel']:
                    await say(f"*Error in command* \n {TableauCommands.list_schedules.value['doc']}")
                else:
                    await TableauCommands.list_schedules.value['func'](app, body, filter_schedule_by)
            else:
                await say(f"Command *{subcommand}* not supported.")
        else:
            await say(f"Check your command *{body['text']}* and try again. Use /{bot_name}-tableau list to see all "
                      f"available commands.")
    else:
        await say(f"Empty text in command is not yet supported. Use `/{bot_name}-tableau list` to see all "
                  f"available commands.")
