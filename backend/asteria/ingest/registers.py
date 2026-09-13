"""The seven customer .xlsx registers -> typed rows + a snapshot per workbook.

Column names, column order and the mess are preserved exactly (REGISTERS.md §3).
The attribute names here are snake_case; HEADERS below is the map back to the
workbook's own spelling, so a generated .xlsx reproduces the customer's file.
"""

import openpyxl
from sqlalchemy.orm import Session

from asteria.config import settings
from asteria.ingest.common import (
    as_bool,
    as_date,
    as_decimal,
    as_dt,
    as_int,
    clean,
    record_snapshot,
    sheet_rows,
)
from asteria.models.capture_fed import Communication, Complaint, DataCheck, Incident, ProductReturn
from asteria.models.enums import (
    Channel,
    ComplaintStatus,
    DenominatorKind,
    IncidentSource,
    RowOrigin,
    ThresholdKind,
    UnitStatus,
)
from asteria.models.reference import (
    ControlledDocument,
    CustomerOrganisation,
    Hub,
    Indicator,
    PatchLotAllocation,
    PMSReviewMeeting,
)

REGISTERS_DIR = settings.mock_company_path / "registers"


def _enum(py_enum, v):
    """Match a source string to a controlled vocabulary, or keep None.

    A value that does not match is a data finding, not a crash — it is returned
    as None and the as-written column (where there is one) keeps the original.
    """
    s = clean(v)
    if s is None:
        return None
    for m in py_enum:
        if m.value.lower() == s.lower():
            return m
    return None


def _capture_cols(r: dict) -> dict:
    """REGISTERS.md §3.0 — the two columns every capture-fed register carries."""
    return {
        "row_origin": _enum(RowOrigin, r.get("Row Origin")) or RowOrigin.HUMAN,
        "captured_from": clean(r.get("Captured From")),
    }


def load_organisations_and_hubs(session: Session) -> None:
    """Register 1 — 3 sheets, reference only. The inventory sheet is authoritative;
    the unit counts on the Organisations sheet are a stale human summary.
    """
    path = REGISTERS_DIR / "PM-Customer-Organisations-and-Hubs-Record.xlsx"
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)

    orgs = sheet_rows(wb["Organisations"])
    for r in orgs:
        session.add(
            CustomerOrganisation(
                customer_id=clean(r["CustomerID"]),
                organisation_name=clean(r["Organisation Name"]),
                legal_entity_name=clean(r["Legal Entity Name"]),
                location=clean(r["Location"]),
                state=clean(r["State"]),
                country_region=clean(r["Country/Region"]),
                status=clean(r["Status"]),
                timezone=clean(r["Timezone"]),
                record_id=clean(r["Record ID"]),
                customer_since=as_date(r["Customer Since"]),
                units_total_stated=as_int(r["PulseOne Units (total)"]),
                units_in_service_stated=as_int(r["PulseOne Units (in service)"]),
                wards=clean(r["Wards"]),
                primary_contact=clean(r["Primary Contact"]),
                primary_contact_email=clean(r["Primary Contact Email"]),
                sales_channel=clean(r["Channel"]),  # sales channel, not comms medium
                account_owner=clean(r["Account Owner"]),
                notes=clean(r["Notes"]),
            )
        )
    session.flush()

    hubs = sheet_rows(wb["PulseOne Hub Inventory"])
    for r in hubs:
        session.add(
            Hub(
                hub_id=clean(r["HubID"]),
                serial_number=clean(r["Serial Number"]),
                customer_id=clean(r["CustomerID"]),
                organisation_name_as_written=clean(r["Organisation"]),
                ward_id=clean(r["WardID"]),
                bed_id=clean(r["BedID"]),
                hw_revision=clean(r["HW Revision"]),
                sw_version_last_observed=clean(r["SW Version (last observed)"]),
                sw_version_observed_on=as_date(r["SW Version Observed On"]),
                install_date=as_date(r["Install Date"]),
                unit_status=_enum(UnitStatus, r["Unit Status"]),
                pairing_id=clean(r["Pairing ID"]),
                pairing_status=clean(r["Pairing Status"]),
                last_online_local=as_dt(r["Last Online (local)"]),
                notes=clean(r["Notes"]),
            )
        )

    lots = sheet_rows(wb["PulsePatch Stock Allocation"])
    for r in lots:
        session.add(
            PatchLotAllocation(
                lot_code=clean(r["Lot Code"]),
                product_code=clean(r["Product Code"]),
                manufactured=as_date(r["Manufactured"]),
                expiry=as_date(r["Expiry"]),
                customer_id=clean(r["CustomerID"]),
                organisation_name_as_written=clean(r["Organisation"]),
                patches_allocated=as_int(r["Patches Allocated"]),
                boxes=as_int(r["Boxes"]),
                shipped_date=as_date(r["Shipped Date"]),
                notes=clean(r["Notes"]),
            )
        )

    record_snapshot(session, path, len(orgs) + len(hubs) + len(lots))
    wb.close()


