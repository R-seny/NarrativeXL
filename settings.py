column_separator = "###THISISOURUNIQUECOLUMNSEPARATORUNLIKELYTOBEENCOUNTEREDINANYBOOK###"
fake_summary_separator = "###THISISOURUNIQUESUMMARYSEPARATORUNLIKELYTOBEENCOUNTEREDINANYBOOK###"
line_separator = "###THISISOURUNIQUELINESEPARATORUNLIKELYTOBEENCOUNTEREDINANYBOOK###"

debug_num_chunks = 25



### Different Recognition Questions per step
lookahead_questions_per_step = 1
scene_negation_questions_per_step = 1
other_book_questions_per_step = 1

false_summaries_for_chunk_0 = 5


number_of_decoy_options = 4

noneabove_option = "None of the above."

SPACY_MAXLEN = 2000 # in symbols. Gave weird silent errors for some books at ~ 900000 symbol lengths # maybe try at least 3k?

OCHUNK_OVERLAP_SYMBOLS = 300