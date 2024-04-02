import json
import re
from glob import glob
from transformers import AutoModelForCausalLM, AutoTokenizer

from openai import OpenAI

import CONSTANTS as c

client = OpenAI()


def score_response(result):
    formatted_question = f"[Question]\n {result['question']}\n\n[Correct Answer]\n{result['answer']}\n\n[The Start of Assistant's Answer]\n {result['prediction']}\n [The End of Assistant's Answer]"
    messages = [
        {"role": "system", "content": c.JUDGE_PROMPT},
        {"role": "user", "content": formatted_question},
    ]

    completion = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=messages,
        max_tokens=1,
        logit_bias={15: 100, 16: 100},
    )

    print(completion.choices[0].message)
    return completion.choices[0].message.content


def evaluate(metadata=None, invoke_model=None):
    if not invoke_model:
        raise ValueError("invoke_model should be a callable")
    if not metadata:
        metadata = {}

    questions = [
        {
            "question": lambda c: f"What is {c['character_name']}'s race?",
            "answer": lambda c: c["race"],
        },
        {
            "question": lambda c: f"What is {c['character_name']}'s class?",
            "answer": lambda c: c["class"],
        },
        {
            "question": lambda c: f"What is {c['character_name']}'s background?",
            "answer": lambda c: c["background"],
        },
    ]

    characters = glob("characters/formatted_characters/*.json")
    scores = []
    for character in characters:
        with open(character, "r", encoding="utf-8") as fh:
            character_sheet = fh.read()

        for q in questions:
            result = invoke_model(character_sheet, q)
        score = score_response(result)
        scores.append(
            {"character": character, "result": result, "score": score, **metadata}
        )

    with open(f"scores.json", "w") as fh:
        fh.write(json.dumps(scores, indent=4))


device = "cuda"  # the device to load the model onto

model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.1", torch_dtype=torch.float16
)
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")


def inference(character=None, question=None):
    encodeds = tokenizer.apply_chat_template(
        [
            {
                "role": "user",
                # mistral does not support a "system" prompt. We prepend it to the user prompt so that we have some relatability between GPT-* and mistral
                "content": f"{const.SYSTEM_MESSAGE}\n\nHere is the character sheet: {json.dumps(character)}\n\n{question['question'](character)}",
            }
        ],
        return_tensors="pt",
    )
    model_inputs = encodeds.to(device)
    model.to(device)

    generated_ids = model.generate(
        model_inputs,
        max_new_tokens=1000,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
    )
    decodeds = tokenizer.batch_decode(generated_ids)

    response = re.search(r"\[/INST\](.*?)</s>", decodeds[0], flags=re.DOTALL)
    if not response:
        raise Exception(
            "Expected to response to look like '<s>[INST] instructions [/INST] response </s>"
        )
    response_content = response.group(1).strip()

    # We omit the system prompt, so that at judging time the conversation can be more
    #  comparable to a ChatGPT conversation (which also omits the system prompt)
    # The intuition here is that at judging time want to evaluate the quality of the system prompt itself,
    #  not simply assess how well the (possibly mediocre) system prompt was respected
    return {
        "question": question["question"](character),
        "prediction": response_content,
        "answer": question["answer"](character),
    }


if __name__ == "__main__":
    evaluate(metadata={"model": "Mistral-7b-Instruct"}, invoke_model=inference)
