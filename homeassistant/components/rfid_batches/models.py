"""Database Models for the RFID Batch component."""

from enum import Enum

import funkybob
from sqlalchemy import Enum as SQLEnum, Float, ForeignKey, Integer, String, event
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.db_schema import Base as BASE
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_CARD_TYPE_BATCH,
    CONF_CARD_TYPE_EQUIPMENT,
    CONF_CARD_TYPE_TAG,
    DOMAIN,
)


def _get_session(hass: HomeAssistant) -> Session:
    """Get the recorder database session."""
    return get_instance(hass).get_session()


class BatchData(BASE):
    """Batch Data Model."""

    __tablename__ = f"{DOMAIN}_batch_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    active_step: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=True)

    # Unique and nullable Foreign Key for 1-to-1 relationship
    active_tag_id: Mapped[int] = mapped_column(ForeignKey(f"{DOMAIN}_active_tags.id"), unique=True, nullable=True)

    # 1-to-1 relationship: use uselist=False
    active_tag: Mapped["ActiveTags"] = relationship("ActiveTags", back_populates="linked_batch", uselist=False)

    def __repr__(self):
        """Return the string representation of the batch data."""
        return f"<BatchData {self.batch_id} {self.active_step} {self.value} {self.active_tag_id}>"

@event.listens_for(BatchData, "after_insert")
def assign_serial_name(mapper, connection, target):
    """Assign a serial name to the batch."""
    if target.batch_id is not None:
        return
    name_generator = funkybob.UniqueRandomNameGenerator(members=2, separator=" ")
    target.batch_id = name_generator


class TagTypes(Enum):
    """Enum for the different types of tags in the system."""

    TAG = CONF_CARD_TYPE_TAG
    EQUIPMENT = CONF_CARD_TYPE_EQUIPMENT
    BATCH = CONF_CARD_TYPE_BATCH


class ActiveTags(BASE):
    """Stores the status of tags in the system."""

    __tablename__ = f"{DOMAIN}_active_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tag_id: Mapped[str] = mapped_column(String, unique=True)
    tag_type: Mapped[TagTypes] = mapped_column(SQLEnum(TagTypes), nullable=False)

    # 1-to-1 relationship: use uselist=False
    linked_batch: Mapped["BatchData"] = relationship("BatchData", back_populates="active_tag", uselist=False)

    def __repr__(self):
        """Return the string representation of the active tag."""
        return f"<ActiveTags {self.tag_id} {self.linked_batch}>"


class TagCreationError(HomeAssistantError):
    """Exception raised for errors in the tag creation process."""

class BatchCreationError(HomeAssistantError):
    """Exception raised for errors in the batch creation process."""

class TagLinkError(HomeAssistantError):
    """Exception raised for errors in the tag linking process."""


async def async_tag_exists(hass: HomeAssistant, tag_id: str) -> bool:
    """Check if a tag exists in the database."""
    session = _get_session(hass)

    def _tag_exists() -> bool:
        return session.query(ActiveTags).filter(ActiveTags.tag_id == tag_id).first() is not None

    return await hass.async_add_executor_job(_tag_exists)

async def async_fetch_or_create_tag(hass: HomeAssistant, tag_id: str) -> ActiveTags:
    """Fetch or create a tag in the database."""
    session = _get_session(hass)

    def _fetch_or_create() -> ActiveTags:
        tag = session.query(ActiveTags).filter(ActiveTags.tag_id == tag_id).first()

        if tag is None:
            try:
                tag = ActiveTags(tag_id=tag_id)
                session.add(tag)
                session.commit()
            except Exception as e:
                session.rollback()
                raise TagCreationError(f"Error creating tag: {e}") from e
            finally:
                session.close()

        return tag

    return await hass.async_add_executor_job(_fetch_or_create)

async def async_create_batch(hass: HomeAssistant, batch_id: str, active_step: str, value: float) -> BatchData:
    """Create a new batch in the database."""
    session = _get_session(hass)

    def _create_batch() -> BatchData:
        try:
            batch = BatchData(batch_id=batch_id, active_step=active_step, value=value)
            session.add(batch)
            session.commit()
        except Exception as e:
            session.rollback()
            raise BatchCreationError(f"Error creating batch: {e}") from e
        finally:
            session.close()

        return batch
    return await hass.async_add_executor_job(_create_batch)

async def async_link_tag_to_batch(hass: HomeAssistant, tag_id: str, batch_id: str) -> BatchData:
    """Link a tag to a batch in the database."""
    session = _get_session(hass)

    def _link_tag_to_batch() -> BatchData:
        tag = session.query(ActiveTags).filter(ActiveTags.tag_id == tag_id).first()
        batch = session.query(BatchData).filter(BatchData.batch_id == batch_id).first()

        if tag is None:
            raise TagLinkError(f"Tag {tag_id} does not exist in the database.")
        if batch is None:
            raise TagLinkError(f"Batch {batch_id} does not exist in the database.")

        try:
            batch.active_tag = tag
            session.commit()
        except Exception as e:
            session.rollback()
            raise TagLinkError(f"Error linking tag to batch: {e}") from e
        finally:
            session.close()

        return batch

    return await hass.async_add_executor_job(_link_tag_to_batch)
