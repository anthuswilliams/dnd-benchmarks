# start with prod Elastic instance
import json
import requests
import os
import pandas as pd

from openai import OpenAI


SEARCH_PROMPT = """
Users are playing an RPG. They will ask questions pertaining to the rules, setting, lore,
and current situation. You will accept the query and return a list of relevant keywords that
can be used to locate relevant sections of the source material.

You will NOT attempt to answer the questions yourself. Your only role is to extract useful keywords
to be used in a search. Organize them in order of likely relevance, from most relevant to least.

Return the keywords in a comma delimited format with no quote characters or extraneous punctuation.
"""

ADJUDICATION_PROMPT = """
Users are playing an RPG. They will ask questions pertaining to the rules, setting, lore,
and current situation. You will answer the question based on the content provided.

Use only the content provided. IMPORTANT: Do NOT base your answers on ANYTHING other than the content itself.
Quote the content verbatim if possible (but only if it is relevant to the question!).
Otherwise, keep your answer as brief as possible. Do NOT include phrases from the original question in your response.
If the content is not sufficient to answer the question, say so.
"""

MODEL = "gpt-4o-mini"
TEMPERATURE = 0.0
KEYWORD_WEIGHTS = 0.2
KNN_WEIGHTS = 0.8


def elastic_request(data=None, url=None):
    if data:
        data = json.dumps(data)

    return requests.get(
        f"{os.getenv('ELASTIC_HOST')}/{url}",
        headers={
            "Accept": "application/json",
            "Authorization": f"ApiKey {os.getenv('K8S_ELASTIC_API_KEY')}",
            "Content-Type": "application/json"
        },
        verify=False,
        data=data
    )


_client = None


def get_client():
    global _client
    if not _client:
        _client = OpenAI()
    return _client


def generate_keywords(question):
    response = get_client().chat.completions.create(
        model=MODEL,
        temperature=TEMPERATURE,
        messages=[{
            "role": "developer",
            "content": [{
                    "type": "text",
                    "text": SEARCH_PROMPT
            }]
        }, {
            "role": "user",
            "content": [{
                "type": "text",
                "text": question
            }]
        }]
    )

    return response.choices[0].message.content


def query_elastic(question, keywords, settings):
    data = {
        "query": {
            "match": {
                "content": {
                    "query": keywords,
                    "operator": "or",
                    "boost": settings["keywordWeight"]
                }
            }
        },
        "knn": {
            "field": "content-embedding",
            "k": 10,
            "boost": settings["knnWeight"],
            "num_candidates": 10,
            "query_vector_builder": {
                "text_embedding": {
                    "model_id": "open-ai-embeddings",
                    "model_text": question
                }
            }
        }
    }

    rslt = elastic_request(url="dnd-5e*/_search", data=data)
    rslt.raise_for_status()
    return rslt.json()


def generate_response(context, question):
    response = get_client().chat.completions.create(
        model=MODEL,
        temperature=TEMPERATURE,
        messages=[
            {
                "role": "developer",
                "content": [{
                    "type": "text",
                    "text": ADJUDICATION_PROMPT
                }]
            },
            {
                "role": "assistant",
                "content": [{"type": "text", "text": c} for c in context]
            },
            {
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": question
                }]
            }
        ]
    )

    return response.choices[0].message.content

# ----
# for each question in questions/*json
   # run search with KNN and keywords settings
   # store referenced documents
   # evaluate prompt
   # store response
   # pass to judge LLM (this could be an ensemble)
   # store response


def benchmark():
    questions = []
    with open("adjudication/5e/2024-12-26.json", "r") as fh:
        questions = json.loads(fh.read())

    data = []
    for q in questions:
        datum = {
            "search_model": MODEL,
            "search_keyword_weight": KEYWORD_WEIGHTS,
            "search_knn_weight": KNN_WEIGHTS,
            "search_temperature": TEMPERATURE,
            "search_prompt": SEARCH_PROMPT,
            "adjudicator_model": MODEL,
            "adjudicator_temperature": TEMPERATURE,
            "adjudicator_prompt": ADJUDICATION_PROMPT,
            "question": q["messages"][0]["content"]
        }
        # generate keywords
        keywords = generate_keywords(datum["question"])
        datum["keywords"] = keywords
        # run search
        docs = query_elastic(datum["question"], keywords, {
                             "keywordWeight": KEYWORD_WEIGHTS, "knnWeight": KNN_WEIGHTS})
        # store referenced documents
        datum["doc_refs"] = [d["_id"] for d in docs["hits"]["hits"]]
        # run prompt
        resp = generate_response(
            context=[d["_source"]["content"] for d in docs["hits"]["hits"]],
            question=datum["question"]
        )
        # store response
        datum["response"] = resp
        data.append(datum)

    df = pd.DataFrame(data)
    print(df)
    df.to_csv("output.csv")


# this gives us a dataset for all questions with a given knn/keywords/prompt/model/temperature
# from here, we take the average for precision, recall, etc
# ---

# run the above with different settings (knn, keywords, temp, models, etc)
# this gives us 1) a set of datasets (one for each settings combo)
# a dataset of the averages, i.e. settings and how they did on precision, recall, latency, and so forth

if __name__ == "__main__":
    benchmark()
