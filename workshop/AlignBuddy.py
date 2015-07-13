#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created on: Nov 18 2014 

"""
DESCRIPTION OF PROGRAM
AlignmentBuddy is a general wrapper for popular DNA and protein alignment programs that handles format conversion
and allows maintencance of rich feature annotation following alignment.
"""

# Standard library imports
import sys
import os
import argparse
from io import StringIO
from random import sample
import re
from tempfile import TemporaryDirectory

# Third party package imports
sys.path.insert(0, "./")  # For stand alone executable, where dependencies are packaged with BuddySuite
from Bio import AlignIO
from Bio.Align import MultipleSeqAlignment
# from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
from Bio.Alphabet import IUPAC

# My functions
import SeqBuddy as SB

# ##################################################### WISH LIST #################################################### #
# - 'Clean' an alignment by removing gaps (like phyutility -clean, or trimal -gt). Default removes cols with 100% gap
# - Map features from a sequence file over to the alignment
# - Extract range (http://biopython.org/DIST/docs/api/Bio.Align.MultipleSeqAlignment-class.html)
# - number of seqs in each alignment
# - Concatenate sequences from multiple alignments by id, taxa, or position in alignment (return new AlignBuddy)
# - Translate
# - Transcribe
# - Back-transcribe
# - Back-translate
# - Order ids
# - Alignment lengths
# - Pull out specific rows from the alignment
# - Delete specific rows from alignment
# - Rename ids
# - Separate multiple alignments into individual files