def load_pms_plan(session: Session) -> None:
    """Register 7 — 3 sheets, reference only. Carries the seven indicators.

    'Escalation Threshold' is written as '2.0x baseline' or
    'Any increase - clinical review'; it is parsed into threshold_kind +
    threshold_multiplier and ALSO kept verbatim, because the controlled document
    is the authority and the parse is ours.
    """
    path = REGISTERS_DIR / "PMS-Plan-and-Report-Register.xlsx"
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)

    docs = sheet_rows(wb["PMS Documents"])
    for r in docs:
        session.add(
            ControlledDocument(
                document_id=clean(r["Document ID"]),
                title=clean(r["Title"]),
                doc_type=clean(r["Type"]),
                version=clean(r["Version"]),
                status=clean(r["Status"]),
                approved_date=as_date(r["Approved Date"]),
                next_review_due=as_date(r["Next Review Due"]),
                owner=clean(r["Owner"]),
                frequency=clean(r["Frequency"]),
                notes=clean(r["Notes"]),
            )
        )

    inds = sheet_rows(wb["Indicators & Thresholds"])
    for r in inds:
        escalation = clean(r["Escalation Threshold"]) or ""
        denom = (clean(r["Denominator"]) or "").lower()
        if "x baseline" in escalation.lower():
            kind = ThresholdKind.RATIO
            multiplier = as_decimal(escalation.lower().split("x")[0])
        else:
            kind = ThresholdKind.ANY_INCREASE
            multiplier = None
        session.add(
            Indicator(
                indicator_id=clean(r["Indicator ID"]),
                product=clean(r["Product"]),
                description=clean(r["Indicator Description"]),
                internal_code=clean(r["Internal Code"]),
                denominator_kind=(
                    DenominatorKind.PATCHES if "patch" in denom else DenominatorKind.UNIT_MONTHS
                ),
                baseline=as_decimal(r["Baseline (trailing 12mo)"]),
                threshold_kind=kind,
                threshold_multiplier=multiplier,
                escalation_as_written=escalation,
                review_function=clean(r["Review Function"]),
                source_document=clean(r["Source Document"]),
            )
        )

    meetings = sheet_rows(wb["PMS Review Meetings"])
    for r in meetings:
        session.add(
            PMSReviewMeeting(
                meeting_id=clean(r["Meeting ID"]),
                meeting_date=as_date(r["Date"]),
                meeting_type=clean(r["Meeting Type"]),
                attendees=clean(r["Attendees"]),
                chair=clean(r["Chair"]),
                minutes_status=clean(r["Minutes Status"]),
                items_reviewed=clean(r["Items Reviewed"]),
                actions_raised=clean(r["Actions Raised"]),
                notes=clean(r["Notes"]),
            )
        )

    record_snapshot(session, path, len(docs) + len(inds) + len(meetings))
    wb.close()


