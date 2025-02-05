# Some directions for this MATRIX Voice fork

Main changes include:
- Adding matrix_voice definitions to `platforms` folder
- Adding matrix_voice SoC configurations to `targets` folder
- Adding our DDR2 RAM definition in `modules.py` in the repo's main folder which is supposed to replace `third_party/litedram/litedram/modules.py`


Primarily followed the instructions [here](https://ewen.mcneill.gen.nz/blog/entry/2018-01-17-fupy-fpga-micropython-on-mimas-v2-and-arty-a7/) for the Mimas V2.

Make sure to have the Xilinx ISE installed to compile for the MATRIX Voice's Spartan-6. Follow the steps [here](https://www.hackster.io/matrix-labs/get-started-with-fpga-programming-on-matrix-devices-525cd5) to do so.

First cloned the following repos in folder of choice

```
git clone https://github.com/samreenislam/litex-buildenv.git
git clone https://github.com/litex-hub/litex-buildenv-udev
```

From second repo, copy `99-hdmi2usb-permissions.rules` permission to `/etc/udev/rules.d` and `/lib/udev/rules.d`. Log out of terminal session & log back in.

Enter `litex-buildenv` repo and run the following

```
cd litex-buildenv

CPU=vexriscv
PLATFORM=matrix_voice
TARGET=base
FIRMWARE=micropython
export CPU PLATFORM TARGET FIRMWARE
```


Then run the following script for the appropriate external module downloads

```
scripts/download-env.sh
```

- Copy `modules.py` in the main folder of the repo and replace the `modules.py` file in `third_party/litedram/litedram` with it. This is to include the MATRIX Voice's DDR2 RAM module definition.

- Copy `matrix_voice.py` in the `platforms` folder of the repo into `third_party/migen/migen/build/platforms`.

Then enter the environment.

```
source scripts/enter-env.sh
```

At this point, you should have a prompt similar to `(LX P=matrix_voice C=vexriscv F=micropython)`.


Then build the FPGA bit file as stated in the article linked above with

```
make gateware
```


Compile the micropython firmware with the following

```
scripts/build-micropython.sh
```


Flash the top.bit file to the MATRIX Voice's Spartan-6 using the directions [here](https://matrix-io.github.io/matrix-documentation/matrix-voice/resources/fpga/).


### TO-DO: Flash BIOS onto FPGA SoC after flashing top.bit.


---

# LiteX Build Environment

[The LiteX Build Environment](https://github.com/timvideos/litex-buildenv)
is a tool for easily developing
[LiteX](https://github.com/enjoy-digital/litex) based systems. It was
originally designed to make the [TimVideos' HDMI2USB](https://hdmi2usb.tv) easy
to develop, but has now expanded to support multiple projects.

## Quick Links

 * [LiteX Build Environment Wiki](https://github.com/timvideos/litex-buildenv/wiki)
 * [Getting Started Guide](https://github.com/timvideos/litex-buildenv/wiki/Getting-Started)

 * TBD: [LiteX Build Environment Docs](https://litex-buildenv.readthedocs.io)

 * Dependency documentation
   - Migen - [[Website](http://m-labs.hk/migen/index.html)] [[User Guide](http://m-labs.hk/migen/manual/)] [[Code Repository](https://github.com/m-labs/migen)]
   - [Enjoy Digital Website](http://www.enjoy-digital.fr/)
   - [LiteX GitHub Repository](https://github.com/enjoy-digital/litex)

 * Projects using LiteX Build Environment:
   - [HDMI2USB](http://hdmi2usb.tv/) - The HDMI2USB project develops affordable hardware options to record and stream HD videos (from HDMI & DisplayPort sources) for conferences, meetings and user groups.
   - [FuPy](https://fupy.github.io) - The aim of the FuPy project is to make MicroPython run on FPGAs using the LiteX & Migen+MiSoC technologies. This allows you to do full stack development (FPGA gateware & soft CPU firmware) in Python!

---

## Important Terminology

 * [Gateware](https://github.com/timvideos/litex-buildenv/wiki/Gateware) - The FPGA configuration.
 * [Soft CPU](https://github.com/timvideos/litex-buildenv/wiki/Soft-CPU) - A CPU running inside the FPGA.
 * [Firmware](https://github.com/timvideos/litex-buildenv/wiki/Firmware) - The software running on the `soft CPU` inside the FPGA.

## Structure

![LiteX BuildEnv Structure Image](https://docs.google.com/drawings/d/e/2PACX-1vTfB_DQ3PXJWKrERnzkGoWdKsTfuI3Kk-9rF1oBDB8NM44qZefU_O_H7rdNoN5cIWZmqzfIm1ftz52B/pub?w=419&h=485)

## [Boards](https://github.com/timvideos/litex-buildenv/wiki/Boards)

The LiteX Build Environment supports a
[large number of FPGA boards](https://github.com/timvideos/litex-buildenv/wiki/Boards),
but not all boards can be used for all projects.

## [Firmware](https://github.com/timvideos/litex-buildenv/wiki/Firmware)

 * [HDMI2USB](https://github.com/timvideos/litex-buildenv/wiki/HDMI2USB) - The firmware currently used for the HDMI2USB project.
 * [Bare Metal](https://github.com/timvideos/litex-buildenv/wiki/Bare-Metal) - Your own firmware running directly on the soft CPU in the FPGA.
 * [Zephyr](https://github.com/timvideos/litex-buildenv/wiki/Zephyr) - Support for [Zephyr RTOS](https://www.zephyrproject.org/).
 * [Linux](https://github.com/timvideos/litex-buildenv/wiki/Linux) - Support for Linux.

## [Gateware](https://github.com/timvideos/litex-buildenv/wiki/Gateware)

The Gateware is the configuration which generates our FPGA bitstream.  It
is generally defined by a `platform` and a `target`.  You can find details
for these under the `platform` and `target` directories in this project.

 * `Platform` - Represents the FPGA platform/devboard for which we will build
   the bitstream. (i.e. `sim` (Verilator Simulator), `arty` , `opsis`)
 * `Target` - There are multiple targets for each platform, this represents an
   SoC configuration for our target application. (i.e. `base`, `net`, `video`)

## [Environment](https://github.com/timvideos/litex-buildenv/wiki/Environment)

The environment is the shell setup and software packages provided by `litex-buildenv`
which allow for litex based FPGA development.  It provides development, build
and troubleshooting capabilities.

To bootstrap or update your environment one generally does:

```
# Download the debian packages needed to support litex environment.  Usually
# we only do this once.
./scripts/download-env-root.sh

# Download/update the litex specific packages (python, verilator, submodules etc)
./scripts/download-env.sh

# Enter the Dev/Debug/Build environment
export PLATFORM=arty TARGET=net CPU=or1k
source ./scripts/enter-env.sh
```

## [Applications](https://github.com/timvideos/litex-buildenv/wiki/Applications)

FIXME: Put stuff here.

![LiteX Application Relationship](https://docs.google.com/drawings/d/e/2PACX-1vTLVQXwkH3p5ZvN-7nIMxRXOyFEsg2x5_yrd3wREw3vaWr3Mc-_P7kfTbeQ--BN0k5VjQgxHchliyno/pub?w=1398&h=838)

## [Other Topics](https://github.com/timvideos/litex-buildenv/wiki/Other-Topics)

FIXME: Put stuff here.

---

# License

This code was developed by the people found in the [AUTHORS](AUTHORS) file
(including major contributions from [EnjoyDigital](http://enjoy-digital.fr))
and released under a [BSD/MIT license](LICENSE).

Code under the [third_party](third_party/) directory comes from external
sources and is available in their own licenses.

# Contact

TimVideo.us:

 * Mailing List:
   * https://groups.google.com/forum/#!forum/hdmi2usb
     [[Join](https://groups.google.com/forum/#!forum/hdmi2usb/join)]
   * hdmi2usb@googlegroups.com

 * IRC:
   * irc://irc.freenode.net/#timvideos
     [[Web Interface](http://webchat.freenode.net/?channels=timvideos)]

EnjoyDigital:
 * florent@enjoy-digital.fr
