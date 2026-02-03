import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os
import csv

# Add src directory to path for dynamic imports
_src_path = os.path.join(os.path.dirname(__file__), 'src')
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)

try:
    from grade_manager import (  # type: ignore
        save_student_record,
        load_student_scores,
        load_student_courses_and_scores,
        FILE_PATH
    )
    from gpa_calculator import calculate_gpa  # type: ignore
    from visualization import show_score_chart, show_all_gpas_chart  # type: ignore
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

# ============= STYLES & COLORS =============
PRIMARY_COLOR = "#667eea"
SECONDARY_COLOR = "#764ba2"
SUCCESS_COLOR = "#4ade80"
WARNING_COLOR = "#ff6b6b"
BG_COLOR = "#0a0f1f"  # Darker base
GLASS_BG = "#1a2a45"  # Frosted glass base
GLASS_LIGHT = "#2a3a55"  # Lighter glass - semi-transparent effect
INPUT_BG = "#f0f4f9"  # Light frosted white
INPUT_FG = "#0a0f1f"  # Dark text on frosted
WHITE = "#ffffff"
TEXT_COLOR = "#ffffff"  # White text
LIGHT_TEXT = "#b0b0c0"
BORDER_COLOR = "#e0e8f0"  # Light borders for glass
LIGHT_BG = "#2a3a55"
ACCENT = "#a8bfff"

# Global variables
all_records = []
active_tab = "save"


def get_all_student_gpas():
    """Calculate GPA for each unique student"""
    student_gpas = {}
    student_scores = {}

    if not os.path.exists(FILE_PATH):
        return student_gpas

    try:
        with open(FILE_PATH, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get('student_name', '').strip()
                if not name:
                    continue
                score = int(row.get('score', 0))

                if name not in student_scores:
                    student_scores[name] = []
                student_scores[name].append(score)
    except:
        pass

    # Calculate GPA for each student
    for name, scores in student_scores.items():
        student_gpas[name] = calculate_gpa(scores)

    return student_gpas


def create_frosted_glass_effect(widget):
    """Add frosted glass styling to a widget"""
    widget.config(
        bg=GLASS_BG,
        relief=tk.FLAT,
        bd=0
    )


def create_gradient_bg(canvas, color1="#667eea", color2="#764ba2", width=900, height=200):
    """Create gradient background with smooth transition"""
    r1, g1, b1 = int(color1[1:3], 16), int(
        color1[3:5], 16), int(color1[5:7], 16)
    r2, g2, b2 = int(color2[1:3], 16), int(
        color2[3:5], 16), int(color2[5:7], 16)

    for i in range(height):
        ratio = i / height
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.create_line(0, i, width, i, fill=color, width=1)

    # Add subtle shine/glow overlay
    canvas.create_rectangle(0, 0, width, height//3,
                            fill='white', stipple='gray12', outline='')


def validate_score(score_str):
    """Validate score input"""
    try:
        score = int(score_str)
        return 0 <= score <= 100
    except ValueError:
        return False


def on_score_change(*args):
    """Validate score in real-time"""
    score = score_entry.get().strip()
    if score and validate_score(score):
        score_val = int(score)
        progress = score_val / 100
        score_status_label.config(text=f"✓ {score_val}%", fg=SUCCESS_COLOR)
        score_progress.set(progress)
    else:
        if score:
            score_status_label.config(text="✗ Invalid", fg=WARNING_COLOR)
        else:
            score_status_label.config(text="", fg=TEXT_COLOR)
        score_progress.set(0)


def load_saved_records():
    """Load and display saved records"""
    global all_records
    all_records = []

    if not os.path.exists(FILE_PATH):
        return

    try:
        with open(FILE_PATH, 'r') as f:
            reader = csv.DictReader(f)
            if reader:
                all_records = list(reader)
    except:
        pass

    update_records_display()


def update_records_display():
    """Update the records treeview"""
    for item in records_tree.get_children():
        records_tree.delete(item)

    for record in all_records:
        records_tree.insert('', 'end', values=(
            record.get('student_name', ''),
            record.get('course', ''),
            record.get('score', ''),
            record.get('level', ''),
            record.get('semester', ''),
            record.get('session', '')
        ))


def save_record():
    name = name_entry.get().strip()
    course = course_entry.get().strip()
    score = score_entry.get().strip()

    level = level_var.get().strip()
    semester = semester_var.get().strip()
    session_val = session_entry.get().strip()

    if not name or not course or not score:
        show_message("⚠️ All fields are required!", "error")
        return

    if not validate_score(score):
        show_message("❌ Score must be between 0-100!", "error")
        return

    score_val = int(score)
    save_student_record(name, course, score_val, level=level,
                        semester=semester, session=session_val)
    show_message(f"✅ Record saved! {name} - {course}: {score_val}", "success")

    clear_form()
    load_saved_records()


def clear_form():
    """Clear all form fields"""
    name_entry.delete(0, tk.END)
    course_entry.delete(0, tk.END)
    score_entry.delete(0, tk.END)
    score_status_label.config(text="")
    score_progress.set(0)
    level_var.set("")
    semester_var.set("")
    session_entry.delete(0, tk.END)


def show_chart():
    name = name_entry.get().strip()

    if not name:
        show_message("⚠️ Enter student name!", "error")
        return

    courses, scores = load_student_courses_and_scores(name)

    if not scores:
        show_message("❌ No records found for this student!", "error")
        return

    show_score_chart(name, courses, scores)


def calculate_student_gpa():
    name = name_entry.get().strip()

    if not name:
        show_message("⚠️ Enter student name!", "error")
        return

    scores = load_student_scores(name)

    if not scores:
        show_message("❌ No records found for this student!", "error")
        return

    gpa = calculate_gpa(scores)
    gpa_value_label.config(text=f"{gpa}", fg=ACCENT)
    gpa_count_label.config(text=f"({len(scores)} scores)")
    gpa_result_frame.pack(pady=20, fill=tk.X, padx=25)

    # Load and display student's courses and scores
    courses, scores_list = load_student_courses_and_scores(name)
    load_student_records_display(courses, scores_list)
    student_records_frame.pack(pady=20, fill=tk.BOTH, expand=True, padx=25)

    show_message(f"✓ GPA calculated for {name}!", "success")


def load_student_records_display(courses, scores):
    """Display student's course records"""
    for item in student_records_tree.get_children():
        student_records_tree.delete(item)

    for course, score in zip(courses, scores):
        student_records_tree.insert('', 'end', values=(course, score))


def load_all_gpas_display():
    """Load and display all students' GPAs"""
    for item in gpa_tree.get_children():
        gpa_tree.delete(item)

    student_gpas = get_all_student_gpas()

    for name, gpa in sorted(student_gpas.items()):
        gpa_tree.insert('', 'end', values=(name, f"{gpa:.2f}"))


def show_all_gpas():
    """Show chart of all student GPAs"""
    student_gpas = get_all_student_gpas()

    if not student_gpas:
        show_message("❌ No GPA records found!", "error")
        return

    show_all_gpas_chart(student_gpas)


def show_message(msg, msg_type):
    """Show success/error message"""
    message_label.config(text=msg)
    if msg_type == "success":
        message_label.config(fg=SUCCESS_COLOR, bg="#1b4d2e")
        message_frame.pack(pady=10, fill=tk.X, padx=25)
    else:
        message_label.config(fg=WARNING_COLOR, bg="#4d1b1b")
        message_frame.pack(pady=10, fill=tk.X, padx=25)

    window.after(4000, lambda: message_frame.pack_forget())


def switch_tab(tab_name):
    """Switch between tabs"""
    global active_tab
    active_tab = tab_name

    # Hide all tabs
    save_tab.pack_forget()
    gpa_tab.pack_forget()
    chart_tab.pack_forget()
    grade_tab.pack_forget()

    # Update button styles
    for btn, tname in tab_button_refs:
        if tname == tab_name:
            btn.config(fg=ACCENT, bg=GLASS_LIGHT, relief=tk.SUNKEN)
        else:
            btn.config(fg=LIGHT_TEXT, bg=GLASS_BG, relief=tk.FLAT)

    # Show selected tab
    if tab_name == "save":
        save_tab.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
    elif tab_name == "gpa":
        load_all_gpas_display()
        gpa_tab.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
    elif tab_name == "grade":
        grade_tab.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
    elif tab_name == "chart":
        chart_tab.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)


