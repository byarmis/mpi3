# Introduction

This is part-guide, part-build log, part-notepad.  Not everything here will remain here as this project progresses, but it'll probably remain somewhere.  I might make a buildlog.md file or something like that and move everything over there.

# Hardware (Electronics)

* Raspberry Pi Zero or Zero W
* Micro SD Card.  You will probably want a larger one than you'd normally put in a Raspberry Pi Zero
* Pin headers
* [Pi Supply PaPiRus Zero ePper pHAT v1.2](https://www.adafruit.com/product/3335)
* [PowerBoost 1000 Charger](https://www.adafruit.com/product/2465)
* [2500 mAh Lithium Ion Polymer Battery](https://www.adafruit.com/product/328) 
* [Small USB OTG Adapter](https://www.adafruit.com/product/2910)
* USB DAC / Amp (See discussion below)
* Sliding switch
  * Exact switch to be determined
* Female USB A Connector
  * One might come with the PowerBoost
* Various electronic hardware including wires, solder, soldering iron, wire strippers, micro USB power supply

# Set-Up and Installation

It is suggested that you use a computer to SSH into the Raspberry Pi Zero in order to set up and configure.  I used my desktop Linux computer and a Mac laptop will be able to SSH in with minimal issues also.  A Windows computer will also be able to SSH in, but will require additional software.  The Raspberry Pi documentation [here](https://www.raspberrypi.org/documentation/remote-access/ssh/) is pretty good.

1. Flash SD card with [Raspbian Lite](https://www.raspberrypi.org/downloads/raspbian/) or another distro of your choice.  Since this will be headless, you probably don't need a windows manager so the leaner the better.
2. Set up wifi, if applicable
    
    In `/etc/wpa_supplicant/wpa_supplicant.conf`, add network SSID(s) and password(s):
    
    ```
    network={
        ssid="NetworkName"
        psk="NetworkPassword"
    }
    ```
    
3. Add a file to the `/boot/` folder called `ssh` to allow SSH by default.
4. Now would be a good time to move the music over to the `~/Music/` folder, creating it if it does not currently exist.  If you want to add music later, you could also use `sftp` to wirelessly upload it.  I originally wanted to use Dropbox to asynchronously synchronize music folders, but Dropbox doesn't have an ARM version (yet?).
5. Note that the above three steps can be done by plugging the micro SD card into another computer and navigating the file system (Windows can only see the `/boot/` folder and not any others).
6. Boot up, SSH in, and update
  * `sudo apt-get update`
  * `sudo apt-get upgrade`
  * `sudo apt-get dist-upgrade`
  * `sudo apt-get autoremove`
  * `sudo apt-get install rpi-update git mpg123 vorbis-toolbox`
  * `sudo rpi-update`
7. Run `sudo raspi-config` and change to auto-login to terminal on boot-up.  Also, update your timezone and wifi settings since we're here
8. Install the [PaPiRus python package](https://github.com/PiSupply/PaPiRus) by running `curl -sSL https://pisupp.ly/papiruscode | sudo bash`
9. Shutdown (`sudo poweroff`) and plug in the DAC using the OTG adapter
10. Boot up and configure your default sound output to be the USB DAC.  I suggest [this](https://raspberrypi.stackexchange.com/a/44825) answer on the Raspberry Pi Stack Exchange.  Test to make sure that everything works by running `speaker-test -c 2` which will play pink noise over the left, followed by the right, channels.
11. Disable the HDMI output per [this](https://www.jeffgeerling.com/blogs/jeff-geerling/raspberry-pi-zero-conserve-energy) page to save a couple milliamps.

# USB DAC and Amp Selection

Since the Raspberry Pi Zero does not have any built-in audio outputs and the preferred method of getting audio out over the I2S interface is not possible due to the PaPiRus taking up the necessary GPIO pins, I decided to go with a USB DAC/amp chip.  There are already many options out there to choose from, as we can see below, and are theoretically easy to work with.

## Candidates

* [UGREEN USB Audio Adapter](https://www.amazon.com/gp/product/B01N905VOY/)
* [CableCreation USB Audio Adapter](https://www.amazon.com/gp/product/B01H2XF8V8/)
* [TROND AC2 External USB Sound Card](https://www.amazon.com/gp/product/B014ANW4VU/)
* [AudioQuest DragonFly Black](https://www.amazon.com/gp/product/B01DP5JHHI/)
* [Fiio E10k](https://www.amazon.com/FiiO-E10K-Headphone-Amplifier-Black/dp/B00LP3AMC2/)
  * This was mostly added as a sanity check.  See [USB DAC Troubleshooting](USB_DAC_TROUBLESHOOTING.md)

## Power Consumption

The testing setup, pictured below, for measuring the power consumption is pretty standard:
![Testing Setup](/imgs/IMG_20170511_181704.jpg)

There is a 5v USB power supply being fed through the multimeter and into the Raspberry Pi.

|   **DAC**       | **Off** | **On / Idle** | **Pink Noise**  |     | *Off Standby Time* | *Music Playing Time* |
|:--------------- | ------- | ------------- | --------------- | --- | ------------------ | -------------------- |
| None            | 35 mA   | 113 mA        | 114 mA          |     | 62 hr              | 19 hr                |
| DragonFly Black | 74 mA   | 152 mA        | 158 mA          |     | 29 hr              | 13 hr                |
| TROND AC2       | 36 mA   | 147 mA        | 150 mA          |     | 61 hr              | 14 hr                |
| UGREEN          | 36 mA   | 145 mA        | 148 mA          |     | 61 hr              | 14 hr                |
| CableCreation   | 37 mA   | 148 mA        | 151 mA          |     | 59 hr              | 14 hr                |

The current draw even after being powered off is surprisingly high-- this will definitely require adding a physical power switch to the PowerBoost to disable it after the Pi is shutdown.

In general, all of the DACs draw roughly the same amount of power either playing songs or not.  The additional power draw of the DragonFly Black is probably due to its LED that illuminates and changes color based on the bitrate of the music being played through it.  Unfortunately, this LED remains on even after shutting down the Pi.  This downside, however, is negated by the fact that the power should be cut after shutdown anyway. 
