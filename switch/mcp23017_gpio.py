"""
## MCP23017 GPIO Switch Platform
The `mcp23017_gpio` switch platform allows you to treat individual pins on MCP23017 expansion boards connected to your Raspberry Pi via its I2C bus (Pins 3 & 5 on the Model 3) as switches.

To use this component, add the following to your configuration.yaml file:
```
  # Example configuration.yaml entry
  switch:
    - platform: mcp23017_gpio
      pins:
        - address: 0x20
          port: A
          index: 0
          invert_logic: true
          name: Track Lighting
        - address: 0x24
          port: B
          index: 7
          invert_logic: true
          name: Overhead Fan
```
Configuration Variables:
+ **address** (Required): The address of the MCP23017 with the pin on the Pi's I2C bus, 0x00-0xff
+ **port** (Required): The port (A or B) with the pin on the MCP23017.
+ **index** (Required): The index of the pin on the port, 0-7.
+ **invert_logic** (Optional): If true, inverts the output logic to ACTIVE LOW. Default is false (ACTIVE HIGH).
+ **name** (Optional): Name to use in the frontend.
"""

import logging

import voluptuous as vol

from custom_components.mcp23017_gpio import (
    PIN_SCHEMA, CONF_ADDRESS, CONF_PORT, CONF_INDEX, CONF_INVERT_LOGIC, CONF_NAME,
    config_pin_as_output, set_pin_output_state, get_pin_config_state)

from homeassistant.components.switch import SwitchDevice, PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv

DEPENDENCIES = ['mcp23017_gpio']

_LOGGER = logging.getLogger(__name__)

CONF_PINS = 'pins'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_PINS): vol.All(
        cv.ensure_list,
        [ PIN_SCHEMA ]
    )
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    switches = []
    for pin in config.get(CONF_PINS):
        switches.append(MCP23017GPIOSwitch(
            address=pin[CONF_ADDRESS],
            port=pin[CONF_PORT],
            index=pin[CONF_INDEX],
            name=pin[CONF_NAME],
            invert_logic=pin[CONF_INVERT_LOGIC]
        ))

    add_devices(switches)

class MCP23017GPIOSwitch(SwitchDevice):
    """
    Switch for MCP23017 GPIO
    """
    def __init__(self, address, port, index, name, invert_logic=False):
        self._address = address
        self._port = port
        self._index = index
        self._invert_logic = invert_logic
        self._name = name if not name == 'MCP23017' else (
            str(hex(address)) + ':' + port + ':' + str(index)
        )

        # Configure pin on bus as output (switch)
        self._config_bus()

        # Set initial state to off
        self._state = False

	# Set pin on bus to initial state
        self._update_bus()

    @property
    def name(self):
        """
        Return the name of the switch,
        defaults to [address]:[port]:[index]
        """
        return self._name

    @property
    def is_on(self):
        """
        Return true if switch is on
        """
        return self._state

    def turn_on(self):
        self._state = True
        self._update_bus()

    def turn_off(self):
        self._state = False
        self._update_bus()

    def toggle(self):
        self._state = not self._state
        self._update_bus()

    def _config_bus(self):
        """
        Configure pin on bus as output.
        """
        address = self._address
        port = self._port
        index = self._index

        if get_pin_config_state(address, port, index) != 0:
            config_pin_as_output(address, port, index)

    def _update_bus(self):
        """
        Write switch state to pin on bus
        """
        if self._state and not self._invert_logic or not self._state and self._invert_logic:
            state = True
        else:
            state = False

        set_pin_output_state(state, address=self._address, port=self._port, index=self._index)