# ============= MAIN WINDOW =============
window = tk.Tk()
window.title("Student Grade Management System")
window.geometry("950x850")
window.resizable(False, False)
window.configure(bg=BG_COLOR)

try:
    window.attributes('-alpha', 0.98)
except:
    pass

# ============= HEADER WITH GRADIENT & GLOW =============
header_frame = tk.Frame(window, bg=BG_COLOR, height=220)
header_frame.pack(side=tk.TOP, fill=tk.X)

header_canvas = tk.Canvas(header_frame, width=950,
                          height=200, highlightthickness=0, bg=BG_COLOR)
header_canvas.pack(pady=(10, 0))
create_gradient_bg(header_canvas, PRIMARY_COLOR, SECONDARY_COLOR, 950, 200)

header_title = tk.Label(
    header_canvas,
    text="📚 Student Grade Manager",
    font=("Segoe UI", 36, "bold"),
    fg=WHITE,
    bg=SECONDARY_COLOR
)
header_canvas.create_window(475, 75, window=header_title)

header_subtitle = tk.Label(
    header_canvas,
    text="Track, calculate, and visualize student grades with ease",
    font=("Segoe UI", 11),
    fg=WHITE,
    bg=SECONDARY_COLOR
)
header_canvas.create_window(475, 135, window=header_subtitle)

# ============= SCROLLABLE CONTENT CONTAINER =============
content_container = tk.Frame(window, bg=BG_COLOR)
content_container.pack(fill=tk.BOTH, expand=True)

