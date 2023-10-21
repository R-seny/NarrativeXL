import anthropic
from settings import OCHUNK_OVERLAP_SYMBOLS
import os
from utils.helper_functions import PreppedQuestions, read_shortform_questions

import csv


import numpy as np

import openai

with open("../GPTkeys/YOURKEY.txt", "r") as f:
    openai.api_key = f.read().strip()


questions_folder = None # Change to the path of your downloaded questions folder.
# For example, 
# questions_folder = "./Results/Questions/substituted/shortform"
# or 
# questions_folder = "./Results/Questions/raw/shortform", for the same questions but with no Named Entity substitution (except for 'other book' questions which always use substitution to avoid book character-based shortcuts).



if questions_folder is None:
    raise ValueError("Please specify your questions folder above.")
    

def ask_question(client, context, questions, model="claude-instant-v1.1-100k"):

    questions_str = "".join(["\nQuestion {}: {}\n".format(i + 1, q) for i, q in enumerate(questions)])

    prompt = "{} You will read a large part of a book, after which I will ask you questions about what you've read. Book part:\n{} \nQuestions:{}\nWrite only the numerical answers to the corresponding questions, separating them by commas. For example, '1,3,4'. Begin your answers with a {} tag. {}".format(
            anthropic.HUMAN_PROMPT, context, questions_str, "###BEGIN_ANSWER###", anthropic.AI_PROMPT)

    resp = client.completion(
        prompt=prompt,
        stop_sequences=[anthropic.HUMAN_PROMPT],
        model=model,
        temperature=0,
        max_tokens_to_sample=150,
    )


    answer_text = resp["completion"]

    if "###BEGIN_ANSWER###" not in answer_text:
        print("Wrong answer format")
        return None
    answer_text = answer_text.split("###BEGIN_ANSWER###")[1]
    answer_text = answer_text.split("###END_ANSWER###")[0]
    return answer_text.strip()

def ask_question_gpt(context, questions):

    questions_str = "".join(["\nQuestion {}: {}\n".format(i + 1, q) for i, q in enumerate(questions)])

    prompt = "You will read a large part of a book, after which I will ask you questions about what you've read. Book part:\n{} \nQuestions:{}\nWrite only the numerical answers to the corresponding questions, separating them by commas. For example, '1,3,4'. Begin your answers with a {} tag.".format(
        context, questions_str, "###BEGIN_ANSWER###")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        temperature=0.0,
        messages=[
          {"role": "system", "content": "You are a helpful assistant that reads large book snippets and asnwers questions about those snippets. Begin your answer with a {} tag.".format("###BEGIN_ANSWER###")},
          {"role": "user", "content": '{}. Start your answer with a "{}" tag.'.format(prompt, "###BEGIN_ANSWER###")} # Add "in under 500 words?
        ]
    )

    response_content = response["choices"][0]["message"]["content"]

    answer_text = response_content.split("###BEGIN_ANSWER###")[1]
    answer_text = answer_text.split("###END_ANSWER###")[0]



    return answer_text



def get_random_questions(question_folder, whentoask=10):

    assert whentoask >= 2
    '''Gets a few random questions (usually 3), associated with a specific reading time in a random book'''
    path = os.path.join(question_folder)

    root, dirs, files = next(os.walk(path))

    chosen_book = np.random.choice(files)
    questions = read_shortform_questions(os.path.join(root, chosen_book))


    if (questions.raw_chunk[whentoask-1][-OCHUNK_OVERLAP_SYMBOLS:] != questions.overlapped_chunk[whentoask][:OCHUNK_OVERLAP_SYMBOLS]):

        context = " ".join(questions.raw_chunk[0:whentoask - 1])
        last_chunk = questions.overlapped_chunk[whentoask]
        last_chunk_prefix = last_chunk[:50]
        context = context[:context.find(last_chunk_prefix)] + last_chunk
    else:
        context = " ".join(questions.raw_chunk[0:whentoask - 1] + (questions.overlapped_chunk[whentoask][:OCHUNK_OVERLAP_SYMBOLS],))

    questions_strings = questions.questions[whentoask]
    answers = questions.answers[whentoask]
    memloads = questions.memory_loads[whentoask]
    question_types = questions.question_types[whentoask]

    return chosen_book, context, questions_strings, answers, memloads, question_types




if __name__ == "__main__":
    with open("./anthropicKEY") as f:
        client = anthropic.Client(api_key=f.read().strip())


    c_whenaskeds = ["WhenAsked"]
    c_qbookfile = ["BookQuestionsFile"]
    c_contextlengths = ["ContextLength"]
    c_memloads = ["RetentionDelay"]
    c_trueanswers = ["CorrectAnswer"]
    c_modelantroanswers = ["AntropicAnswer"]
    c_modelgptans = ["GPTAns"]
    c_questiontypes = ["QuestionType"]
    c_contexts = ["Contexts"]



    for whentoask in [2, 8]: # Which memory loads to test. Care should be taken to avoid overly long contexts for the gpt model
        for i in range(3): # how many random questions to sample.
            raise ValueError("Make sure you want to run it, it costs money.")
            chosen_book, context, questions_strings, answers, memloads, question_types = get_random_questions(question_folder, whentoask=whentoask)

            model_ans = ask_question(client, context, questions_strings, model="claude-v1.3-100k")
            model_gpt_ans = ask_question_gpt(context, questions_strings) # Change to "model_gpt_ans = 'NA' when working with very long context

            print("True answers: {}, antropic model answers: {}, gpt model answers {}".format(answers, model_ans, model_gpt_ans))

            if len(model_ans.split(",")) != len(answers):
                model_ans = ["NA" for _ in answers]
            else:
                model_ans = [str(el).strip() for el in model_ans.split(",")]

            if len(model_gpt_ans.split(",")) != len(answers):
                model_gpt_ans = ["NA" for _ in answers]
            else:
                model_gpt_ans = [str(el).strip() for el in model_gpt_ans.split(",")]


            contlen = len(context.split())
            for mans, gptans, ans, mem, qtype in zip(model_ans, model_gpt_ans, answers, memloads, question_types):

                ## Same for each query
                c_whenaskeds.append(whentoask)
                c_qbookfile.append(chosen_book)
                c_contextlengths.append(contlen)
                c_contexts.append("{}".format(context))

                ## Vary per question within one query
                c_memloads.append(mem)
                c_questiontypes.append(qtype)
                c_trueanswers.append(ans)
                c_modelantroanswers.append(mans)
                c_modelgptans.append(gptans)


    with open("Results/anthropic_tests_substituted_large_long.csv", "w", newline='') as csvfile:

        writer = csv.writer(csvfile, delimiter=",")
        for elts in zip(c_whenaskeds, c_qbookfile, c_contextlengths, c_memloads, c_trueanswers, c_modelantroanswers, c_modelgptans, c_questiontypes):

            writer.writerow(list(elts))

    with open("Results/anthropic_tests_substituted_large_long_withcontext.csv", "w", newline='') as csvfile:

        writer = csv.writer(csvfile, delimiter=chr(255))
        for elts in zip(c_whenaskeds, c_qbookfile, c_contextlengths, c_memloads, c_trueanswers, c_modelantroanswers, c_modelgptans, c_questiontypes, c_contexts):
            writer.writerow(list(elts))
