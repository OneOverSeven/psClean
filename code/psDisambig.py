############################
## Author: Mark Huberty, Mimi Tam, and Georg Zachmann
## Date Begun: 23 May 2012
## Purpose: Module to disambiguate inventor / assignee names in the PATSTAT patent ##          database
## License: BSD Simplified
## Copyright (c) 2012, Authors
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met: 
## 
## 1. Redistributions of source code must retain the above copyright notice, this
##    list of conditions and the following disclaimer. 
## 2. Redistributions in binary form must reproduce the above copyright notice,
##    this list of conditions and the following disclaimer in the documentation
##    and/or other materials provided with the distribution. 
## 
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
## ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
## 
## The views and conclusions contained in the software and documentation are those
## of the authors and should not be interpreted as representing official policies, 
## either expressed or implied, of the FreeBSD Project.
############################

import string
import scipy.sparse
import numpy as np
import re

def build_ngram_dict(string_list, n=1):
    """
    Given a list of strings and a desired n-gram,
    builds an ngram dictionary of unique ngrams in the entire list
    Args:
      string_list: a list of strings to be parsed into ngrams
      param n:           an integer specifying the n-gram to use
    Returns:
      A list of unique ngrams in the string list
    """
    ngrams = []
    for s in string_list:
        for i in range((len(s) - n)):
            this_ngram = ''.join(s[j] for j in range(i, i + n))
            if this_ngram not in ngrams:
                ngrams.append(this_ngram)
    return ngrams

def build_ngram_freq(string_list, ngram_dict):
    """
    Given an ngram dictionary and a list of strings, returns the ngram frequency
    distribution for each ngram in each string

    Args:
      string_list:   a list of strings to be parsed into ngram frequencies
      ngram_dict:    a dictionary of unique ngrams to use in parsing the strings
    Returns:
      A list of dicts, one per string in string_list, with keys
      as ngrams and values as ngram frequencies in that string.
    """
    frequency_list = []
    for s in string_list:
        s_freq_dict = {}
        for n in ngram_dict:
            n_freq = len(re.findall(n, s))
            s_freq_dict[n] = n_freq
        frequency_list.append(s_freq_dict)
    return frequency_list

def build_ngram_mat(string_list, n=1):
    """
    Given a string list, build a sparse term-frequency matrix of ngram frequencies
    in each string

    Args:
      string_list:  a list of strings
      n:            an integer value indicating the ngram to use
    Returns:
      A scipy CSR matrix containing the ngram frequency vectors,
      with rows representing strings and columns representing ngrams
    """
    ngram_dictionary = build_ngram_dict(string_list, n)
    ngram_frequency = build_ngram_freq(string_list, ngram_dictionary)
    row_idx = []
    col_idx = []
    val = []
    for i, f in enumerate(ngram_frequency):
        row_idx.extend( [i] * len(f) )
        col_idx.extend( [ngram_dictionary.index(f_val) for f_val in f] )
        val.extend( [f[f_val] for f_val in f] )
    mat = scipy.sparse.csc_matrix((np.array(val),
                                   (np.array(row_idx),
                                    np.array(col_idx)
                                    )
                                   )
                                  )
    out = {'tf_matrix': mat,
           'ngram_dict': ngram_dictionary
           }
    return out



