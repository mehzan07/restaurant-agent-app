from pathlib import Path
import re

from agents import Agent, Runner

SKILLS_DIR = Path(__file__).parent / "skills"


def get_available_skills():
    """
    Read only the folder name and description of each Skill.
    The complete SKILL.md content is not loaded yet.
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
    Load the complete SKILL.md content only
    for the Skills selected by the selector Agent.
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
    """
    Build a small catalog containing only
    Skill names and descriptions.
    """

    lines = []

    for name, description in skills.items():
        lines.append(f"- {name}: {description}")

    return "\n".join(lines)


def build_skill_instructions(skills):
    """
    Combine the complete contents of only
    the selected Skills.
    """

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
Build the reservation part of the restaurant website.

Do not build the complete restaurant application yet.
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
    # Load only the selected Skills
    # ========================================

    selected_skills = load_selected_skills(
        selected_skill_names
    )

    selected_skill_instructions = build_skill_instructions(
        selected_skills
    )

    # ========================================
    # STAGE 4
    # Restaurant Development Agent
    # ========================================

    development_agent = Agent(
        name="Restaurant Development Agent",
        instructions=f"""
You are an AI software development agent.

Your goal is to help build a restaurant application.

For this task, the following Skills have been selected.

Follow their instructions carefully.

SELECTED SKILLS:

{selected_skill_instructions}

For the current request:

1. Explain which Skills are being used.
2. Explain why each Skill is relevant.
3. Create a short implementation plan.
4. Do not build the complete application yet.
5. Do not claim that files were modified unless
   tools actually modified them.
""",
    )

    result = Runner.run_sync(
        development_agent,
        user_request,
    )

    print("\nAgent response:\n")

    print(result.final_output)