
def adjust_length(s, max_length):

    '''Adjusting the length of the string s to match the max_length requirement
    :param s: the string to adjust
    :param max_length: maximum chunk length in symbols.
    :return: list of book chunks, each of length <= max_length
    '''

    if len(s) <= max_length:
        return [s]

    else:
        chunks = []
        while len(s) > max_length:

            split_index = s.rfind(" ", 1, max_length)

            if split_index == -1:
                split_index = s.rfind(",", 1, max_length)

            if split_index == -1:
                split_index = max_length

            chunks.append(s[:split_index])
            s = s[split_index:]
    if s:
        chunks.append(s)

    return chunks


def chunk_book(bookstring, max_length=1500):

    '''
    Attempting to split the book into sentences (naively using "."). If any of the sentences are too long,
    they are chunked with adjust_length function
    :param bookstring: the book to chunk, as a unicode string
    :param max_length: maximum chunk length in symbols. The function attempts to split the book into sentences, but
    if any of the sentences are too long - they are further chunked into max_length-long fragments
    :return: list of book chunks, each of length <= max_length
    '''

    sentence_chunks = bookstring.split(".")

    if len(sentence_chunks) > 1:
        sentence_chunks = [sc + "." for sc in sentence_chunks[:-1]] + [sentence_chunks[-1]]

    all_sentence_chunks = []

    for c in sentence_chunks:
        all_sentence_chunks.extend(adjust_length(c, max_length))

    return all_sentence_chunks

def rechunk_book(chunks, maxlen):

    """A simple function that collapses subsequent chunks into bigger ones, as long as they don't exceed the length"""

    result = []

    current = ""

    for c in chunks:
        if len(current) + len(c) <= maxlen or len(current) == 0:
            current = current + c
        else:
            result.append(current)
            current = c

    if current:
        result.append(current)

    return result