# ################################################# HELPER FUNCTIONS ################################################# #
class GuessError(Exception):
    """Raised when input format cannot be guessed"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


def _stderr(message, quiet=False):
    if not quiet:
        sys.stderr.write(message)
    return


def _stdout(message, quiet=False):
    if not quiet:
        sys.stdout.write(message)
    return


def _get_seq_recs(_alignbuddy):
    seq_recs = []
    for _alignment in _alignbuddy.alignments:
        for _rec in _alignment:
            seq_recs.append(_rec)
    return seq_recs


# #################################################### ALIGN BUDDY ################################################### #
class AlignBuddy:  # Open a file or read a handle and parse, or convert raw into a Seq object
    def __init__(self, _input, _in_format=None, _out_format=None):
        # ####  IN AND OUT FORMATS  #### #
        # Holders for input type. Used for some error handling below
        in_handle = None
        raw_seq = None
        in_file = None

        # Handles
        if str(type(_input)) == "<class '_io.TextIOWrapper'>":
            if not _input.seekable():  # Deal with input streams (e.g., stdout pipes)
                temp = StringIO(_input.read())
                _input = temp
            _input.seek(0)
            in_handle = _input.read()
            _input.seek(0)

        # Plain text in a specific format
        if type(_input) == str and not os.path.isfile(_input):
            raw_seq = _input
            temp = StringIO(_input)
            _input = temp
            _input.seek(0)

        # File paths
        try:
            if os.path.isfile(_input):
                in_file = _input

        except TypeError:  # This happens when testing something other than a string.
            pass

        if not _in_format:
            self.in_format = guess_format(_input)
            self.out_format = str(self.in_format) if not _out_format else _out_format

        else:
            self.in_format = _in_format

        if not self.in_format:
            if in_file:
                raise GuessError("Could not determine format from _input file '{0}'.\n"
                                 "Try explicitly setting with -f flag.".format(in_file))
            elif raw_seq:
                raise GuessError("Could not determine format from raw input\n{0} ..."
                                 "Try explicitly setting with -f flag.".format(raw_seq)[:50])
            elif in_handle:
                raise GuessError("Could not determine format from input file-like object\n{0} ..."
                                 "Try explicitly setting with -f flag.".format(in_handle)[:50])
            else:  # This should be unreachable.
                raise GuessError("Unable to determine format or input type. Please check how SeqBuddy is being called.")

        self.out_format = self.in_format if not _out_format else _out_format

        # ####  ALIGNMENTS  #### #
        if type(_input) == AlignBuddy:
            _alignments = _input.alignments

        elif isinstance(_input, list):
            # make sure that the list is actually MultipleSeqAlignment objects
            _sample = _input if len(_input) < 5 else sample(_input, 5)
            for _seq in _sample:
                if type(_seq) != MultipleSeqAlignment:
                    raise TypeError("Seqlist is not populated with SeqRecords.")
            _alignments = _input

        elif str(type(_input)) == "<class '_io.TextIOWrapper'>" or isinstance(_input, StringIO):
            _alignments = list(AlignIO.parse(_input, self.in_format))

        elif os.path.isfile(_input):
            with open(_input, "r") as _input:
                _alignments = list(AlignIO.parse(_input, self.in_format))
        else:  # May be unreachable
            _alignments = None

        self.alpha = guess_alphabet(_alignments)
        for _alignment in _alignments:
            _alignment._alphabet = self.alpha
            for _seq in _alignment:
                _seq.seq.alphabet = self.alpha
        self.alignments = _alignments

    def print(self):
        print(self)
        return

    def __str__(self):
        _output = ""
        for _alignment in self.alignments:
            _output += _alignment.format(self.out_format)
        return _output

    def write(self, _file_path):
        with open(_file_path, "w") as _ofile:
            AlignIO.write(self.alignments, _ofile, self.out_format)
        return


def guess_alphabet(_alignbuddy):
    _align_list = _alignbuddy if isinstance(_alignbuddy, list) else _alignbuddy.alignments
    _seq_list = []
    for _alignment in _align_list:
        _seq_list += [str(x.seq) for x in _alignment]

    _sequence = "".join(_seq_list).upper()
    _sequence = re.sub("[NX\-?]", "", _sequence)

    if len(_sequence) == 0:
        return None

    if 'U' in _sequence:  # U is unique to RNA
        return IUPAC.ambiguous_rna

    percent_dna = len(re.findall("[ATCG]", _sequence)) / float(len(_sequence))
    if percent_dna > 0.85:  # odds that a sequence with no Us and such a high ATCG count be anything but DNA is low
        return IUPAC.ambiguous_dna
    else:
        return IUPAC.protein


def guess_format(_input):  # _input can be list, SeqBuddy object, file handle, or file path.
    # If input is just a list, there is no BioPython in-format. Default to gb.
    if isinstance(_input, list):
        return "stockholm"

    # Pull value directly from object if appropriate
    if type(_input) == AlignBuddy:
        return _input.in_format

    # If input is a handle or path, try to read the file in each format, and assume success if not error and # seqs > 0
    if os.path.isfile(str(_input)):
        _input = open(_input, "r")

    if str(type(_input)) == "<class '_io.TextIOWrapper'>" or isinstance(_input, StringIO):
        # Die if file is empty
        if _input.read() == "":
            sys.exit("Input file is empty.")
        _input.seek(0)

        possible_formats = ["gb", "phylip-relaxed", "stockholm", "fasta", "nexus", "clustal"]
        for _format in possible_formats:
            try:
                _input.seek(0)
                _alignments = AlignIO.parse(_input, _format)
                if next(_alignments):
                    _input.seek(0)
                    return _format
                else:
                    continue
            except StopIteration:  # ToDo check that other types of error are not possible
                continue
            except ValueError:
                continue
        return None  # Unable to determine format from file handle

    else:
        raise GuessError("Unsupported _input argument in guess_format(). %s" % _input)


def phylipi(_alignbuddy, _format="relaxed"):  # _format in ["strict", "relaxed"]
    _output = ""
    for _alignment in _alignbuddy.alignments:
        max_id_length = 0
        max_seq_length = 0
        for _rec in _alignment:
            max_id_length = len(_rec.id) if len(_rec.id) > max_id_length else max_id_length
            max_seq_length = len(_rec.seq) if len(_rec.seq) > max_seq_length else max_seq_length

        _output += " %s %s\n" % (len(_alignment), max_seq_length)
        for _rec in _alignment:
            _seq_id = _rec.id.ljust(max_id_length) if _format == "relaxed" else _rec.id[:10].ljust(10)
            _output += "%s  %s\n" % (_seq_id, _rec.seq)
        _output += "\n"
    return _output

# #################################################################################################################### #

def list_ids(_alignbuddy, _columns=1):
    _columns = 1 if _columns == 0 else abs(_columns)
    _output = ""
    for _indx, alignment in enumerate(_alignbuddy.alignments):
        _output += "# Alignment %s\n" % (_indx + 1) if len(_alignbuddy.alignments) > 1 else ""
        _counter = 1
        for _rec in alignment:
            _output += "%s\t" % _rec.id
            if _counter % _columns == 0:
                _output = "%s\n" % _output.strip()
            _counter += 1
        _output += "\n"
    return "%s\n" % _output.strip()


def uppercase(_alignbuddy):
    for _rec in _get_seq_recs(_alignbuddy):
        _rec.seq = Seq(str(_rec.seq).upper(), alphabet=_rec.seq.alphabet)
    return _alignbuddy


def lowercase(_alignbuddy):
    for _rec in _get_seq_recs(_alignbuddy):
        _rec.seq = Seq(str(_rec.seq).lower(), alphabet=_rec.seq.alphabet)
    return _alignbuddy
# ################################################# COMMAND LINE UI ################################################## #
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="alignBuddy", description="Sequience alignment with a splash of Kava")

    parser.add_argument("alignment", help="The file(s) you want to start working on", nargs="*", default=[sys.stdin])
    parser.add_argument('-v', '--version', action='version',
                        version='''\
AlignBuddy 1.alpha (2015)

Gnu General Public License, Version 2.0 (http://www.gnu.org/licenses/gpl.html)
This is free software; see the source for detailed copying conditions.
There is NO warranty; not even for MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.
Questions/comments/concerns can be directed to Steve Bond, steve.bond@nih.gov''')

    parser.add_argument('-sf', '--screw_formats', action='store', help="Arguments: <out_format>")
    parser.add_argument('-uc', '--uppercase', action='store_true', help='Convert all sequences to uppercase')
    parser.add_argument('-lc', '--lowercase', action='store_true', help='Convert all sequences to lowercase')
    parser.add_argument('-an', '--features', action="store_true")
    parser.add_argument('-li', '--list_ids', nargs='?', action='append', type=int, metavar='int (optional)',
                        help="Output all the sequence identifiers in a file. Optionally, pass in an integer to "
                             "specify the # of columns to write")

    parser.add_argument("-i", "--in_place", help="Rewrite the input file in-place. Be careful!", action='store_true')
    parser.add_argument('-p', '--params', help="Free form arguments for some functions", nargs="+", action='store')
    parser.add_argument('-q', '--quiet', help="Suppress stderr messages", action='store_true')
    parser.add_argument('-t', '--test', action='store_true',
                        help="Run the function and return any stderr/stdout other than sequences.")
    parser.add_argument('-o', '--out_format', help="Some functions use this flag for output format", action='store')
    parser.add_argument('-f', '--in_format', action='store',
                        help="If AlignBuddy can't guess the file format, just specify it directly.")
    in_args = parser.parse_args()

    alignbuddy = []
    align_set = ""

    for align_set in in_args.alignment:
        align_set = AlignBuddy(align_set, in_args.in_format, in_args.out_format)
        alignbuddy += align_set.alignments

    alignbuddy = AlignBuddy(alignbuddy, align_set.in_format, align_set.out_format)

    # ############################################## INTERNAL FUNCTIONS ############################################## #
    def _print_aligments(_alignbuddy):
        if len(_alignbuddy.alignments) == 0:
            _stderr("Nothing returned.\n", in_args.quiet)
            return False

        if _alignbuddy.out_format == "fasta" and len(_alignbuddy.alignments) > 1:
            _stderr("Error: FASTA format does not support multiple alignments in one file.")
            return False

        elif _alignbuddy.out_format == "phylipi":
            _output = phylipi(_alignbuddy)

        elif _alignbuddy.out_format == "phylipis":
            _output = phylipi(_alignbuddy, "strict")

        else:
            tmp_dir = TemporaryDirectory()
            with open("%s/align.tmp" % tmp_dir.name, "w") as _ofile:
                AlignIO.write(_alignbuddy.alignments, _ofile, _alignbuddy.out_format)

            with open("%s/align.tmp" % tmp_dir.name, "r") as ifile:
                _output = ifile.read()

        if in_args.test:
            _stderr("*** Test passed ***\n", in_args.quiet)
            pass

        elif in_args.in_place:
            _in_place(_output, in_args.sequence[0])

        else:
            _stdout("{0}\n".format(_output.rstrip()))
        return True


    def _in_place(_output, _path):
        if not os.path.exists(_path):
            _stderr("Warning: The -i flag was passed in, but the positional argument doesn't seem to be a "
                    "file. Nothing was written.\n", in_args.quiet)
            _stderr("%s\n" % _output.rstrip(), in_args.quiet)
        else:
            with open(os.path.abspath(_path), "w") as _ofile:
                _ofile.write(_output)
            _stderr("File over-written at:\n%s\n" % os.path.abspath(_path), in_args.quiet)

    # ############################################## COMMAND LINE LOGIC ############################################## #
    # Screw formats
    if in_args.screw_formats:
        alignbuddy.out_format = in_args.screw_formats
        _print_aligments(alignbuddy)

    # List identifiers
    if in_args.list_ids:
        columns = 1 if not in_args.list_ids[0] else in_args.list_ids[0]
        _stdout(list_ids(alignbuddy, columns))

    # Uppercase
    if in_args.uppercase:
        _print_aligments(uppercase(alignbuddy))

    # Lowercase
    if in_args.lowercase:
        _print_aligments(lowercase(alignbuddy))

    # This is temporary for testing purposes
    if in_args.features:
        blahh = ['annotations', 'dbxrefs', 'description', 'features', 'id', 'letter_annotations', 'name', 'seq']
        foo = alignbuddy.alignments[0][0]
        bar = [foo.annotations, foo.dbxrefs, foo.description, foo.features, foo.id, foo.letter_annotations, foo.name, foo.seq]
        for indx, value in enumerate(blahh):
            print("{0}: {1}".format(value, bar[indx]))
        print("\nannotations{0}: ".format(alignbuddy.alignments[0].annotations))