from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, XC3SProg


_io = [

    #OSC
    ("clk_50", 0, Pins("T7"), IOStandard("LVCMOS33")), 

    # RESET
    ("resetn", 0, Pins("C3"), IOStandard("LVCMOS33"), Misc("PULLDOWN")), #UNUSED PIN

    # EVERLOOP CONTROL
    ("everloop_ctl", 0,  Pins("A9"),  IOStandard("LVCMOS33")),

    #######################
    # RPi SPI BUS
    #######################
    ("rpi_sck"     , 0,  Pins("R9"),  IOStandard("LVCMOS33")),
    ("rpi_mosi"    , 0,  Pins("M10"), IOStandard("LVCMOS33")),
    ("rpi_miso"    , 0,  Pins("M9"),  IOStandard("LVCMOS33")),
    ("rpi_ss"      , 0,  Pins("N9"),  IOStandard("LVCMOS33")),

    ("spiflash", 0,
        Subsignal("cs_n", Pins("T3")),
        Subsignal("clk", Pins("R11")),
        Subsignal("mosi", Pins("T10")),
        Subsignal("miso", Pins("P10"), Misc("PULLUP")),
        IOStandard("LVCMOS33"), Misc("SLEW=FAST")),

    #######################
    # ESP32 SPI BUS
    #######################
    ("esp_sck"     , 0,  Pins("B3"),  IOStandard("LVCMOS33")), #ESP_IO32
    ("esp_mosi"    , 0,  Pins("C5"),  IOStandard("LVCMOS33")), #ESP_IO33
    ("esp_miso"    , 0,  Pins("K6"),  IOStandard("LVCMOS33")), #ESP_IO21
    ("esp_ss"      , 0,  Pins("L3"),  IOStandard("LVCMOS33")), #ESP_IO23

    ("EN_ESP"      , 0,  Pins("A4"),  IOStandard("LVCMOS33")),
    ("EN_PROG_ESP" , 0,  Pins("F3"),  IOStandard("LVCMOS33")),

    ("ESP_TX"      , 0,  Pins("L5"),  IOStandard("LVCMOS33")),
    ("ESP_RX"      , 0,  Pins("K5"),  IOStandard("LVCMOS33")),
    ("GPIO_24"     , 0,  Pins("A14"), IOStandard("LVCMOS33"), Misc("PULLUP")), #RPI_GPIO24 to EN_PROG_ESP
    ("GPIO_25"     , 0,  Pins("B14"), IOStandard("LVCMOS33"), Misc("PULLUP")) ,#RPI_GPIO25 to EN_ESP

    ("serial", 0,
        Subsignal("tx" , Pins("A12")),
        Subsignal("rx" , Pins("B12")),
        IOStandard("LVCMOS33")
    ),

    # NET "GPIO_12"      LOC = "N8" | IOSTANDARD = LVCMOS33 ;
    # NET "GPIO_16"      LOC = "P8" | IOSTANDARD = LVCMOS33 ;

    #######################
    # AUDIO OUTPUT
    #######################
    ("dac_output<0>", 0, Pins("E1"), IOStandard("LVCMOS33")),
    ("dac_output<1>", 0, Pins("F1"), IOStandard("LVCMOS33")),
    ("dac_volumen"  , 0, Pins("C1"), IOStandard("LVCMOS33")),
    ("dac_mute"     , 0, Pins("B1"), IOStandard("LVCMOS33")),
    ("dac_hp_nspk"  , 0, Pins("D1"), IOStandard("LVCMOS33")),

    #NET "hp_detect"     LOC = "T4"  | IOSTANDARD = LVCMOS33;

    #######################
    # MIC ARRAY           #
    #######################
    ("pdm_clk"    , 0, Pins("B5"), IOStandard("LVCMOS33")),
    ("pdm_data<0>", 0, Pins("E6"), IOStandard("LVCMOS33")),
    ("pdm_data<1>", 0, Pins("B8"), IOStandard("LVCMOS33")),
    ("pdm_data<2>", 0, Pins("A8"), IOStandard("LVCMOS33")),
    ("pdm_data<3>", 0, Pins("C7"), IOStandard("LVCMOS33")),
    ("pdm_data<4>", 0, Pins("A7"), IOStandard("LVCMOS33")),
    ("pdm_data<5>", 0, Pins("A6"), IOStandard("LVCMOS33")),
    ("pdm_data<6>", 0, Pins("B6"), IOStandard("LVCMOS33")),
    ("pdm_data<7>", 0, Pins("A5"), IOStandard("LVCMOS33")),
    ("mic_irq<0>" , 0, Pins("R7"), IOStandard("LVCMOS33")), #RPI_GPIO6
    ("mic_irq<1>" , 0, Pins("H4"), IOStandard("LVCMOS33")), #ESP_IO5

    #######################
    #    EXP-CONN         #
    #######################

    ("gpio_io<15>", 0, Pins("R2"), IOStandard("LVCMOS33")),
    ("gpio_io<14>", 0, Pins("R1"), IOStandard("LVCMOS33")),
    ("gpio_io<13>", 0, Pins("P2"), IOStandard("LVCMOS33")),
    ("gpio_io<12>", 0, Pins("P1"), IOStandard("LVCMOS33")),
    ("gpio_io<11>", 0, Pins("N1"), IOStandard("LVCMOS33")),
    ("gpio_io<10>", 0, Pins("M2"), IOStandard("LVCMOS33")),
    ("gpio_io<9>" , 0, Pins("M1"), IOStandard("LVCMOS33")),
    ("gpio_io<8>" , 0, Pins("L1"), IOStandard("LVCMOS33")),
    ("gpio_io<7>" , 0, Pins("K2"), IOStandard("LVCMOS33")),
    ("gpio_io<6>" , 0, Pins("K1"), IOStandard("LVCMOS33")),
    ("gpio_io<5>" , 0, Pins("J3"), IOStandard("LVCMOS33")),
    ("gpio_io<4>" , 0, Pins("J1"), IOStandard("LVCMOS33")),
    ("gpio_io<3>" , 0, Pins("H2"), IOStandard("LVCMOS33")),
    ("gpio_io<2>" , 0, Pins("H1"), IOStandard("LVCMOS33")),
    ("gpio_io<1>" , 0, Pins("G3"), IOStandard("LVCMOS33")),
    ("gpio_io<0>" , 0, Pins("G1"), IOStandard("LVCMOS33")),

    #DDR2 pins
    
    ("ddram_clock", 0,
        Subsignal("p", Pins("G12")),
        Subsignal("n", Pins("H11")),
        IOStandard("MOBILE_DDR")),

    ("ddram", 0,
        Subsignal("a", Pins("H15 H16 F16 H13 C16 J11 J12 F15 F13 F14 C15 G11 D16")),  #13 pins
        Subsignal("ba", Pins("G14 G16")), #2 pins
        Subsignal("cke", Pins("D14")),
        Subsignal("ras_n", Pins("J13")),
        Subsignal("cas_n", Pins("K14")),
        Subsignal("we_n", Pins("E15")),
        Subsignal("dq", Pins("L14 L16 M15 M16 J14 J16 K15 K16 P15 P16 R15 R16 T14 T13 R12 T12")), #16 pins
        Subsignal("dqs", Pins("N14 R14")), #2 pins #LDQS+ & UDQS+ : Check on this
        Subsignal("dm", Pins("K11 K12")),  #2 pins- LDM UDM : Check on this
        IOStandard("MOBILE_DDR")
    )
]

