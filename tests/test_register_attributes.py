"""Every register sensor names the controller register it reads from."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
import pytest

from .conftest import Controller
from .test_init import setup_entry

pytestmark = pytest.mark.usefixtures("enable_custom_integrations")


def _register(hass: HomeAssistant, entity_id: str) -> str | None:
    state = hass.states.get(entity_id)
    assert state is not None, entity_id
    return state.attributes.get("modbus_register")


async def test_a_register_sensor_names_its_register(
    hass: HomeAssistant, controller: Controller
) -> None:
    """A single register reads as its address; the boiler's high temperature is 2002."""
    await setup_entry(hass, controller, legacy=True)

    assert _register(hass, "sensor.eu08l_boil1_actual_high_temperature") == "2002"


async def test_a_32_bit_value_names_both_registers(
    hass: HomeAssistant, controller: Controller
) -> None:
    """The compressor's 32-bit energy counter spans two registers, 1020 and 1021."""
    await setup_entry(hass, controller, legacy=True)

    assert (
        _register(hass, "sensor.eu08l_hp1_compressor_power_consumption_accumulated")
        == "1020-1021"
    )
