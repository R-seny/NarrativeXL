import random

import warnings

import os

import Dataloaders as dl
import settings

import numpy as np
random.seed(42)
np.random.seed(42)

from collections import Counter

from entity_replacement import EntityReplacer

import character_list_generator as clg
import pickle as pkl

from settings import column_separator, fake_summary_separator, line_separator

class RecognitionQuestion:

    def __init__(self, correct_answer, decoys, decoy_types, when_asked, retention_delay, noneabove):

        self.correct_answer = correct_answer

        self.noneabove = noneabove

        self.decoys = decoys
        self.decoy_types = decoy_types
        self.when_asked = when_asked
        self.retention_delay = retention_delay if not self.noneabove else when_asked # You need to remember the whole book read so far to select "none of the above"

        self.is_mixed = True if len(set(decoy_types)) > 1 else False

        self.question_type = "mixed" if self.is_mixed else self.decoy_types[0]

        if not self.noneabove:
            self.decoys.append(settings.noneabove_option)
            self.decoy_types.append("Default")

        self.n_options = len(self.decoys) + 1

        self.all_options = decoys.copy()

        if self.noneabove:
            self.true_ans_position = self.n_options - 1 # The true answer is "None of the above" and it is added to the end of the array

        else:
            self.true_ans_position = np.random.randint(self.n_options - 1) # -1 Because we don't want to insert the correct answer after "None of the above"

        self.all_options.insert(self.true_ans_position, correct_answer)

    def question_string(self):
        return "".join(["Which of the following scenes was in the book?\n"] + [str(i + 1) + ") " + self.all_options[i] + "\n" for i in range(self.n_options)])

    def answer(self):
        return str(self.true_ans_position + 1)

    def detailed_question_string(self):

        description = "A {} decoy type recognition question:\n".format(self.question_type)


        answer_options = []
        i = 0
        dec_i = 0
        while i < self.n_options:
            if i != self.true_ans_position:
                answer_options.append("({} decoy) ".format(self.decoy_types[dec_i]) + str(i + 1) + ") " + self.all_options[i] + "\n")
                dec_i += 1
            else:
                answer_options.append("(True answer) " + str(i + 1) + ") " + self.all_options[i] + "\n")

            i += 1


        question = "".join(["Which of the following scenes was in the book?\n"] + answer_options)

        return description + question

    def __str__(self):

        answer = "Answer:" + str(self.true_ans_position + 1)

        return self.question_string() + answer

    def __repr__(self):

        return self.detailed_question_string()

    def IsComplete(self):
        '''Since some summaries or false summaries might have been None (GPT failed to generate them),
        we need to filter out questions that got affected by that'''

        if self.correct_answer is None or any([el is None for el in self.decoys]):
            return False
        else:
            return True


