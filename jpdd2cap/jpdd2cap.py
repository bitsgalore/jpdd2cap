#! /usr/bin/env python
# 
# Changes Default Display Resolution box in JP2 image into a Capture Resolution
# box. This will probaly work with the other JPEG 2000 formats (JPX, JPM) as well.
#
# No output is created under the following conditions:
#
# 1. Input image doesn't contain resolution box
# 2. Input image doesn't contain display resolution box
# 3. Input image contains capture resolution box
# 4. Input image contains both display and capture resolution box
#
# Requires: Python 2.7 (older versions won't work) OR Python 3.2 or more recent
#  (Python 3.0 and 3.1 won't work either!)
#
# Copyright (C) 2013, Johan van der Knijff, Koninklijke Bibliotheek -
#  National Library of the Netherlands
#
# This software is copyrighted by the SCAPE Project Consortium.
# The SCAPE project is co-funded by the European Union under
# FP7 ICT-2009.4.1 (Grant Agreement number 270137).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os
import time
import imp
import glob
import struct
import argparse
import xml.etree.ElementTree as ET
import byteconv as bc
scriptPath, scriptName = os.path.split(sys.argv[0])

__version__= "0.1.0"

# Create parser
parser = argparse.ArgumentParser(
    description="Converts Default Display Resolution box in JP2 image to Capture Resolution box")

def main_is_frozen():
    return (hasattr(sys, "frozen") or # new py2exe
        hasattr(sys, "importers") # old py2exe
        or imp.is_frozen("__main__")) # tools/freeze

def get_main_dir():
    if main_is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(sys.argv[0])
    
def printWarning(msg):
    msgString=("User warning: " + msg +"\n")
    sys.stderr.write(msgString)

def errorExit(msg):
    msgString=("Error: " + msg + "\n")
    sys.stderr.write(msgString)
    sys.exit()

def checkFileExists(fileIn):
    # Check if file exists and exit if not
    if os.path.isfile(fileIn)==False:
        msg=fileIn + " does not exist"
        errorExit(msg)
    
def readFileBytes(file):
    # Read file, return contents as a byte object

    # Open file
    f = open(file,"rb")

    # Put contents of file into a byte object.
    fileData=f.read()
    f.close()

    return(fileData)
    
def writeBytes(file, data):
    # Write bytes to binary file

    # Open file
    f = open(file,"wb")

    # Put contents of file into a byte object.
    f.write(data)
    f.close()

def getBox(bytesData, byteStart, noBytes):
    
    # Parse JP2 box and return information on its
    # size, type and contents
        
    # Box length (4 byte unsigned integer)
    boxLengthValue=bc.bytesToUInt(bytesData[byteStart:byteStart+4])

    # Box type
    boxType=bytesData[byteStart+4:byteStart+8]
    
    # Start byte of box contents
    contentsStartOffset=8

    # Read extended box length if box length value equals 1
    # In that case contentsStartOffset should also be 16 (not 8!)
    # (See ISO/IEC 15444-1 Section I.4)
    if boxLengthValue == 1:
        boxLengthValue=strToULongLong(bytesData[byteStart+8:byteStart+16])
        
        contentsStartOffset=16
    
    # For the very last box in a file boxLengthValue may equal 0, so we need
    # to calculate actual value
    if boxLengthValue == 0:
        boxLengthValue=noBytes-byteStart
    
    # End byte for current box
    byteEnd=byteStart + boxLengthValue
    
    # Contents of this box as a byte object (i.e. 'DBox' in ISO/IEC 15444-1 Section I.4)
    boxContents=bytesData[byteStart+contentsStartOffset:byteEnd]

    return(boxLengthValue,boxType,byteEnd,boxContents)

