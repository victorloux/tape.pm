# tape.pm

This is a rough dump of the tape.pm project source, *not well documented* but hopefully the code can be of use to anyone as a starter for a similar project, any question on it please email me at <io@victorloux.uk>. The whole thing is a prototype so don't expect code to be production-ready or be very clean.

## What is it even?

> tape.pm is an interactive installation accompanying innovative musical instruments. It encourages experimentation and exploration by offering a way to record improvisations on the instrument “in hindsight”, providing the players with a physical token that can be reused and shared later on. It is an exploration of playful and purposefully ambiguous design to trigger curiosity and multiple interpretations by the people who play with an instrument.

In other words: it's a reverse recording machine. It *constantly* records what it hears on its microphone/line input, puts the last 60 seconds in a buffer, and whenever the button is pressed, it uses a thermal printer to print a unique code with a URL, and when people go to that URL they can listen to a one-minute recording of what they've played before pressing the button. It's a way to experiment with instruments and go back on that “eureka!” moment when you've done something that suddenly sounded cool.

It's been developed as part of my placement with [b00t](http://www.b00tconsultants.com) and has been exhibited alongside the [Collidoscope](http://collidoscope.io/) at Sónar+D, and with the [Magnetic Resonator Piano](http://music.ece.drexel.edu/research/mrp) at Intersections 2016.

![Photograph of the box from above](casing/image1.png?raw=true "tape.pm")
![Photograph of the box from front](casing/image2.jpg?raw=true "tape.pm")

Listen to examples at http://tape.pm/npzp333 (Collidoscope) and http://tape.pm/6092kkw (MRP)

## Hardware

The casing is laser-cut on a thick (5mm I think?) plexiglas sheet, see instructions and PDF file for more details. It's got enough space to fit everything.

You need:

* A Raspberry Pi 3 (or 2 with a wifi connection)
* A soundcard to connect a microphone
* A thermal printer (I used the Adafruit serial one, the code can probably be adapted to use any USB one)
* A pushbutton connected to GPIO pin 23

## Software

### Box

If you use a Raspberry Pi 3 and the Adafruit printer you'll need to go through this to use the serial connection, and use the modified library provided here (which work on the different port and on Python 3) that'll work (except images, didn't fix that yet). Set up your Pi to autoconnect to a wifi network (NetworkManager was my best bet).

Copy all software code in a folder called `installation` in your home folder, and check it works with `sudo python3 record.py --startup`. (⚠️ you *need* to use sudo else you can't access GPIO and your button won't work). If all goes well straight away (it won't) it should, after a bit, print a message confirming you're connected to the wifi, with IP addresses (useful for ssh-ing into the box). If you press the button it should print out a code and a MP3 should be in your `media` folder. Check the logs if not.

To launch at boot: `sudo crontab -e` and add the line:

```
@reboot sh /home/pi/installation/startup.sh >/home/pi/installation/cronlog 2>&1
```

### Server

The server is a very basic piece of PHP. The box itself uploads MP3s through /uploads.php, with a secret key to avoid anyone uploading anything (this really isn't secure if you don't use HTTPS, and you should also bar your server to serve or execute anything in that folder that isn't a .mp3). In the box side, edit the endpoint and keys to match (hardcoded into `_save.py:16` and :17).

The frontend requires you to copy files in `script/` from SoundManager2 and the 360 example available here: http://schillmania.com/projects/soundmanager2/

