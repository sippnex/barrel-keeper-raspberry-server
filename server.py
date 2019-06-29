from bluetooth import *
import time
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
while True:
	try:
		time.sleep(1)
		val = hx.get_weight(5)
		if val < 0:
			val = 0
		message = "%s" % (val / 1000)
		client_sock.send(message)
		print("sent [%s]" % message)

	except (KeyboardInterrupt, SystemExit):
		cleanAndExit()

print("disconnected")
client_sock.close()
server_sock.close()
cleanAndExit()
print("all done")