content_canvas = tk.Canvas(
    content_container, bg=BG_COLOR, highlightthickness=0)
content_scroll = ttk.Scrollbar(
    content_container, orient="vertical", command=content_canvas.yview)
content_canvas.configure(yscrollcommand=content_scroll.set)
content_scroll.pack(side=tk.RIGHT, fill=tk.Y)
content_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

content_frame = tk.Frame(content_canvas, bg=BG_COLOR)
content_canvas.create_window((0, 0), window=content_frame, anchor='nw')


def _on_config(event):
    content_canvas.configure(scrollregion=content_canvas.bbox('all'))


content_frame.bind('<Configure>', _on_config)


def _on_mousewheel(event):
    # Windows delta
    try:
        content_canvas.yview_scroll(int(-1*(event.delta/120)), 'units')
    except Exception:
        pass


content_canvas.bind_all('<MouseWheel>', _on_mousewheel)

# ============= TAB BUTTONS =============
tab_frame = tk.Frame(content_frame, bg=GLASS_BG, height=70)
tab_frame.pack(fill=tk.X, padx=0, pady=0)

tab_button_refs = []
for i, (text, icon, cmd) in enumerate([
    ("Save Record", "💾", lambda: switch_tab("save")),
    ("Calculate GPA", "📊", lambda: switch_tab("gpa")),
    ("View Chart", "📈", lambda: switch_tab("chart")),
    ("Grade Manager", "🧾", lambda: switch_tab("grade"))
]):
    is_active = (i == 0)
    btn = tk.Button(
        tab_frame,
        text=f"{icon} {text}",
        command=cmd,
        font=("Segoe UI", 11, "bold"),
        fg=ACCENT if is_active else LIGHT_TEXT,
        bg=GLASS_LIGHT if is_active else GLASS_BG,
        activebackground=GLASS_LIGHT,
        activeforeground=ACCENT,
        relief=tk.SUNKEN if is_active else tk.FLAT,
        bd=2 if is_active else 0,
        padx=25,
        pady=15,
        cursor="hand2"
    )
    btn.pack(side=tk.LEFT, padx=5, pady=10)

    # Add tab button hover effects (non-active buttons)
    if not is_active:
        def make_hover(button):
            def on_tab_hover(event):
                button.config(bg="#3a4a6a")  # Slightly lighter on hover

            def on_tab_leave(event):
                button.config(bg=GLASS_BG)   # Back to normal
            return on_tab_hover, on_tab_leave

        hover, leave = make_hover(btn)
        btn.bind('<Enter>', hover)
        btn.bind('<Leave>', leave)

    tab_button_refs.append((btn, ["save", "gpa", "chart", "grade"][i]))

# Message frame
message_frame = tk.Frame(content_frame, bg=GLASS_BG)
message_label = tk.Label(
    message_frame,
    text="",
    font=("Segoe UI", 10, "bold"),
    wraplength=850,
    justify=tk.CENTER,
    padx=15,
    pady=10,
    bg=GLASS_BG
)
message_label.pack()

# ============= SAVE RECORD TAB =============
save_tab = tk.Frame(content_frame, bg=GLASS_BG)

# Create shadow effect for form
form_shadow = tk.Frame(save_tab, bg="#0d1420", highlightthickness=0)
form_shadow.pack(fill=tk.X, padx=20, pady=(15, 0))

# Form section with frosted glass effect
form_frame = tk.Frame(form_shadow, bg=GLASS_LIGHT, highlightthickness=0)
form_frame.pack(fill=tk.X, padx=3, pady=3)

# Add subtle border glow effect
form_border = tk.Frame(form_shadow, bg="#3a5f8f", highlightthickness=0)
form_border.pack(fill=tk.X)
# Student Name
name_label = tk.Label(form_frame, text="👤 Student Name:", font=(
    "Segoe UI", 11, "bold"), fg=TEXT_COLOR, bg=GLASS_BG)
name_label.pack(anchor=tk.W, pady=(20, 8), padx=20)
name_entry = tk.Entry(form_frame, font=("Segoe UI", 11), fg=INPUT_FG, bg=INPUT_BG,
                      relief=tk.FLAT, bd=1, insertbackground=PRIMARY_COLOR, disabledbackground=INPUT_BG)
name_entry.pack(fill=tk.X, ipady=12, padx=20)
name_entry.insert(0, "")
# Add glow effect on focus


def on_name_focus(event):
    name_entry.config(relief=tk.FLAT, bd=2)


def on_name_unfocus(event):
    name_entry.config(relief=tk.FLAT, bd=1)


name_entry.bind('<FocusIn>', on_name_focus)
name_entry.bind('<FocusOut>', on_name_unfocus)

# Course
course_label = tk.Label(form_frame, text="📚 Course Name:", font=(
    "Segoe UI", 11, "bold"), fg=TEXT_COLOR, bg=GLASS_BG)
