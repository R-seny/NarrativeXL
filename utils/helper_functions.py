from settings import line_separator, column_separator, fake_summary_separator

from collections import namedtuple

PreppedQuestions = namedtuple("PreppedQuestions", ["whenasked", "raw_chunk", "overlapped_chunk", "questions", "answers", "question_types", "memory_loads"])

def read_shortform_questions(path):

    with open(path, "r") as f:

        raw = f.read()

        lines = raw.split(line_separator)

        whenasked, chunks, ochunks, questions, answers, qtypes, memoloads = zip(*[l.split(column_separator) for l in lines if l])

        # Dropping the first line since it's the column name
        whenasked, chunks, ochunks, questions, answers, qtypes, memoloads = [el[1:] for el in (whenasked, chunks, ochunks, questions, answers, qtypes, memoloads)]

        questions, answers, qtypes, memoloads =  [[el.split(fake_summary_separator) for el in col] for col in (questions, answers, qtypes, memoloads)]
        #"WHEN_ASKED", "RAW_CHUNK", "OVERLAPPED_CHUNK", "QUESTIONS", "QUESTION_ANSWERS", "QUESTION_TYPES", "MEMLOADS"

        return PreppedQuestions(whenasked, chunks, ochunks, questions, answers, qtypes, memoloads)

if __name__ == "__main__":
    # Usage. Read all questions for a given book, along with corresponding contexts.
    # For questions with randomized named entities (to mitigate data contamination).
    res = read_shortform_questions("../TrainSet/substituted/shortform/2960.questions_shortform")

    # For raw questions (with original named entities, except for "otherbook questions", for which all decoys from other books always get NEs from the true book.
    res = read_shortform_questions("../TrainSet/raw/shortform/2960.questions_shortform")

    # Now different elements of this namedtuple correspond to different columns in the data.
    # E.g. "res.questions[3]" would yield the list of questions associated with the fourth book scene, while "res.raw_chunk[3]" would yield the third book scene.
    # As a reminder, a question in position i can test knowledge of information in any of the chunks in positions from 0 to i inclusive.
    # "memory_loads" column specifies, for each question, the memory retention demand.