def load_incidents(session: Session) -> None:
    """Register 2 — 737 rows. 307 carry an indicator; 430 are noise.

    `Last Online` is copied from the inventory, not the time of the incident —
    a column that looks event-related and is not. Loaded as written anyway.
    """
    path = REGISTERS_DIR / "PM-Incident-and-Outage-Log.xlsx"
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = sheet_rows(wb["Incidents & Outages"])
    for r in rows:
        session.add(
            Incident(
                incident_id=clean(r["Incident/Outage ID"]),
                pairing_id=clean(r["Pairing ID"]),
                pairing_status=clean(r["Pairing Status"]),
                organisation_as_written=clean(r["Organisation"]),
                hub_id=clean(r["HubID"]),
                serial_number_as_written=clean(r["Serial Number"]),
                ward_id=clean(r["WardID"]),
                bed_id=clean(r["BedID"]),
                last_online=as_dt(r["Last Online"]),
                offline_duration_hrs=as_decimal(r["Offline Duration (hrs)"]),
                reported_date=as_date(r["Reported Date"]),
                incident_description=clean(r["Incident Description"]),
                status=clean(r["Status"]),
                date_of_last_email_sent=as_date(r["Date of Last Email Sent"]),
                reported_by=clean(r["Reported By"]),
                assigned_to=clean(r["Assigned To"]),
                sw_version_at_time=clean(r["SW Version at Time"]),
                notes=clean(r["Notes"]),
                event_code=clean(r["Event Code"]),
                source=_enum(IncidentSource, r["Source"]),
                **_capture_cols(r),
            )
        )
    record_snapshot(session, path, len(rows))
    wb.close()


def load_returns(session: Session) -> None:
    """Register 3 — 308 rows. SW Version blank on 48%, recoverable by a join."""
    path = REGISTERS_DIR / "Product-Return-and-Replacement-Register.xlsx"
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = sheet_rows(wb["Returns & Replacements"])
    for r in rows:
        session.add(
            ProductReturn(
                rma_number=clean(r["RMA Number"]),
                date_raised=as_date(r["Date Raised"]),
                organisation_as_written=clean(r["Organisation"]),
                customer_id=clean(r["CustomerID"]),
                product=clean(r["Product"]),
                serial_number_as_written=clean(r["Serial Number"]),
                hw_rev=clean(r["HW Rev"]),
                sw_version=clean(r["SW Version"]),
                customer_reported_fault=clean(r["Customer Reported Fault"]),
                date_received=as_date(r["Date Received"]),
                technician_findings=clean(r["Technician Findings"]),
                component_replaced=clean(r["Component Replaced"]),
                linked_complaint=clean(r["Linked Complaint"]),
                disposition=clean(r["Disposition"]),
                replacement_serial=clean(r["Replacement Serial"]),
                date_closed=as_date(r["Date Closed"]),
                technician=clean(r["Technician"]),
                warranty_status=clean(r["Warranty Status"]),
                notes=clean(r["Notes"]),
                linked_signal=clean(r["Linked Signal"]),
                **_capture_cols(r),
            )
        )
    record_snapshot(session, path, len(rows))
    wb.close()


def load_data_checks(session: Session) -> None:
    """Register 4 — 712 rows. Four free-text issue columns, mostly blank,
    mapping imperfectly onto the seven indicators.
    """
    path = REGISTERS_DIR / "PM-Data-Check-and-Troubleshooting-Log.xlsx"
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = sheet_rows(wb["Data Check & Troubleshooting"])
    for r in rows:
        session.add(
            DataCheck(
                check_id=clean(r["Check ID"]),
                check_date=as_date(r["Date"]),
                organisation_as_written=clean(r["Organisation"]),
                ward=clean(r["Ward"]),
                bed=clean(r["Bed"]),
                pairing=clean(r["PulseOne-PulsePatch Pairing"]),
                serial_number_as_written=clean(r["Serial Number"]),
                patch_lot=clean(r["Patch Lot"]),
                hardware_issues=clean(r["Hardware Issues"]),
                alert_misclassifications=clean(r["Alert Misclassifications"]),
                patient_and_alert_issues=clean(r["Patient & Alert Issues"]),
                software_issues=clean(r["Software Issues"]),
                issue_found=clean(r["Issue Found"]),
                checked_by=clean(r["Checked By"]),
                action_taken=clean(r["Action Taken"]),
                **_capture_cols(r),
            )
        )
    record_snapshot(session, path, len(rows))
    wb.close()


