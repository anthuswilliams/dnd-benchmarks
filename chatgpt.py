from openai import OpenAI

import pipeline

client = OpenAI()

def start_game(theme, setting, character_sheet, system_message):
    formatted_question = f"I would like to play a {theme} game in {setting}.  Here is my character sheet: {character_sheet}"
    messages = [
        {"role": "system", "content": system_message},
        {
            "role": "user",
            "content": formatted_question,
        }
    ]

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages
    )

    resp = completion.choices[0].message
    return formatted_question, messages + [{"role": resp.role, "content": resp.content}]


if __name__ == "__main__":
    pipeline.evaluate(metadata={
        "model": "gpt-3.5-turbo"
    }, start_game=start_game)