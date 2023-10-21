
def read_gender_list() -> tuple[list,list]:
    male_names = []
    female_names = []
    with open("NameDatasets/name_gender_dataset.csv", "r")  as f:
        for line in f:
            if line.rstrip("\n").split(",")[1] == "M": #Checks if the name is male
                male_names.append(line.rstrip("\n").split(",")[0])
            else:
                female_names.append(line.rstrip("\n").split(",")[0])

    return male_names, female_names

def read_unisex_names() -> list:
    uni_names = []
    with open("NameDatasets/unisex-names~2Funisex_names_table.csv", "r")  as f:
        for line in f:
            uni_names.append(line.rstrip("\n").split(",")[2])

    return uni_names

def read_exceptions() -> list:
    name_exceptions = []
    with open("NameDatasets/name_exceptions.txt", "r") as f:
        for line in f:
            name_exceptions.append(line.rstrip())

    return name_exceptions

def read_figures() -> list:
    celebrities = []
    with open("NameDatasets/historical_figures", "r") as f:
        for line in f:
            celebrities.append(line.rstrip())

    return celebrities

def read_character_list(character_file_path) -> list[str, str]:
    """
    The character list is split by 3 line breaks
    :param character_file_path: Path directory
    :return: Character Counts, Character randomized names
    """
    with open(character_file_path, "r") as f:
        character_list = f.read()

    return character_list.split("\n\n\n")