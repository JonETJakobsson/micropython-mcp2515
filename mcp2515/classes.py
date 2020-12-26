from micropython import const


# SPI instructions:
class mcp_spi():
    RESET = const(0xC0)
    READ = const(0x03)
    READ_RX_BUFFER_0 = const(0x90)
    READ_RX_BUFFER_1 = const(0x94)
    WRITE = const(0x02)
    WRITE_TX_BUFFER_0 = const(0x40)
    WRITE_TX_BUFFER_1 = const(0x42)
    WRITE_TX_BUFFER_2 = const(0x44)
    READ_STATUS = const(0xA0)
    RX_STATUS = const(0xB0)
    BIT_MODIFY = const(0x05)
    RTS0 = const(0x81)
    RTS1 = const(0x82)
    RTS2 = const(0x84)


# operating modes
class op_mode():
    op_mask = const(0xE0)
    normal = const(0x00)
    sleep = const(0x20)
    loopback = const(0x40)
    listen = const(0x60)
    configuration = const(0x80)


# address to registers
class address():
    CANCTRL = const(0x0F)
    CANSTAT = const(0x0E)
    CNF1 = const(0x2A)
    CNF2 = const(0x29)
    CNF3 = const(0x28)