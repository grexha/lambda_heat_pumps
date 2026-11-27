"""Settings the cockpit's settings tab writes, kept in Home Assistant's storage.

The card reads and writes them through two websocket commands. They live in the
integration's storage, not in the dashboard, so a dashboard that is rewritten
(a layout change, or the service that regenerates it) does not lose them, and
they come back after a restart.

Keys:
- ``buffer_setpoint_sensor``: the sensor to take the buffer setpoint from, or
  nothing for the controller's own value.
- ``buffer_fallback``: whether a value worked out from the heating circuit may
  stand in when there is no value (off by default: a wrong value is worse than
  none).
- ``heating_type_<n>``: ``floor`` or ``radiator`` for heating circuit n.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.storage import Store

from .const import DOMAIN

STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.cockpit_settings"
BUFFER_SENSOR = "buffer_setpoint_sensor"
BUFFER_FALLBACK = "buffer_fallback"
HEATING_TYPE_PREFIX = "heating_type_"
HEATING_TYPES = ("floor", "radiator")

_REGISTERED = f"{DOMAIN}_cockpit_settings_registered"
_STORE = f"{DOMAIN}_cockpit_settings_store"


def _store(hass: HomeAssistant) -> Store[dict[str, Any]]:
    """The one store for all controllers' cockpit settings."""
    if _STORE not in hass.data:
        hass.data[_STORE] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    return hass.data[_STORE]


async def async_load(hass: HomeAssistant) -> dict[str, Any]:
    """The settings as stored, with the defaults filled in."""
    stored = await _store(hass).async_load() or {}
    return {BUFFER_SENSOR: None, BUFFER_FALLBACK: False} | stored


def _check(key: str, value: Any) -> Any:
    """The value for a key, or ValueError if the key or value is not allowed."""
    if key == BUFFER_SENSOR:
        if value is None or value == "":
            return None
        if not isinstance(value, str) or not value.startswith("sensor."):
            raise ValueError("buffer_setpoint_sensor must be a sensor entity")
        return value
    if key == BUFFER_FALLBACK:
        if not isinstance(value, bool):
            raise ValueError("buffer_fallback must be true or false")
        return value
    if key.startswith(HEATING_TYPE_PREFIX) and key[len(HEATING_TYPE_PREFIX) :].isdigit():
        if value not in HEATING_TYPES:
            raise ValueError(f"{key} must be one of {', '.join(HEATING_TYPES)}")
        return value
    raise ValueError(f"unknown cockpit setting {key!r}")


async def async_set(hass: HomeAssistant, key: str, value: Any) -> dict[str, Any]:
    """Store one setting and return all of them."""
    value = _check(key, value)
    data = await async_load(hass)
    data[key] = value
    await _store(hass).async_save(data)
    return data


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/cockpit_settings"})
@websocket_api.async_response
async def _ws_get(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    connection.send_result(msg["id"], await async_load(hass))


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/cockpit_settings/set",
        vol.Required("key"): str,
        vol.Required("value"): vol.Any(str, bool, None),
    }
)
@websocket_api.async_response
async def _ws_set(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    try:
        data = await async_set(hass, msg["key"], msg["value"])
    except ValueError as err:
        connection.send_error(msg["id"], "invalid_setting", str(err))
        return
    connection.send_result(msg["id"], data)


@callback
def async_register_commands(hass: HomeAssistant) -> None:
    """Register the two commands once, however many controllers are set up."""
    if hass.data.get(_REGISTERED):
        return
    websocket_api.async_register_command(hass, _ws_get)
    websocket_api.async_register_command(hass, _ws_set)
    hass.data[_REGISTERED] = True
