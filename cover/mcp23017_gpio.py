"""
## MCP23017 GPIO Cover Platform

To use this component, add the following to your configuration.yaml file:
```
  # Example configuration.yaml entry
  cover:
    - platform: mcp23017_gpio
      covers:
        - name: Bedroom Blinds
          down_pin:
            address: 0x20
            port: A
            index: 0
            invert_logic: true
          up_pin:
            address: 0x24
            port: B
            index: 7
```
Configuration Variables:
+ **name** (Optional): Name to use in the frontend.
+ **address** (Required): The address of the MCP23017 with the pin on the Pi's I2C bus, 0x00-0xff
+ **port** (Required): The port (A or B) with the pin on the MCP23017.
+ **index** (Required): The index of the pin on the port, 0-7.
+ **invert_logic** (Optional): If true, inverts the output logic to ACTIVE LOW. Default is false (ACTIVE HIGH).
"""
import logging
import voluptuous as vol

from custom_components.mcp23017_gpio import (
    PIN_SCHEMA, CONF_ADDRESS, CONF_PORT, CONF_INDEX, CONF_INVERT_LOGIC, CONF_NAME,
    config_pin_as_output, set_pin_output_state, get_pin_config_state, get_pin_output_state)

from homeassistant.components.cover import CoverDevice, PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv

DEPENDENCIES = ['mcp23017_gpio']

_LOGGER = logging.getLogger(__name__)

CONF_COVERS = 'covers'
CONF_DOWN_PIN = 'down_pin'
CONF_UP_PIN = 'up_pin'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_COVERS): vol.All(
        cv.ensure_list,
        [ vol.Schema({
            vol.Required(CONF_UP_PIN): PIN_SCHEMA,
            vol.Required(CONF_DOWN_PIN): PIN_SCHEMA,
            vol.Optional(CONF_NAME, default='MCP23017'): cv.string,
        }) ]
    )
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    covers = []

    for cover in config.get(CONF_COVERS):
        name=cover.get(CONF_NAME)
        down_pin = dict(cover.get(CONF_DOWN_PIN))
        up_pin = dict(cover.get(CONF_UP_PIN))

        covers.append(MCP23017GPIOCover(
            down_pin,
            up_pin,
            name
        ))

    add_devices(covers)

class MCP23017GPIOCover(CoverDevice):
    """
    Representation of a window cover whose motor is controled by two relay switches in turn
    controlled by two GPIO pins of a MCP23017 chip driven from the I2C bus of a Raspberry Pi
    """
    def __init__(self, down_pin, up_pin, name):
        self._down_pin = down_pin
        self._up_pin = up_pin
        self._name = name if not name == 'MCP23017' else (
            str(hex(up_pin.get(CONF_ADDRESS))) + ':' + up_pin.get(CONF_PORT) + ':' + str(up_pin.get(CONF_INDEX))
            + " | " +
            
            str(hex(down_pin.get(CONF_ADDRESS))) + ':' + down_pin.get(CONF_PORT) + ':' + str(down_pin.get(CONF_INDEX))
        )

    @property
    def name(self):
        """
        Return the name of the cover.
        Default: [up_pin_address]:[up_pin_port]:[up_pin_index]|[down_pin_address]:[down_pin_port]:[down_pin_index]
        """
        return self._name

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
        # down_pin = dict(self._down_pin[0])

        pin_state=get_pin_output_state(
	    address=self._down_pin.get(CONF_ADDRESS),
	    port=self._down_pin.get(CONF_PORT),
	    index=self._down_pin.get(CONF_INDEX)
        )
        invert_logic=self._down_pin.get(CONF_INVERT_LOGIC)

        return self._determine_state(pin_state, invert_logic)

    @property
    def is_closing(self):
        """
        Return if the cover is closing or not
        """
        # up_pin = dict(self._up_pin[0])

        pin_state=get_pin_output_state(
	    address=self._up_pin.get(CONF_ADDRESS),
	    port=self._up_pin.get(CONF_PORT),
	    index=self._up_pin.get(CONF_INDEX)
        )
        invert_logic=self._up_pin.get(CONF_INVERT_LOGIC)
            
        return self._determine_state(pin_state, invert_logic)

    @property
    def is_closed(self):
        """
        Return if the cover is closed or not
        """
        return None

    def open_cover(self):
        """
        Open the cover.
        """
        #up_pin = dict(self._up_pin[0])

        self.stop_cover()
        set_pin_output_state(
            False if self._up_pin.get(CONF_INVERT_LOGIC) else True,
            self._up_pin.get(CONF_ADDRESS), 
            self._up_pin.get(CONF_PORT), 
            self._up_pin.get(CONF_INDEX) 
        )

    def close_cover(self):
        """
        Close the cover.
        """
        # down_pin = dict(self._down_pin[0])

        self.stop_cover()
        set_pin_output_state(
            False if self._down_pin.get(CONF_INVERT_LOGIC) else True,
            self._down_pin.get(CONF_ADDRESS), 
            self._down_pin.get(CONF_PORT), 
            self._down_pin.get(CONF_INDEX) 
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
        # up_pin = dict(self._up_pin[0])
        # down_pin = dict(self._down_pin[0])

        set_pin_output_state(
            True if self._down_pin.get(CONF_INVERT_LOGIC) else False,
            self._down_pin.get(CONF_ADDRESS), 
            self._down_pin.get(CONF_PORT), 
            self._down_pin.get(CONF_INDEX) 
        )
        set_pin_output_state(
            True if self._up_pin.get(CONF_INVERT_LOGIC) else False,
            self._up_pin.get(CONF_ADDRESS), 
            self._up_pin.get(CONF_PORT), 
            self._up_pin.get(CONF_INDEX) 
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

    def _determine_state(self, pin_state, invert_logic):
        if pin_state and not invert_logic or not pin_state and invert_logic:
            return True
        else:
            return False
