"""sources/mail/{quality,sales,service,support}/*.eml -> email_message.

Threading is formed from the header chain (In-Reply-To / References). THREADS.json
is ground truth for scoring and is NEVER read here — if inbox triage can see it,
the thread-reconstruction score means nothing.
"""

from email import policy
from email.parser import BytesParser
from email.utils import parseaddr, parsedate_to_datetime

from sqlalchemy.orm import Session

from asteria.config import settings
from asteria.ingest.common import clean
from asteria.models.sources import EmailMessage

MAIL_DIR = settings.mock_company_path / "sources" / "mail"
ASTERIA_DOMAIN = "asteriamedical.example"


def _body(msg) -> str | None:
    """Plain text only. These are text/plain with quoted-printable encoding."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_content()
        return None
    return msg.get_content()


def load_all(session: Session) -> int:
    n = 0
    for mailbox_dir in sorted(p for p in MAIL_DIR.iterdir() if p.is_dir()):
        for path in sorted(mailbox_dir.glob("*.eml")):
            with path.open("rb") as fh:
                msg = BytesParser(policy=policy.default).parse(fh)

            from_name, from_email = parseaddr(msg.get("From", ""))
            try:
                sent_at = parsedate_to_datetime(msg["Date"]) if msg.get("Date") else None
            except (TypeError, ValueError):
                sent_at = None

            session.add(
                EmailMessage(
                    message_id=clean(msg.get("Message-ID")),
                    mailbox=mailbox_dir.name,
                    file_path=f"{mailbox_dir.name}/{path.name}",
                    sent_at=sent_at,
                    from_name=clean(from_name),
                    from_email=clean(from_email),
                    to_emails=clean(msg.get("To")),
                    cc_emails=clean(msg.get("Cc")),
                    subject=clean(msg.get("Subject")),
                    body=_body(msg),
                    in_reply_to=clean(msg.get("In-Reply-To")),
                    references=clean(msg.get("References")),
                    direction=(
                        "outbound" if ASTERIA_DOMAIN in (from_email or "") else "inbound"
                    ),
                )
            )
            n += 1
    return n
