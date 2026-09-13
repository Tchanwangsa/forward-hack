"""Bot 4 — service work orders -> Product-Return-and-Replacement-Register. Stub.

Thinner source, same primitive. Resolves SW Version from the hub inventory as at
the RMA date (48% blank). A stub that looks like a different product costs more
than it saves.
"""

from asteria.capture.primitive import CaptureBot


class RMACapture(CaptureBot):
    name = "rma-capture"
    source = "service"
    target_register = "return"