_connectors = [
]


class Platform(XilinxPlatform):
    name = "matrix_voice"
    default_clk_name = "clk_50"
    default_clk_period = 20   #ns- as advised by Andres

    # The MATRIX Voice has a XC6SLX9 which bitstream takes up ~2.6Mbit (1484472 bytes)
    # 0x80000 offset (4Mbit) gives plenty of space
    gateware_size = 0x80000

    # MX25L6406E - component
    # 16Mb - 75 MHz clock frequency
    # FIXME: Create a "spi flash module" object in the same way we have SDRAM
    # module objects.
    #	/*             name,  erase_cmd, chip_erase_cmd, device_id, pagesize, sectorsize, size_in_bytes */
    #	FLASH_ID("st m25p16",      0xd8,           0xc7, 0x00152020,   0x100,    0x10000,      0x200000),
    spiflash_model = "25l6406e" #mx25l6406e
    spiflash_read_dummy_bits = 4    #2048 equal sectors, 4 kb each
    spiflash_clock_div = 4
    spiflash_total_size = int((64/8)*1024*1024) # 64Mbit
    spiflash_page_size = 256    #256 bytes
    spiflash_sector_size = 0x01000  #4 kB each

    def __init__(self):    #maybe include self, programmer="xc3sprog" since we use that to flash bit file to MATRIX Voice
        XilinxPlatform.__init__(self, "xc6slx9-2ftg256", _io, _connectors)
        #XC3SProg("matrix_voice")

    def create_programmer(self):
        raise NotImplementedError