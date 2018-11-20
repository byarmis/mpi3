# Introduction

This is part-guide, part-build log, part-notepad.  Not everything here will remain here as this project progresses, but it'll probably remain somewhere.  I might make a buildlog.md file or something like that and move everything over there.

# Hardware
## Electronics

* Raspberry Pi Zero or Zero W
* Micro SD Card.  You will probably want a larger one than you'd normally put in a Raspberry Pi Zero
* Pin headers
* [Pi Supply PaPiRus Zero ePper pHAT v1.2](https://www.adafruit.com/product/3335)
* [PowerBoost 1000 Charger](https://www.adafruit.com/product/2465)
* [2500 mAh Lithium Ion Polymer Battery](https://www.adafruit.com/product/328) 
* [Small USB OTG Adapter](https://www.adafruit.com/product/2910)
* [DragonFly Black USB DAC / Amp](https://www.amazon.com/AudioQuest-DragonFly-Black-Headphone-Amplifier/dp/B01DP5JHHI/ref=sr_1_3/134-4811355-5992615?ie=UTF8&qid=1503088617&sr=8-3&keywords=dragonfly+black) (See OTHER FILE for discussion)
  * You can use a different one, but the 3D-printed case will require modifications
* [Sliding switch](https://www.adafruit.com/product/805)
* Female USB A Connector
  * One should with the PowerBoost
* Various electronic hardware including wires, solder, soldering iron, wire strippers, micro USB power supply

## Nuts and bolts

`TBD`

## 3D-Printed

`TBD`

# Set-Up and Installation

## Software

It is suggested that you use a computer to SSH into the Raspberry Pi Zero in order to set up and configure.  I used my desktop Linux computer but a Mac laptop will be able to SSH in with minimal issues also.  A Windows computer will also be able to SSH in, but will require additional software (PuTTY, I think should work).  The Raspberry Pi documentation [here](https://www.raspberrypi.org/documentation/remote-access/ssh/) is pretty good.

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
4. Now would be a good time to move the music over to the `/home/pi/Music/` folder, creating it if it does not currently exist since transferring a couple of gigabytes would definitely be faster over a USB card reader compared to the Pi's built-in WiFi.  If you want to add music later, you could also use `sftp` to wirelessly upload it.  I originally wanted to use Dropbox to asynchronously synchronize music folders, but Dropbox doesn't have an ARM version (yet?).
5. Note that the above three steps can be done by plugging the micro SD card into another computer and navigating the file system (Windows can only see the `/boot/` folder and not any others).
6. Boot up, SSH in, and update
  * `sudo apt-get update`
  * `sudo apt-get upgrade`
  * `sudo apt-get dist-upgrade`
  * `sudo apt-get autoremove`
  * `sudo apt-get install rpi-update git mpg123 sqlite3`
  * `sudo rpi-update`
7. Run `sudo raspi-config` and change to auto-login to terminal on boot-up.  Also, update your timezone and WiFi settings since we're here
8. Install the [PaPiRus python package](https://github.com/PiSupply/PaPiRus) by running `curl -sSL https://pisupp.ly/papiruscode | sudo bash`
9. Shutdown (`sudo poweroff`) and plug in the DAC using the OTG adapter
10. Boot up and configure your default sound output to be the USB DAC.  I suggest [this](https://raspberrypi.stackexchange.com/a/44825) answer on the Raspberry Pi Stack Exchange.  Test to make sure that everything works by running `speaker-test -c 2` which will play pink noise over the left, followed by the right, channels.
11. Disable the HDMI output per [this](https://www.jeffgeerling.com/blogs/jeff-geerling/raspberry-pi-zero-conserve-energy) page to save a couple milliamps.

## Hardware

### PowerBoost 1000

The PowerBoost comes with resistors that signal over the data lines an iPhone or iPad can draw higher current than normal (500 mA).  These aren't neccessary and I worry about their effects on the data lines that will be connected later.  There's also a really bright LED that indicates that the PowerBoost is on-- this is duplicating the function of the green LED already on the Raspberry Pi and is really bright.

The components that can be removed are:

* R9, R10, R11, and R12-- the resistors on the data lines
* R5 and LED2-- the LED that indicates power

To remove the unneeded components, I just used a soldering iron with a blob of solder on the tip and a pair of tweezers.  I went back after with some desoldering braid to clean up the extra solder.  Be sure to leave the capacitor that's near the inductor.

![PowerBoost without components](/imgs/powerboost_no_components.jpg)

