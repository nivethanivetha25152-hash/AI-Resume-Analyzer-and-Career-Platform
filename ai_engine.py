import pdfplumber

def analyze_resume(filepath):

    text = ""

    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text += page.extract_text()

    text = text.lower()

    skills = ["python","flask","html","css","mysql","java","javascript"]

    found_skills = [s for s in skills if s in text]

    missing_skills = [s for s in skills if s not in text]

    score = int((len(found_skills) / len(skills)) * 100)

    if "python" in text:
        role = "Python Developer"
    elif "java" in text:
        role = "Java Developer"
    else:
        role = "Fresher"

    suggestions = []

    if "github" not in text:
        suggestions.append("Add GitHub Profile")

    if "internship" not in text:
        suggestions.append("Mention Internship")

    if score < 60:
        suggestions.append("Improve ATS Keywords")

    return score, role, found_skills, missing_skills, suggestions