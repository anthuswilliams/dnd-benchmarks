import json


def convert_json(input):
    """
    Converts from DNDBeyond JSON encoding to our custom encoding which is smaller, contains
    the parts relevant to our LLM and doesn't use as much context.
    
    input - dict
      Deserialized from DND Beyond JSON format

    Returns dict
    """
    data = input["data"]
    ret = {
        "character_name": data["name"],
        "class": data["?"]
        "level": data["level"]
        "background": data["background"]
        "player_name":
        "race":
        "alignment":
        "experience_points":
        "abilities": {
            "strength":
            "dexterity":
            "constitution":
            "intelligence":
            "wisdom":
            "charisma":

        }
# Skills

    }

    
def convert_file(input_file, output_file):
    with open(input_file, 'r') as fh:
        input_dict = json.decodes(fh.read())
        output_dict = convert_json(input_dict)
        with open(output_file, 'w') as w:
            w.write(json.encodes(output_dict))
