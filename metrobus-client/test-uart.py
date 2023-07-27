import serial
import time

def setup_uart(port, baudrate):
    # Open the UART port
    ser = serial.Serial(port, baudrate)
    return ser

def send_command(ser, command):
    # Send a command to the PN532 module
    ser.write(bytes(command))

def receive_response(ser):
    # Wait for the response and read data from the PN532 module
    response = ser.read(16)
    return response

def main():
    # Modify the port and baudrate based on your setup
    uart_port = "/dev/ttyS0"  # or something like "COM1" on Windows
    uart_baudrate = 115200    # Adjust the baudrate as per your PN532 settings

    try:
        # Setup UART communication
        ser = setup_uart(uart_port, uart_baudrate)

        # Verify UART communication with PN532
        send_command(ser, b"\x55\x55\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\x03\xFD\xD4\x14\x01\x17\x00")
        time.sleep(0.1)  # Allow some time for the PN532 module to respond
        response = receive_response(ser)

        if response:
            print("UART communication with PN532 is working!")
        else:
            print("No response received from PN532. Check your connections and settings.")

        # Close the UART port when done
        ser.close()

    except serial.SerialException as e:
        print("Error: ", e)

if __name__ == "__main__":
    main()
