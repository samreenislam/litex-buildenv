#!/bin/bash

SETUP_SRC=$(realpath ${BASH_SOURCE[0]})
SETUP_DIR=$(dirname $SETUP_SRC)

set -x
set -e

apt-get install -y realpath
apt-get install -y wget
apt-get install -y build-essential
# Need gpg to do the unencryption of Xilinx tools
apt-get install -y gnupg
# migen
# iverilog and gtkwave are needed for migen
apt-get install -y iverilog gtkwave
# FIXME: Also need to install the vpi module....
# cd vpi
# make all
# sudo make install

# misoc
# Nothing needed
# FIXME: Also need to install toools....
# cd tools
# make
# sudo make install

# liteeth
# Nothing needed

# libfpgalink

while true; do
    read -p "Are you working under a proxy server? (yes/no) " yn
    case $yn in
        [Yy]* ) echo "Enter the proxy site and port number"
				read -p "Enter the proxy adress : " siteproxy
				read -p "Enter port number : " portnumber
				export http_proxy=http://$siteproxy:$portnumber
                export https_proxy=https://$siteproxy:$portnumber
                break;;
        [Nn]* ) break;;
        * ) echo "Please answer yes or no.";;
    esac
done

sudo apt-get install -y libreadline-dev libusb-1.0-0-dev libftdi-dev python-yaml fxload

# Load custom udev rules
(
	cp -uf  $SETUP_DIR/52-hdmi2usb.rules /etc/udev/rules.d/
	sudo adduser $USER dialout
)

# Get the vizzini module needed for the Atlys board
sudo apt-get install -y software-properties-common
sudo -E add-apt-repository -y ppa:timvideos/fpga-support
sudo apt-get update
sudo apt-get install -y vizzini-dkms
sudo apt-get install -y ixo-usb-jtag
