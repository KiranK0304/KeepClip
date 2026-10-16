import os
import fcntl
import struct
import time

UI_SET_EVBIT = 0x40045564
UI_SET_KEYBIT = 0x40045565
UI_DEV_SETUP = 0x405c5503
UI_DEV_CREATE = 0x5501
UI_DEV_DESTROY = 0x5502

EV_KEY = 1
EV_SYN = 0
SYN_REPORT = 0

KEY_LEFTCTRL = 29
KEY_V = 47
KEY_LEFTSHIFT = 42
KEY_INSERT = 110

class VirtualPaster:
    def __init__(self):
        self.fd = None
        try:
            self.fd = os.open('/dev/uinput', os.O_WRONLY | os.O_NONBLOCK)
            fcntl.ioctl(self.fd, UI_SET_EVBIT, EV_KEY)
            fcntl.ioctl(self.fd, UI_SET_KEYBIT, KEY_LEFTCTRL)
            fcntl.ioctl(self.fd, UI_SET_KEYBIT, KEY_V)
            fcntl.ioctl(self.fd, UI_SET_KEYBIT, KEY_LEFTSHIFT)
            fcntl.ioctl(self.fd, UI_SET_KEYBIT, KEY_INSERT)
            
            setup = struct.pack('HHHH80sI', 3, 1, 1, 1, b'clip-virtual-kb', 0)
            fcntl.ioctl(self.fd, UI_DEV_SETUP, setup)
            fcntl.ioctl(self.fd, UI_DEV_CREATE)
            time.sleep(0.04)
        except Exception:
            self.fd = None

    def _emit(self, type_, code, val):
        if self.fd is not None:
            ev = struct.pack('qqHHi', 0, 0, type_, code, val)
            os.write(self.fd, ev)

    def paste(self):
        if self.fd is None:
            return False
        # Press Ctrl + V
        self._emit(EV_KEY, KEY_LEFTCTRL, 1)
        self._emit(EV_SYN, SYN_REPORT, 0)
        self._emit(EV_KEY, KEY_V, 1)
        self._emit(EV_SYN, SYN_REPORT, 0)
        # Release V, then Ctrl
        self._emit(EV_KEY, KEY_V, 0)
        self._emit(EV_SYN, SYN_REPORT, 0)
        self._emit(EV_KEY, KEY_LEFTCTRL, 0)
        self._emit(EV_SYN, SYN_REPORT, 0)
        return True

    def close(self):
        if self.fd is not None:
            try:
                fcntl.ioctl(self.fd, UI_DEV_DESTROY)
                os.close(self.fd)
            except Exception:
                pass
            self.fd = None
