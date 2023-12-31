import random
import json
from glob import glob

from openai import OpenAI
from conversations import chat_one

import CONSTANTS as c

client = OpenAI()

system_message = """You are a dungeon master, ready to start a one shot for Dungeons and Dragons 5th edition.
Don't make any assumptions about player actions and say the total result with modifiers for any dice rolls.
If the player provides a character sheet, use it to inform your responses.  If a character is proficient in a skill,
then when they roll the dice, add the proficiency bonus and the relevant ability modifier to the result.
To get the ability modifier, subtract 10 from the ability score, divide by 2, and round down."""


def start_game(theme, setting, character_sheet):
    formatted_question = f"I would like to play a {theme} game in {setting}.  Here is my character sheet: {character_sheet}"
    messages = [
        {"role": "system", "content": system_message},
        {
            "role": "user",
            "content": formatted_question,
        },
        # {"role": "assistant", "content": chat_one.response_one},
        # {"role": "user", "content": chat_one.input_one},
        # {"role": "assistant", "content": chat_one.response_two},
        # {"role": "user", "content": chat_one.input_two},
    ]

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages
    )

    resp = completion.choices[0].message
    return formatted_question, messages + [{"role": resp.role, "content": resp.content}]


judge_prompt = """
Please act as an impartial judge and evaluate the quality of the response provided by an
AI assistant to the user question displayed below. Your evaluation should consider factors
such as the helpfulness, relevance, accuracy, depth, creativity, and level of detail of
the response. Begin your evaluation by providing a short explanation. Be as objective as
possible. After providing your explanation, please rate the response on a scale of 1 to 10
by strictly following this format: "[[rating]]", for example: "Rating: [[5]]"
"""


def score_game(initial_question, bot_response):
    formatted_question = f"[Question]\n {initial_question}\n [The Start of Assistant's Answer]\n {bot_response}\n [The End of Assistant's Answer]"
    messages = [
        {"role": "system", "content": judge_prompt},
        {"role": "user", "content": formatted_question},
    ]

    completion = client.chat.completions.create(
        model="gpt-4-1106-preview", messages=messages
    )

    print(completion.choices[0].message)
    return completion.choices[0].message.content


if __name__ == "__main__":
    theme = random.choice(c.DND_CAMPAIGN_THEMES)
    setting = random.choice(c.DND_SETTINGS)
    character = random.choice(glob("characters/formatted_characters/*.json"))

    print("Evaluating %s theme in %s with character %s" % (theme, setting, character))

    with open(character, "r", encoding="utf-8") as fh:
        character_sheet = fh.read()

    initial_prompt, setting_decl = start_game(theme, setting, character_sheet)
    convo_num = len(glob("conversations/*.json"))
    with open(f"conversations/{convo_num}.json", "w") as fh:
        fh.write(json.dumps(setting_decl))

    score = score_game(initial_prompt, setting_decl[-1]["content"])

    with open(f"scores.txt", "a") as fh:
        score_dict = {
            "convo_number": convo_num,
            "system_message": system_message,
            "theme": theme,
            "setting": setting,
            "character": character.split("/")[-1].split(".")[0],
            "score": score,
        }
        fh.write(f"{json.dumps(score_dict)}\n")