course_label.pack(anchor=tk.W, pady=(20, 8), padx=20)
course_entry = tk.Entry(form_frame, font=("Segoe UI", 11), fg=INPUT_FG,
                        bg=INPUT_BG, relief=tk.FLAT, bd=1, insertbackground=PRIMARY_COLOR)
course_entry.pack(fill=tk.X, ipady=12, padx=20)


def on_course_focus(event):
    course_entry.config(relief=tk.FLAT, bd=2)


def on_course_unfocus(event):
    course_entry.config(relief=tk.FLAT, bd=1)


course_entry.bind('<FocusIn>', on_course_focus)
course_entry.bind('<FocusOut>', on_course_unfocus)

# Score
score_label = tk.Label(form_frame, text="⭐ Score (0-100):",
                       font=("Segoe UI", 11, "bold"), fg=TEXT_COLOR, bg=GLASS_BG)
score_label.pack(anchor=tk.W, pady=(20, 8), padx=20)

score_entry_frame = tk.Frame(form_frame, bg=GLASS_BG)
score_entry_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

score_entry = tk.Entry(score_entry_frame, font=("Segoe UI", 11), fg=INPUT_FG,
                       bg=INPUT_BG, relief=tk.FLAT, bd=1, insertbackground=PRIMARY_COLOR)
score_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=12)

score_status_label = tk.Label(score_entry_frame, text="", font=(
    "Segoe UI", 10, "bold"), fg=TEXT_COLOR, bg=GLASS_BG)
score_status_label.pack(side=tk.LEFT, padx=(10, 0))


def on_score_focus(event):
    score_entry.config(relief=tk.FLAT, bd=2)


def on_score_unfocus(event):
    score_entry.config(relief=tk.FLAT, bd=1)


score_entry.bind('<FocusIn>', on_score_focus)
score_entry.bind('<FocusOut>', on_score_unfocus)

# Score progress bar with enhanced styling
score_progress = tk.DoubleVar()

# Configure progress bar style for glassmorphism
progress_style = ttk.Style()
progress_style.configure('GlassProgress.Horizontal.TProgressbar',
                         background=PRIMARY_COLOR,
                         troughcolor=GLASS_LIGHT,
                         bordercolor=GLASS_LIGHT,
                         lightcolor=PRIMARY_COLOR,
                         darkcolor=SECONDARY_COLOR)

score_progress_bar = ttk.Progressbar(form_frame, variable=score_progress,
                                     maximum=1.0, mode='determinate', style='GlassProgress.Horizontal.TProgressbar')
score_progress_bar.pack(fill=tk.X, padx=20, pady=(0, 15))

# Bind score validation
score_var = tk.StringVar()
score_entry['textvariable'] = score_var
score_var.trace('w', on_score_change)

# Level field
level_label = tk.Label(form_frame, text="🏷️ Level:", font=(
    "Segoe UI", 11, "bold"), fg=TEXT_COLOR, bg=GLASS_BG)
level_label.pack(anchor=tk.W, pady=(10, 4), padx=20)
level_var = tk.StringVar()
level_options = ("100", "200")
level_menu = ttk.Combobox(
    form_frame, values=level_options, textvariable=level_var)
level_menu.set("")
level_menu.pack(fill=tk.X, padx=20, pady=(0, 8))

# Semester field
semester_label = tk.Label(form_frame, text="📆 Semester:", font=(
    "Segoe UI", 11, "bold"), fg=TEXT_COLOR, bg=GLASS_BG)
semester_label.pack(anchor=tk.W, pady=(10, 4), padx=20)
semester_var = tk.StringVar()
semester_menu = ttk.Combobox(form_frame, values=(
    "1", "2"), textvariable=semester_var)
semester_menu.set("")
semester_menu.pack(fill=tk.X, padx=20, pady=(0, 8))

# Session field
session_label = tk.Label(form_frame, text="🏫 Session (e.g., 2024/2025):",
                         font=("Segoe UI", 11, "bold"), fg=TEXT_COLOR, bg=GLASS_BG)
session_label.pack(anchor=tk.W, pady=(10, 4), padx=20)
session_entry = tk.Entry(form_frame, font=("Segoe UI", 11), fg=INPUT_FG,
                         bg=INPUT_BG, relief=tk.FLAT, bd=1, insertbackground=PRIMARY_COLOR)
session_entry.pack(fill=tk.X, ipady=8, padx=20, pady=(0, 12))

# Buttons
button_frame = tk.Frame(form_frame, bg=GLASS_BG)
button_frame.pack(fill=tk.X, padx=20, pady=(20, 0))

save_btn = tk.Button(
    button_frame,
    text="💾 Save Record",
    command=save_record,
    font=("Segoe UI", 12, "bold"),
    fg=WHITE,
    bg=SUCCESS_COLOR,
    activebackground="#3ad565",
    relief=tk.FLAT,
    bd=0,
    padx=20,
    pady=12,
    cursor="hand2"
)
save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

# Save button hover effects