def load_communications(session: Session) -> None:
    """Register 5 — 566 rows, all feedback channels in one register.

    `Type = Complaint` here is a casual human label, not a complaint record.
    """
    path = REGISTERS_DIR / "PM-Client-Communications-Log.xlsx"
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = sheet_rows(wb["Client Communications"])
    for r in rows:
        session.add(
            Communication(
                comm_id=clean(r["Comm ID"]),
                email_subject=clean(r["Email Subject"]),  # holds meeting title on Meeting rows
                date_of_initial_email=as_date(r["Date of Initial Email"]),
                date_of_last_email_sent=as_date(r["Date of Last Email Sent"]),
                status=clean(r["Status"]),
                comm_type=clean(r["Type"]),
                organisation_as_written=clean(r["Organisation"]),
                client_contact=clean(r["Client Contact"]),
                contact_role=clean(r["Contact Role"]),
                contact_email=clean(r["Contact Email"]),
                handled_by=clean(r["Handled By"]),
                mailbox=clean(r["Mailbox"]),
                notes=clean(r["Notes"]),
                attachments=clean(r["Attachments"]),
                cross_reference=clean(r["Cross-reference"]),
                channel=_enum(Channel, r["Channel"]),
                **_capture_cols(r),
            )
        )
    record_snapshot(session, path, len(rows))
    wb.close()


def load_complaints(session: Session) -> None:
    """Register 6 — the formal complaint record. Declined rows are first-class."""
    path = REGISTERS_DIR / "Complaint-Register.xlsx"
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = sheet_rows(wb["Complaints"])
    for r in rows:
        session.add(
            Complaint(
                complaint_id=clean(r["Complaint ID"]),
                date_received=as_date(r["Date Received"]),
                date_opened=as_date(r["Date Opened"]),
                channel=_enum(Channel, r["Channel"]),
                organisation_as_written=clean(r["Organisation"]),
                customer_id=clean(r["CustomerID"]),
                complainant=clean(r["Complainant"]),
                contact_role=clean(r["Contact Role"]),
                contact_email=clean(r["Contact Email"]),
                product=clean(r["Product"]),
                serial_number_as_written=clean(r["Serial Number"]),
                patch_lot=clean(r["Patch Lot"]),
                description_as_reported=clean(r["Complaint Description (as reported)"]),
                indicator_id=clean(r["Indicator"]),
                event_code=clean(r["Event Code"]),
                investigation_required=as_bool(r["Investigation Required (Y/N)"]),
                investigation_summary=clean(r["Investigation Summary"]),
                vigilance_screen_required=as_bool(r["Vigilance screen required (Y/N)"]),
                linked_comm=clean(r["Linked Comm"]),
                linked_incident=clean(r["Linked Incident"]),
                linked_rma=clean(r["Linked RMA"]),
                linked_signal=clean(r["Linked Signal"]),
                linked_nc=clean(r["Linked NC"]),
                status=_enum(ComplaintStatus, r["Status"]),
                owner=clean(r["Owner"]),
                date_closed=as_date(r["Date Closed"]),
                closure_rationale=clean(r["Closure Rationale"]),
                customer_informed=as_bool(r["Customer Informed (Y/N)"]),
                date_informed=as_date(r["Date Informed"]),
                **_capture_cols(r),
            )
        )
    record_snapshot(session, path, len(rows))
    wb.close()


def load_all(session: Session) -> None:
    load_organisations_and_hubs(session)
    load_pms_plan(session)
    load_incidents(session)
    load_returns(session)
    load_data_checks(session)
    load_communications(session)
    load_complaints(session)
