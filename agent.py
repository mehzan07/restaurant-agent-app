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

@function_tool
def read_project_file(relative_path: str) -> str:
    """
    Read a text file inside the restaurant project.

    Args:
        relative_path: File path relative to the project root,
            for example app.py or templates/index.html.
    """

    target_path = (PROJECT_DIR / relative_path).resolve()

    try:
        target_path.relative_to(PROJECT_DIR)
    except ValueError:
        return "ERROR: Reading outside the project directory is not allowed."

    if not target_path.exists():
        return f"ERROR: File does not exist: {relative_path}"

    if not target_path.is_file():
        return f"ERROR: Not a file: {relative_path}"

    return target_path.read_text(encoding="utf-8")

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
Upgrade the existing restaurant reservation application to Version 6.

The application already has:

- Flask backend
- responsive reservation form
- SQLite reservation database
- unique booking references
- Gmail SMTP confirmation email
- server-side validation

Do not rebuild the application from scratch.

Add automated tests for the reservation workflow.

Requirements:

1. Use pytest.
2. Create automated tests for:
   - home page loads successfully
   - valid reservation succeeds
   - missing customer name is rejected
   - invalid email is rejected
   - zero guests are rejected
   - negative guests are rejected
   - past reservation date is rejected
   - invalid reservation time is rejected
   - successful reservation is stored in SQLite
   - booking reference is generated
   - booking reference is unique
   - confirmation response contains the booking reference
3. Email sending must not send real emails during automated tests.
4. Mock or disable SMTP during tests.
5. Test email success behavior.
6. Test email failure behavior.
7. If email sending fails:
   - reservation must remain stored
   - booking reference must remain valid
8. Tests must use a temporary test database, not the real reservations.sqlite3 file.
9. Preserve all existing V5 functionality.
10. Do not add deployment functionality yet.

Before modifying any existing file, read it first.

Use the project tools to create or update the files.
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

You have two project tools:

- read_project_file
- write_project_file

Before modifying an existing file, read it first.

Preserve existing working functionality unless the current task
explicitly requires changing it.

Never attempt to read or write outside the project directory.

Never modify the Skill files.

Never expose credentials or secrets.

Use environment variables for sensitive configuration such as
SMTP usernames, passwords, API keys, or access tokens.

Preserve the existing SQLite reservation database.

Preserve the existing booking reference functionality.

Preserve the existing email confirmation functionality.

Preserve the responsive desktop, tablet and mobile design.

When creating tests, never send real emails and never modify
the production reservation database.

Tests must use isolated test data and a temporary test database.

Do not add deployment configuration yet.

Use write_project_file to create or update project files.

After completing the task, summarize exactly what was created
or modified.
""",

        tools=[
                read_project_file,
               write_project_file,
            ],
         )

    result = Runner.run_sync(
        development_agent,
        user_request,
    )

    print("\nAgent response:\n")

    print(result.final_output)