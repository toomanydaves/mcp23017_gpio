# mcp23017_gpio
Home-Assistant component and platforms for Raspberry Pi GPIO via MCP23017 Chips

## MCP23017 GPIO Switch Platform
The `mcp23017_gpio` switch platform allows you to treat individual pins on MCP23017 expansion boards connected to your Raspberry Pi via its I2C bus (Pins 3 & 5 on the Model 3) as switches.

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
+ **i2c_address** (Required): The address of the MCP23017 with the pin on the Pi's I2C bus, 0x00-0xff
+ **register_index** (Required): The index of the register (0 or 1) with the pin on the MCP23017.
+ **pin_index** (Required): The index of the pin on the register, 0-7.
+ **name** (Optional): Name to use in the frontend, default "[i2c_address]:[register_index]:[pin_index]".
+ **invert_logic** (Optional): If true, inverts the output logic to ACTIVE LOW. Default is false (ACTIVE HIGH).
