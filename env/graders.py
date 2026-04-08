def grade_task(task_name: str, state) -> float:
    emails = state["emails"]

    if task_name == "spam_filter":
        correct = 0
        for e in emails:
            if e.is_spam and e.archived:
                correct += 1
            elif not e.is_spam and not e.archived:
                correct += 1
        return correct / len(emails)

    if task_name == "customer_support":
        replied = sum(e.replied for e in emails)
        return replied / len(emails)

    if task_name == "multi_step":
        score = 0
        for e in emails:
            if e.is_spam and e.archived:
                score += 1
            if e.category == "priority" and e.replied:
                score += 1
        return score / (2 * len(emails))

    return 0.0