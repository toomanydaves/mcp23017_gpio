import logging
import time
import voluptuous as vol

from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'mcp23017_gpio'

REQUIREMENTS = ['smbus2==0.2.1']

CONF_ADDRESS = 'address'
CONF_PORT = 'port'
CONF_INDEX = 'index'
CONF_INVERT_LOGIC = 'invert_logic'
CONF_NAME = CONF_NAME

PIN_SCHEMA = vol.Schema({
    vol.Required(CONF_ADDRESS): vol.All(int, vol.Range(min=0x00, max=0xff)),
    vol.Required(CONF_PORT): vol.Any('A', 'B', msg='Expected A or B'),
    vol.Required(CONF_INDEX): vol.All(int, vol.Range(min=0, max=7)),
    vol.Optional(CONF_NAME, default='MCP23017'): cv.string,
    vol.Optional(CONF_INVERT_LOGIC, default=False): cv.boolean,
})

def setup(hass, config):
    return True

def config_pin_as_output(address, port, index):
    """
    Set the pin on bus to function as output
    """
    from smbus2 import SMBusWrapper

    polarity_register = 0x00 if port == 'A' else 0x01

    with SMBusWrapper(1) as smbus:
        # Output is configured by a 0 at the pin's offset on the register. 
        # We want to change only that bit and leave the rest.
        
        data = smbus.read_byte_data(address, polarity_register) & ~(1 << index)

        smbus.write_byte_data(address, polarity_register, data)

def set_pin_output_state(state, address, port, index):
    """
    Write state to output register of pin on bus
    """
    from smbus2 import SMBusWrapper

    output_register = 0x12 if port == 'A' else 0x13

    with SMBusWrapper(1) as smbus:
        data = smbus.read_byte_data(address, output_register)

        if state:
            data = data | (1 << index)
        else:
            data = data & ~(1 << index)

        smbus.write_byte_data(address, output_register, data)

def get_pin_config_state(address, port, index):
    """
    Return state of output register for pin on bus
    """
    from smbus2 import SMBusWrapper

    polarity_register = 0x00 if port == 'A' else 0x01

    with SMBusWrapper(1) as smbus:
        data = smbus.read_byte_data(address, polarity_register)

        return (data >> index & 1)

def get_pin_output_state(address, port, index):
    """
    Return state of output register for pin on bus
    """
    from smbus2 import SMBusWrapper

    output_register = 0x12 if port == 'A' else 0x13

    with SMBusWrapper(1) as smbus:
        data = smbus.read_byte_data(address, output_register)

        return True if (data >> index & 1) == 1 else False
