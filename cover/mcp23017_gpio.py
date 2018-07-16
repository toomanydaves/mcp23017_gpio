"""
## MCP23017 GPIO Cover Platform

To use this component, add the following to your configuration.yaml file:
```
  # Example configuration.yaml entry
  cover:
    - platform: mcp23017_gpio
      name: Bedroom Blinds
      down_pin:
        address: 0x20
        port: A
        pin: 0
        invert_logic: true
      up_pin:
        address: 0x24
        port: B
        pin: 7
```
Configuration Variables:
+ **address** (Required): The address of the MCP23017 with the pin on the Pi's I2C bus, 0x00-0xff
+ **port** (Required): The port (A or B) with the pin on the MCP23017.
+ **pin** (Required): The index of the pin on the port, 0-7.
+ **invert_logic** (Optional): If true, inverts the output logic to ACTIVE LOW. Default is false (ACTIVE HIGH).
+ **name** (Optional): Name to use in the frontend.
"""
import logging
import voluptuous as vol

from homeassistant.components.cover import CoverDevice, PLATFORM_SCHEMA
from custom_components.mcp23017_gpio import (
    config_pin_as_output, set_pin_output_state, get_pin_output_state,
    PIN_SCHEMA, CONF_ADDRESS, CONF_PORT, CONF_PIN)

import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_NAME

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['mcp23017_gpio']

CONF_DOWN_PIN = 'down_pin'
CONF_UP_PIN = 'up_pin'
CONF_INVERT_LOGIC = 'invert_logic'

PIN_SCHEMA = PIN_SCHEMA.extend({
    vol.Optional(CONF_INVERT_LOGIC, default=False):cv.boolean
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_DOWN_PIN): PIN_SCHEMA,
    vol.Required(CONF_UP_PIN): PIN_SCHEMA
    vol.Optional(CONF_NAME, default="MCP23017"): cv.string,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    add_devices(MCP23017GPIOCover(
        down_pin=config.get(CONF_DOWN_PIN),
        up_pin=config.get(CONF_UP_PIN),
        name=config.get(CONF_NAME)
    ))

class MCP23017GPIOCover(CoverDevice):
    """
    Representation of a window cover whose motor is controled by two relay switches in turn
    controlled by two GPIO pins of a MCP23017 chip driven from the I2C bus of a Raspberry Pi
    """
    def __init__(self, down_pin, up_pin, name):
        self._down_pin = down_pin
        self._up_pin = up_pin,
        self._name = name

    @property
    def current_cover_position(self):
        """
        Return current position of cover.

        None is unknown, 0 is closed, 100 is fully open
        """
        return None

    @property
    def current_cover_tilt_position(self):
        """
        Return current position of cover tilt.

        None is unknown, 100 is fully open, 0 is closed angled down, 200 is closed angled up
        """
        return None

    @property
    def is_opening(self):
        """"
        Return if the cover is opening or not
        """
        return self._determine_state(
            pin_state=get_pin_output_state(
                address=self._down_pin.get(CONF_ADDRESS),
                port=self._down_pin.get(CONF_PORT),
                pin_index=self._down_pin.get(CONF_PIN)
            ),
            invert_logic=self._down_pin.get(CONF_INVERT_LOGIC)
        )

    @property
    def is_closing(self):
        """
        Return if the cover is closing or not
        """
        return self._determine_state(
            pin_state=get_pin_output_state(
                address=self._up_pin.get(CONF_ADDRESS),
                port=self._up_pin.get(CONF_PORT),
                pin_index=self._up_pin.get(CONF_PIN)
            ),
            invert_logic=self._up_pin.get(CONF_INVERT_LOGIC)
        )

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
        set_pin_output_state(
            False if self._up_pin.get(CONF_INVERT_LOGIC) else True,
            self._up_pin.get(CONF_ADDRESS), 
            self._up_pin.get(PORT), 
            self._up_pin.get(PIN) 
        )

    def close_cover(self):
        """
        Close the cover.
        """
        self.stop_cover()
        set_pin_output_state(
            False if self._down_pin.get(CONF_INVERT_LOGIC) else True,
            self._down_pin.get(CONF_ADDRESS), 
            self._down_pin.get(PORT), 
            self._down_pin.get(PIN) 
        )

    def set_cover_position (self, **kwargs):
        """
        Move the cover to a specific position
        """
        pass

    def stop_cover(self):
        """
        Stop the opening and closing of the cover.
        """
        self._up_switch.turn_off()
        set_pin_output_state(
            True if self._down_pin.get(CONF_INVERT_LOGIC) else False,
            self._down_pin.get(CONF_ADDRESS), 
            self._down_pin.get(PORT), 
            self._down_pin.get(PIN) 
        )
        set_pin_output_state(
            True if self._up_pin.get(CONF_INVERT_LOGIC) else False,
            self._up_pin.get(CONF_ADDRESS), 
            self._up_pin.get(PORT), 
            self._up_pin.get(PIN) 
        )

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
