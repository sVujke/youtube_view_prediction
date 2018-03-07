
# coding: utf-8

# In[1]:

import pandas as pd 
import string
import sys

data = pd.read_pickle("../data/videos_fetched")


data["title"][0].split(" - ")[0].split(": ")[1]


def get_guest(title):
    """ Extracts guest name from title
    """
    return title.split(" - ")[0].split(": ")[1]


def add_guest(df):
    """ Adds guest column and fills it with guest names
    """
    df["guest_name"] = df.title.apply(lambda x: get_guest(x))
    return df

def remove_punctuation(translator, token):
    """ Removes punctuation from tokens
    """
    return token.translate(translator)


def tokenize(title):
    """ Returns tokens from quote in title
    """
    translator = str.maketrans('', '', string.punctuation)
    tokens = title.split(" ")
    return [remove_punctuation(translator, token).lower() for token in tokens]

def get_quote(title):
    """ Returns quote from title
    """
#     print(title)
    try:
        quote = " ".join(title.split(" - ")[1].split(" ")[:-1])
    except:
        print(title)
        quote = "No"
    return quote


def find_ngrams(input_list, n):
    """ Returns itterable with n-gram touples
    """
    return zip(*[input_list[i:] for i in range(n)])

def get_ngrams(title,n):
    """ Returns ngram lst
    """
    tokens = tokenize(title)
    lst = [" ".join(list(x)) for x in find_ngrams(tokens, n)]
    return lst

def add_quote(data):
    """ Adds quote column
    """
    data["quote"] = data.title.apply(lambda x: get_quote(x))
    return data

def add_tokens(df):
    """ Adds column with tokenized and lowercased quote 
    """
    df["tokens"] = df["quote"].apply(lambda x: tokenize(x))
    return df

def add_ngram(df, n):
    """ Add column with n gram
    """
    df["{}_gram".format(n)] = df["quote"].apply(lambda x: get_ngrams(x, n))
    return df

def add_page_name(df):
    """ Takes name and converts it to a format suitable for wikipedia pages
    """
    df["page_name"] = df["guest_name"].apply(lambda x: x.replace(" ", "_"))
    return df

def main():

    path_read = sys.argv[1]
    path_save = sys.argv[2]

    data = pd.read_pickle(path_read)

    data = add_guest(data)

    data = add_quote(data)

    data = data[data["quote"] != "No"]

    data = add_tokens(data)

    data = add_ngram(data, 2)

    data = add_ngram(data, 3)

    data = add_page_name(data)

    data.to_pickle(path_save)

if __name__ == '__main__':
    main()



