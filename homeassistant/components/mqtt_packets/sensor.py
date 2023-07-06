"""Sensor platform for MQTT Packets integration."""
from __future__ import annotations

import json

import paho.mqtt.client as mqtt

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize MQTT Packets config entry."""
    registry = er.async_get(hass)
    # Validate + resolve entity registry id to entity_id
    entity_id = er.async_validate_entity_id(
        registry, config_entry.options[CONF_ENTITY_ID]
    )
    name = config_entry.data["name"]
    topic = config_entry.data["topic"]
    unique_id = f"{name}_{entity_id}"

    async_add_entities([mqtt_packetsSensorEntity(unique_id, name, entity_id, topic)])


data = []
data_index = 0


def on_message(client, userdata, message):
    global data
    data = message.payload.decode("utf-8")
    data = json.loads(data)


class mqtt_packetsSensorEntity(SensorEntity):
    """mqtt_packets Sensor."""

    def __init__(
        self, unique_id: str, name: str, wrapped_entity_id: str, topic: str
    ) -> None:
        """Initialize mqtt_packets Sensor."""
        super().__init__()
        self._wrapped_entity_id = wrapped_entity_id
        self._attr_name = name
        self._attr_unique_id = unique_id

        # Connect to MQTT broker
        self._mqtt_client = mqtt.Client()
        self._mqtt_client.username_pw_set("mosquitto", "ILoveSensors")
        self._mqtt_client.on_message = on_message
        self._mqtt_client.connect("homeassistant.factory.uga.edu")

        # Subscribe to topic
        self._mqtt_client.subscribe(topic)

    def update(self) -> None:
        """Update the sensor."""
        self._mqtt_client.loop_start()
        global data, data_index
        self._attr_native_value = data[data_index] if data_index < len(data) else None
        data_index += 1
        self._mqtt_client.loop_stop()
