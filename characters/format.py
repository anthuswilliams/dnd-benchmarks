import json
import glob

def convert_json(input):
    """
    Converts from DNDBeyond JSON encoding to our custom encoding which is smaller, contains
    the parts relevant to our LLM and doesn't use as much context.
    
    input - dict
      Deserialized from DND Beyond JSON format

    Returns dict
    """
    data = input["data"]
    # print(data["classes"])
    ret = {
        "character_name": data["name"],
        "class": data["classes"][0]["definition"]["name"],
        "subclass": data["classes"][0]["definition"]["subclassDefinition"],
        "level": data["classes"][0]["level"],
        "background": data["background"]["definition"]["name"],
        "race": data["race"]["fullName"],
        "alignment": data["alignmentId"],
        "experience_points": data["currentXp"],
        "max_hit_points": data["baseHitPoints"],
        "abilities": {
            "strength": data["stats"][0]["value"],  
            "dexterity": data["stats"][1]["value"],
            "constitution": data["stats"][2]["value"],
            "intelligence": data["stats"][3]["value"],
            "wisdom": data["stats"][4]["value"],
            "charisma": data["stats"][5]["value"],
        },
        "expertise": get_abilities(data, "expertise"),
        "proficiencies": get_abilities(data, "proficiency"),
        "languages": get_abilities(data, "language"),
        "equipment": get_equipment(data),
        "currency": data["currencies"],
        "class_features": get_class_features(data),
        "spells": get_spell_list(data),
        "racial_traits": get_racial_traits(data),
        "personality_traits": data["traits"],
    }
    return ret
# Skills
def get_racial_traits(input):
    """
    Returns a list of racial traits that the character has.
    """
    racial_trait_list = set()
    for trait in input["race"]["racialTraits"]:
        racial_trait_list.add(trait["definition"]["name"])
    return list(racial_trait_list)

def get_equipment(input):
    """
    Returns a list of equipment that the character has.
    """
    equipment_list = set()
    for item in input["inventory"]:
        equipment_list.add(item["definition"]["name"])
    return list(equipment_list)


def get_class_features(input):
    """
    Returns a list of class features that the character has.
    """
    class_feature_list = set()
    for feature in input["classes"][0]["classFeatures"]:
        if feature["definition"]["requiredLevel"] <= input["classes"][0]["level"]:
            class_feature_list.add(feature["definition"]["name"])
    return list(class_feature_list)

def get_spell_list(input):
    """
    Returns a list of spells that the character has.
    """
    spell_list = set()
    
    check_list = ["class", "race", "background", "item", "feat"]

    for check in check_list:
        print(check)
        try:
            for spell in input["spells"][check]:
                try:
                    spell_list.add(spell["definition"]["name"])
                except:
                    pass
        except:
            pass
    return list(spell_list)


def get_abilities(input, type):
    """
    Returns a list of skills that the character has expertise in.
    """
    proficiency_list = set()

    check_list = ["class", "background", "race"] 
    for check in check_list:
        for skill in input["modifiers"][check]:
            if skill["type"] == type:
                proficiency_list.add(skill["friendlySubtypeName"])
    return list(proficiency_list)
    
def convert_file(input_file, output_file):
    with open(input_file, 'r') as fh:
        input_dict = json.loads(fh.read())
        output_dict = convert_json(input_dict)
        with open(output_file, 'w') as w:
            w.write(json.dumps(output_dict))

file_list = glob.glob("[0-9][0-9].json")
print(file_list)
for file in file_list:
    convert_file(file, file.replace(".json", "_formatted.json"))