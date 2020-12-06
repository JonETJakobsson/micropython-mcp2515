# SPI instructions:
RESET = 0xC0
READ = 0x03
READ_RX_BUFFER_0 = 0x90
READ_RX_BUFFER_1 = 0x94
WRITE = 0x02
WRITE_TX_BUFFER_0 = 0x40
WRITE_TX_BUFFER_1 = 0x42
WRITE_TX_BUFFER_2 = 0x44
READ_STATUS = 0xA0
RX_STATUS = 0xB0
BIT_MODIFY = 0x05


# operating modes
op_mask = 0xE0
normal_mode = 0x00
sleep_mode = 0x20
loopback_mode = 0x40
listen_only_mode = 0x60
configuration_mode = 0x80

# address to registers
CANCTRL = 0x0F
CANSTAT = 0x0E