===================
Micropython-mcp2515
===================
.. raw:: html

    <img src="mcp2515.jpg" height="200px", align="right">
    
 
Communicate with the mcp2515 CAN module using SPI on a micropython board.

Note:
    Please take a look at this `micropython mcp2515 library <https://github.com/jxltom/micropython-mcp2515/>`_ by jxltom. 

........
Features
........
* Automatic configuration given CAN baud rate and crystal frequency
* Read standard and extended id messages
* write standard and extended id messages
* support RTR

.....
TODO:
.....
* Set filters
* Set masks

.......
Install
.......
Copy the mcp2515 folder to your pyboard. I utilize rshell for this.

.. code-block:: bash

    rshell -p COM3
    
in rshell:
    
.. code-block:: bash
    
    cp -r mcp2515/ /pyboard/
    repl

Import the CAN object under mcp2515.can in your code, and supply the nessesary spi pins (mosi, miso, sck and cs). Instanciate the CAN object with the spi pins and the chip select (supports connections with as many CAN modules as available GPIO for chip select).

.. code-block:: python

  import time
  from machine import SPI, Pin
  from mcp2515.can import CAN

  miso = Pin(19, Pin.IN)
  mosi = Pin(23, Pin.OUT)
  sck = Pin(18, Pin.OUT)
  cs = Pin(26, Pin.OUT)

  can = CAN(miso, mosi, sck, cs)

Initiate the can communication using the init method, supply information about bit-rate and crystal clock frequency. You have access to specific settings here as well. Check this manual for further information. http://ww1.microchip.com/downloads/en/DeviceDoc/MCP2515-Stand-Alone-CAN-Controller-with-SPI-20001801J.pdf

The default values are shown here:

.. code-block:: python
    
    can.init(
        bit_rate=500E3, 
        clock_freq=8E6, 
        SJW=1,
        BTLMODE=1,
        SAM=0,
        PRESEG=0,
        PHSEG1=2,
        PHSEG2=2)
        
Read messages using the read_message() method. If no message is available the method returns False. Here is an example:

.. code-block:: python

  while True:
    message = can.read_message()
    if message:
        print(message["id"], message["data"])
  
Write messages by supplying message id and a data list. 

.. code-block:: python

  id = 0x123
  data = [1, 2, 3, 4, 5, 6, 7, 8]
  can.write_message(id, data)
  
  
............
Contributing
............

Any help with this package would be higly apprechiated! The package is new, and not highly optimized. Critical features like setting masks and filters are not implemented. If you find bugs, please report this, as I have only tested this package using the tinyPICO esp32 board.

Kindly,
Jon
