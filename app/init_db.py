from app.models.db_slackbot_schedule_metadata import SlackbotScheduleMetadata
from app.utils.database import engine, Base

table_objects = [SlackbotScheduleMetadata.__table__]
Base.metadata.create_all(engine, tables=table_objects)
