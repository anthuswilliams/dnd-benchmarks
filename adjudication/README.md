# Adjudication

This folder contains a set of benchmark conversations for adjudicating on the rules of an RPG.
They are captured from actual conversations generated using OpenAI's `gpt-4o-mini`, but in some cases
the final responses have been replaced by hand in favor of a more ideal response.

## Ideal responses

This corpus is specifically selected to favor a RAW (rules as written) interpretation of D&D 5th edition.
Some of the questions are particularly hard to answer using only RAW materials. In those situations, we prefer
responses that explicitly include phrases of the form "it is up to the DM's discretion". The reason is that
we would like to use a model trained on this corpus as an adjudicator agent for a different LLM acting as the DM,
and that type of phrasing could be a useful hook for the DM agent to extemporize without violating the spirit of
the game. This could result in an experience that is more fun for players if the DM seems more human-like in these
situations. If you are using this benchmark for a different purpose, this might be a bias you should be aware of.