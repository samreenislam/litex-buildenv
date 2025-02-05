# Support for the MATRIX Voice (https://voice.matrix.one)

import os

from fractions import Fraction

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.build.generic_platform import *

from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *

from litedram.modules import MT47H32M16
from litedram.phy import s6ddrphy
from litedram.core import ControllerSettings

from targets.utils import csr_map_update

from litex.soc.cores import uart
from litex.soc.cores.uart import UARTWishboneBridge

from litescope import LiteScopeAnalyzer
from litescope import LiteScopeIO

from gateware import info
from gateware import cas
from gateware import spi_flash


class _CRG(Module):
    def __init__(self, platform, clk_freq):
        # Clock domains for the system (soft CPU and related components run at).
        self.clock_domains.cd_sys = ClockDomain()
        # Clock domains for the DDR interface.
        self.clock_domains.cd_sdram_half = ClockDomain()
        self.clock_domains.cd_sdram_full_wr = ClockDomain()
        self.clock_domains.cd_sdram_full_rd = ClockDomain()

        # Input 50MHz clock
        f0 = 50*1000000
        clk50 = platform.request("clk_50")
        clk50a = Signal()
        # Input 50MHz clock (buffered)
        self.specials += Instance(
            "IBUFG",
            i_I=clk50,
            o_O=clk50a
        )

        clk50b = Signal()

        self.specials += Instance(
            "BUFIO2",
            p_DIVIDE=1,
            p_DIVIDE_BYPASS="TRUE", p_I_INVERT="FALSE",
            i_I=clk50a,
            o_DIVCLK=clk50b
        )

        #PLL parameters
        f = Fraction(10, 1)
        n, d = f.numerator, f.denominator
        p = 8

        assert f0*n/d/p/4 == clk_freq
        assert 19e6     <= f0/d     <= 500e6    # pfd
        assert 400e6    <= f0*n/d   <= 1000e6   # vco

        # Unbuffered output signals from the PLL. They need to be buffered
        # before feeding into the fabric.
        unbuf_sdram_full    = Signal()
        unbuf_sdram_half_a  = Signal()
        unbuf_sdram_half_b  = Signal()
        unbuf_unused_a      = Signal()
        unbuf_unused_b      = Signal()
        unbuf_sys           = Signal()

        # PLL signals
        pll_lckd = Signal()
        pll_fb = Signal()
        self.specials.pll = Instance(
            "PLL_ADV",
            name="crg_pll_adv",
            p_SIM_DEVICE="SPARTAN6", p_BANDWIDTH="OPTIMIZED", p_COMPENSATION="INTERNAL",
            p_REF_JITTER=.01,
            i_DADDR=0, i_DCLK=0, i_DEN=0, i_DI=0, i_DWE=0, i_RST=0, i_REL=0,
            p_DIVCLK_DIVIDE=d,
            # Input Clocks (50MHz)
            i_CLKIN1=clk50b,
            p_CLKIN1_PERIOD=1e9/f0,
            i_CLKIN2=0,
            p_CLKIN2_PERIOD=0.,
            i_CLKINSEL=1,
            # Feedback
            i_CLKFBIN=pll_fb, o_CLKFBOUT=pll_fb, o_LOCKED=pll_lckd,
            p_CLK_FEEDBACK="CLKFBOUT",
            p_CLKFBOUT_MULT=n, p_CLKFBOUT_PHASE=0.,
            # Outputs
            # (125 MHz) sdram wr rd
            o_CLKOUT0=unbuf_sdram_full,   p_CLKOUT0_DUTY_CYCLE=.5,
            p_CLKOUT0_PHASE=0.,   p_CLKOUT0_DIVIDE=p,
            # (125 MHz) unused
            o_CLKOUT1=unbuf_unused_a,     p_CLKOUT1_DUTY_CYCLE=.5,
            p_CLKOUT1_PHASE=0.,   p_CLKOUT1_DIVIDE=p,
            # (62.5 MHz) sdram_half - sdram dqs adr ctrl
            o_CLKOUT2=unbuf_sdram_half_a, p_CLKOUT2_DUTY_CYCLE=.5,
            p_CLKOUT2_PHASE=270., p_CLKOUT2_DIVIDE=(p*2),
            # (62.5 MHz) off-chip ddr
            o_CLKOUT3=unbuf_sdram_half_b, p_CLKOUT3_DUTY_CYCLE=.5,
            p_CLKOUT3_PHASE=270., p_CLKOUT3_DIVIDE=(p*2),
            # (31.25 MHz) unused
            o_CLKOUT4=unbuf_unused_b,     p_CLKOUT4_DUTY_CYCLE=.5,
            p_CLKOUT4_PHASE=0.,   p_CLKOUT4_DIVIDE=(p*4),
            # (31.25 MHz) sysclk
            o_CLKOUT5=unbuf_sys,          p_CLKOUT5_DUTY_CYCLE=.5,
            p_CLKOUT5_PHASE=0.,   p_CLKOUT5_DIVIDE=(p*4),
        )

        #power on reset?
        # reset_pin = [("reset", 0, Pins("P2:0")), ]
        # platform.add_extension(reset_pin)
        # reset = platform.request("reset")
        # self.clock_domains.cd_por = ClockDomain()
        # por = Signal(max=1 << 11, reset=(1 << 11) - 1)
        # self.sync.por += If(por != 0, por.eq(por - 1))
        # self.specials += AsyncResetSynchronizer(self.cd_por, reset)

        #System clock
        self.specials += Instance("BUFG", i_I=unbuf_sys, o_O=self.cd_sys.clk)
        #self.comb += self.cd_por.clk.eq(self.cd_sys.clk)
        #self.specials += AsyncResetSynchronizer(self.cd_sys, ~pll_lckd | (por > 0))

        # SDRAM clocks
        # ------------------------------------------------------------------------------
        self.clk4x_wr_strb = Signal()
        self.clk4x_rd_strb = Signal()

        # sdram_full
        self.specials += Instance(
            "BUFPLL",
            p_DIVIDE=4,
            i_PLLIN=unbuf_sdram_full,
            i_GCLK=self.cd_sys.clk,
            i_LOCKED=pll_lckd,
            o_IOCLK=self.cd_sdram_full_wr.clk,
            o_SERDESSTROBE=self.clk4x_wr_strb
        )

        self.comb += [
            self.cd_sdram_full_rd.clk.eq(self.cd_sdram_full_wr.clk),
            self.clk4x_rd_strb.eq(self.clk4x_wr_strb),
        ]

        # sdram_half
        self.specials += Instance(
            "BUFG",
            i_I=unbuf_sdram_half_a,
            o_O=self.cd_sdram_half.clk
        )

        clk_sdram_half_shifted = Signal()
        self.specials += Instance(
            "BUFG",
            i_I=unbuf_sdram_half_b,
            o_O=clk_sdram_half_shifted
        )

        clk = platform.request("ddram_clock")
        self.specials += Instance(
            "ODDR2",
            p_DDR_ALIGNMENT="NONE",
            p_INIT=0, p_SRTYPE="ASYNC",
            i_D0=1, i_D1=0, i_S=0, i_R=0, i_CE=1,
            i_C0=clk_sdram_half_shifted,
            i_C1=~clk_sdram_half_shifted,
            o_Q=clk.p
        )

        self.specials += Instance(
            "ODDR2",
            p_DDR_ALIGNMENT="NONE",
            p_INIT=0, p_SRTYPE="SYNC",
            i_D0=0, i_D1=1, i_S=0, i_R=0, i_CE=1,
            i_C0=clk_sdram_half_shifted,
            i_C1=~clk_sdram_half_shifted,
            o_Q=clk.n
        )

        # add verilog sources
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        vdir = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "matrix-voice-fpga")
        #platform.add_verilog_include_path(os.path.join(vdir, "third_party", "unisims"))
        platform.add_sources(os.path.join(vdir, "voice_core"))
        platform.add_verilog_include_path(os.path.join(vdir, "voice_core","wb_bram"))
        platform.add_verilog_include_path(os.path.join(vdir, "voice_core","wb_conbus"))
        platform.add_verilog_include_path(os.path.join(vdir, "voice_core","wb_dac"))
        platform.add_verilog_include_path(os.path.join(vdir, "voice_core","wb_everloop"))
        platform.add_verilog_include_path(os.path.join(vdir, "voice_core","wb_gpio"))
        platform.add_verilog_include_path(os.path.join(vdir, "voice_core","wb_mic_array"))
        platform.add_verilog_include_path(os.path.join(vdir, "voice_core","wb_spi_slave"))
        # End Verilog add