def on_save_hover(event):
    save_btn.config(bg="#2fc956")


def on_save_leave(event):
    save_btn.config(bg=SUCCESS_COLOR)


save_btn.bind('<Enter>', on_save_hover)
save_btn.bind('<Leave>', on_save_leave)

clear_btn = tk.Button(
    button_frame,
    text="🗑️ Clear Form",
    command=clear_form,
    font=("Segoe UI", 12, "bold"),
    fg=LIGHT_TEXT,
    bg=GLASS_LIGHT,
    activebackground=INPUT_BG,
    relief=tk.FLAT,
    bd=0,
    padx=20,
    pady=12,
    cursor="hand2"
)
clear_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

# Clear button hover effects


def on_clear_hover(event):
    clear_btn.config(bg="#2a3f5c")


def on_clear_leave(event):
    clear_btn.config(bg=GLASS_LIGHT)


clear_btn.bind('<Enter>', on_clear_hover)
clear_btn.bind('<Leave>', on_clear_leave)

# ============= GPA RESULT FRAME =============
gpa_result_frame = tk.Frame(save_tab, bg=LIGHT_BG, relief=tk.FLAT, bd=0)

gpa_result_title = tk.Label(
    gpa_result_frame,
    text="📊 GPA Result",
    font=("Segoe UI", 13, "bold"),
    fg=ACCENT,
    bg=LIGHT_BG
)
gpa_result_title.pack(pady=(15, 10))

gpa_value_label = tk.Label(
    gpa_result_frame,
    text="0.0",
    font=("Segoe UI", 40, "bold"),
    fg=ACCENT,
    bg=LIGHT_BG
)
gpa_value_label.pack(pady=(0, 5))

gpa_count_label = tk.Label(
    gpa_result_frame,
    text="",
    font=("Segoe UI", 10),
    fg=LIGHT_TEXT,
    bg=LIGHT_BG
)
gpa_count_label.pack(pady=(0, 15))

# Student's course records frame (when GPA is calculated)
student_records_frame = tk.Frame(save_tab, bg=LIGHT_BG, relief=tk.FLAT, bd=0)

student_records_title = tk.Label(
    student_records_frame,
    text="📚 Course Records",
    font=("Segoe UI", 12, "bold"),
    fg=ACCENT,
    bg=LIGHT_BG
)
student_records_title.pack(pady=(15, 10))

# Create shadow frame for student records
student_records_shadow = tk.Frame(
    student_records_frame, bg="#0d1420", highlightthickness=0)
student_records_shadow.pack(fill=tk.BOTH, expand=True, padx=0, pady=(0, 15))

# Create treeview for student records
student_records_tree_frame = tk.Frame(
    student_records_shadow, bg=GLASS_BG, highlightthickness=0)
student_records_tree_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

student_records_scroll = ttk.Scrollbar(student_records_tree_frame)
student_records_scroll.pack(side=tk.RIGHT, fill=tk.Y)

student_records_tree = ttk.Treeview(student_records_tree_frame, columns=(
    'Course', 'Score'), height=5, yscrollcommand=student_records_scroll.set)
student_records_scroll.config(command=student_records_tree.yview)

student_records_tree.column('#0', width=0, stretch=tk.NO)
student_records_tree.column('Course', anchor=tk.W, width=200)
student_records_tree.column('Score', anchor=tk.CENTER, width=100)

student_records_tree.heading('#0', text='', anchor=tk.W)
student_records_tree.heading('Course', text='Course', anchor=tk.W)
student_records_tree.heading('Score', text='Score', anchor=tk.CENTER)

student_records_tree.pack(fill=tk.BOTH, expand=True)

# Records table
records_label = tk.Label(save_tab, text="📋 Saved Records", font=(
    "Segoe UI", 12, "bold"), fg=TEXT_COLOR, bg=GLASS_BG)
records_label.pack(anchor=tk.W, padx=20, pady=(20, 10))

# Create shadow frame for records table
table_shadow = tk.Frame(save_tab, bg="#0d1420", highlightthickness=0)
table_shadow.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

# Create treeview for records with shadow effect
tree_frame = tk.Frame(table_shadow, bg=GLASS_BG, highlightthickness=0)
tree_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

tree_scroll = ttk.Scrollbar(tree_frame)
tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

records_tree = ttk.Treeview(tree_frame, columns=('Student', 'Course', 'Score',
                            'Level', 'Semester', 'Session'), height=6, yscrollcommand=tree_scroll.set)
tree_scroll.config(command=records_tree.yview)

records_tree.column('#0', width=0, stretch=tk.NO)
records_tree.column('Student', anchor=tk.W, width=140)
records_tree.column('Course', anchor=tk.W, width=180)
records_tree.column('Score', anchor=tk.CENTER, width=80)
records_tree.column('Level', anchor=tk.CENTER, width=80)
records_tree.column('Semester', anchor=tk.CENTER, width=80)
records_tree.column('Session', anchor=tk.W, width=120)

