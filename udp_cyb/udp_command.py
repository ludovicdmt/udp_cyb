#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Interface to handle the UDP communications with the 2024 Cybathlon game.

Author: Ludovic Darmet
email: ludovic.darmet@gmail.com
"""
__author__ = "Ludovic Darmet"

import socket
import struct
import secrets
import threading
import time

class UDPClient:
    """Interface to handle the UDP communication with the Cybathlon game."""

    def __init__(self, ip: str = "localhost", port: int = 59075) -> None:
        """Create the UDP socket.
        
        Args:
        ip (str): Targeted IP for the connexion. Default to "localhost".
        port (int): Targeted port for the connexion. Default to 59075.
        """
        self.UDP_IP = ip
        self.UDP_PORT = port

        # Create a UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Session token only to initiate connection
        self.session_token = secrets.token_bytes(9)
        # Hand check to initiate connexion
        self.hand_check()
        self.running = False
        # Initate heartbeat thread
        self.thread_heartbeat = None
        # Initate listening from the game
        self.thread_listening = None

        # Is a mini-game started
        self.control = False
        # Which mini-game
        self.device = "None"

    def send_message(self, message: bytes) -> None:
        """Send a message to the game.

        Args:
        message (bytes): The message in bytes format to send. Can't send directly str or int or float type.
        """
        self.sock.sendto(message, (self.UDP_IP, self.UDP_PORT))

    def receive_message(self) -> bytes:
        """Decode a received message from the game."""
        try:
            data, _ = self.sock.recvfrom(1024)
        except ConnectionResetError as e:
            raise ConnectionError(e, '\n Game not running or connection lost.')
        # Handcheck
        if len(data) == 18:
            header, _ = struct.unpack('!10s8s', data)
            if header[:1] == b'\x02':
                print("Connection accepted")
            else:
                self.hand_check()
                self.start()
                raise ConnectionError("Connection rejected during handcheck")
        # Heartbeat
        elif len(data) == 10:
            header = struct.unpack('!10s', data)
            header = header[0]
            if (header[:1] == b'\x03'):
                print('Connection was lost, try to restart it.')
                # Try to restart
                self.hand_check()
                self.start()
            
        else:
            return data
        
    def send_heartbeat(self) -> None:
        """Send a ping message to the game."""
        # Ping the server
        ping_type_byte = 0x05
        flags_byte = 0x00

        heartbeat = struct.pack('!BB9s', ping_type_byte, flags_byte, self.session_token)
        # Send the message
        self.send_message(heartbeat)
    
    def send_command(self, binary_input_1: int, binary_input_2: int, analogue_input_1: float, analogue_input_2: float) -> None:
        """Send commands to the game.
        Analogue command produce a continous command that should be stopped to produce
        incrementals movements.
        
        Args:
            binary_input_1 (int): The first binary input (0 or 1). Command A
            binary_input_2 (int): The second binary input(0 or 1). Command B
            analogue_input_1 (float): The first analogue input (between -1 and 1). Left/Right command
            analogue_input_2 (float): The second analogue input (between -1 and 1). Forward/Backward command.
        """
        if binary_input_1 not in [0, 1]:
            raise ValueError("The first binary input must be 0 or 1")
        if binary_input_2 not in [0, 1]:
            raise ValueError("The second binary input must be 0 or 1")
        if not -1 <= analogue_input_1 <= 1:
            raise ValueError("The first analogue input must be between -1 and 1")
        if not -1 <= analogue_input_2 <= 1:
            raise ValueError("The second analogue input must be between -1 and 1")
        
        # Encode the inputs into a payload
        binary_inputs = self.binary_inputs_to_payload(binary_input_1, binary_input_2)
        continuous_inputs = self.analogue_inputs_to_payload(analogue_input_1, analogue_input_2)
        # Format the message
        header = struct.pack("!BB8s", 0x04, 0x00, self.session_token)
        # Combine all data into a single message
        payload = binary_inputs + continuous_inputs
        # Combine header and payload
        message = header + payload
        # Send the message
        self.send_message(message)

        # Stop the movement after a short period of time to move only from an increment
        time.sleep(0.13)
        binary_inputs = self.binary_inputs_to_payload(0, 0)
        continuous_inputs = self.analogue_inputs_to_payload(0, 0)
        # Format the message
        header = struct.pack("!BB8s", 0x04, 0x00, self.session_token)
        # Combine all data into a single message
        payload = binary_inputs + continuous_inputs
        # Combine header and payload
        message = header + payload
        # Send the message
        self.send_message(message)
        

    def analogue_inputs_to_payload(self, input1: float, input2: float) -> bytes:
        """Convert the analogue inputs to a payload."""
        # Scale the inputs to fit within the range [0, 255]
        scaled_input1 = int((input1 + 1) * 127.5)
        scaled_input2 = int((input2 + 1) * 127.5)

        # Apply dead-zone correction
        if scaled_input1 == 127:
            scaled_input1 = 128
        if scaled_input2 == 127:
            scaled_input2 = 128

        # Convert the scaled inputs to bytes
        payload = scaled_input1.to_bytes(1, 'big') + scaled_input2.to_bytes(1, 'big')

        return payload

    def binary_inputs_to_payload(self, input1: int, input2: int) -> bytes:
        """Convert the binary inputs to a payload."""
        # Create a 16-bit mask for the binary inputs
        input_mask = (input2 << 1) | input1

        # Convert the input mask to a 2-byte little-endian representation
        payload = input_mask.to_bytes(2, 'little')

        return payload

    def hand_check(self) -> None:
        """Send a hand check message to the game."""
        # hand check
        MESSAGE_FORMAT = "!BB8s"
        type_byte = 0x00
        flags_byte = 0x00
        message = struct.pack(MESSAGE_FORMAT, type_byte, flags_byte, self.session_token)
        # Send the message
        self.send_message(message)
        # Receive data from the UDP interface
        data, addr = self.sock.recvfrom(1024)
        if len(data) == 18:
            header, session_token = struct.unpack('!10s8s', data)
            # Session token communicated during handcheck
            self.session_token = session_token
            print("Received message:", header, session_token)
            print("header:", header[:1])
            if header[:1] == b'\x02':
                print("Connection accepted")
            else: 
                raise ConnectionRefusedError("Handcheck was not sucessfull")
        else:
            ConnectionRefusedError(f"Received data of incorrect length: {len(data)} bytes")
        
    def _start_heartbeat(self):
        """Start the heartbeat thread."""
        self.running = True
        self.thread_heartbeat = threading.Thread(target=self._heartbeat)
        self.thread_heartbeat.start()

    def _stop_heartbeat(self):
        """Stop the heartbeat thread."""
        self.running = False
        if self.thread_heartbeat:
            self.thread_heartbeat.join()

    def _heartbeat(self):
        """Send a ping message to the game every 0.5s."""
        print('Heartbeat is running. \n')
        while self.running:
            self.send_heartbeat()
            time.sleep(1)

    def _start_listening(self):
        """Start the listening thread."""
        self.thread_listening = threading.Thread(target=self._listening)
        self.thread_listening.start()
        print('Listening started. \n')
    
    def _stop_listening(self):
        """Stop the listening thread."""
        if self.thread_listening:
            self.thread_listening.join()
    
    def _listening(self):
        """Listen for incoming messages from the game."""
        while self.running:
            data = self.receive_message()
            time.sleep(0.1)
            if data is not None:
                try:
                    
                    startandstop = data[-2:-1]
                    device = data[-1:]
                    if startandstop == b'\x01':
                        self.control = True
                    elif  startandstop == b'\x02':
                        self.control = False
                    if device == b'\x01':
                        self.device = "wheelchair"
                    elif device == b'\x02':
                        self.device = "arm"
                    elif device == b'\x03':
                        self.device = "cursor"
                    print(f"Control: {self.control}, Device: {self.device}.")
                except:
                    print("Not a message to indicate device")
                    print("Received message:", data)

    def start(self) -> None:
        """Start the background threads"""
        self._start_heartbeat()
        self._start_listening()

    def stop(self) -> None:
        """Stop the background threads"""
        self._stop_heartbeat()
        self._stop_listening()

    def close(self) -> None:
        """Close the UDP socket."""
        self.stop()
        self.sock.close()
