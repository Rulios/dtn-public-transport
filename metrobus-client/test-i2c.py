from pn532pi import Pn532I2c, Pn532

i2c = Pn532I2c(1)
nfc = Pn532(i2c)

def main():
    try:
        # Initialize the PN532 module over I2C
        nfc.begin()

        # Wait for an NFC card to be detected
        print("Hold an NFC card near the PN532...")
        while True:
            uid = nfc.read_passive_target()
            if uid is not None:
                break

        # Convert UID to hexadecimal string
        uid_hex = "".join([format(byte, "02X") for byte in uid])

        # Print UID of the detected NFC card
        print("Card UID: ", uid_hex)

        # Write a sample ID (4 bytes) to the NFC card
        sample_id = [0x12, 0x34, 0x56, 0x78]
        nfc.mifare_classic_write_block(4, sample_id)

        print("Sample ID (", sample_id, ") written to the NFC card.")

    except Exception as e:
        print("Error: ", e)

if __name__ == "__main__":
    main()
