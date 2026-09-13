"""Which hub, which organisation, which lot, which ward.

The resolutions tier 1 depends on:
    pairing ID + ward + bed        -> serial number   (11% blank on incidents)
    hub inventory as at a date     -> SW version      (48% blank on RMAs)
    lot allocation for a ward+window -> patch lot     (51% blank on checks)
    email domain / signature block -> organisation, contact role

Organisation names arrive in variants — see ground-truth/organisation-variants.csv
for how many, but resolve them from the reference register, not from that file.
"""
