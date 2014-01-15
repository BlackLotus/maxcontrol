import socket
import base64

class MaxControl(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.system_information = {}
        self.devices = {}

    def __connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))

    def __close(self):
        self.socket.close()

    def set_temperature(self, rf_addr, celsius):
        self.__connect()
        req = '000440000000'.decode('hex')
        req += base64.b64decode(rf_addr)
        req += chr(1)
        bits = '01' + bin(celsius * 2)[2:].zfill(6)
        req += chr(int(bits, 2))
        req += chr(0) + chr(0)

        req_b64 = base64.b64encode(req)

        request = 's:%s\r\n' % req_b64
        self.socket.send(request)
        self.__close()

    def read_values(self):
        self.__connect()
        b = self.socket.recv(1)
        index = ''
        while index != 'L':
            index = b
            resp = ''
            while b != '\r':
                resp += b
                b = self.socket.recv(1)
            if index == 'H':
                # initial information
                resp = resp.replace('H:', '')
                resp_ = resp.split(',')
                self.system_information['serial_number'] = resp_[0]
                self.system_information['hwaddr'] = resp_[1]
                self.system_information['version'] = resp_[2]
            elif index == 'M':
                # metadata
                resp = resp.replace('M:', '')
                resp_ = resp.split(',')
                b64data = resp_[-1]
                data = base64.b64decode(b64data)
                data = data[2:]
                room_id = '%s%s' % (ord(data[0]), ord(data[1]))
                data = data[2:]
                room_name_length = ord(data[0])
                room_name = data[1:room_name_length + 1]
                data = data[room_name_length + 2:]
                data = data[7:]  # Offset??
                device_serial = data[:10]
                data = data[10:]
                device_name_length = ord(data[0])
                data = data[1:]
                device_name = data[:device_name_length]
                data = data[device_name_length:]
                device_room_id = '%s%s' % (ord(data[0]), ord(data[1]))

                self.rooms = {
                    room_id: room_name,
                }
                self.devices = {
                    device_serial: {
                        'name': device_name,
                        'room': device_room_id,
                    },
                }
            elif index == 'C':
                # Connect RF addresses with serial numbers
                resp = resp.replace('C:', '')
                resp_ = resp.split(',')
                rf_addr = resp_[0]
                b64data = resp_[1]
                data = base64.b64decode(b64data)
                serial = data[8:18]
                rf_addr = base64.b64encode(data[1:4])

                if serial in self.devices:
                    self.devices[serial]['rfaddr'] = rf_addr
            elif index == 'L':
                resp = resp.replace('L:', '')
                data = base64.b64decode(resp)
                while data:
                    data_ = data[1:ord(data[0])]
                    data = data[ord(data[0]) + 1:]
                    rf_addr = base64.b64encode(data_[:3])
                    celsius = ord(data_[7]) / 2
                    valve_percent = ord(data_[6])
                    info = bin(ord(data_[5]))[2:].zfill(7)
                    program = {
                        '00': 'auto schedule',
                        '01': 'Manual',
                        '10': 'Vacation',
                        '11': 'Boost'
                    }[info[-2:]]
                    link_status = 'Error' if int(info[1]) else 'Ok'
                    battery = 'Low' if int(info[0]) else 'Ok'

                    for device in self.devices:
                        if self.devices[device]['rfaddr'] == rf_addr:
                            self.devices[device].update({
                                'celsius': celsius,
                                'valve_percent': valve_percent,
                                'program': program,
                                'link_status': link_status,
                                'battery': battery,
                            })
            if index != 'L':
                self.socket.recv(1)
                b = self.socket.recv(1)
        self.__close()
        return self.devices

