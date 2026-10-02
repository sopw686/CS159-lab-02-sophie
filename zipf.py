#!/usr/bin/env python3

import math
import os.path
from collections import Counter
from spacy.lang.en import English
import random

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot

nlp = English(pipeline=[], max_length=5000000)


def H_approx(n):
    """
    Returns an approximate value of n-th harmonic number.
    http://en.wikipedia.org/wiki/Harmonic_number
    """
    # Euler-Mascheroni constant
    gamma = 0.57721566490153286060651209008240243104215933593992
    return gamma + math.log(n) + 0.5/n - 1./(12*n**2) + 1./(120*n**4)

def do_zipf_plot(counts, label=""):
    fig = pyplot.figure()
    total = sum(counts.values())
    n = len(counts)
    print(label, n)
    xData = [i for i in range(1, len(counts)+1)]
    yData = [count / total for element, count in counts.most_common()]

    # Expected relative frequency from Zipf's law
    h = H_approx(n)
    expected = [1 / (h * k) for k in xData]

    pyplot.loglog(xData, yData)
    pyplot.xlabel("log(rank)")
    pyplot.ylabel("log(freq)")
    pyplot.suptitle(label)

    pyplot.loglog(xData, yData, label="Empirical")
    pyplot.loglog(xData, expected, label="Zipf's law (expected)")
    pyplot.xlabel("log(rank)")
    pyplot.ylabel("log(freq)")
    pyplot.suptitle(label)
    pyplot.legend()

    pyplot.show()
    pyplot.savefig('zipf_{}.png'.format(label))
    pyplot.close()
    



def read_all(directory, extension=None):
    walkTups = os.walk(directory)
    # dirpath is a string
    # dirnames is a list of subdirectories and i think we ignore this
    # files is the list of just files
    allCount = Counter()
    for path, name, files in walkTups:
        
        for fileName in files:
            startsh, end = os.path.splitext(fileName)
            if extension == None or end == extension:
                currCount = read_one(os.path.join(path, fileName))
                allCount += currCount
        
    return allCount
    # find the file with the is.walk for directory




def read_one(fname):
    with open(fname, 'r', encoding='latin1') as fp: 
        # lowercase the input
        content = fp.read()
        content = content.lower()

        # text file open in one window
        
        # file pointer pointing to different locations in the file
        # loop through the file one character, loop, or byte at a time etc
        # in this case we want the whole string

        doc = nlp(content)
        tokens = [tok.text for tok in doc]
        tokenCount = Counter(tokens)
        return tokenCount

def plot_all(directory):
    counts = read_all(directory, ".txt")
    do_zipf_plot(counts, os.path.basename(directory))

def plot_one(fname):
    counts = read_one(fname)
    title = os.path.splitext(os.path.basename(fname))[0]

    do_zipf_plot(counts, label=title)

def plot_random():
    chars = "abcdefg... "   # note the space at the end
    text = "".join(random.choice(chars) for _ in range(1_000_000))

    tokens = text.split()
    counts = Counter(tokens)
    do_zipf_plot(counts, "random")

def main():
    # plot_one('/courses/cs159/data/gutenberg/carroll-alice.txt')
    # plot_all('/courses/cs159/data/gutenberg')

    # plot_one('/courses/cs159/data/gutenberg/blake-poems.txt')
    # plot_one('/courses/cs159/data/gutenberg/melville-moby_dick.txt')
    # plot_one('/courses/cs159/data/gutenberg/whitman-leaves.txt')

    plot_random()

if __name__ == "__main__":
    main()
