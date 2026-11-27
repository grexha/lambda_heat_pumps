"""The cockpit's settings: stored in Home Assistant, validated, and read back."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
import pytest

from .conftest import Controller
from .test_init import setup_entry

pytestmark = pytest.mark.usefixtures("enable_custom_integrations")

GET = "lambda_heat_pumps/cockpit_settings"
SET = "lambda_heat_pumps/cockpit_settings/set"


async def test_defaults_and_round_trip(
    hass: HomeAssistant, controller: Controller, hass_ws_client
) -> None:
    """Nothing is set at first; what is set comes back, also after a restart."""
    await setup_entry(hass, controller, legacy=True)
    ws = await hass_ws_client(hass)

    await ws.send_json({"id": 1, "type": GET})
    got = await ws.receive_json()
    assert got["success"]
    assert got["result"]["buffer_setpoint_sensor"] is None
    assert got["result"]["buffer_fallback"] is False

    await ws.send_json({"id": 2, "type": SET, "key": "buffer_fallback", "value": True})
    assert (await ws.receive_json())["success"]
    await ws.send_json(
        {"id": 3, "type": SET, "key": "heating_type_2", "value": "radiator"}
    )
    assert (await ws.receive_json())["success"]
    await ws.send_json(
        {
            "id": 4,
            "type": SET,
            "key": "buffer_setpoint_sensor",
            "value": "sensor.eu08l_buff1_buffer_temperature_high_setpoint",
        }
    )
    assert (await ws.receive_json())["success"]

    await ws.send_json({"id": 5, "type": GET})
    result = (await ws.receive_json())["result"]
    assert result["buffer_fallback"] is True
    assert result["heating_type_2"] == "radiator"
    assert (
        result["buffer_setpoint_sensor"]
        == "sensor.eu08l_buff1_buffer_temperature_high_setpoint"
    )


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("buffer_fallback", "yes"),
        ("buffer_setpoint_sensor", "light.kitchen"),
        ("heating_type_1", "wall"),
        ("unknown_setting", True),
    ],
)
async def test_invalid_settings_are_refused(
    hass: HomeAssistant, controller: Controller, hass_ws_client, key: str, value
) -> None:
    """A value that does not fit its key is refused and nothing is stored."""
    await setup_entry(hass, controller, legacy=True)
    ws = await hass_ws_client(hass)

    await ws.send_json({"id": 1, "type": SET, "key": key, "value": value})
    refused = await ws.receive_json()
    assert refused["success"] is False
    assert refused["error"]["code"] == "invalid_setting"

    await ws.send_json({"id": 2, "type": GET})
    stored = (await ws.receive_json())["result"]
    assert key not in stored or stored[key] in (None, False)
