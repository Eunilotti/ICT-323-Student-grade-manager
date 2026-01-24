def score_to_point(score):
    if score >= 70:
        return 5
    elif score >= 60:
        return 4
    elif score >= 50:
        return 3
    elif score >= 45:
        return 2
    elif score >= 40:
        return 1
    else:
        return 0


def calculate_gpa(scores):
    if len(scores) == 0:
        return 0.0

    total_points = 0
    for score in scores:
        total_points += score_to_point(score)

    gpa = total_points / len(scores)
    return round(gpa, 2)