records_tree.heading('#0', text='', anchor=tk.W)
records_tree.heading('Student', text='Student Name', anchor=tk.W)
records_tree.heading('Course', text='Course', anchor=tk.W)
records_tree.heading('Score', text='Score', anchor=tk.CENTER)
records_tree.heading('Level', text='Level', anchor=tk.CENTER)
records_tree.heading('Semester', text='Semester', anchor=tk.CENTER)
records_tree.heading('Session', text='Session', anchor=tk.W)

records_tree.pack(fill=tk.BOTH, expand=True)

# Style the treeview for glassmorphism dark theme
style = ttk.Style()
style.theme_use('clam')
style.configure('Treeview', background=GLASS_BG,
                foreground=WHITE, fieldbackground=GLASS_BG)
style.map('Treeview', background=[('selected', GLASS_LIGHT)])
style.configure('Treeview.Heading', background=GLASS_LIGHT,
                foreground=WHITE, relief=tk.FLAT, borderwidth=0)

# ============= CALCULATE GPA TAB =============
gpa_tab = tk.Frame(content_frame, bg=GLASS_BG)

# GPA form shadow and container
gpa_shadow = tk.Frame(gpa_tab, bg="#0d1420", highlightthickness=0)
gpa_shadow.pack(fill=tk.X, padx=20, pady=(15, 0))

gpa_form_frame = tk.Frame(gpa_shadow, bg=GLASS_LIGHT, highlightthickness=0)
gpa_form_frame.pack(fill=tk.X, padx=3, pady=3)

gpa_label = tk.Label(gpa_form_frame, text="👤 Student Name:", font=(
    "Segoe UI", 11, "bold"), fg=TEXT_COLOR, bg=GLASS_LIGHT)
gpa_label.pack(anchor=tk.W, pady=(20, 8), padx=20)

gpa_name_entry = tk.Entry(gpa_form_frame, font=("Segoe UI", 11), fg=INPUT_FG,
                          bg=INPUT_BG, relief=tk.FLAT, bd=1, insertbackground=PRIMARY_COLOR)
gpa_name_entry.pack(fill=tk.X, ipady=12, padx=20)

# GPA entry focus effects


def on_gpa_name_focus(event):
    gpa_name_entry.config(relief=tk.FLAT, bd=2)


def on_gpa_name_unfocus(event):
    gpa_name_entry.config(relief=tk.FLAT, bd=1)


gpa_name_entry.bind('<FocusIn>', on_gpa_name_focus)
gpa_name_entry.bind('<FocusOut>', on_gpa_name_unfocus)


def calculate_gpa_from_entry():
    name = gpa_name_entry.get().strip()
    name_entry.delete(0, tk.END)
    name_entry.insert(0, name)
    calculate_student_gpa()
    switch_tab("save")


gpa_btn = tk.Button(
    gpa_form_frame,
    text="📊 Calculate GPA",
    command=calculate_gpa_from_entry,
    font=("Segoe UI", 12, "bold"),
    fg=WHITE,
    bg=PRIMARY_COLOR,
    activebackground=ACCENT,
    relief=tk.FLAT,
    bd=0,
    pady=12,
    cursor="hand2"
)
gpa_btn.pack(fill=tk.X, padx=20, pady=(0, 20))

# GPA button hover effects


def on_gpa_hover(event):
    gpa_btn.config(bg="#5969d9")


def on_gpa_leave(event):
    gpa_btn.config(bg=PRIMARY_COLOR)


gpa_btn.bind('<Enter>', on_gpa_hover)
gpa_btn.bind('<Leave>', on_gpa_leave)

# All GPAs table
all_gpas_label = tk.Label(gpa_tab, text="📊 All Students' GPAs", font=(
    "Segoe UI", 12, "bold"), fg=TEXT_COLOR, bg=GLASS_BG)
all_gpas_label.pack(anchor=tk.W, padx=20, pady=(20, 10))

# Create shadow frame for GPA table
gpa_table_shadow = tk.Frame(gpa_tab, bg="#0d1420", highlightthickness=0)
gpa_table_shadow.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

# Create treeview for all GPAs
gpa_tree_frame = tk.Frame(gpa_table_shadow, bg=GLASS_BG, highlightthickness=0)
gpa_tree_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

gpa_tree_scroll = ttk.Scrollbar(gpa_tree_frame)
gpa_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

gpa_tree = ttk.Treeview(gpa_tree_frame, columns=(
    'Student', 'GPA'), height=8, yscrollcommand=gpa_tree_scroll.set)
gpa_tree_scroll.config(command=gpa_tree.yview)

gpa_tree.column('#0', width=0, stretch=tk.NO)
gpa_tree.column('Student', anchor=tk.W, width=250)
gpa_tree.column('GPA', anchor=tk.CENTER, width=100)

gpa_tree.heading('#0', text='', anchor=tk.W)
gpa_tree.heading('Student', text='Student Name', anchor=tk.W)
gpa_tree.heading('GPA', text='GPA', anchor=tk.CENTER)

