"""Registers 2-6 — human rows plus capture-bot rows. See plan/REGISTERS.md §3.

Every capture-fed table carries the two capture columns (§3.0):

    row_origin     'Human' | 'Agent (accepted)' | 'Agent (edited)'
                   never 'Agent (pending)' — a pending draft lives in CaptureDraft
    captured_from  'tel:TEL-2026-0084210' | 'eml:<msgid>'
                   | 'tx:TX-2026-0187@00:14:02-00:14:28' | 'wo:WO-21412'
                   | 'round:RD-2026-0412'    blank on human rows

Resolvable, or it is a bug (ARCHITECTURE.md, capture rule 3).
"""

# TODO: Incident, Return, DataCheck, Communication, Complaint
