"""Database Models for the RFID Batch component."""

from datetime import datetime
from enum import Enum

from sqlalchemy import Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.db_schema import Base as BASE
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_CARD_TYPE_BATCH,
    CONF_CARD_TYPE_EQUIPMENT,
    CONF_CARD_TYPE_NONE,
    CONF_CARD_TYPE_TAG,
    CONF_STEP_RECEIVE,
    DOMAIN,
)


def _get_session(hass: HomeAssistant) -> Session:
    """Get the recorder database session."""
    return get_instance(hass).get_session()


class BatchData(BASE):
    """Batch Data Model."""

    __tablename__ = f"{DOMAIN}_batch_data"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    batch_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    batch_creation: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)

    active_step: Mapped[str] = mapped_column(nullable=False, default=CONF_STEP_RECEIVE)

    parent_batch_id = mapped_column(ForeignKey(f"{DOMAIN}_batch_data.batch_id"), nullable=True)
    parent_batch: Mapped["BatchData"] = relationship("BatchData", remote_side=[batch_id], foreign_keys=[parent_batch_id])

    active_tag_id = mapped_column(ForeignKey(f"{DOMAIN}_active_tags.id"), unique=True, nullable=True)
    active_tag: Mapped["ActiveTags"] = relationship("ActiveTags", back_populates="linked_batch", uselist=False)

    def __repr__(self):
        """Return the string representation of the batch data."""
        return f"<BatchData {self.batch_id} {self.batch_creation} {self.active_step} {self.active_tag_id}>"


class TagTypes(Enum):
    """Enum for the different types of tags in the system."""

    TAG = CONF_CARD_TYPE_TAG
    EQUIPMENT = CONF_CARD_TYPE_EQUIPMENT
    BATCH = CONF_CARD_TYPE_BATCH
    NONE = CONF_CARD_TYPE_NONE


class ActiveTags(BASE):
    """Stores the status of tags in the system."""

    __tablename__ = f"{DOMAIN}_active_tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tag_id: Mapped[str] = mapped_column(unique=True)
    tag_type: Mapped[TagTypes] = mapped_column(SQLEnum(TagTypes), nullable=False, default=TagTypes.NONE)

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

        return tag

    return await hass.async_add_executor_job(_fetch_or_create)

async def async_create_batch(hass: HomeAssistant,
                             batch_id: str,
                             batch_creation: datetime = datetime.now(),
                             active_step: str = CONF_STEP_RECEIVE,
                             parent_batch_id: str | None = None) -> BatchData:
    """Create a new batch in the database."""
    session = _get_session(hass)

    def _create_batch() -> BatchData:
        try:
            batch = BatchData(batch_id=batch_id, batch_creation=batch_creation, active_step=active_step, parent_batch_id=parent_batch_id)
            session.add(batch)
            session.commit()
        except Exception as e:
            session.rollback()
            raise BatchCreationError(f"Error creating batch: {e}") from e

        session.refresh(batch)
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

        return batch

    return await hass.async_add_executor_job(_link_tag_to_batch)
