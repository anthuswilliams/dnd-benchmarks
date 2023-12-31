import json
import random
import re
from glob import glob

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from openai import OpenAI

import CONSTANTS as c

device = "cuda" # the device to load the model onto

model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1", torch_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")

system_message = """You are a dungeon master, ready to start a one shot for Dungeons and Dragons 5th edition.
Don't make any assumptions about player actions and say the total result with modifiers for any dice rolls.
If the player provides a character sheet, use it to inform your responses.  If a character is proficient in a skill,
then when they roll the dice, add the proficiency bonus and the relevant ability modifier to the result.
To get the ability modifier, subtract 10 from the ability score, divide by 2, and round down."""

def start_game(theme, setting, character):
    formatted_question = f"I would like to play a {theme} game in {setting}.  Here is my character sheet: {character_sheet}"

    encodeds = tokenizer.apply_chat_template([{
        "role": "user",
        # mistral does not support a "system" prompt. We prepend it to the user prompt so that we have some relatability between GPT-* and mistral
        "content": system_message #f"{system_message}\n\n{formatted_question}",
    }], return_tensors="pt")
    model_inputs = encodeds.to(device)
    model.to(device)

    generated_ids = model.generate(model_inputs, max_new_tokens=1000, do_sample=True)
    decodeds = tokenizer.batch_decode(generated_ids)

    response = re.search(r"\[/INST\](.*?)</s>", decodeds[0], flags=re.DOTALL)
    if not response:
        raise Exception("Expected to response to look like '<s>[INST] instructions [/INST] response </s>")
    response_content = response.group(1).strip()

    return formatted_question, [{
        "role": "user",
        # We omit the system prompt, so that at judging time the conversation can be more
        #  comparable to a ChatGPT conversation (which also omits the system prompt)
        # The intuition here is that at judging time want to evaluate the quality of the system prompt itself,
        #  not simply assess how well the (possibly mediocre) system prompt was respected
        "content": formatted_question
    }, {
        "role": "assistant",
        "content": response_content
    }]


judge_prompt = """
Please act as an impartial judge and evaluate the quality of the response provided by an
AI assistant to the user question displayed below. Your evaluation should consider factors
such as the helpfulness, relevance, accuracy, depth, creativity, and level of detail of
the response. Begin your evaluation by providing a short explanation. Be as objective as
possible. After providing your explanation, please rate the response on a scale of 1 to 10
by strictly following this format: "[[rating]]", for example: "Rating: [[5]]"
"""

client = OpenAI()

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
        fh.write(json.dumps(setting_decl, indent=4))

    score = score_game(initial_prompt, setting_decl[-1]["content"])

    with open(f"scores.json", "r", encoding="utf-8") as fh:
        current_scores = json.loads(fh.read())

    current_scores.append({
        "convo_number": convo_num,
        "model": "Mistral-7B-Instruct-v0.1",
        "system_message": system_message,
        "theme": theme,
        "setting": setting,
        "character": character.split("/")[-1].split(".")[0],
        "score": score,
    })

    with open(f"scores.json", "w") as fh:    
        fh.write(json.dumps(current_scores, indent=4))