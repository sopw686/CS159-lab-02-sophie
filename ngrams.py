#!/usr/bin/env python3

import argparse
from lxml import etree
from collections import Counter
import html

import spacy

nlp = spacy.load("en_core_web_sm")

def do_xml_parse(fp, tag):
    """ 
    Iteratively parses XML files
    """
    fp.seek(0)

    for (event, elem) in etree.iterparse(fp, tag=tag):
        yield elem
        elem.clear()

def get_examples(args, attribute, value):
    unigrams, bigrams, trigrams = Counter(), Counter(), Counter()
    for example in do_xml_parse(args.examples, 'example'):
        if example.get(attribute) == value:
            text = html.unescape(example.text)
            doc = nlp(text)
            unigrams.update(get_unigrams(doc))
            bigrams.update(get_bigrams(doc))
            trigrams.update(get_trigrams(doc))
    return unigrams, bigrams, trigrams

def get_unigrams(doc, do_lower=True): 
    if do_lower:
        return [token.text.lower() for token in doc]
    return [token.text for token in doc]

def get_bigrams(doc, do_lower=True):
    unigrams = get_unigrams(doc, do_lower)
    return list(zip(unigrams, unigrams[1:]))

def get_trigrams(doc, do_lower=True):
    unigrams = get_unigrams(doc, do_lower)
    return list(zip(unigrams, unigrams[1:], unigrams[2:]))

def compare(train_counter, test_counter, unique=False):
    absent = 0
    total = 0
    for word, count in test_counter.items():
        weight = 1 if unique else count
        total += weight
        if train_counter[word] == 0:
            absent += weight
    return (absent, total)




def do_experiment(args, attribute, train_value, test_value):
    """Print a pandoc-compatible table of experiment results"""
    train_counters = get_examples(args, attribute, train_value)
    test_counters = get_examples(args, attribute, test_value)

    table_header = "Results for {}, using {} as train and {} as test:"
    print(table_header.format(attribute, train_value, test_value))

    print("| Order | Type/Token | Total | Zeros | % Zeros | ")
    print("| ----  | ---------- | ----- | ----- | ------- | ")
    table_row = "| {order} | {typetoken} | {total} | {zeros} | {pct:.1%} | "

    orders = ("Unigram", "Bigram", "Trigram")
    for order, train, test in zip(orders, train_counters, test_counters):
        for do_types in (True, False):
            typetoken = "Type" if do_types else "Token"
            num_zeros, N = compare(train, test, do_types)
            print(table_row.format(order=order, typetoken=typetoken,
                                   total=N, zeros=num_zeros, pct=num_zeros/N))
    print()

def main(args):
    # counts = get_examples(args, 'condescension', 'true')
    # print(counts.get("the"))
    # print(compare(Counter(['a','b','c']), Counter(['c','d','d']), unique=False))

    do_experiment(args, 'randomchunk', 'a', 'b')   # train=false, test=true
    do_experiment(args, 'randomchunk', 'b', 'a')   # train=true, test=false


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # 'rb' means "read as bytes", which means that it doesn't assume
    # the data is UTF-8 text when it's read in.
    parser.add_argument("--examples", "-a",
                        type=argparse.FileType('rb'),
                        help="Content of examples")

    args = parser.parse_args()

    main(args)