class BaseSoC(SoCSDRAM):
    csr_peripherals = (
        "ddrphy",
        #"analyzer",
        #"io",
        "spiflash",
    )
    csr_map_update(SoCSDRAM.csr_map, csr_peripherals)

    # FIXME: Add spiflash
    mem_map = {
       "spiflash": 0x20000000,  # (default shadow @0xa0000000)
    }
    mem_map.update(SoCSDRAM.mem_map)

    def __init__(self, platform, **kwargs):
        if 'integrated_rom_size' not in kwargs:
            kwargs['integrated_rom_size']=None
        if 'integrated_sram_size' not in kwargs:
            kwargs['integrated_sram_size']=0x4000
        
        kwargs['cpu_reset_address']=self.mem_map["spiflash"]+platform.gateware_size
        #kwargs['uart_baudrate']=115200


        clk_freq = (15 + Fraction(5, 8))*1000*1000 #15625000

        SoCSDRAM.__init__(self, platform, clk_freq, **kwargs) #with_uart=False,

        self.submodules.crg = _CRG(platform, clk_freq)

        # spi flash
        self.submodules.spiflash = spi_flash.SpiFlashSingle(
            platform.request("spiflash"),
            dummy=platform.spiflash_read_dummy_bits,
            div=platform.spiflash_clock_div)
        self.add_constant("SPIFLASH_PAGE_SIZE", platform.spiflash_page_size)
        self.add_constant("SPIFLASH_SECTOR_SIZE", platform.spiflash_sector_size)
        #self.flash_boot_address = self.mem_map["spiflash"]+platform.gateware_size
        self.register_mem("spiflash", self.mem_map["spiflash"],
            self.spiflash.bus, size=platform.spiflash_total_size)

        bios_size = 0x8000
        self.add_constant("ROM_DISABLE", 1)
        self.add_memory_region("rom", kwargs['cpu_reset_address'], bios_size)
        self.flash_boot_address = self.mem_map["spiflash"]+platform.gateware_size+bios_size


        # self.submodules.uart_phy = uart.RS232PHYModel(platform.request("serial"))
        # self.submodules.uart = uart.UART(self.uart_phy)

        # self.submodules.bridge = UARTWishboneBridge(platform.request("serial"), self.clk_freq, baudrate=115200)
        # self.add_wb_master(self.bridge.wishbone)

        # # Litescope for analyzing the BIST output
        # # --------------------
        # self.submodules.io = LiteScopeIO(8)
        # for i in range(8):
        #     try:
        #         self.comb += platform.request("user_led", i).eq(self.io.output[i])
        #     except:
        #         pass

        # analyzer_signals = [
        #     self.spiflash.bus,
        # #    self.spiflash.cs_n,
        # #    self.spiflash.clk,
        # #    self.spiflash.dq_oe,
        # #    self.spiflash.dqi,
        # #    self.spiflash.sr,
        # ]
        # self.submodules.analyzer = LiteScopeAnalyzer(analyzer_signals, 1024)

        # def do_exit(self, vns, filename="test/analyzer.csv"):
        #     self.analyzer.export_csv(vns, filename)

        # sdram
        sdram_module = MT47H32M16(self.clk_freq, "1:2")
        self.submodules.ddrphy = s6ddrphy.S6HalfRateDDRPHY(
            platform.request("ddram"),          
            sdram_module.memtype,
            rd_bitslip=2,
            wr_bitslip=3,
            dqs_ddr_alignment="C1"
        )

        controller_settings = ControllerSettings(
            with_bandwidth=True
        )

        self.register_sdram(self.ddrphy,
            sdram_module.geom_settings,
            sdram_module.timing_settings,
            controller_settings=controller_settings
        )

        self.comb += [
            self.ddrphy.clk4x_wr_strb.eq(self.crg.clk4x_wr_strb),
            self.ddrphy.clk4x_rd_strb.eq(self.crg.clk4x_rd_strb),
        ]

SoC = BaseSoC