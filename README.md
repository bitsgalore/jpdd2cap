#jpdd2cap

## About
*Jpdd2cap* changes the *Default Display Resolution* box of a JP2 [(JPEG 2000 Part 1)][2] image into a *Capture Resolution* box. It does this by simply changing the box type field of the *Default Display Resolution* box from *resd* to *resc*. Everything else in the image remains unchanged.

## Why change resolution headers in a JP2?
Most decoders expect the resolution info to be stored in the *Capture Resolution* box; however, the JPEG 2000 standard used to be less than clear about where to store resolution, and some encoders are/were using the *Default Display Resolution* fields instead. This in turn led to several interoperability problems. More info on this can be found [here](http://wiki.opf-labs.org/display/TR/Resolution+not+in+expected+header+fields). *Jpdd2cap* allows you to normalise images that are affected by this. 

<!-- 
## Downloads

* [Windows binaries][5] - stand-alone Windows binaries that allow you to run *jpdd2cap* without any *Python* dependencies 
-->

## Command line use

### Usage
`usage: jpdd2cap.py [-h] [--version] jp2In jp2Out`

### Positional arguments

`jp2In` : input JP2 image;

`jp2Out` : output JP2 image.

### Optional arguments

`-h, --help` : show this help message and exit;

`-v, --version` : show program's version number and exit.

### Example

`jpdd2cap.py balloon_ddr.jp2 balloon_cr.jp2`

##General behaviour and limitations
*Jpdd2cap* will *only* create an output image if the input image contains a *Default Display Resolution* box. No output is created if:

1. the input image doesn't contain a *Resolution* box at all;
2. the input image doesn't contain a *Default Display Resolution* box;
3. the input image already contains a *Capture Resolution* box;
4. the input image contains both a *Default Display Resolution* box and a *Capture Resolution* box.

In each of the above cases *jpdd2cap* will output a warning message.

Also, *extremely* large images may result in problems because *jpdd2cap* needs to load the image to memory in its entirety. This may change in future versions.

##Behaviour with other JPEG 2000 formats
*Jpdd2cap* was primarily created for JP2, but it will most likely work with the other JPEG 2000 formats (JPX, JPM) as well.

## Disclaimer
Note that his tool is in its early stages and has had *very* limited testing so far. Use at your own risk!

## Changes

###0.10
Initial release.



[2]: http://www.jpeg.org/public/15444-1annexi.pdf
[3]: http://www.itu.int/rec/T-REC-T.800/en
[5]: https://bintray.com/pkg/show/general/openplanets/binaries/jpdd2cap