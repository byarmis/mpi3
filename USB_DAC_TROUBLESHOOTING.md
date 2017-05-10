# USB DAC Issues and Troubleshooting

## First Attempt
I purchased the AudioQuest DragonFly Black with the intention of using it in this project as it seemed very well-suited for my purposes:

* It has what appears to be low power consumption since it's designed to work with mobile phones
* It's small
* It has pretty good audio and build quality

I also found using a USB DAC/amp that costs 10x more than the thing driving it mildly amusing.

~~Unfortunately, the AudioQuest DragonFly Black does *not* work with the Raspberry Pi Zero.~~  Acceptably, `pulseaudio` has to be installed for it to be detected and be properly used by `speaker-test`.  After installing it and attempting to play music (either through `mpg123` or `speaker-test`) resulted in no sound.  Turning the volume all the way up made the white noise faintly audible, indicating that some communication was going on, but no audio came out.

I did confirm that both the headphones I was using as well as the DragonFly Black worked and worked with Linux (Ubuntu 16.10).

Plugging it in with the Raspberry Pi on (leading to an expected brownout) or booting up the Pi after plugging it in did not matter and the audio problem remained.

Other attempted fixes included limiting the USB OTG port to USB 1.1 (full-speed) and overclocking the Raspberry Pi.

Looking at the output from `dmesg` indicates the cause of the problem.  On bootup, there's nothing suspicious, but when I first tried to interface with the DAC (either playing music with `mpg123`/`speaker-test` or changing the music volume with `alsamixer`), the below errors are generated repeatedly:

```
...

[ 1098.381359] usb 1-1: cannot submit urb 0, error -1: unknown error
[ 1098.391790] INFO:: schedule_periodic: Insufficient periodic bandwidth for periodic transfer.

[ 1098.391813] ERROR::dwc_otg_hcd_urb_enqueue:544: DWC OTG HCD URB Enqueue failed adding QTD. Error status -1

...
```

