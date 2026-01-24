import csv
import os

# Get the parent directory (StudentGradeManager folder)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FOLDER = os.path.join(BASE_DIR, "data")
FILE_PATH = os.path.join(DATA_FOLDER, "students.csv")


def ensure_data_folder():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)


def save_student_record(student_name, course, score):
    ensure_data_folder()

    file_exists = os.path.isfile(FILE_PATH)

    with open(FILE_PATH, mode="a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["student_name", "course", "score"])

        writer.writerow([student_name, course, score])


def load_student_scores(student_name):
    ensure_data_folder()

    scores = []

    if not os.path.isfile(FILE_PATH):
        return scores

    with open(FILE_PATH, mode="r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["student_name"].lower() == student_name.lower():
                scores.append(int(row["score"]))

    return scores


def load_student_courses_and_scores(student_name):
    ensure_data_folder()

    courses = []
    scores = []

    if not os.path.isfile(FILE_PATH):
        return courses, scores

    with open(FILE_PATH, mode="r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["student_name"].lower() == student_name.lower():
                courses.append(row["course"])
                scores.append(int(row["score"]))

    return courses, scores
