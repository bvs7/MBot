#!/usr/bin/env python3

import getopt
import logging
import os
import socket
import sys

# BaseHandler Class

class BaseHandler(object):

    def __init__(self, fd, address):
        ''' Construct handler from file descriptor and remote client address '''
        self.socket  = fd                         # Store socket file descriptor
        self.address = '{}:{}'.format(*address)   # Store address
        self.stream  = self.socket.makefile('w+') # Open file object from file descriptor

        self.debug('Connect')

    def handle(self):
        ''' Handle connection '''
        self.debug('Handle')
        raise NotImplementedError

    def finish(self):
        ''' Finish connection by flushing stream, shutting down socket, and
        then closing it '''
        self.debug('Finish')
        try:
            self.stream.flush()
            self.socket.shutdown(socket.SHUT_RDWR)
        except socket.error as e:
            pass    # Ignore socket errors
        finally:
            self.socket.close()

