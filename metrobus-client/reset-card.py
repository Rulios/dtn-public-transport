import binascii
import time

from pn532pi import pn532, Pn532
from pn532pi import Pn532Hsu
from pn532pi import Pn532I2c
from pn532pi import Pn532Spi

SPI = False
I2C = True
HSU = False

if SPI:
    PN532_SPI = Pn532Spi(Pn532Spi.SS0_GPIO8)
    nfc = Pn532(PN532_SPI)
elif HSU:
    PN532_HSU = Pn532Hsu(Pn532Hsu.RPI_MINI_UART)
    nfc = Pn532(PN532_HSU)
elif I2C:
    PN532_I2C = Pn532I2c(Pn532I2c.RPI_BUS1)
    nfc = Pn532(PN532_I2C)

# The default Mifare Classic key
KEY_DEFAULT_KEYAB = bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])

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

def reset_factory_state():
    authenticated = False
    numOfSector = 16                 # Assume Mifare Classic 1K for now (16 4-block sectors)

    print("Place your Mifare Classic 1K card on the reader to reset to factory state")
    # Wait for user input before proceeding
    input("and press any key to continue ...")

    # Wait for an ISO14443A type card (Mifare, etc.). When one is found,
    # 'uid' will be populated with the UID, and uidLength will indicate
    # if the uid is 4 bytes (Mifare Classic) or 7 bytes (Mifare Ultralight)
    success, uid = nfc.readPassiveTargetID(pn532.PN532_MIFARE_ISO14443A_106KBPS)

    if success:
        # We seem to have a tag ...
        # Display some basic information about it
        print("Found an ISO14443A card")
        print("UID Length: {:d}".format(len(uid)))
        print("UID Value: {}".format(binascii.hexlify(uid)))

        # Make sure this is a Mifare Classic card
        if len(uid) != 4:
            print("Ooops ... this doesn't seem to be a Mifare Classic card!")
            return

        print("Seems to be a Mifare Classic card (4 byte UID)")
        print("")
        print("Resetting card to factory state...")

        # Now run through the card sector by sector
        for idx in range(numOfSector):
            # Step 1: Authenticate the current sector using key B 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF
            success = nfc.mifareclassic_AuthenticateBlock(uid, BLOCK_NUMBER_OF_SECTOR_TRAILER(idx), 1, KEY_DEFAULT_KEYAB)
            if not success:
                print("Authentication failed for sector {}".format(numOfSector))
                return

            # Step 2: Reset both keys to 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF
            blockBuffer = KEY_DEFAULT_KEYAB + blankAccessBits + b'\x69' + KEY_DEFAULT_KEYAB

            # Step 3: Write the trailer block
            if not nfc.mifareclassic_WriteDataBlock(BLOCK_NUMBER_OF_SECTOR_TRAILER(idx), blockBuffer):
                print("Unable to write trailer block of sector {}".format(numOfSector))
                return

        print("Card successfully reset to factory state.")

    # Wait a bit before trying again
    print("\n\nDone!")
    time.sleep(1)

if __name__ == '__main__':
    setup()
    while True:
        reset_factory_state()
