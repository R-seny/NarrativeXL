from settings import line_separator, column_separator, fake_summary_separator, OCHUNK_OVERLAP_SYMBOLS
from collections import namedtuple

PreppedQuestions = namedtuple("PreppedQuestions", ["whenasked", "raw_chunk", "overlapped_chunk", "questions", "answers", "question_types", "memory_loads"])



def read_shortform_questions(path):

    """
    :param path: A path to the file storing shortform questions for a given book.
    :returns: A PreppedQuestions object.

    PreppedQuestions will have the following fields (all lists). For a given scene number i in the book,

    whenasked[i] a numbers indicating when the associated questions should be asked.
    Note that whenasked[i] should be very close to i, unless some scene was skipped (GPT3.5 repeatedly failed to summarize it) which is exceedingly rare.
    raw_chunk[i] book chunk (scene) number i. To get all book context up to the present step, you can use '" ".join'
    ochunk[i] overlapped book chunk (scene) number i. Same as chunks, but with peeking into the next and previous chunks. This is done so that scenes did not end too abruptly.

    ## Plus fields below which can have more than one entry per row.
    questions[i] questions for that timestep, separated by 'fake_summary_separator'
    answers[i] answers for that timestep, separated by 'fake_summary_separator'
    question_types[i] question types for that timestep (i.e. how the decoys were generated), separated by 'fake_summary_separator'
    memory_loads[i] memory loads for that timestep (i.e. how many scenes information needed for the question was presented), separated by 'fake_summary_separator'

    See usage example in the main section of helper_functions.py
    
    """

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
    questions = read_shortform_questions("../TrainSet/substituted/shortform/2960.questions_shortform")

    # For raw questions (with original named entities, except for "otherbook questions", 
    # for which all decoys from other books always get NEs from the true book.
    questions = read_shortform_questions("../TrainSet/raw/shortform/2960.questions_shortform")

    #To reconstruct context for a set of questions asked at a scene i, use
    #context = ' '.join(questions.raw_chunk[:i - 1] + (questions.overlapped_chunk[i][:OCHUNK_OVERLAP_SYMBOLS],))
