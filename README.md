# Introduction

# Hardware (Electronics)

* Raspberry Pi Zero or Zero W
* Micro SD Card.  You will probably want a larger one than you'd normally put in a Raspberry Pi Zero for the various songs
* Pin headers
* [Pi Supply PaPiRus Zero ePper pHAT v1.2](https://www.adafruit.com/product/3335)
* [PowerBoost 1000 Charger](https://www.adafruit.com/product/2465)
* [Small USB OTG Adapter](https://www.adafruit.com/product/2910)
* [2500 mAh Lithium Ion Polymer Battery](https://www.adafruit.com/product/328) 
* USB DAC / Amp (See discussion below)
* Sliding switch
  * Exact switch to be determined
* Female USB A Connector
  * One might come with the PowerBoost
* Various electronic hardware including wires, solder, soldering iron, wire strippers, micro USB power supply

# Set-Up and Installation

1. Flash SD card with [Raspbian Lite](https://www.raspberrypi.org/downloads/raspbian/) or another distro of your choice
2. Set up wifi if applicable
    
    In `/etc/wpa_supplicant/wpa_supplicant.conf`, add network SSID and password:
    
    ```
    network={
        ssid="NetworkName"
        psk="NetworkPassword"
    }
    ```
    
3. Add a file to the `/boot/` folder called `ssh`, if you want to allow SSH by default.
4. Boot up and update
  * `sudo apt-get update`
  * `sudo apt-get upgrade`
  * `sudo apt-get dist-upgrade`
  * `sudo apt-get autoremove`
  * `sudo apt-get install rpi-update git mpg123 vorbis-toolbox`
  * `sudo rpi-update`
5. Run `sudo raspi-config` and change to auto-login to terminal on boot-up.  Also, update your timezone and WiFi settings since we're here
6. Install the [PaPiRus python package](https://github.com/PiSupply/PaPiRus) by running `curl -sSL https://pisupp.ly/papiruscode | sudo bash`
7. Shutdown (`sudo poweroff`) and plug in the DAC using the OTG adapter
8. Boot up and configure your default sound output to be the USB DAC.  I suggest [this](https://raspberrypi.stackexchange.com/a/44825) answer on the Raspberry Pi Stack Exchange.  Test to make sure that everything works by running `speaker-test -c 2` which will play pink noise over the left, followed by the right, channels.

# USB DAC and Amp Selection

Since the Raspberry Pi Zero does not have any built-in audio outputs and the preferred method of getting audio out over the I2S interface is not possible due to the PaPiRus taking up the necessary GPIO pins, I decided to go with a USB DAC/amp chip.  There are already many options out there to choose from, as we can see below.

## Candidates

* [UGREEN USB Audio Adapter](https://www.amazon.com/gp/product/B01N905VOY/)
* [CableCreation USB Audio Adapter](https://www.amazon.com/gp/product/B01H2XF8V8/)
* [TROND AC2 External USB Sound Card](https://www.amazon.com/gp/product/B014ANW4VU/)
* [AudioQuest DragonFly Black](https://www.amazon.com/gp/product/B01DP5JHHI/)
* [Fiio E10k](https://www.amazon.com/FiiO-E10K-Headphone-Amplifier-Black/dp/B00LP3AMC2/)
  * This was mostly added as a sanity check

## False Starts and Failures

Originally, I purchased the AudioQuest DragonFly Black with the intention of using it in this project as it seemed very well-suited: 

* It has what appears to be low power consumption since it's designed to work with mobile phones
* It's small
* It's pretty good quality

I also found using a USB DAC/amp that costs 10x more than the thing driving it mildly amusing.

Unfortunately, the AudioQuest DragonFly Black does *not* work with the Raspberry Pi Zero.  Acceptably, `pulseaudio` has to be installed for it to work properly.  After installing it and attempting to play music (either through `mpg123` or `speaker-test`
Plugging it in with the Raspbeery Pi on (leading to an expected brownout) or booting up the Pi after plugging it in.