class RecognitionQuestionGenerator:

    def __init__(self, book_processor, book_filename, parallel_books=None, ent_rep_dict=None):
        '''Takes a book processor (already with true and fake summaries generated. Generates questions based on that.'''

        self.book_filename = book_filename
        self.book_processor = book_processor
        self.parallel_books = parallel_books ### A list of book processor objects, to draw decoy answers from. Only relevant for the "other book" type of recognition decoys.

        self.questions = [] # A list that stores a list of RecognitionQuestion objects as its elements.
        self.read_progress = 0 # Index of the last read chunk.

        self.book_length = len(self.book_processor.book_chunk_summaries)

        # By default, false summaries may have None values where false summary generation failed
        self.false_summaries_filtered = [[s for s in fs if s] for fs in self.book_processor.false_book_chunk_summaries] # Remove all None summaries (failed to generate)
        self.false_summary_chunk_weights = np.array([len(el) for el in self.false_summaries_filtered])

        if np.sum(self.false_summary_chunk_weights) <= 0.5:
            raise ValueError("No false summaries available for this book.")
        if np.sum(self.false_summary_chunk_weights) <= 10.5:
            warnings.warn("Few false summaries available for the current book.")

        self.ent_rep_dict = ent_rep_dict

    def advance(self):

        current_questions = []
        for _ in range(settings.lookahead_questions_per_step):
            q = self.generate_lookahead_question()
            if q and RecognitionQuestion.IsComplete(q):
                current_questions.append(q)

        for _ in range(settings.scene_negation_questions_per_step):
            q = self.generate_scene_negation_question()

            if q and RecognitionQuestion.IsComplete(q):
                current_questions.append(q)

        for _ in range(settings.other_book_questions_per_step):
            q = self.generate_other_book_question()

            if q and RecognitionQuestion.IsComplete(q):
                current_questions.append(q)

        self.read_progress += 1
        self.questions.append(current_questions)

    def generate_lookahead_question(self):

        no_true_ans = np.random.random() < (1 / (settings.number_of_decoy_options + 2)) # Total number of options is + 2 because of the true ans and "None of the above"
        n_decoys = settings.number_of_decoy_options + 1 if no_true_ans else settings.number_of_decoy_options

        if self.read_progress > self.book_length - (n_decoys + 1):
            return None # Can not generate lookahead questions too close to the end of the book
        else:

            decoy_id_candidates = np.arange(self.read_progress + 1, self.book_length)
            
            decoy_ids = np.random.choice(decoy_id_candidates, n_decoys, replace=False)


            if no_true_ans:
                true_ans = settings.noneabove_option
                retention_delay = self.read_progress
            else:

                true_ans, true_idx = self.get_random_summary(self.read_progress + 1)
                retention_delay=self.read_progress-true_idx

            decoys = [self.book_processor.book_chunk_summaries[id] for id in decoy_ids]
            decoy_types = ["Lookahead" for _ in decoy_ids]

            return RecognitionQuestion(correct_answer=true_ans, decoys=decoys, decoy_types=decoy_types,
                                       when_asked=self.read_progress, retention_delay=retention_delay, noneabove=no_true_ans)

    def generate_scene_negation_question(self):

        no_true_ans = np.random.random() < (1 / (settings.number_of_decoy_options + 2)) # Total number of options is + 2 because of the true ans and "None of the above"
        n_decoys = settings.number_of_decoy_options + 1 if no_true_ans else settings.number_of_decoy_options

        available_fake_weights = self.false_summary_chunk_weights[:self.read_progress + 1].copy()

        if np.sum(available_fake_weights) < n_decoys:
            return None
        else:

            decoys = []


            idx_to_numpicks = Counter()
            for _ in range(n_decoys):

                fake_weights_normalized = available_fake_weights / np.sum(available_fake_weights)

                chunk_choice = np.random.choice(np.arange(self.read_progress + 1), p=fake_weights_normalized)
                available_fake_weights[chunk_choice] -= 1

                idx_to_numpicks[chunk_choice] += 1

            for chunk, numpicks in idx_to_numpicks.items():
                decoys_from_chunk = np.random.choice(self.false_summaries_filtered[chunk], numpicks, replace=False)
                decoys.extend(decoys_from_chunk)

            np.random.shuffle(decoys) # Otherwise decoys from the same chunk would be close
            decoy_types = ["Change" for _ in range(n_decoys)]

            if no_true_ans:
                true_ans = settings.noneabove_option
                retention_delay = self.read_progress

            else:
                true_ans, true_idx = self.get_random_summary(self.read_progress + 1)
                retention_delay = self.read_progress - true_idx

        return RecognitionQuestion(true_ans, decoys, decoy_types, when_asked=self.read_progress, retention_delay=retention_delay, noneabove=no_true_ans)

    def get_random_summary(self, sample_up_to=None):

        if sample_up_to is None:
            sample_up_to = self.book_length
        
        candidates = np.arange(sample_up_to)



        true_idx = np.random.choice(candidates) 
        
        true_ans = self.book_processor.book_chunk_summaries[true_idx]
        return true_ans, true_idx
    def generate_other_book_question(self):

        no_true_ans = np.random.random() < (1 / (settings.number_of_decoy_options + 2))
        n_decoys = settings.number_of_decoy_options + 1 if no_true_ans else settings.number_of_decoy_options

        if no_true_ans:
            true_ans = settings.noneabove_option
            retention_delay = self.read_progress
        else:
            true_ans, true_idx = self.get_random_summary(self.read_progress + 1)
            retention_delay = self.read_progress - true_idx


        decoy_books = np.random.choice(np.arange(len(self.parallel_books)), size=n_decoys, replace=False)
        decoy_books = [self.parallel_books[i] for i in decoy_books]
        decoys = [el.get_random_summary()[0] for el in decoy_books]

        ### Substitute entities from this book into entities from another.
        decoys = [EntityReplacer.sub_nonrandom_characters(self.ent_rep_dict, b.ent_rep_dict, text=d) for d, b in zip(decoys, decoy_books)]

        decoy_types = ["Otherbook" for _ in range(n_decoys)]

        return RecognitionQuestion(true_ans, decoys, decoy_types, when_asked=self.read_progress, retention_delay=retention_delay, noneabove=no_true_ans)

    def set_parallel_books(self, pb):
        '''Each PB is also a question generator'''
        self.parallel_books = pb

    def generate_questions(self):

        while self.read_progress < self.book_length:
            self.advance()