The most promising thing I found through Googling was [this](http://www.cl.cam.ac.uk/~atm26/ephemeral/rpi/dwc_otg/dwc_otg_hcd_queue.c) page containing the `dwc_otg_hcd_queue.c` file with the following code part-way down:

```c
/**
 * Schedules an interrupt or isochronous transfer in the periodic schedule.
 *
 * @param hcd The HCD state structure for the DWC OTG controller.
 * @param qh QH for the periodic transfer. The QH should already contain the
 * scheduling information.
 *
 * @return 0 if successful, negative error code otherwise.
 */
static int schedule_periodic(dwc_otg_hcd_t * hcd, dwc_otg_qh_t * qh)
{
    int status = 0;

    status = periodic_channel_available(hcd);
    if (status) {
        DWC_INFO("%s: No host channel available for periodic " "transfer.\n", __func__);    //NOTICE
        return status;
    }

    status = check_periodic_bandwidth(hcd, qh);
    if (status) {
        DWC_INFO("%s: Insufficient periodic bandwidth for " "periodic transfer.\n", __func__);  //NOTICE
        return status;
    }

    status = check_max_xfer_size(hcd, qh);
    if (status) {
        DWC_INFO("%s: Channel max transfer size too small " "for periodic transfer.\n", __func__);  //NOTICE
        return status;
    }

    if (hcd->core_if->dma_desc_enable) {
        /* Don't rely on SOF and start in ready schedule */
        DWC_LIST_INSERT_TAIL(&hcd->periodic_sched_ready, &qh->qh_list_entry);
    }
    else {
    /* Always start in the inactive schedule. */
    DWC_LIST_INSERT_TAIL(&hcd->periodic_sched_inactive, &qh->qh_list_entry);
    }

    /* Reserve the periodic channel. */
    hcd->periodic_channels++;

    /* Update claimed usecs per (micro)frame. */
    hcd->periodic_usecs += qh->usecs;

    return status;
}
```

and this `check_periodic_bandwidth` function:

```c
/**
 * Checks that there is sufficient bandwidth for the specified QH in the
 * periodic schedule. For simplicity, this calculation assumes that all the
 * transfers in the periodic schedule may occur in the same (micro)frame.
 *
 * @param hcd The HCD state structure for the DWC OTG controller.
 * @param qh QH containing periodic bandwidth required.
 *
 * @return 0 if successful, negative error code otherwise.
 */
static int check_periodic_bandwidth(dwc_otg_hcd_t * hcd, dwc_otg_qh_t * qh)
{
    int status;
    int16_t max_claimed_usecs;

    status = 0;

    if ((qh->dev_speed == DWC_OTG_EP_SPEED_HIGH) || qh->do_split) {
        /*
         * High speed mode.
         * Max periodic usecs is 80% x 125 usec = 100 usec.
         */

        max_claimed_usecs = 100 - qh->usecs;
    } else {
        /*
         * Full speed mode.
         * Max periodic usecs is 90% x 1000 usec = 900 usec.
         */
        max_claimed_usecs = 900 - qh->usecs;
    }

    if (hcd->periodic_usecs > max_claimed_usecs) {
        DWC_INFO("%s: already claimed usecs %d, required usecs %d\n", __func__, hcd->periodic_usecs, qh->usecs);    //NOTICE
        status = -DWC_E_NO_SPACE;
    }

    return status;
}
```

Since the OTG port does not have sufficient bandwidth to provide what the DAC requested, it just errors out.

The same behavior was observed with the Fiio E10k, which is incredibly frustrating-- many pages online, including:

* [This](https://www.reddit.com/r/raspberry_pi/comments/2ynxpt/turn_your_raspberry_pi_into_a_music_player/) Reddit thread
* [This](http://www.raspyfi.com/raspberry-pi-usb-dac-and-raspyfi-supported-dacs/) raspyFi page 
* [This](http://www.runeaudio.com/forum/fiio-e10k-t930.html) rune audio post

all indicate that one or both of the two USB DACs I tried should work but they do not.  I wonder if there's an appreciable difference in USB speed with the Raspberry Pi Zero (W) compared with the normal "full" Raspberry Pis.

I did a cursory test of the USB transfer speed of the Raspberry Pi Zero compared with my desktop computer (Ubuntu 16.10)

| Computer            | Transfer Speed |
| ------------------- | -------------- |
| Desktop             | 18.66 MB/sec   |
| Raspberry Pi Zero W | 6.219 MB/sec   |

The file used was the compressed zip file of the Raspbian Jessie Lite image since the drive used had only 1GB storage and that was the largest file I had that was less than that size.

I thought that this was the end of the road for the DragonFly Black

*but then...*

## Second Attempt

### Good News!
Adding the following line to `/boot/config.txt` solved the issue-- well, at least the issue that I had run into previously:

```
dtoverlay=dwc2
```

I found it in [this](https://volumio.org/forum/with-new-rpi-zero-t6050-50.html) thread and, for some reason, it worked.  After additional searching, that configuration option is generally referenced with regards to making the Raspberry Pi Zero behave like a USB HID (mouse, keyboard, etc.).  For some reason though, adding that option here makes sound come out!

### Bad News!

*... but not perfectly*

Unfortunately, the audio isn't perfect.

When running `speaker-test` (with or without the `-c 2` option for stereo channel testing) or `aplay` with a sample .wav file, there are pops and crackles during sound playback.  They somewhat appear related to the relative volume of the sound being played in that the hard "c" and the sharp "t" in "front center" has more pops and crackles than the middle of the first word.

This behavior is not observed with the Fiio E10k.

Alternative power sources were tried: alternate USB power sources as well as battery power (through the PowerBoost), neither resolving the popping issue.

This time, the cause appears to be due to USB jitter.  Running `speaker-test` along with `watch`ing `cat /proc/asound/card1/stream0`, the output is something like this:

#### `speaker-test`

```
speaker-test 1.0.28

Playback device is default
Stream parameters are 48000Hz, S16_LE, 1 channels
Using 16 octaves of pink noise
Rate set to 48000Hz (requested 48000Hz)
...
```

#### `cat /proc/asound/card1/stream0`

```
AudioQuest AudioQuest DragonFly Black v1.5 at usb-20980000.usb-1, full speed : U
SB Audio

Playback:
  Status: Running
    Interface = 2
    Altset = 1
    Packet Size = 360
    Momentary freq = 48050 Hz (0x30.0ccc)
    Feedback Format = 10.14
  Interface 2
    Altset 1
    Format: S24_3LE
    Channels: 2
    Endpoint: 3 OUT (ASYNC)
    Rates: 44100, 48000, 88200, 96000
```

Note that the `Momentary freq` is just 50 Hz higher than the requested frequency.  Sometimes, the frequency is seen to be a similar amount (50 - 100 Hz) lower instead.  

## The Plot Thickens

After `speaker-test` has played pink noise for several minutes, the `Momentary freq` returns back to `48000 Hz (0x30.0000)` and the popping and crackling goes away.  If I stop `speaker-test` for several seconds (5 count) and start it back up again, the pink noise resumes without any issues.  If I instead wait a little longer (10 count) to resume the `speaker-test`, the `Momentary freq` will again be slightly higher or lower than it should be.  It settles down and corrects itself after several moments.

A similar behavior is not observed  listening to music, however.  Running `mpg123` and listening to an .mp3 file, there is always crackling and popping and `Momentary freq` does not appear to settle to the bit-rate of the song even when given additional time compared with the `speaker-test`.

Taxing the CPU with running [`dd if=/dev/urandom | bzip2 -9 >> /dev/null`](http://stackoverflow.com/questions/2925606/how-to-create-a-cpu-spike-with-a-bash-command#comment27590337_2927364) while, at the same time, running a `speaker-test` and `watch`ing `/proc/asound/card1/stream0` does not appear to hinder the `Momentary freq`'s return back to 48 kHz, taking roughly the same amount of time to settle back when running a speaker test.  The `bzip2` process causes roughly 70% CPU load.

Trying the following (taken from [this](https://volumio.org/forum/solution-pops-and-clicks-t772.html) forum post) did not appear to help, unfortunately:

#### `/boot/cmdline.txt`

```
dwc_otg.fiq_enable=1 dwc_otg.fiq_fsm_enable=1 dwc_otg.fiq_fsm_mask=0x3
```

