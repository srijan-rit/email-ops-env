def grade_easy(emails):
    total = len(emails)
    if total == 0:
        return 0.0

    correct = 0
    for e in emails:
        if e.category == "spam" and e.archived:
            correct += 1
        elif e.category != "spam" and not e.archived:
            correct += 1

    return correct / total


def grade_medium(emails):
    total = len(emails)
    if total == 0:
        return 0.0

    correct = 0
    for e in emails:
        if e.category == "spam" and e.archived:
            correct += 1
        elif e.category in ["complaint", "inquiry"] and e.replied:
            correct += 1

    return correct / total


def grade_hard(emails):
    total = len(emails)
    if total == 0:
        return 0.0

    correct = 0
    urgent_total = 0
    urgent_handled = 0

    for e in emails:
        if e.category == "spam" and e.archived:
            correct += 1
        elif e.category != "spam" and e.replied:
            correct += 1

        if e.urgency >= 4:
            urgent_total += 1
            if e.replied:
                urgent_handled += 1

    accuracy = correct / total
    urgency_score = (urgent_handled / urgent_total) if urgent_total > 0 else 1.0

    score = 0.7 * accuracy + 0.3 * urgency_score

    return max(min(score, 1.0), 0.0)