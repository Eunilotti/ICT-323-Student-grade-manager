import matplotlib.pyplot as plt


def show_score_chart(student_name, courses, scores):
    plt.figure(figsize=(6, 4))
    plt.bar(courses, scores)
    plt.title(f"{student_name}'s Course Scores")
    plt.xlabel("Courses")
    plt.ylabel("Scores")
    plt.ylim(0, 100)
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()


def show_all_gpas_chart(student_gpas):
    """Display all students' GPAs as a bar chart
    
    Args:
        student_gpas: dict {student_name: gpa}
    """
    if not student_gpas:
        print("No GPA data to display")
        return
    
    students = list(student_gpas.keys())
    gpas = list(student_gpas.values())
    
    plt.figure(figsize=(10, 5))
    bars = plt.bar(students, gpas, color='#667eea')
    plt.title("All Students' GPAs", fontsize=14, fontweight='bold')
    plt.xlabel("Student Name")
    plt.ylabel("GPA")
    plt.ylim(0, 5)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}',
                ha='center', va='bottom', fontweight='bold')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()
