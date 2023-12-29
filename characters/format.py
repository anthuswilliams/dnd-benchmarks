import json
import glob
import re 
from bs4 import BeautifulSoup

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
        "proficiency_bonus": proficiency_bonus(data["classes"][0]["level"]),
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

def proficiency_bonus(level):
    """
    Calculate the proficiency bonus for a given level in Dungeons & Dragons 5e.
    
    The proficiency bonus starts at +2 for a 1st level character and increases
    as the character gains levels. The progression is as follows:
    Level 1-4: +2, Level 5-8: +3, Level 9-12: +4, Level 13-16: +5, Level 17-20: +6
    
    Parameters:
    level (int): The level of the character.
    
    Returns:
    int: The proficiency bonus for the given level.
    """
    # Ensure the level is within the 1-20 range
    if not 1 <= level <= 20:
        raise ValueError("Level must be between 1 and 20")
    
    # Calculate proficiency bonus based on level
    if level < 5:
        return 2
    elif level < 9:
        return 3
    elif level < 13:
        return 4
    elif level < 17:
        return 5
    else:  # Level 17-20
        return 6

def get_racial_traits(input):
    """
    Returns a list of racial traits that the character has.
    """
    racial_trait_list = set()
    for trait in input["race"]["racialTraits"]:
        racial_trait_list.add(f'{trait["definition"]["name"]} - {trait["definition"]["description"]}')
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
        if feature["definition"]["name"] in ("Hit Points", "Proficiencies"):
            continue
        if feature["definition"]["requiredLevel"] <= input["classes"][0]["level"]:
            class_feature_list.add(f'{feature["definition"]["name"]} - {feature["definition"]["description"]}')
    return list(class_feature_list)

def get_spell_list(input):
    """
    Returns a list of spells that the character has.
    """
    spell_list = set()
    
    check_list = ["class", "race", "background", "item", "feat"]

    for check in check_list:
        try:
            for spell in input["spells"][check]:
                try:
                    spell_list.add(f'{spell["definition"]["name"]} - {spell["definition"]["description"]}')
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

def format_output_file(input):
    """
    Removed unicode and HTML tags from the output file.
    """
    # Replace Unicode characters and newlines
    cleaned_input = re.sub(r"\\u201[0-9a-z]{1}", "'", input)
    cleaned_input = re.sub(r"\\[nr]", " ", cleaned_input)

    # Remove html tags
    soup = BeautifulSoup(cleaned_input, "html.parser")
    clean_content = soup.get_text()

    return clean_content


def convert_file(input_file, output_file):
    with open(input_file, 'r') as fh:
        input_dict = json.loads(fh.read())
        output_dict = convert_json(input_dict)

        content = json.dumps(output_dict)

        output_content = format_output_file(content)

        with open(output_file, 'w') as w:
            w.write(output_content)

file_list = glob.glob("characters/dndbeyond_format/[0-9][0-9].json")
for file in file_list:
    filename = file.split("/")[-1]
    convert_file(file, f'characters/formatted_characters/{filename.replace(".json", "_formatted.json")}')