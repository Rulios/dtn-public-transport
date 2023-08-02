import spidev

def find_spi_buses():
    available_buses = []
    for bus in range(4):  # Try checking buses 0 to 3 (you can adjust the range as needed)
        try:
            spi = spidev.SpiDev()
            spi.open(bus, 0)
            spi.close()
            available_buses.append(bus)
        except Exception as e:
            pass
    return available_buses

if __name__ == "__main__":
    available_buses = find_spi_buses()
    if available_buses:
        print("Available SPI buses:", available_buses)
    else:
        print("No SPI buses found.")
