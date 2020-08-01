from watson_iot import Device
import utime as time
import time, network, sensor, image, time, math, ustruct, struct, tf, math, rpc

interface = rpc.rpc_usb_vcp_slave()

SSID='Karam2' # Network SSID
KEY='1F9018396A'  # Network key

threshold_list = [(0, 255)]
elevatedTemperature = 0
nonElevatedTemperatures = 0
i = 0

min_temp_in_celsius = 32.0
max_temp_in_celsius = 41.0
coordinates = [0,0,0,0]
run = "False"

# Init wlan module and connect to network
print("Trying to connect... (may take a while)...")
wlan = network.WINC()
wlan.connect(SSID, key=KEY, security=wlan.WPA_PSK)
print(wlan.ifconfig())

device = Device(
    device_id="*******",
    device_type= ******",
    org="******",
    token="*****r"
)

print("Resetting Lepton...")
sensor.reset()
sensor.ioctl(sensor.IOCTL_LEPTON_SET_MEASUREMENT_MODE, True)
sensor.ioctl(sensor.IOCTL_LEPTON_SET_MEASUREMENT_RANGE, min_temp_in_celsius, max_temp_in_celsius)
print("Lepton Res (%dx%d)" % (sensor.ioctl(sensor.IOCTL_LEPTON_GET_WIDTH),
                              sensor.ioctl(sensor.IOCTL_LEPTON_GET_HEIGHT)))
print("Radiometry Available: " + ("Yes" if sensor.ioctl(sensor.IOCTL_LEPTON_GET_RADIOMETRY) else "No"))
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=2000)
clock = time.clock()

def start_ffc():
    sensor.ioctl(sensor.IOCTL_LEPTON_RUN_COMMAND, 0x0242)

def get_ffc_running():
    state = ustruct.unpack("<I", sensor.ioctl(sensor.IOCTL_LEPTON_GET_ATTRIBUTE, 0x0244, 2))[0]
    # LEP_SYS_STATUS_WRITE_ERROR == -2
    # LEP_SYS_STATUS_ERROR == -1
    # LEP_SYS_STATUS_READY == 0
    # LEP_SYS_STATUS_BUSY == 1
    # LEP_SYS_FRAME_AVERAGE_COLLECTING_FRAMES == 2
    return state

def map_g_to_temp(g):
     return (g*(max_temp_in_celsius - min_temp_in_celsius)/255)+ min_temp_in_celsius

def get_temp(x,y,w,h):
    stats = img.get_statistics(thresholds=threshold_list, roi=(x,y,w,h))
    return cToF((map_g_to_temp(stats.mean())))

def cToF(temp):
    return (temp * 1.8 + 32)

def jpeg_snapshot(data):
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    return sensor.snapshot().compress(quality=90).bytearray()

def ready(data):
    return run.encode('utf-8')

def accessed(data):
    coordinates = data.bytes(data).decode().split(",")

# Register call backs.
interface.register_callback(jpeg_snapshot)
interface.register_callback(ready)
interface.register_callback(accessed)


# connect to MQTT broker
device.connect()
start_ffc()
device.publishEvent('CityData', {'City': "Gambrills"})
device.publishEvent('StateData', {'State': "Maryland"})
device.publishEvent('CountryData', {'Country': "United States Of America"})


while True:
    img = sensor.snapshot()
    interface.loop()
    screenTemp = get_temp(0,0,160,120)
    print(screenTemp)
    time.sleep(5000)
    if (screenTemp > 93):
        run = "True"
        interface.register_callback(ready)
        tempReading = get_temp(int(coordinates[0]),int(coordinates[1]),int(coordinates[2]),int(coordinates[3]))
        if (tempReading > 100.4):
            elevatedTemperatures += 1
            device.publishEvent('TempDataE', {'elevatedPersons': elevatedTemperatures})
        else:
            nonElevatedtemperature +=1
            device.publishEvent('TempDataN', {'nonElevatedPersons': nonElevatedTemperatures})

    i+=1
    if i % 100 == 0:
        start_ffc()









