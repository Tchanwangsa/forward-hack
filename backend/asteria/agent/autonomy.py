"""Autonomy levels and the gates no confidence level may bypass.

    1 Observe                read and organise
    2 Recommend              a classification, a next step, a complaint, a CAPA
    3 Draft                  a register row, a record, a message — for review
    4 Execute with approval  act after a named user confirms
    5 Automatic              normalisation, entity resolution, rate calculation,
                             the nightly run

Capture is level 3, always.

Gates (ARCHITECTURE.md, DIAGRAMS.md §The gates):
    commit any drafted register row
    classify an inbound communication as a complaint
    promote a Signal to a Product NC
    approve or close a Product NC
    the CAPA-considered decision, and opening a CAPA
    any outbound customer communication

Every action carries its level, visible in the UI, logged in the Agent Action Log.
"""

from enum import IntEnum


class Autonomy(IntEnum):
    OBSERVE = 1
    RECOMMEND = 2
    DRAFT = 3
    EXECUTE_WITH_APPROVAL = 4
    AUTOMATIC = 5