gpa_tree.pack(fill=tk.BOTH, expand=True)

# Add button to show all GPAs chart
all_gpas_chart_btn = tk.Button(
    gpa_tab,
    text="📈 Show All GPAs Chart",
    command=show_all_gpas,
    font=("Segoe UI", 11, "bold"),
    fg=WHITE,
    bg=SUCCESS_COLOR,
    activebackground="#3ad565",
    relief=tk.FLAT,
    bd=0,
    padx=20,
    pady=12,
    cursor="hand2"
)
all_gpas_chart_btn.pack(fill=tk.X, padx=20, pady=(0, 20))

# ============= CHART TAB =============
chart_tab = tk.Frame(content_frame, bg=GLASS_BG)

# Chart form shadow and container
chart_shadow = tk.Frame(chart_tab, bg="#0d1420", highlightthickness=0)
chart_shadow.pack(fill=tk.X, padx=20, pady=(15, 0))

chart_form_frame = tk.Frame(chart_shadow, bg=GLASS_LIGHT, highlightthickness=0)
chart_form_frame.pack(fill=tk.X, padx=3, pady=3)

chart_label = tk.Label(chart_form_frame, text="👤 Student Name:", font=(
    "Segoe UI", 11, "bold"), fg=TEXT_COLOR, bg=GLASS_LIGHT)
chart_label.pack(anchor=tk.W, pady=(20, 8), padx=20)

chart_name_entry = tk.Entry(chart_form_frame, font=(
    "Segoe UI", 11), fg=INPUT_FG, bg=INPUT_BG, relief=tk.FLAT, bd=1, insertbackground=PRIMARY_COLOR)
chart_name_entry.pack(fill=tk.X, ipady=12, padx=20)

# Chart entry focus effects


def on_chart_name_focus(event):
    chart_name_entry.config(relief=tk.FLAT, bd=2)


def on_chart_name_unfocus(event):
    chart_name_entry.config(relief=tk.FLAT, bd=1)


chart_name_entry.bind('<FocusIn>', on_chart_name_focus)
chart_name_entry.bind('<FocusOut>', on_chart_name_unfocus)


def show_chart_from_entry():
    name = chart_name_entry.get().strip()
    name_entry.delete(0, tk.END)
    name_entry.insert(0, name)
    show_chart()
    switch_tab("save")


chart_btn = tk.Button(
    chart_form_frame,
    text="📈 Show Chart",
    command=show_chart_from_entry,
    font=("Segoe UI", 12, "bold"),
    fg=WHITE,
    bg=PRIMARY_COLOR,
    activebackground=ACCENT,
    relief=tk.FLAT,
    bd=0,
    pady=12,
    cursor="hand2"
)
chart_btn.pack(fill=tk.X, padx=20, pady=(0, 20))

# Chart button hover effects


def on_chart_hover(event):
    chart_btn.config(bg="#5969d9")


def on_chart_leave(event):
    chart_btn.config(bg=PRIMARY_COLOR)


chart_btn.bind('<Enter>', on_chart_hover)
chart_btn.bind('<Leave>', on_chart_leave)

# Separator
separator = tk.Frame(chart_tab, bg=GLASS_LIGHT, height=2)
separator.pack(fill=tk.X, padx=20, pady=(20, 20))

# All GPAs chart section
all_gpas_section_label = tk.Label(chart_tab, text="📊 View All Students' GPAs", font=(
    "Segoe UI", 12, "bold"), fg=TEXT_COLOR, bg=GLASS_BG)
all_gpas_section_label.pack(anchor=tk.W, padx=20, pady=(0, 10))

chart_all_gpas_btn = tk.Button(
    chart_tab,
    text="📈 Show All Students' GPA Chart",
    command=show_all_gpas,
    font=("Segoe UI", 12, "bold"),
    fg=WHITE,
    bg=SUCCESS_COLOR,
    activebackground="#3ad565",
    relief=tk.FLAT,
    bd=0,
    padx=20,
    pady=12,
    cursor="hand2"
)
chart_all_gpas_btn.pack(fill=tk.X, padx=20, pady=(0, 20))

# ============= GRADE MANAGER TAB =============
grade_tab = tk.Frame(content_frame, bg=GLASS_BG)

gm_shadow = tk.Frame(grade_tab, bg="#0d1420", highlightthickness=0)
gm_shadow.pack(fill=tk.X, padx=20, pady=(15, 0))

gm_frame = tk.Frame(gm_shadow, bg=GLASS_LIGHT, highlightthickness=0)
gm_frame.pack(fill=tk.X, padx=3, pady=3)

gm_label = tk.Label(gm_frame, text="👤 Student Name:", font=(
    "Segoe UI", 11, "bold"), fg=TEXT_COLOR, bg=GLASS_LIGHT)
gm_label.pack(anchor=tk.W, pady=(20, 8), padx=20)

