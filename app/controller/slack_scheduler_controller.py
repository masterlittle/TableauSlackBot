import datetime
import json
import logging

from slack_bolt.app.async_app import AsyncApp

from app.models.db_slackbot_schedule_metadata import SlackbotScheduleMetadata
from app.controller.scheduler import remove_schedule_from_scheduler, add_schedule_from_scheduler, \
    edit_schedule_from_scheduler
from app.slack_views.edit_schedule_view import get_edit_schedule_view
from app.utils.database import session_scope


def get_schedules(hour, minute):
    return {
        'HOURLY': f'{minute} */1 * * * ',
        'DAILY': f'{minute} {hour} * * *',
        'WEEKLY-MONDAY': f'{minute} {hour} * * MON',
        'WEEKLY-WEDNESDAY': f'{minute} {hour} * * WED'
    }


async def _remove_schedule_fromdb(job_id):
    remove_schedule_from_scheduler(job_id)
    with session_scope() as session:
        job = session.query(SlackbotScheduleMetadata).filter(SlackbotScheduleMetadata.job_id == job_id)
        job.delete(synchronize_session=False)
        session.commit()


async def _get_scheduled_parameters(body):
    entity_url = None
    channel_names = []
    for block in body['view']['blocks']:
        if block['block_id'] == 'url':
            entity_url = block['text']['text']
    channels = body['view']['state']['values']['channels']['select_channels']['selected_conversations']
    time = body['view']['state']['values']['time']['accessory_time']['selected_time']
    frequency = body['view']['state']['values']['schedule']['select_schedule']['selected_option']['value']
    hour = time.split(':')[0]
    minute = time.split(':')[1]
    last_changed_by = body['user']['username']
    cron_schedule = get_schedules(hour, minute).get(frequency)
    if not entity_url:
        raise ValueError("URL not found")
    app = AsyncApp()
    for channel in channels:
        channel_info = await app.client.conversations_info(channel=channel)
        channel_names.append(channel_info['channel']['name'])
    return channel_names, channels, cron_schedule, entity_url, frequency, last_changed_by, time


async def _get_list_of_records_from_db(body, filter_list_by):
    with session_scope() as session:
        if filter_list_by == 'user':
            result = session.query(SlackbotScheduleMetadata).filter(
                SlackbotScheduleMetadata.owner == body['user_name']).all()
            header_text = body['user_name']
        elif filter_list_by == 'channel':
            result = session.query(SlackbotScheduleMetadata).filter(
                SlackbotScheduleMetadata.target_channels.any(f"{body['channel_name']}")).all()
            header_text = body['channel_name']
        else:
            return
    return result, header_text


async def action_submit_schedule_report(body, scheduled_func):
    channel_names, channels, cron_schedule, entity_url, frequency, last_changed_by, time = await _get_scheduled_parameters(
        body)

    job = add_schedule_from_scheduler(scheduled_func, [body, entity_url, channels], cron_schedule)
    with session_scope() as session:
        new_schedule_job = SlackbotScheduleMetadata(updated_at=datetime.datetime.now(),
                                                    job_id=job.id,
                                                    owner=last_changed_by,
                                                    last_changed_by=last_changed_by,
                                                    scheduled_entity_custom_name='',
                                                    scheduled_entity_text=entity_url,
                                                    cron_expression=cron_schedule,
                                                    target_channels=channel_names,
                                                    target_channels_id=channels,
                                                    backend_tool='tableau',
                                                    schedule_name=frequency,
                                                    schedule_time=time)
        session.add(new_schedule_job)
        session.commit()
        logging.info(f"New schedule added for {entity_url} created by {last_changed_by} at {datetime.datetime.now()}")


async def action_view_edit_schedule(app, body):
    with session_scope() as session:
        job_info = session.query(SlackbotScheduleMetadata).filter(
            SlackbotScheduleMetadata.job_id == body['actions'][0]['value']).all()

    if job_info:
        await app.client.views_open(
            # Pass a valid trigger_id within 3 seconds of receiving it
            trigger_id=body["trigger_id"],
            # View payload
            view=get_edit_schedule_view(job_info[0]))
    else:
        print(body)
        await app.client.chat_postEphemeral(text=f"Job has already been removed.", user=body['user']['id'],
                                      channel=body['container']['channel_id'])


async def action_submit_edit_scheduled_report(body):
    job_id = json.loads(body['view']['private_metadata'])['job_id']
    channel_names, channels, cron_schedule, entity_url, frequency, last_changed_by, time = await _get_scheduled_parameters(
        body)
    edited_job = edit_schedule_from_scheduler([body, entity_url, channels], cron_schedule, job_id=job_id)
    if edited_job:
        with session_scope() as session:
            job = session.query(SlackbotScheduleMetadata).filter(SlackbotScheduleMetadata.job_id == job_id).first()

            job.job_id = edited_job.id
            job.target_channels_id = channels
            job.target_channels = channel_names
            job.updated_at = datetime.datetime.now(),
            job.last_changed_by = last_changed_by,
            job.scheduled_entity_text = entity_url,
            job.cron_expression = cron_schedule,
            job.backend_tool = 'tableau',
            job.schedule_name = frequency,
            job.schedule_time = time

            session.commit()
            logging.info(f"Schedule edited for {entity_url} created by {last_changed_by} at {datetime.datetime.now()}")


async def action_submit_remove_scheduled_report(app, body):
    job_id = body['actions'][0]['value']
    await _remove_schedule_fromdb(job_id)
    await app.client.chat_postEphemeral(channel=body['channel']['name'], user=body['user']['id'],
                                        text="Job deleted successfully!")
