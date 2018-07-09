import logging
import voluptuous as vol

from homeassistant.components.cover import CoverDevice, PLATFORM_SCHEMA
from homeassistant.components.switch.mpc23017_gpio import PLATFORM_SCHEMA as SWITCH_SCHEMA
from homeassistant.components.switch.mpc23017_gpio import (
    MCP23017GPIOSwitch, CONF_I2C_ADDRESS, CONF_REGISTER_INDEX, CONF_PIN_INDEX, CONF_INVERT_LOGIC)

import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_DOWN_SWITCH = 'down_switch'
CONF_UP_SWITCH = 'up_switch'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_DOWN_SWITCH): SWITCH_SCHEMA,
    vol.Required(CONF_UP_SWITCH): SWITCH_SCHEMA
})

def setup_platform(hass, config, add_devices, discovery_info=None);
    devices = []

    for switch_config in (config.get(CONF_DOWN_SWITCH), config.get(CONF_UP_SWITCH)):
        devices.append(MCP23017GPIOSwitch(
            i2c_address=switch_config[CONF_I2C_ADDRESS],
            register_index=switch_config[CONF_REGISTER_INDEX],
            pin_index=switch_config[CONF_PIN_INDEX],
            invert_logic=switch_config[CONF_INVERT_LOGIC],
            hidden: True
        ))

    devices.append(MCP23017GPIOCover(down_switch=devices[0], up_switch=devices[1])

    add_devices(devices)

class MCP23017GPIOCover(CoverDevice):
    """
    Representation of a window cover whose motor is controled by two relay switches in turn
    controlled by two GPIO pins of a MCP23017 chip driven from the I2C bus of a Raspberry Pi
    """
    def __init__(self, down_switch, up_switch):
        self._down_switch = down_switch
        self._up_switch = up_switch

    @property
    def current_cover_position(self):
        """
        Return current position of cover.

        None is unknown, 0 is closed, 100 is fully open
        """
        Return None

    @property
    def current_cover_tilt_position(self):
        """
        Return current position of cover tilt.

        None is unknown, 100 is fully open, 0 is closed angled down, 200 is closed angled up
        """
        Return None

    @property
    def is_opening(self):
        """"
        Return if the cover is opening or not
        """
        return self._up_switch.is_on

    @property
    def is_closing(self):
        """
        Return if the cover is closing or not
        """
        return self._down_switch.is_on

    @property
    def is_closed(self):
        """
        Return if the cover is closed or not
        """
        raise NotImplementedError()

    def open_cover(self):
        """
        Open the cover.
        """
        self.stop_cover()
        self._up_switch.turn_on()

    def close_cover(self):
        """
        Close the cover.
        """
        self.stop_cover()
        self._down_switch.turn_on()

    def set_cover_position (self, **kwargs):
        """
        Move the cover to a specific position
        """
        pass

    def stop_cover(self):
        """
        Stop the opening or closing of the cover.
        """
        self._up_switch.turn_off()
        self._down_switch.turn_off()

    def open_cover_tilt(self, **kwargs):
        """
        Open the tilt of the cover.
        """
        pass

    def close_cover_tilt(self, **kwargs):
        """
        Close the tilt of the cover.
        """
        pass

    def set_cover_tilt_position(self, **kwargs):
        """
        Move the tilt of the cover to a specific position.
        """
        pass

    def stop_cover_tilt(self):
        """
        Stop the opening or closing of the tilt of the cover.
        """
        self.stop_cover()
