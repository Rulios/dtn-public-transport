"""
    This example attempts to format a clean Mifare Classic 1K card as
    an NFC Forum tag (to store NDEF messages that can be read by any
    NFC enabled Android phone, etc.)

    Note that you need the baud rate to be 115200 because we need to print
    out the data and read from the card at the same time!

    To enable debug message, define DEBUG in nfc/pn532_debug.h
"""
import binascii
import time

from pn532pi import Pn532, pn532
from pn532pi import Pn532Hsu
from pn532pi import Pn532I2c
from pn532pi import Pn532Spi

import ndef 

SPI = False
I2C = True
HSU = False

if SPI:
    PN532_SPI = Pn532Spi(Pn532Spi.SS0_GPIO8)
    nfc = Pn532(PN532_SPI)
# When the number after #elif set as 1, it will be switch to HSU Mode
elif HSU:
    PN532_HSU = Pn532Hsu(Pn532Hsu.RPI_MINI_UART)
    nfc = Pn532(PN532_HSU)

# When the number after #if & #elif set as 0, it will be switch to I2C Mode
elif I2C:
    PN532_I2C = Pn532I2c(1)
    nfc = Pn532(PN532_I2C)

# We can encode many different kinds of pointers to the card,
# from a URL, to an Email address, to a phone number, and many more
# check the library header .h file to see the large # of supported
# prefixes!

# For a http:#www. url:
url = "google.com"
ndefprefix = pn532.NDEF_URIPREFIX_HTTP_WWWDOT

# for an email address
# url = "mail@example.com"
# ndefprefix = NDEF_URIPREFIX_MAILTO

# for a phone number
# url = "+1 212 555 1212"
# ndefprefix = NDEF_URIPREFIX_TEL


def setup():
  print("-------Looking for PN532--------")

  nfc.begin()

  versiondata = nfc.getFirmwareVersion()
  if not versiondata:
    print("Didn't find PN53x board")
    raise RuntimeError("Didn't find PN53x board")  # halt

  # Got ok data, print it out!
  print("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format((versiondata >> 24) & 0xFF, (versiondata >> 16) & 0xFF,
                                                             (versiondata >> 8) & 0xFF))

  # configure board to read RFID tags
  nfc.SAMConfig()

def loop():
  authenticated = False               # Flag to indicate if the sector is authenticated

  # Use the default key
  keya = bytearray([ 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF ])

  print("")
  print("PLEASE NOTE: Formatting your card for NDEF records will change the")
  print("authentication keys.  To reformat your NDEF tag as a clean Mifare")
  print("Classic tag, use the mifareclassic_ndeftoclassic example!")
  print("")
  print("Place your Mifare Classic card on the reader to format with NDEF")
  print("and press any key to continue ...")
  # Wait for user input before proceeding
  input('Press a key to continue')

  # Wait for an ISO14443A type card (Mifare, etc.).  When one is found
  # 'uid' will be populated with the UID, and uidLength will indicate
  # if the uid is 4 bytes (Mifare Classic) or 7 bytes (Mifare Ultralight)
  success, uid = nfc.readPassiveTargetID(cardbaudrate=pn532.PN532_MIFARE_ISO14443A_106KBPS)

  if (success):
    # Display some basic information about the card
    print("Found an ISO14443A card")
    print("UID Length: {:d}".format(len(uid)))
    print("UID Value: {}".format(binascii.hexlify(uid)))

    # Make sure this is a Mifare Classic card
    if (len(uid) != 4):
      print("Ooops ... this doesn't seem to be a Mifare Classic card!")
      return

    # We probably have a Mifare Classic card ...
    print("Seems to be a Mifare Classic card (4 byte UID)")

    # Create an NDEF message with a Text record in English ("en")
    ndef_message = [
        ndef.TextRecord("Hola Mundo", language="es")
    ]

    # Write the NDEF message to the NFC tag
    success = nfc.writeNDEF(ndef_message)

    if success:
        print("NDEF message written to the NFC tag successfully.")
    else:
        print("Failed to write NDEF message to the NFC tag.")

  # Wait a bit before trying again
  print("\n\nDone!")
  time.sleep(1)

if __name__ == '__main__':
    setup()
    while True:
      loop()