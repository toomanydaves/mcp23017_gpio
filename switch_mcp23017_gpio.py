"""
## MCP23017 GPIO Switch Platform The `mcp23017_gpio` switch platform allows you to treat individual pins on MCP23017 expansion boards connected to your Raspberry Pi via its I2C bus (Pins 3 & 5 on the Model 3) as switches.

To use this component, add the following to your configuration.yaml file:
```
  # Example configuration.yaml entry
  switch:
    - platform: mcp23017_gpio
      invert_logic: true
      i2c_address: 0x20
      register_index: 0
      pin_index: 0
      name: track_lighting
```
Configuration Variables:
+ **invert_logic** (Optional): If true, inverts the output logic to ACTIVE LOW. Default is false (ACTIVE HIGH).
+ **i2c_address** (Required): The address of the MCP23017 with the pin on the Pi's I2C bus, 0x00-0xff
+ **register_index** (Required): The index of the register (0 or 1) with the pin on the MCP23017.
+ **pin_index** (Required): The index of the pin on the register, 0-7.
+ **name** (Optional): Name to use in the frontend.
"""

import logging

import voluptuous as vol

from homeassistant.components.switch import SwitchDevice, PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['smbus2==0.2.1']

_LOGGER = logging.getLogger(__name__)

CONF_INVERT_LOGIC = 'invert_logic'
CONF_I2C_ADDRESS = 'i2c_address'
CONF_REGISTER_INDEX = 'register_index'
CONF_PIN_INDEX = 'pin_index'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_I2C_ADDRESS): vol.All(int, vol.Range(min=0x00, max=0xff)),
    vol.Required(CONF_REGISTER_INDEX): vol.All(int, vol.Range(min=0, max=1)),
    vol.Required(CONF_PIN_INDEX): vol.All(int, vol.Range(min=0, max=7)),
    vol.Optional(CONF_INVERT_LOGIC, default=False): cv.boolean,
    vol.Optional(CONF_NAME, default="MCP23017"): cv.string,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    invert_logic = config.get(CONF_INVERT_LOGIC)
    i2c_address = config.get(CONF_I2C_ADDRESS)
    register_index = config.get(CONF_REGISTER_INDEX)
    pin_index = config.get(CONF_PIN_INDEX)
    name = config.get(CONF_NAME)

    add_devices([MCP23017GPIOSwitch(i2c_address, register_index, pin_index, name, invert_logic)])

class MCP23017GPIOSwitch(SwitchDevice):
    """
    Switch for MCP23017 GPIO
    """
    def __init__(self, i2c_address, register_index, pin_index, name, invert_logic=False):
        self._i2c_address = i2c_address
        self._register_index = register_index
        self._pin_index = pin_index
        self._invert_logic = invert_logic
        self._name = name if not name == 'MCP23017' else (
            str(hex(i2c_address)) + ':' + str(register_index) + ':' + str(pin_index)
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
        defaults to [i2c_address]:[register_index]:[pin_index]
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
        from smbus2 import SMBusWrapper

        output_register = 0x00 if self._register_index == 0 else 0x01

        with SMBusWrapper(1) as smbus:

            # Output is configured by a 0 at the pin's offset on the register 
            # We want to change only that bit and leave the rest
            data_byte = smbus.read_byte_data(self._i2c_address, output_register) & ~(1 << self._pin_index
)

            smbus.write_byte_data(self._i2c_address, output_register, data_byte)


    def _update_bus(self):
        """
        Write switch state to pin on bus
        """
        from smbus2 import SMBusWrapper

        write_register = 0x12 if self._register_index == 0 else 0x13

        with SMBusWrapper(1) as smbus:
            current_value = smbus.read_byte_data(self._i2c_address, write_register)

            if self._state and not self._invert_logic or not self._state and self._invert_logic:
                desired_value = current_value | (1 << self._pin_index)
            else:
                desired_value = current_value & ~(1 << self._pin_index)

            smbus.write_byte_data(self._i2c_address, write_register, desired_value)
