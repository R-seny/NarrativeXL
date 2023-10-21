import re
from typing import Pattern

def template(name) -> str:
    return f"(){name}(\W)"

def last_ntemplate(last_name) -> str:
    return f"(){last_name}(\W)"


def preprocess_name_dictionary(firsts,middles,lasts) -> Pattern[str]:
    """
    Converts dictionary names into a regex pattern
    references code from
    https://gist.github.com/carlsmith/b2e6ba538ca6f58689b4c18f46fef11c

    Ex: (Harry)(\W)| N.(\W)|(Potter)(\W)
    """
    substrings = list(map(template, firsts.keys() + middles.keys()))
    last_strings = list(map(last_ntemplate, lasts.keys()))
    regex = re.compile('|'.join(substrings + last_strings))

    return regex

def replace(string, substitutions):

    substrings = list(substitutions.keys())
    regex = re.compile('( )foo(\W)')
    return regex.sub("\\1FOO\\1",string)

if __name__ == "__main__":
    string = "spam foo bar foo bar spam"
    substitutions = {"foo": "FOO", "bar": "BAR"}
    output = replace(string, substitutions)
    print(output)

