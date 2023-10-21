from __future__ import annotations
import argparse
from pathlib import Path
import re
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from argparse import Namespace
import character_list_generator as clg
from tqdm import tqdm
import utils.read_name_files as rn

from collections import defaultdict

import numpy as np

"""
NOTE:
-----------------------------------------------------------------------------------
This script works by placing the substituted summaries within the book folder.

It CANNOT work without the original texts, as SpaCy will reference the original
placement of characters in the text in order to replace the string for generating
substitutions or performing modifications.
------------------------------------------------------------------------------------
"""

male_names, female_names = rn.read_gender_list()
neutral_names = rn.read_unisex_names()

class EntityReplacer():
    def __init__(self, text: str, rand_ch_dict:dict):
        self.text = text
        self.rand_ch = rand_ch_dict
        self.first_n = self.rand_ch["First Names"]
        self.middle_n = self.rand_ch["Middle Names"]
        self.last_n = self.rand_ch["Last Names"]
        self.all_names = self.first_n | self.middle_n | self.last_n

    def replace_names(self) -> None:
        """
        rand_name[0] will be the name, rand_name[1] is the gender
        """
        for name, rand_label in self.all_names.items():
            pattern = f"( |\n|\"){re.escape(name)}(\n|\W)"
            self.text = re.sub(pattern, f"\\1{rand_label[0]}\\2", self.text)

    def randomized_character_section(self):
        "Randomized Character Section at the bottom"
        self.text = self.text + "\n\n" + f"Randomized Local characters: {self.rand_ch}"

    def create_text_file(self) -> str:
        self.replace_names()
        self.randomized_character_section()

        return self.text

    @staticmethod
    def create_nonrandom_character_insertion_dict(source_book_dict: dict, target_book_dict: str):

        '''Makes a dictionary that maps actual character names from the target book to random actual character names in the source book'''

        insertion_dict = {"First Names": {}, "Middle Names": {}, "Last Names": {}}

        candidates = defaultdict(lambda: list())


        for nametype in ["First Names", "Middle Names", "Last Names"]:

            for true_char_name, (rand_char_name, gender) in source_book_dict[nametype].items():

                candidates[(nametype, gender)].append(true_char_name)


        cand_names_no_gender = {}
        for nametype in ["First Names", "Middle Names", "Last Names"]:
            cand_names_no_gender[nametype] = candidates[(nametype, "male")] + candidates[(nametype, "female")] + candidates[(nametype, "neutral")]

        all_cand_names = cand_names_no_gender["First Names"] + cand_names_no_gender["Middle Names"] + cand_names_no_gender["Last Names"]

        if not all_cand_names:
            print("WARNING: SOURCE BOOK HAS NO CHARACTERS! Leaving the dictionary unchanged")
            return target_book_dict

        for nametype in ["First Names", "Middle Names", "Last Names"]:

            for true_char_name, (rand_char_name, gender) in target_book_dict[nametype].items():

                if candidates[(nametype, gender)]:
                    replacement = np.random.choice(candidates[(nametype, gender)])
                    insertion_dict[nametype][true_char_name] = replacement, gender
                elif cand_names_no_gender[nametype]:
                    replacement = np.random.choice(cand_names_no_gender[nametype])
                    insertion_dict[nametype][true_char_name] = replacement, "unknown"
                else:
                    replacement = np.random.choice(all_cand_names)
                    insertion_dict[nametype][true_char_name] = replacement, "unknown"

        return insertion_dict

    @staticmethod
    def sub_nonrandom_characters(source_book_rand_ch:dict, other_book_rand_ch:dict, text:str):

        '''Takes a snippet from another book and its associated random character sub dict. Substitutes original characters from this
        book (the book associated with this EntityReplacer) object instead of original characters in the provided snippet.'''

        insertion_dict = EntityReplacer.create_nonrandom_character_insertion_dict(source_book_rand_ch, other_book_rand_ch)
        all_ins = insertion_dict["First Names"] | insertion_dict["Middle Names"] | insertion_dict["Last Names"]

        for name, (rand_name, gender) in all_ins.items():
            try:
                pattern = f"(^|\W){re.escape(name)}($|\W)"
                text = re.sub(pattern, f"\\g<1>{rand_name}\\g<2>", text)
            except re.error as e:
                print("Re error")
                print("Pattern")
                print(pattern)
                print("Text")
                print(text)
                print("Name: {}, rand name {}, gender {}".format(name, rand_name, gender))
                raise e
        return text

    @staticmethod
    def sub_random_characters(source_book_rand_ch: dict, text: str):

        '''Takes a snippet a book and substitutes random characters instead of the original ones.'''

        all_ins = source_book_rand_ch["First Names"] | source_book_rand_ch["Middle Names"] | source_book_rand_ch["Last Names"]

        for name, (rand_name, gender) in all_ins.items():

            pattern = f"(^|\W){re.escape(name)}($|\W)"
            text = re.sub(pattern, f"\\g<1>{rand_name}\\g<2>", text)

        return text