gm_name_entry = tk.Entry(gm_frame, font=("Segoe UI", 11), fg=INPUT_FG,
                         bg=INPUT_BG, relief=tk.FLAT, bd=1, insertbackground=PRIMARY_COLOR)
gm_name_entry.pack(fill=tk.X, ipady=12, padx=20)

# Level select
gm_level_label = tk.Label(gm_frame, text="🏷️ Level:", font=(
    "Segoe UI", 11, "bold"), fg=TEXT_COLOR, bg=GLASS_LIGHT)
gm_level_label.pack(anchor=tk.W, pady=(10, 4), padx=20)
gm_level_var = tk.StringVar()
gm_level_menu = ttk.Combobox(gm_frame, values=(
    "100", "200"), textvariable=gm_level_var)
gm_level_menu.set("")
gm_level_menu.pack(fill=tk.X, padx=20, pady=(0, 8))

# Session
gm_session_label = tk.Label(gm_frame, text="🏫 Session (e.g., 2024/2025):",
                            font=("Segoe UI", 11, "bold"), fg=TEXT_COLOR, bg=GLASS_LIGHT)
gm_session_label.pack(anchor=tk.W, pady=(10, 4), padx=20)
gm_session_entry = tk.Entry(gm_frame, font=("Segoe UI", 11), fg=INPUT_FG,
                            bg=INPUT_BG, relief=tk.FLAT, bd=1, insertbackground=PRIMARY_COLOR)
gm_session_entry.pack(fill=tk.X, ipady=8, padx=20, pady=(0, 8))

# Semester selector for single-semester GPA
gm_sem_label = tk.Label(gm_frame, text="📆 Semester (for single-semester GPA):",
                        font=("Segoe UI", 11, "bold"), fg=TEXT_COLOR, bg=GLASS_LIGHT)
gm_sem_label.pack(anchor=tk.W, pady=(10, 4), padx=20)
gm_sem_var = tk.StringVar()
gm_sem_menu = ttk.Combobox(gm_frame, values=(
    "1", "2"), textvariable=gm_sem_var)
gm_sem_menu.set("")
gm_sem_menu.pack(fill=tk.X, padx=20, pady=(0, 8))

gm_btn_frame = tk.Frame(gm_frame, bg=GLASS_LIGHT)
gm_btn_frame.pack(fill=tk.X, padx=20, pady=(10, 20))


def gm_calculate_semester():
    name = gm_name_entry.get().strip()
    level = gm_level_var.get().strip()
    session_val = gm_session_entry.get().strip()
    semester = gm_sem_var.get().strip()

    if not name or not level or not session_val or not semester:
        show_message('⚠️ Name, level, session and semester required', 'error')
        return

    scores = load_student_scores(
        name, level=level, semester=semester, session=session_val)
    if not scores:
        show_message('❌ No records found for this selection', 'error')
        return
    gpa = calculate_gpa(scores)
    gm_result_var.set(
        f"Semester {semester} GPA: {gpa} ({len(scores)} course(s))")
    show_message('✓ Semester GPA calculated', 'success')


def gm_calculate_session():
    name = gm_name_entry.get().strip()
    level = gm_level_var.get().strip()
    session_val = gm_session_entry.get().strip()

    if not name or not level or not session_val:
        show_message('⚠️ Name, level and session required', 'error')
        return

    s1 = load_student_scores(
        name, level=level, semester='1', session=session_val)
    s2 = load_student_scores(
        name, level=level, semester='2', session=session_val)
    gpa1 = calculate_gpa(s1)
    gpa2 = calculate_gpa(s2)
    combined = s1 + s2
    cgpa = calculate_gpa(combined) if combined else 0.0
    gm_result_var.set(
        f"Sem1: {gpa1} ({len(s1)})  |  Sem2: {gpa2} ({len(s2)})  |  CGPA: {cgpa}")
    show_message('✓ Session CGPA calculated', 'success')


gm_calc_sem_btn = tk.Button(gm_btn_frame, text="Calculate Semester GPA", command=gm_calculate_semester, font=(
    "Segoe UI", 11, "bold"), fg=WHITE, bg=PRIMARY_COLOR, relief=tk.FLAT, bd=0, padx=10, pady=10)
gm_calc_sem_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 8))

gm_calc_sess_btn = tk.Button(gm_btn_frame, text="Get Session CGPA", command=gm_calculate_session, font=(
    "Segoe UI", 11, "bold"), fg=WHITE, bg=SUCCESS_COLOR, relief=tk.FLAT, bd=0, padx=10, pady=10)
gm_calc_sess_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(8, 0))

gm_result_var = tk.StringVar()
gm_result_label = tk.Label(gm_frame, textvariable=gm_result_var, font=(
    "Segoe UI", 11, "bold"), fg=ACCENT, bg=GLASS_LIGHT)
gm_result_label.pack(fill=tk.X, padx=20, pady=(10, 20))

# Show first tab and load records
switch_tab("save")
load_saved_records()

window.mainloop()
