import uuid
from .models import Email


def generate_emails(task_name: str):
    emails = []

    if task_name == "spam_filter_easy":
        for _ in range(5):
            emails.append(Email(
                id=str(uuid.uuid4()),
                subject="Buy now",
                body="Limited offer",
                category="spam",
                urgency=1
            ))
        for _ in range(5):
            emails.append(Email(
                id=str(uuid.uuid4()),
                subject="Hello",
                body="Just checking in",
                category="inquiry",
                urgency=2
            ))

    elif task_name == "priority_inbox":
        categories = ["spam", "complaint", "inquiry"]
        for i in range(10):
            emails.append(Email(
                id=str(uuid.uuid4()),
                subject=f"Email {i}",
                body="Message",
                category=categories[i % 3],
                urgency=(i % 5) + 1
            ))

    else:  # hard
        categories = ["spam", "complaint", "inquiry"]
        for i in range(12):
            emails.append(Email(
                id=str(uuid.uuid4()),
                subject=f"URGENT {i}",
                body="Customer issue",
                category=categories[i % 3],
                urgency=(i % 5) + 1
            ))

    return emails