def create_subdirectory(book : Path) -> Path:
    "Creates a new subfolder to store a file of all the subsituted names"

    sub_folder_path = book / f"{book.name.replace(' ', '')}_substituted"
    sub_folder_path.mkdir(parents=True, exist_ok=True) #Creates the subdirectory

    return sub_folder_path


def write_file_sub(filepath: Path, summary: Path, rand_ch_dict) -> None:
    with filepath.open("w", encoding = "utf-8") as f:
        """
       Read the json_object, but create an entirely new file with labeled data
       using create_text_file()
       """
        json_file = open(summary, "r")
        sub_file = EntityReplacer(json_file.read(), eval(rand_ch_dict))
        f.write(sub_file.create_text_file())
        json_file.close()


def parse_summaries(book: Path, sub_folder_path: Path, rand_ch_dict: Path):
    "For each summary create the file path for it"
    file_list = list((entry for entry in book.iterdir() if entry.is_file() and entry.match('*.txt')))

    for summary in tqdm(file_list, desc="List of Summaries", unit="sections"):
        file_name = str(summary.stem) + "_substituted.txt"
        filepath = sub_folder_path / file_name
        print("")

        write_file_sub(filepath, summary, rand_ch_dict)

def parse_corpus(corpus_path: Path) -> None:
    "Parses through each website, and then each book folder in the BookSum Dataset"

    for website in corpus_path.iterdir(): #i.e. Shmoop, Sparknotes
        for book in tqdm(list(website.iterdir()), desc = "Books list", unit = "Amount of books"): # i.e. Hamlet, Frankenstein
            print(book.name)

            sub_folder_path = create_subdirectory(book) # Create the subfolder

            character_file = clg.Universal_Character_list(book, sub_folder_path, male_names, female_names, neutral_names) #Create the character list
            character_file_path = character_file.generate_file()
            _, random = rn.read_character_list(character_file_path)

            parse_summaries(book, sub_folder_path, random)  # Write to file


def modify_book(book_path: Path) -> None:
    sub_folder_path = book_path / f"{book_path.name.replace(' ', '')}_substituted"
    character_file_path = sub_folder_path /  f"{book_path.name.replace(' ', '')}_character_list.txt"
    _, random = rn.read_character_list(character_file_path)

    parse_summaries(book_path, sub_folder_path, random)  # Write to file


def modify_file(file_path: Path) -> None:
    book_path = file_path.parent
    sub_folder_path = book_path / f"{book_path.name.replace(' ', '')}_substituted"
    character_file_path = sub_folder_path /  f"{book_path.name.replace(' ', '')}_character_list.txt"

    write_file_sub(file_path, sub_folder_path, character_file_path)

def main(options: Namespace) -> None:

    if options.all:
        parse_corpus(Path(" ".join(options.all)))

    elif options.book:
        modify_book(Path(" ".join(options.book)))

    else:
        modify_file(Path(" ".join(options.file)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "Replace entities with an assigned substitutes")
    option = parser.add_mutually_exclusive_group(required=True)

    option.add_argument(
        "--all",
        type = str,
        nargs = "+",
        default=None,
        help = "Specify the directory to read. Will parse through the entire corpus. Generating character lists and assigning characters." )

    #Modification Options
    option.add_argument(
        "--book",
        type = str,
        nargs = "+",
        default=None,
        help = "Will replace characters within the book. Assumes there already is a character list" ) #error handling for books

    option.add_argument(
        "--file",
        type=str,
        nargs = "+",
        default=None,
        help="Assumes you want a single file that will be modified. CANNOT generate it's own character list")

    parsed_args = parser.parse_args()

    if parsed_args.all is None and parsed_args.book is None and parsed_args.file is None:
        parsed_args.error("At least one of the parsing options is required")

    main(parsed_args)
