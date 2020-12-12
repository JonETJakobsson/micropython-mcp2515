class CAN:
    """Class providing interface with the mcp2515 module.

    Must be initiated with a pin objects for
    miso, mosi, sck and select chip pin.
    """

    def __init__(self, miso, mosi, sck, cs):
        from machine import SPI
        self.spi = SPI(1)
        self.miso = miso
        self.mosi = mosi
        self.sck = sck
        self.cs = cs

    # SPI helper methods
    def spi_start(self):
        from machine import SPI

        self.spi.init(
            baudrate=int(10E6),
            polarity=0,
            phase=0,
            bits=8,
            firstbit=SPI.MSB,
            miso=self.miso,
            mosi=self.mosi,
            sck=self.sck
        )

        self.cs.off()

    def spi_end(self):
        self.cs.on()
        self.spi.deinit()

    # SPI CONTOLS

    def write_register(self, address, data):
        from mcp2515.address import WRITE
        from ustruct import pack

        self.spi_start()

        self.spi.write(pack("<B", WRITE))
        self.spi.write(pack("<B", address))
        for byte in data:
            self.spi.write(pack("<B", byte))

        self.spi_end()

    def bitmodify_register(self, address, mask, data):
        from mcp2515.address import BIT_MODIFY
        from ustruct import pack

        self.spi_start()

        self.spi.write(pack("<B", BIT_MODIFY))
        self.spi.write(pack("<B", address))
        self.spi.write(pack("<B", mask))
        self.spi.write(pack("<B", data))

        self.spi_end()

    def read_register(self, address):
        from mcp2515.address import READ
        from ustruct import pack, unpack

        self.spi_start()

        self.spi.write(pack("<B", READ))
        self.spi.write(pack("<B", address))
        data = unpack("<B", self.spi.read(1))[0]

        self.spi_end()
        return data

    def reset(self):
        from mcp2515.address import RESET
        from ustruct import pack, unpack

        self.spi_start()

        self.spi.write(pack("<B", RESET))

        self.spi_end()

    def read_rx_buffer(self, buffer=0):
        """fetch all data from a recieve buffer.
        First 5 bytes are info, adn last 8 bytes are data

        buffer: rx buffer to read from: 0 or 1
        """
        from mcp2515.address import READ_RX_BUFFER_0, READ_RX_BUFFER_1
        from ustruct import pack, unpack

        self.spi_start()

        if buffer == 0:
            self.spi.write(pack("<B", READ_RX_BUFFER_0))
        if buffer == 1:
            self.spi.write(pack("<B", READ_RX_BUFFER_1))

        info = unpack("<5B", self.spi.read(5))
        data = unpack("<8B", self.spi.read(8))

        self.spi_end()
        return info, data

    def load_tx_buffer(self, buffer, info, data):
        """Write provided info and data to selected TX buffer"""
        from mcp2515.address import WRITE_TX_BUFFER_0, WRITE_TX_BUFFER_1, WRITE_TX_BUFFER_2
        from ustruct import pack, unpack

        self.spi_start()

        if buffer == 0:
            self.spi.write(pack("<B", WRITE_TX_BUFFER_0))

        if buffer == 1:
            self.spi.write(pack("<B", WRITE_TX_BUFFER_1))

        if buffer == 2:
            self.spi.write(pack("<B", WRITE_TX_BUFFER_2))

        for byte in info:
            self.spi.write(pack("<B", byte))

        for byte in data:
            self.spi.write(pack("<B", byte))

        self.spi_end()

    def request_to_send(self, buffer=0):
        from ustruct import pack

        self.spi_start()

        if buffer == 0:
            self.spi.write(pack("<B", 0x81))

        if buffer == 1:
            self.spi.write(pack("<B", 0x82))

        if buffer == 2:
            self.spi.write(pack("<B", 0x84))

        self.spi_end()

    def read_status(self):
        """Fetch recieve and transmit status and flags"""
        from mcp2515.address import READ_STATUS
        from ustruct import pack, unpack

        self.spi_start()

        self.spi.write(pack("<B", READ_STATUS))
        data = unpack("<B", self.spi.read(1))[0]

        self.spi_end()

        status = {
            "RX0IF": data & 0x01,
            "RX1IF": data >> 1 & 0x01,
            "TX0REQ": data >> 2 & 0x01,
            "TX0IF": data >> 3 & 0x01,
            "TX1REQ": data >> 4 & 0x01,
            "TX1IF": data >> 5 & 0x01,
            "TX2REQ": data >> 6 & 0x01,
            "TX2IF": data >> 7 & 0x01,
        }

        return status

    def rx_status(self):
        from mcp2515.address import RX_STATUS
        from ustruct import pack, unpack

        self.spi_start()

        self.spi.write(pack("<B", RX_STATUS))
        data = unpack("<B", self.spi.read(1))[0]

        self.spi_end()

        status = {
            "filter_match": data & 0x07,
            "RTR": data >> 3 & 0x01,
            "extendedID": data >> 4 & 0x01,
            "RXB0": data >> 6 & 0x01,
            "RXB1": data >> 7 & 0x01
        }

        return status
    # SET MODES ----------------------------

    def get_opmod(self):
        from mcp2515.address import CANSTAT

        data = self.read_register(CANSTAT)
        opmod = data >> 5

        return opmod

    # Set OPMOD on CANCTRL and check that the mode is sucessfuly set
    def set_opmod(self, mode):
        from mcp2515.address import CANCTRL, op_mask
        import time

        cur_mode = self.get_opmod()
        if cur_mode == mode >> 5:
            print("mode already set")
            return
        else:
            i = 0
            while i < 10:  # try to set mode 10 times
                self.bitmodify_register(CANCTRL, op_mask, mode)
                time.sleep_ms(100)

                cur_mode = self.get_opmod()
                if cur_mode == mode >> 5:
                    print("mode sucessfully set")
                    return
                else:
                    print("retrying setting mode...")
                    i += 1
            print("Failed setting mode")
            return

    # initiate CAN communication
    def init(
            self,
            bit_rate=500E3,
            clock_freq=8E6,
            SJW=1,
            BTLMODE=1,
            SAM=0,
            PRESEG=0,
            PHSEG1=2,
            PHSEG2=2):
        """
        Initiate the can controller with selected baudrate.
        bit_rate: CAN bus bit rate
        clock_freq: Can module occilator frequency
        SJW: synchronization Jump Width: 1 to 4, default(1)
        BTLMODE: : PS2 Bit Time Length bit: 0 or 1, default(1)
        SAM: Sample Point Configuration bit: 0 or 1, default(0)
        PHSEG1: lenght of PS1, default(7)
        PHSEG2: lenght of PS2, default(2) (only valid when BTLMODE=1)
        PRESEG: lengh of propagation segment: default(2)

        """
        from mcp2515.address import configuration_mode, normal_mode
        import time

        self.reset()
        time.sleep_ms(10)

        print("Entering configuration mode...")
        self.set_opmod(configuration_mode)

        print("calulating BRP and setting configuration registers 1, 2 and 3")
        self._set_timing(bit_rate, clock_freq, SJW, BTLMODE,
                         SAM, PRESEG, PHSEG1, PHSEG2)

        print("Entering normal mode...")
        self.set_opmod(normal_mode)

    def _set_timing(
            self,
            bit_rate,
            clock_freq,
            SJW,
            BTLMODE,
            SAM,
            PRESEG,
            PHSEG1,
            PHSEG2):
        """
        SJW: synchronization Jump Width: 1 to 4, default(1)
        BTLMODE: : PS2 Bit Time Length bit: 0 or 1, default(0)
        SAM: Sample Point Configuration bit: 0 or 1, default(1)
        PHSEG1: lenght of PS1, default(7)
        PHSEG2: lenght of PS2, default(6) (only valid when BTLMODE=1)
        PRESEG: lengh of propagation segment: default(2)
        """

        # Calculate bit time and time quantum
        bit_time = 1 / bit_rate
        tq = bit_time / 16

        # Calculate Baud rate prescaler
        BRP = int((tq * clock_freq) / 2 - 1)
        # assert BRP % 1 > 0, "warning, bit-rate and
        # clock-frequency is not compatible"

        # Set configuration register 1
        SJW = SJW - 1  # length of 1 is 0 etc.
        assert len(bin(SJW)) - 2 <= 2, "SJW must be 1 to 4"
        assert len(bin(BRP)) - 2 <= 5, "BRP must be under 31"

        self.bitmodify_register(0x2a, 0xc0, SJW << 6)
        self.bitmodify_register(0x2a, 0x3f, BRP)
        print(hex(self.read_register(0x2a)))  # error checking

        # Set configuration register 2
        assert len(bin(BTLMODE)) - 2 <= 1, "BTLMODE must be 0 or 1"
        assert len(bin(SAM)) - 2 <= 1, "SAM must be 0 or 1"
        assert len(bin(PHSEG1)) - 2 <= 3, "PHSEG1 must be 0 to 7"
        assert len(bin(PRESEG)) - 2 <= 3, "PRESEG must be 0 to 7"

        self.bitmodify_register(0x29, 0x80, BTLMODE << 7)
        self.bitmodify_register(0x29, 0x40, SAM << 6)
        self.bitmodify_register(0x29, 0x38, PHSEG1 << 3)
        self.bitmodify_register(0x29, 0x07, PRESEG)
        print(hex(self.read_register(0x29)))  # error checking

        # Set configuration register 3
        assert len(bin(PHSEG2)) - 2 <= 3, "PHSEG2 must be 0 to 7"

        self.bitmodify_register(0x28, 0x07, PHSEG2)
        print(hex(self.read_register(0x28)))  # error checking

    # Filter and masks (currently not working)

    def set_filter(self, id=0x000, filter=0, extendedID=False, clear=False):
        from mcp2515.address import configuration_mode, normal_mode

        self.set_opmod(configuration_mode)

        address = [0x00, 0x04, 0x08, 0x10, 0x14, 0x18]

        if filter <= 1:
            mask_address = 0x20
            ctrl_address = 0x60
        else:
            mask_address = 0x24
            ctrl_address = 0x70

        info = self._prepare_id(id, extendedID)

        self.write_register(address=address[filter], data=info)
        self.write_register(address=mask_address, data=[
                            0xff, 0xff, 0x00, 0x00])

        self.bitmodify_register(ctrl_address, 0x60, 0x00)  # activate filtering

        if clear:
            self.bitmodify_register(0x60, 0x60, 0xff)  # clear filtering
            self.bitmodify_register(0x70, 0x60, 0xff)  # clear filtering

        self.set_opmod(normal_mode)

    def _prepare_id(self, id, ext):

        id = id & 0x0ffff
        info = [0, 0, 0, 0]
        if ext:
            info[3] = id & 0xff
            info[2] = id >> 8
            id = id >> 16
            info[1] = id & 0x03
            info[1] += (id & 0x1c) << 3
            info[1] |= 0x08
            info[0] = id >> 5
        else:
            info[0] = id >> 3
            info[1] = (id & 0x07) << 5
            info[2] = 0
            info[3] = 0

        return info

    # read messages
    def read_message(self):
        """returns a dictionary containing message info
        id: message id
        rtr: remote transmit request
        extended: extended id
        data_lenght: number of bytes recieved
        data: list of bytes"""

        # fetch recieve status
        status = self.rx_status()
        if status["RXB0"] == 1:
            info, data = self.read_rx_buffer(buffer=0)
        elif status["RXB1"] == 1:
            info, data = self.read_rx_buffer(buffer=1)
        else:
            return False  # exit if no buffer is full

        id = info[0] << 3 | info[1] >> 5
        if status["extendedID"] == 1:
            id = id << 8 | info[2]
            id = id << 8 | info[3]

        data_length = info[4] & 0x0f

        if data_length > 0:
            data = data[0:data_length]
        else:
            data = list()

        message = {
            "id": id,
            "RTR": status["RTR"],
            "extendedID": status["extendedID"],
            "data_length": data_length,
            "data": data
        }
        return message

    # Write message
    def write_message(self, id, data_message, rtr=0, extendedID=False):
        """Prepares a message to be sent on available trasmission buffer

        id: a standar or extended message id
        data: list of bytes max = 8
        rtr: remote transmission request, if 1, no data is sent, default(0)
        extendedID: Set to True if message ID is extended, else Fales
        """
        data_length = len(data_message)

        info = self._prepare_id(id, extendedID)

        if rtr:
            dlc = data_length | 0x40
        else:
            dlc = data_length

        info.append(dlc)

        status = self.read_status()

        if status["TX0REQ"] == 0:
            self.load_tx_buffer(buffer=0, info=info, data=data_message)
            self.request_to_send(buffer=0)
            TXIF = 0x04
            self.bitmodify_register(0x2c, TXIF, 0x00)  # clear interupt flag

        elif status["TX1REQ"] == 0:
            self.load_tx_buffer(buffer=1, info=info, data=data_message)
            self.request_to_send(buffer=1)
            TXIF = 0x10
            self.bitmodify_register(0x2c, TXIF, 0x00)  # clear interupt flag

        elif status["TX2REQ"] == 0:
            self.load_tx_buffer(buffer=2, info=info, data=data_message)
            self.request_to_send(buffer=2)
            TXIF = 0x20
            self.bitmodify_register(0x2c, TXIF, 0x00)  # clear interupt flag

        else:
            return  # no transmit buffers are available

    # quick function to check for incoming messages
    def message_available(self):
        status = self.rx_status()
        if status["RXB0"] == 1 or status["RXB1"] == 1:
            return True
        else:
            return False

    # enableing and clearing interrupts -----------------
    def enable_interrupts(
            self,
            message_error=False,
            wake_up=False,
            errors=False,
            tx0_empty=False,
            tx1_empty=False,
            tx2_empty=False,
            rx0_full=False,
            rx1_full=False):
        """Enables interrupt conditions that will activate the INT pin.

        Note: errors must be cleared by MCU.
        use clear_message_error(), clear_wake_up()
        and clear_errors() to clear these flags

        tx_empty and rx_full are automatically cleared
         when reading or writing messages

        """

        if message_error:
            self.bitmodify_register(0x2b, 0x80, 0xff)

        if wake_up:
            self.bitmodify_register(0x2b, 0x40, 0xff)

        if errors:
            self.bitmodify_register(0x2b, 0x20, 0xff)

        if tx0_empty:
            self.bitmodify_register(0x2b, 0x04, 0xff)
        if tx1_empty:
            self.bitmodify_register(0x2b, 0x08, 0xff)
        if tx2_empty:
            self.bitmodify_register(0x2b, 0x10, 0xff)

        if rx0_full:
            self.bitmodify_register(0x2b, 0x01, 0xff)
        if rx1_full:
            self.bitmodify_register(0x2b, 0x02, 0xff)

    def clear_message_error(self):
        self.bitmodify_register(0x2c, 0x80, 0x00)

    def clear_wake_up(self):
        """Clears the wake-up interrupt flag and wakes-up the device"""
        self.bitmodify_register(0x2c, 0x40, 0x00)

    def clear_error(self):
        self.bitmodify_register(0x2c, 0x20, 0x00)

    def which_interrupt(self):
        """returns information about which interrupt condition
         triggered the interrupt"""
        canstat = self.read_register(0x0e)
        i_code = canstat >> 1 & 0x07

        codes = ["No interrupts", "Error", "Wake-up",
                 "TX0", "TX1", "TX2", "RX0", "RX1"]
        return codes[i_code]

    def abort_messages(self):
        """Request abort of all pending transmissions"""
        self.bitmodify_register(0x0f, 0x10, 0xff)
