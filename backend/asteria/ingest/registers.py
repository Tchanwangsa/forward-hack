"""The seven customer .xlsx registers -> versioned snapshots + typed rows.

Each import is retained as a snapshot; source rows are never overwritten
(ARCHITECTURE.md §Runtime and storage). Column names in the workbooks are
human-written and inconsistent — normalise here, once.
"""
