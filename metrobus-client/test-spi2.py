import spidev

# Define the SPI bus and device
SPI_BUS = 0
SPI_DEVICE = 0

def check_nfc_connection():
    try:
        # Initialize SPI interface
        spi = spidev.SpiDev()
        spi.open(SPI_BUS, SPI_DEVICE)
        spi.max_speed_hz = 1000000  # Set SPI speed (adjust as needed)

        # Perform a simple communication with the NFC PN532 module
        # You can send any command you like to check the response
        # For example, we'll send a "GetFirmwareVersion" command (byte values: 0x02, 0x00, 0x01, 0x06, 0x07)
        command = [0x02, 0x00, 0x01, 0x06, 0x07]
        response = spi.xfer2(command)

        # If we receive a response, the NFC module is connected and responsive
        if response:
            print("NFC PN532 module is connected and responsive.")
        else:
            print("NFC PN532 module is not responding.")

        # Close the SPI connection
        spi.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_nfc_connection()
