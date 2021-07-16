from sqlalchemy import Column, Integer, String, DateTime, func, Text
from sqlalchemy.dialects.postgresql import ARRAY

from app.utils.database import Base


class SlackbotScheduleMetadata(Base):
    __tablename__ = "slackbot_schedule_metadata"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    job_id = Column(Text, unique=True)
    owner = Column(Text)
    last_changed_by = Column(Text)
    scheduled_entity_custom_name = Column(Text, nullable=True)
    scheduled_entity_text = Column(Text)
    cron_expression = Column(Text)
    target_channels = Column(ARRAY(Text))
    target_channels_id = Column(ARRAY(Text))
    backend_tool = Column(Text)  # eg - Tableau, Redash etc.
    schedule_name = Column(Text)
    schedule_time = Column(Text)

