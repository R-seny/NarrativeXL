import pickle as pkl
import random
import os
import Dataloaders as dl
import numpy as np
random.seed(94)
np.random.seed(94)
import character_list_generator as clg


if __name__ == "__main__":

    sum_folder = "Processed_Books"  # Where to look for processed books
    results_folder = "CharacterSubstitution" # Where to save char sub dicts

    respath = os.path.join("Data", results_folder)

    done = set([f.split('.')[0] for f in os.listdir(respath) if os.path.isfile(os.path.join(respath, f))])

    sumpath = os.path.join("Data", sum_folder)

    sums_to_process = [f for f in os.listdir(sumpath) if os.path.isfile(os.path.join(sumpath, f)) and f.split(".tagseparated")[0] not in done]

    for k, f in enumerate(sums_to_process):

        print("Beginning to process book {}/{}".format(k + 1, len(sums_to_process)))

        sp = os.path.join(sumpath, f)
        print(sp)
        b = dl.BookProcessor.init_from_summaries(sp)
        ent_count, ent_rep_dict = clg.get_counts_and_subs(b.original_book_text)

        resname = f.split(".tagseparated")[0]

        rp = os.path.join(respath, resname)
        with open(rp + ".count", "wb") as o:
            pkl.dump(ent_count, o)

        with open(rp + ".repl", "wb") as o:
            pkl.dump(ent_rep_dict, o)
