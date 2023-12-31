import re

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import pipeline

device = "cuda" # the device to load the model onto

model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1", torch_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")

def start_game(theme, setting, character_sheet, system_message):
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

if __name__ == "__main__":
    pipeline.evaluate(metadata={
        "model": "Mistral-7B-Instruct-v0.1"
    }, start_game=start_game)