def locateBox(data,targetBoxType):
  
    noBytes=len(data)
    byteStart = 0
    boxLengthValue=10 # dummy value
    boxExists=False
    targetBoxContents="N/A" # dummy value
    startOffsetTargetBox=0
        
    while byteStart < noBytes and boxLengthValue != 0:
 
        boxLengthValue, boxType, byteEnd, boxContents = getBox(data,byteStart, noBytes)    
        
        if boxType == targetBoxType:
            targetBoxContents=boxContents
            startOffsetTargetBox=byteStart
            boxExists=True
            break
        byteStart = byteEnd
        
    return(boxExists, targetBoxContents,startOffsetTargetBox)
    
def convertResDToResC(file):

    # Read file contents to bytearray object
    fileData = bytearray(readFileBytes(file))
    
    conversionSuccessFlag = False
    jp2HeaderBoxExists = False
    resolutionBoxExists = False
    displayResolutionBoxExists = False
    captureResolutionBoxExists = False
                
    # Scan top-level boxes for JP2 Header box
    jp2HeaderBoxExists, jp2HeaderBoxContents,startOffsetHeaderBox = \
        locateBox(fileData,b'\x6a\x70\x32\x68')
    
    if jp2HeaderBoxExists:
    
        # Scan JP2 Header box for Resolution box
        resolutionBoxExists,resolutionBoxContents,startOffsetResolutionBox = \
            locateBox(jp2HeaderBoxContents,b'\x72\x65\x73\x20')
            
        if resolutionBoxExists:
    
            # Scan Resolution box for Display Resolution box
            displayResolutionBoxExists,displayResolutionBoxContents, startOffsetDisplayResolutionBox = \
                locateBox(resolutionBoxContents,b'\x72\x65\x73\x64')
    
            # Scan Resolution box for Capture Resolution box
            captureResolutionBoxExists,captureResolutionBoxContents, startOffsetCaptureResolutionBox = \
                locateBox(resolutionBoxContents,b'\x72\x65\x73\x63')
    
    if jp2HeaderBoxExists and resolutionBoxExists and displayResolutionBoxExists and not captureResolutionBoxExists:
       
        # Position of display resolution box from start of file
        dResOffsetFromFileStart=startOffsetHeaderBox + 16 + startOffsetResolutionBox + startOffsetDisplayResolutionBox
    
        # Box type field position
        boxTypeOffset=dResOffsetFromFileStart + 4
        
        # Position of byte that needs to be changed - 4th byte of box type field
        changeByteOffset=boxTypeOffset + 3
        
        # Replace 'd' by 'c' in box type field
        replaceByte=bc.bytesToUnsignedChar(b'\x63')
        fileData[changeByteOffset]=replaceByte
    
        conversionSuccessFlag=True
        
    else:
        if resolutionBoxExists == False:
            printWarning("No resolution box found")
        if displayResolutionBoxExists == False:
            printWarning("No display resolution box found")
        if captureResolutionBoxExists == True:
            printWarning("Input image already contains capture resolution box")
        
        fileData=""
    
    return(conversionSuccessFlag,fileData)
  
def parseCommandLine():
    # Add arguments
    parser.add_argument('jp2In', 
        action = "store", 
        type = str, 
        help = "input JP2 image")
    parser.add_argument('jp2Out', 
        action = "store", 
        type = str, 
        help = "output JP2 image")
    parser.add_argument('--version', '-v',
        action = 'version', 
        version = __version__)

    # Parse arguments
    args=parser.parse_args()

    return(args)

def main():
    # Get input from command line
    args=parseCommandLine()
     
    # Input images
    jp2In=args.jp2In
    jp2Out=args.jp2Out
    
    # Does input image exist?
    checkFileExists(jp2In)
    
    # Convert image, result as bytes object
    conversionSuccessFlag,convertedData=convertResDToResC(jp2In)
    
    # Write output image if conversion was successful
    if conversionSuccessFlag == True:
        try:
            writeBytes(jp2Out, convertedData)
        except:
            errorExit("Error writing output image")
    else:
        sys.stderr.write("No output image created")


if __name__ == "__main__":
    main()

