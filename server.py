from bluetooth import *
import sys
import RPi.GPIO as GPIO
from hx711 import HX711

server_sock=BluetoothSocket( RFCOMM )
server_sock.bind(("", PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"


def cleanAndExit():
    print "Cleaning..."
    GPIO.cleanup()
    print "Bye!"
    sys.exit()

hx = HX711(22, 11)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(20)
hx.reset()
hx.tare()

advertise_service( server_sock, "SampleServer",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ] 
                    )
                   
print("Waiting for connection on RFCOMM channel %d" % port)

client_sock, client_info = server_sock.accept()
print("Accepted connection from ", client_info)

def send_weight():
    val = hx.get_weight(5)
    if val < 0:
        val = 0
    message = "RESPONSE GET_WEIGHT OK %s" % val
    client_sock.send(message)
    print("sent [%s]" % message)
    return

def reset_scale():
    hx.reset()
    hx.tare()
    message = "RESPONSE RESET_SCALE OK"
    client_sock.send(message)
    print("sent [%s]" % message)
    return

def process_data( data ):

    data.split()
    method = data[0]
    command = data[1]

    if(method != 'REQUEST'):
        return

    if command == 'GET_WEIGHT':
        send_weight()
    elif command == 'RESET_SCALE':
        reset_scale()

    return

while True:
	try:
        data = client_sock.recv(1024)
        if len(data) == 0: break
        print("received [%s]" % data)
        process_data(data)
    except (IOError, KeyboardInterrupt, SystemExit):
            pass

print("disconnected")
client_sock.close()
server_sock.close()
cleanAndExit()
print("all done")
