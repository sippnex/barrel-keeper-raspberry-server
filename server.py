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

def send_weight():
    val = hx.get_weight(5)
    if val < 0:
        val = 0
    message = "RESPONSE GET_WEIGHT OK %s" % val
    client_sock.send(message)
    print("sent [%s]" % message)

def reset_scale():
    hx.reset()
    hx.tare()
    message = "RESPONSE RESET_SCALE OK"
    client_sock.send(message)
    print("sent [%s]" % message)

def process_data( data ):
	method = data.split()[0]
	command = data.split()[1]
	if command == 'GET_WEIGHT':
		send_weight()
	elif command == 'RESET_SCALE':
		reset_scale()

def waiting_for_connection():
    print("Waiting for connection on RFCOMM channel %d" % port)
    client_sock, client_info = server_sock.accept()
    print("Accepted connection from ", client_info)
    client_connected(client_sock)

def disconnect(client_sock):
    client_sock.close()
    print("disconnected")

def client_connected(client_sock):
    while True:
	    try:
		    data = client_sock.recv(1024)
		    if len(data) == 0: break
		    print("received [%s]" % data)
		    process_data(data)
	    except IOError:
            disconnect(client_sock)
		    waiting_for_connection(client_sock)
	    except (KeyboardInterrupt, SystemExit):
		    disconnect(client_sock)
            break


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

waiting_for_connection()

server_sock.close()
cleanAndExit()
print("all done")