def process_folder_from_prepared(summary_folder, ent_dict_folder, num_to_process=15, start_at=0):
    sumpath = os.path.join("Data", summary_folder)
    entpath = os.path.join("Data", ent_dict_folder)

    bookf_to_process = [f.strip(".tagseparated") for f in os.listdir(sumpath) if os.path.isfile(os.path.join(sumpath, f))]
    bookf_to_process = bookf_to_process[start_at:num_to_process]

    summaries_to_process = [os.path.join(sumpath, f + ".tagseparated") for f in bookf_to_process]
    ent_dicts_to_process = [os.path.join(entpath, f + ".repl") for f in bookf_to_process]

    assert all([os.path.isfile(f) for f in ent_dicts_to_process]), 'Missing a preprocessed replacement dictionary {}'.format(ent_dicts_to_process)

    book_processors = [dl.BookProcessor.init_from_summaries(s) for s in summaries_to_process]

    ent_rep_dicts = []

    for p in ent_dicts_to_process:
        with open(p, "rb") as f:
            ent_rep_dicts.append(pkl.load(f))

    question_generators = [RecognitionQuestionGenerator(b, book_filename=bookf_to_process[i], ent_rep_dict=ent_rep_dicts[i]) for i, b in enumerate(book_processors)]

    for i, g in enumerate(question_generators):

        g.set_parallel_books(question_generators[0:i] + question_generators[i+1:])


    return question_generators


def generate_questions(question_generators, saveto, subchars=True, rewrite=False):

    subc = EntityReplacer.sub_random_characters if subchars else lambda x, y: y

    is_subbed = "substituted" if subchars else "raw"
    savefolder = os.path.join("Data", saveto, is_subbed, "shortform")
    if not os.path.exists(savefolder):
        os.makedirs(savefolder)

    for qg_num, qg in enumerate(question_generators):

        savepath = os.path.join("Data", saveto, is_subbed, "shortform", qg.book_filename + ".questions_shortform")

        if os.path.exists(savepath) and not rewrite:
            continue

        if not qg.questions:
            qg.generate_questions()

        ### Save questions in a conveniently loadable way

        ### Short dataset format
        ### Filename - bookid.questshort
        ### WHENASKED, CHUNK, OVERLAPPEDCHUNK, QUESTIONS (WITHIN ONE COLUMN), QUESTION ANSWERS (WITHIN ONE COLUMN), QUESTION TYPES (WITHIN ONE COLUMN), MEMLOADS (WITHIN ONE COLUMN)
        ###



        with open(savepath, "w") as f:

            f.write(column_separator.join(
                ["WHEN_ASKED", "RAW_CHUNK", "OVERLAPPED_CHUNK", "QUESTIONS", "QUESTION_ANSWERS", "QUESTION_TYPES",
                 "MEMLOADS"]))
            f.write(line_separator)

            for chunkind, qs in enumerate(qg.questions):

                chunk = subc(qg.ent_rep_dict, qg.book_processor.book_chunks[chunkind])
                ochunk = subc(qg.ent_rep_dict, qg.book_processor.overlapped_book_chunks[chunkind])

                question_texts = fake_summary_separator.join([subc(qg.ent_rep_dict, q.question_string()) for q in qs])
                question_answers = fake_summary_separator.join([q.answer() for q in qs])
                question_types = fake_summary_separator.join([q.question_type for q in qs])
                memloads = fake_summary_separator.join([str(q.retention_delay) for q in qs])

                f.write(column_separator.join([str(chunkind), chunk, ochunk, question_texts, question_answers, question_types, memloads]))

                f.write(line_separator)


        ### Long dataset format
        ### Filename - bookid.questlong
        ### WHENASKED, CHUNK, OVERLAPPEDCHUNK, QUESTION, QUESTION TYPE, QUESTION ANSWER, MEMLOAD
        ###

        print("Generated questions for {} out of {} books".format(qg_num + 1, len(qgs)))





if __name__ == "__main__":

    qgs = process_folder_from_prepared("TrueAndFalseSummaries/TestSet500", ent_dict_folder="CharacterSubstitution",
                                       num_to_process=500, start_at=0)

    generate_questions(qgs, saveto="TestQuestions", subchars=True)
    generate_questions(qgs, saveto="TestQuestions", subchars=False)
