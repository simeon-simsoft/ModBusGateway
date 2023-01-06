#/usr/bin/env python

import fcntl
import struct
import ConfigParser
import SocketServer
import serial.rs485
import logging
import logging.handlers
import crc16


class ModbusGateway(SocketServer.BaseRequestHandler):

    def setup(self):
        self.load_config()
        self.serial = serial.rs485.RS485(
            port=self.config.get("ModbusRTU", "port"), 
            baudrate=self.config.getint("ModbusRTU", "baudrate"), 
            timeout=self.config.getint("ModbusRTU", "timeout"))
        self.serial.rs485_mode = serial.rs485.RS485Settings(False,True)
        self.serial_connect()
        logger.info("Serial port {} is connected: {}".format(self.serial.port,self.serial.isOpen()))

    def load_config(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read('modbus-gateway.cfg')

    def serial_connect(self):
        if not self.serial.isOpen():
            self.serial.open()

    def handle(self):
        # check if serial port is open, open if not
        if not self.serial.isOpen():
            self.serial_connect()
        logger.info("Connection established with {}".format(self.client_address[0]))
        while True:
            # receive the ModbusTCP request
            tcp_request = self.request.recv(128)
            if not tcp_request or len(tcp_request) ==0:
                logger.info("Connection closed")
                break
            logger.debug("TCP Request {}".format(":".join("{:02X}".format(ord(c)) for c in tcp_request)))
            # convert ModbusTCP request into a ModbusRTU request
            rtu_request = tcp_request[6:] + crc16.calculate(tcp_request[6:])
            logger.debug("RTU Request {}".format(":".join("{:02X}".format(ord(c)) for c in rtu_request)))
            # make sure that the input buffer is clean
            self.serial.flushInput()
            # send the ModbusRTU request 
            self.serial.write(rtu_request) 
            # read first three bytes of the response to check for errors
            rtu_response = self.serial.read(3)
            if not rtu_response:
                logger.warning("RTU Timeout")
            else:
                if ord(rtu_response[1]) > 0x80:
                    logger.debug("RTU Error Response {}".format(":".join("{:02X}".format(ord(c)) for c in rtu_response)))
                    tcp_response = tcp_request[0:5] + chr(3) + rtu_response
                    logger.debug("TCP Error Response {}".format(":".join("{:02X}".format(ord(c)) for c in tcp_response)))
                    self.request.sendall(tcp_response)
                else:
                    # if no error, read number of bytes indicated in RTU response or fixed if response to a write command
                    bytes_to_read = ord(rtu_response[2]) + 2 if ord(rtu_response[1]) < 0x5 else 8-3
                    rtu_response += self.serial.read(bytes_to_read)
                    logger.debug("RTU Response {}".format(":".join("{:02X}".format(ord(c)) for c in rtu_response)))
                    # convert ModbusRTU response into a Modbus TCP response 
                    tcp_response = tcp_request[0:5] + chr(len(rtu_response)-2) + rtu_response[0:-2]
                    logger.debug("TCP Response {}".format(":".join("{:02X}".format(ord(c)) for c in tcp_response)))
                    # return converted TCP response
                    self.request.sendall(tcp_response)

    def finish(self):
        self.serial.close()

if __name__ == "__main__":
    config = ConfigParser.RawConfigParser()
    config.read('modbus-gateway.cfg')
    logging.basicConfig(level=config.get("Logging", "Level"), format='%(asctime)s: %(levelname)-8s - %(message)s')
    logger = logging.getLogger('Modbus Gateway')
    handler = logging.handlers.SysLogHandler(address=(config.get("Logging", "Syslog"),514))
    logger.addHandler(handler)
    address = (config.get("ModbusTCP", "host"), config.getint("ModbusTCP","port"))
    server = SocketServer.TCPServer(address, ModbusGateway)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
