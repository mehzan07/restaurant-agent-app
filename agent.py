from pathlib import Path
import re

from agents import Agent, Runner, function_tool

PROJECT_DIR = Path(__file__).parent.resolve()
SKILLS_DIR = PROJECT_DIR / "skills"


def get_available_skills():
    """
    Read only the folder name and description of each Skill.
    """

    skills = {}

    for skill_folder in SKILLS_DIR.iterdir():

        if not skill_folder.is_dir():
            continue

        skill_file = skill_folder / "SKILL.md"

        if not skill_file.exists():
            continue

        content = skill_file.read_text(encoding="utf-8")

        description_match = re.search(
            r"^description:\s*(.+)$",
            content,
            re.MULTILINE,
        )

        if description_match:
            description = description_match.group(1).strip()
        else:
            description = "No description available."

        skills[skill_folder.name] = description

    return skills


def load_selected_skills(selected_skill_names):
    """
    Load complete SKILL.md content only for selected Skills.
    """

    selected_skills = {}

    for skill_name in selected_skill_names:

        skill_file = SKILLS_DIR / skill_name / "SKILL.md"

        if skill_file.exists():
            selected_skills[skill_name] = skill_file.read_text(
                encoding="utf-8"
            )

    return selected_skills


def build_skill_catalog(skills):
    lines = []

    for name, description in skills.items():
        lines.append(f"- {name}: {description}")

    return "\n".join(lines)


def build_skill_instructions(skills):
    parts = []

    for name, content in skills.items():

        parts.append(
            f"""
==============================
SKILL: {name}
==============================

{content}
"""
        )

    return "\n".join(parts)


@function_tool
def write_project_file(relative_path: str, content: str) -> str:
    """
    Create or overwrite a text file inside the restaurant project.

    Args:
        relative_path: File path relative to the project root,
            for example templates/index.html.
        content: Complete text content to write to the file.
    """

    target_path = (PROJECT_DIR / relative_path).resolve()

    try:
        target_path.relative_to(PROJECT_DIR)
    except ValueError:
        return "ERROR: Writing outside the project directory is not allowed."

    target_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    target_path.write_text(
        content,
        encoding="utf-8"
    )

    return f"Created file: {relative_path}"


if __name__ == "__main__":

    # ========================================
    # STAGE 1
    # Discover available Skills
    # ========================================

    available_skills = get_available_skills()

    print("Available skills:")

    for skill_name, description in available_skills.items():
        print(f"- {skill_name}: {description}")

    skill_catalog = build_skill_catalog(available_skills)

    user_request = """
Create the first version of the restaurant reservation application.

For this version create only:

- app.py
- templates/index.html
- static/css/style.css
- static/js/app.js

Requirements:

- Python Flask backend
- modern responsive restaurant interface
- reservation form
- name
- email
- phone
- reservation date
- reservation time
- number of guests
- special requests

The reservation form does not need database storage yet.

Create the actual files using the available file tool.
"""

    # ========================================
    # STAGE 2
    # Select relevant Skills
    # ========================================

    selector_agent = Agent(
        name="Skill Selector",
        instructions=f"""
You are responsible for selecting the correct Skills
for a software development task.

AVAILABLE SKILLS:

{skill_catalog}

Analyze the user's request.

Return ONLY the folder names of the Skills
that are required.

Return one Skill name per line.

Do not include explanations.
Do not include bullets.
Do not invent Skill names.
""",
    )

    selection_result = Runner.run_sync(
        selector_agent,
        user_request,
    )

    selected_skill_names = [
        line.strip()
        for line in selection_result.final_output.splitlines()
        if line.strip() in available_skills
    ]

    print("\nSelected skills:")

    for skill_name in selected_skill_names:
        print(f"- {skill_name}")

    # ========================================
    # STAGE 3
    # Load selected Skills
    # ========================================

    selected_skills = load_selected_skills(
        selected_skill_names
    )

    selected_skill_instructions = build_skill_instructions(
        selected_skills
    )

    # ========================================
    # STAGE 4
    # Development Agent with file tool
    # ========================================

    development_agent = Agent(
        name="Restaurant Development Agent",

        instructions=f"""
You are an AI software development agent.

You are working only inside this restaurant project.

Use the selected Skills below.

SELECTED SKILLS:

{selected_skill_instructions}

You have a tool named write_project_file.

Use that tool to create the requested project files.

Rules:

1. Create only files required by the current task.
2. Never attempt to write outside the project directory.
3. Do not modify the Skills.
4. Do not create database files yet.
5. Do not add email functionality yet.
6. Do not add deployment configuration yet.
7. Make the interface responsive for desktop, tablet and mobile.
8. After creating the files, summarize exactly what was created.
""",

        tools=[
            write_project_file
        ],
    )

    result = Runner.run_sync(
        development_agent,
        user_request,
    )

    print("\nAgent response:\n")

    print(result.final_output)