import json
import random
from glob import glob

from openai import OpenAI

import CONSTANTS as c

client = OpenAI()

def score_game(initial_question, bot_response):
    formatted_question = f"[Question]\n {initial_question}\n [The Start of Assistant's Answer]\n {bot_response}\n [The End of Assistant's Answer]"
    messages = [
        {"role": "system", "content": c.JUDGE_PROMPT},
        {"role": "user", "content": formatted_question},
    ]

    completion = client.chat.completions.create(
        model="gpt-4-1106-preview", messages=messages
    )

    print(completion.choices[0].message)
    return completion.choices[0].message.content

def evaluate(metadata=None, start_game=None, iterations=20):
    if not start_game:
        raise ValueError("start_game should be a callable")
    if not metadata:
        metadata = {}

    convo_dir = f"conversations/{metadata['model']}"
    for i in range(iterations):
        theme = random.choice(c.DND_CAMPAIGN_THEMES)
        setting = random.choice(c.DND_SETTINGS)
        character = random.choice(glob("characters/formatted_characters/*.json"))

        print("Evaluating %s theme in %s with character %s" % (theme, setting, character))

        with open(character, "r", encoding="utf-8") as fh:
            character_sheet = fh.read()

        initial_prompt, setting_decl = start_game(theme, setting, character_sheet, c.SYSTEM_MESSAGE)
        convo_num = len(glob(f"{convo_dir}/*.json"))
        with open(f"{convo_dir}/{convo_num}.json", "w") as fh:
            fh.write(json.dumps(setting_decl, indent=4))

        score = score_game(initial_prompt, setting_decl[-1]["content"])

        with open(f"scores.json", "r", encoding="utf-8") as fh:
            current_scores_str = fh.read()
            current_scores = json.loads(current_scores_str) if current_scores_str else []

        current_scores.append({
            "convo_number": convo_num,
            "file": f"{convo_dir}/{convo_num}.json",
            **metadata,
            "theme": theme,
            "setting": setting,
            "character": character.split("/")[-1].split(".")[0],
            "judge_prompt": c.JUDGE_PROMPT,
            "score": score,
        })

        with open(f"scores.json", "w") as fh:    
            fh.write(json.dumps(current_scores, indent=4))