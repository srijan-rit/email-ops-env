import uuid
from env.models import Email


def load_task(task_name: str):
    if task_name == "spam_filter":
        return {
            "emails": [
                Email(id=str(uuid.uuid4()), subject="Win money!", body="Click now", is_spam=True),
                Email(id=str(uuid.uuid4()), subject="Meeting", body="Schedule meeting", is_spam=False),
            ]
        }

    if task_name == "customer_support":
        return {
            "emails": [
                Email(id=str(uuid.uuid4()), subject="Refund", body="Need refund", category="billing"),
                Email(id=str(uuid.uuid4()), subject="Bug", body="App crash", category="tech"),
            ]
        }

    if task_name == "multi_step":
        return {
            "emails": [
                Email(id=str(uuid.uuid4()), subject="URGENT complaint", body="Bad service", category="priority"),
                Email(id=str(uuid.uuid4()), subject="Spam offer", body="Buy now", is_spam=True),
                Email(id=str(uuid.uuid4()), subject="Refund", body="Money back", category="billing"),
            ]
        }

    raise ValueError("Unknown task")