from pathlib import Path
from agents import Agent, Runner

SKILLS_DIR = Path(__file__).parent / "skills"


def load_skills():
    skills = {}

    for skill_folder in SKILLS_DIR.iterdir():
        if skill_folder.is_dir():
            skill_file = skill_folder / "SKILL.md"

            if skill_file.exists():
                skills[skill_folder.name] = skill_file.read_text(
                    encoding="utf-8"
                )

    return skills


def build_skill_instructions(skills):
    parts = []

    for skill_name, skill_content in skills.items():
        parts.append(
            f"""
==============================
SKILL: {skill_name}
==============================

{skill_content}
"""
        )

    return "\n".join(parts)


if __name__ == "__main__":
    skills = load_skills()

    print("Loaded skills:")
    for skill_name in skills:
        print(f"- {skill_name}")

    skill_instructions = build_skill_instructions(skills)

    agent = Agent(
        name="Restaurant Development Agent",
        instructions=f"""
You are an AI software development agent.

Your goal is to help build a complete restaurant application.

You have access to several specialized Skills.

For every task:

1. Analyze the user's request.
2. Decide which Skills are relevant.
3. Do not use unrelated Skills.
4. Tell the user which Skills you selected.
5. Follow the instructions from the selected Skills.
6. Create a short implementation plan.
7. Do not claim that files were changed unless you actually have tools
   that can modify files.

AVAILABLE SKILLS:

{skill_instructions}
""",
    )

    request = """
Build the reservation part of the restaurant website.

Do not create the complete application yet.

First:

1. Identify which Skills are required.
2. Explain why each Skill is needed.
3. Create a short implementation plan.
"""

    result = Runner.run_sync(agent, request)

    print("\nAgent response:\n")
    print(result.final_output)