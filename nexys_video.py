#!/usr/bin/env python3

from nexys_base import *

from litevideo.output.hdmi.s7 import S7HDMIOutClocking
from litevideo.output.hdmi.s7 import S7HDMIOutEncoderSerializer
from litevideo.output.hdmi.s7 import S7HDMIOutPHY

from litevideo.output.core import TimingGenerator


class VideoOutSoC(BaseSoC):
    def __init__(self, platform, *args, **kwargs):
        BaseSoC.__init__(self, platform, *args, **kwargs)

        pads = platform.request("hdmi_out")
        self.comb += pads.scl.eq(1)

        # # #

        self.submodules.vtg = ClockDomainsRenamer("pix")(TimingGenerator(1))
        self.comb += [
            self.vtg.timing.valid.eq(1),

            self.vtg.timing.hres.eq(1920),
            self.vtg.timing.hsync_start.eq(1920+88),
            self.vtg.timing.hsync_end.eq(1920+88+44),
            self.vtg.timing.hscan.eq(2200),

            self.vtg.timing.vres.eq(1080),
            self.vtg.timing.vsync_start.eq(1080+4),
            self.vtg.timing.vsync_end.eq(1080+4+5),
            self.vtg.timing.vscan.eq(1125),

            self.vtg.pixels.valid.eq(1)
        ]

        self.submodules.hdmi_clocking = S7HDMIOutClocking(self.crg.clk100)
        self.submodules.hdmi_phy = S7HDMIOutPHY(pads)
        self.comb += [
            self.hdmi_phy.hsync.eq(self.vtg.phy.hsync),
            self.hdmi_phy.vsync.eq(self.vtg.phy.vsync),
            self.hdmi_phy.de.eq(self.vtg.phy.de),
            self.hdmi_phy.r.eq(0x00),
            self.hdmi_phy.g.eq(0x00),
            self.hdmi_phy.b.eq(0xff),
            self.vtg.phy.ready.eq(1)
        ]
        self.submodules.clk_es = S7HDMIOutEncoderSerializer(pads.clk_p, pads.clk_n, bypass_encoder=True)
        self.comb += self.clk_es.data.eq(Signal(10, reset=0b0000011111))


def main():
    parser = argparse.ArgumentParser(description="Nexys LiteX SoC")
    builder_args(parser)
    soc_sdram_args(parser)
    parser.add_argument("--nocompile-gateware", action="store_true")
    args = parser.parse_args()

    platform = nexys.Platform()
    soc = VideoOutSoC(platform, **soc_sdram_argdict(args))
    builder = Builder(soc, output_dir="build",
                      compile_gateware=not args.nocompile_gateware,
                      csr_csv="test/csr.csv")
    vns = builder.build()

if __name__ == "__main__":
    main()

