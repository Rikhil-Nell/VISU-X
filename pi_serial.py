import serial

ser = serial.Serial('/dev/COM6', 9600, timeout=1)

def send_number_to_rpi(number: int):

    if number in range(9):
        serial_message = f"{number}\n"
        ser.write(serial_message.encode())
        print(f"Sent to RPi: {serial_message.strip()}")
    else:
        print("Number out of range (0-9)")

send_number_to_rpi(number= 2)