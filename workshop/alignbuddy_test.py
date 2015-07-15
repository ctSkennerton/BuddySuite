#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# NOTE: BioPython 16.6+ required.

import pytest
from hashlib import md5
import os
from io import StringIO
import re
from copy import deepcopy
from Bio.Alphabet import IUPAC
from Bio.Seq import Seq
import SeqBuddy as SB

try:
    import workshop.AlignBuddy as Alb
except ImportError:
    import AlignBuddy as Alb


def align_to_hash(_alignbuddy, mode='hash'):
    if mode != "hash":
        return str(_alignbuddy)
    _hash = md5("{0}\n".format(str(_alignbuddy).rstrip()).encode()).hexdigest()
    return _hash

root_dir = os.getcwd()


def resource(file_name):
    return "{0}/unit_test_resources/{1}".format(root_dir, file_name)


def test_guess_format():
    assert Alb.guess_format(["dummy", "list"]) == "stockholm"
    assert Alb.guess_format(alb_objects[0]) == "nexus"

    with open(resource("Alignments_pep.stklm"), "r") as ifile:
        assert Alb.guess_format(ifile) == "stockholm"
        ifile.seek(0)
        string_io = StringIO(ifile.read())
    assert Alb.guess_format(string_io) == "stockholm"
    with pytest.raises(Alb.GuessError):
        Alb.guess_format({"Dummy dict": "Type not recognized by guess_format()"})


align_files = ["Mnemiopsis_cds.nex", "Mnemiopsis_cds.phy", "Mnemiopsis_cds.phyr", "Mnemiopsis_cds.stklm",
               "Mnemiopsis_pep.nex", "Mnemiopsis_pep.phy", "Mnemiopsis_pep.phyr", "Mnemiopsis_pep.stklm",
               "Alignments_pep.phy", "Alignments_pep.phyr", "Alignments_pep.stklm",
               "Alignments_cds.phyr", "Alignments_cds.stklm"]

file_types = ["nexus", "phylip", "phylip-relaxed", "stockholm",
              "nexus", "phylip", "phylip-relaxed", "stockholm",
              "phylip", "phylip-relaxed", "stockholm",
              "phylip-relaxed", "stockholm"]

nucl_indices = [0, 1, 2, 3, 11, 12]

input_tuples = [(next_file, file_types[indx]) for indx, next_file in enumerate(align_files)]


@pytest.mark.parametrize("align_file,file_type", input_tuples)
def test_instantiate_alignbuddy_from_file(align_file, file_type):
    assert type(Alb.AlignBuddy(resource(align_file), _in_format=file_type)) == Alb.AlignBuddy


@pytest.mark.parametrize("align_file", align_files)
def test_instantiate_alignbuddy_from_file_guess(align_file):
    assert type(Alb.AlignBuddy(resource(align_file))) == Alb.AlignBuddy


@pytest.mark.parametrize("align_file", align_files)
def test_instantiate_alignbuddy_from_handle(align_file):
    with open(resource(align_file), 'r') as ifile:
        assert type(Alb.AlignBuddy(ifile)) == Alb.AlignBuddy


@pytest.mark.parametrize("align_file", align_files)
def test_instantiate_alignbuddy_from_raw(align_file):
    with open(resource(align_file), 'r') as ifile:
        assert type(Alb.AlignBuddy(ifile.read())) == Alb.AlignBuddy


@pytest.mark.parametrize("align_file", align_files)
def test_instantiate_alignbuddy_from_alignbuddy(align_file):
    tester = Alb.AlignBuddy(resource(align_file))
    assert type(Alb.AlignBuddy(tester)) == Alb.AlignBuddy


@pytest.mark.parametrize("align_file", align_files)
def test_instantiate_alignbuddy_from_list(align_file):
    tester = Alb.AlignBuddy(resource(align_file))
    assert type(Alb.AlignBuddy(tester.alignments)) == Alb.AlignBuddy

    with pytest.raises(TypeError):  # When non-MultipleSeqAlignment objects are in the .alignments list
        tester.alignments.append("Dummy string object")
        Alb.AlignBuddy(tester.alignments)


def test_empty_file():
    with open(resource("blank.fa"), "r") as ifile:
        with pytest.raises(SystemExit):
            Alb.AlignBuddy(ifile)


def test_guess_error():
    # File path
    with pytest.raises(Alb.GuessError):
        Alb.AlignBuddy(resource("unrecognizable.txt"))

    with open(resource("unrecognizable.txt"), 'r') as ifile:
        # Raw
        with pytest.raises(Alb.GuessError):
            Alb.AlignBuddy(ifile.read())

        # Handle
        with pytest.raises(Alb.GuessError):
            ifile.seek(0)
            Alb.AlignBuddy(ifile)

    # GuessError output
    try:
        Alb.AlignBuddy(resource("unrecognizable.txt"))
    except Alb.GuessError as e:
        assert str(e) == "Could not determine format from _input file '/Users/bondsr/Documents/BuddySuite/workshop/" \
                         "unit_test_resources/unrecognizable.txt'.\nTry explicitly setting with -f flag."


def test_stderr(capsys):
    Alb._stderr("Hello std_err", quiet=False)
    out, err = capsys.readouterr()
    assert err == "Hello std_err"

    Alb._stderr("Hello std_err", quiet=True)
    out, err = capsys.readouterr()
    assert err == ""


def test_stdout(capsys):
    Alb._stdout("Hello std_out", quiet=False)
    out, err = capsys.readouterr()
    assert out == "Hello std_out"

    Alb._stdout("Hello std_out", quiet=True)
    out, err = capsys.readouterr()
    assert out == ""

# Now that we know that all the files are being turned into AlignBuddy objects okay, make them all objects so it doesn't
# need to be done over and over for each subsequent test.
alb_objects = [Alb.AlignBuddy(resource(x)) for x in align_files]


# AlignBuddy print() and __str__() methods
hashes = ["cb1169c2dd357771a97a02ae2160935d", "f59e28493949f78637691caeb617ab50",
          "52c23bd793c9761b7c0f897d3d757c12", "228e36a30e8433e4ee2cd78c3290fa6b",
          "17ff1b919cac899c5f918ce8d71904f6", "5af1cf061f003d3351417458c0d23811",
          "f3e98897f1bbb3d3d6c5507afa9f814e", "c0dce60745515b31a27de1f919083fe9",
          "90578980479ad235338dbb767444b05b", "9c6773e7d24000f8b72dd9d25620cff1",
          "3fd5805f61777f7f329767c5f0fb7467"]
hashes = [(alb_objects[indx], value) for indx, value in enumerate(hashes)]


@pytest.mark.parametrize("alignbuddy,next_hash", hashes)
def test_print(alignbuddy, next_hash, capsys):
    alignbuddy.print()
    out, err = capsys.readouterr()
    out = "{0}\n".format(out.rstrip())
    tester = md5(out.encode()).hexdigest()
    assert tester == next_hash


@pytest.mark.parametrize("alignbuddy,next_hash", hashes)
def test_str(alignbuddy, next_hash):
    tester = str(alignbuddy)
    tester = md5(tester.encode()).hexdigest()
    assert tester == next_hash


@pytest.mark.parametrize("alignbuddy,next_hash", hashes)
def test_write1(alignbuddy, next_hash):
    alignbuddy.write("/tmp/alignbuddywritetest")
    with open("/tmp/alignbuddywritetest", "r") as ifile:
        out = "{0}\n".format(ifile.read().rstrip())
    tester = md5(out.encode()).hexdigest()
    assert tester == next_hash


def test_write2():  # Unloopable components
    tester = Alb._make_copies(alb_objects[8])
    tester.out_format = "fasta"
    with pytest.raises(ValueError):
        str(tester)

    tester.alignments = []
    assert str(tester) == "AlignBuddy object contains no alignments.\n"

    tester = Alb._make_copies(alb_objects[2])
    tester.out_format = "phylipi"
    assert md5(str(tester).encode()).hexdigest() == "0379295eb39370bdba17c848ec9a8b73"

    tester.out_format = "phylipis"
    assert md5(str(tester).encode()).hexdigest() == "729a3de75d70179a27a802bc0437f4ee"



def test_get_seq_recs():
    tester = str(Alb._get_seq_recs(alb_objects[8]))
    tester = md5(tester.encode()).hexdigest()
    assert tester == "6168f8b57d0ff78d70fd22ee09d713b5"


def test_phylipi():
    tester = Alb.phylipi(alb_objects[0], _format="relaxed")
    tester = "{0}\n".format(tester.rstrip())
    tester = md5(tester.encode()).hexdigest()
    assert tester == "c5fb6a5ce437afa1a4004e4f8780ad68"

    tester = Alb.phylipi(alb_objects[8], _format="relaxed").rstrip()
    tester = "{0}\n".format(tester.rstrip())
    tester = md5(tester.encode()).hexdigest()
    assert tester == "af97ddb03817ff050d3dfb42472c91e0"

    tester = Alb.phylipi(alb_objects[0], _format="strict").rstrip()
    tester = "{0}\n".format(tester.rstrip())
    tester = md5(tester.encode()).hexdigest()
    assert tester == "270f1bac51b2e29c0e163d261795c5fe"

    tester = Alb.phylipi(alb_objects[8], _format="strict").rstrip()
    tester = "{0}\n".format(tester.rstrip())
    tester = md5(tester.encode()).hexdigest()
    assert tester == "af97ddb03817ff050d3dfb42472c91e0"


def test_guess_alphabet():
    assert str(type(Alb.guess_alphabet(alb_objects[0]))) == "<class 'Bio.Alphabet.IUPAC.IUPACAmbiguousDNA'>"
    assert str(type(Alb.guess_alphabet(alb_objects[4]))) == "<class 'Bio.Alphabet.IUPAC.IUPACProtein'>"
    tester = Alb.AlignBuddy(resource("Mnemiopsis_rna.nex"))
    assert str(type(Alb.guess_alphabet(tester))) == "<class 'Bio.Alphabet.IUPAC.IUPACAmbiguousRNA'>"
    assert not Alb.guess_alphabet(Alb.AlignBuddy("", _in_format="fasta"))


def test_list_ids():
    tester = Alb.list_ids(alb_objects[0])
    tester = md5(tester.encode()).hexdigest()
    assert tester == "1c4a395d8aa3496d990c611c3b6c4d0a"

    tester = Alb.list_ids(alb_objects[0], _columns=4)
    tester = md5(tester.encode()).hexdigest()
    assert tester == "26fa56b979d009015612647c87a47a51"

    tester = Alb.list_ids(alb_objects[8])
    tester = md5(tester.encode()).hexdigest()
    assert tester == "7f7cc5d09164cb2f5deb915193b06639"

    tester = Alb.list_ids(alb_objects[8], _columns=4)
    tester = md5(tester.encode()).hexdigest()
    assert tester == "74bd0e70fd325d59c0399c4f8a0ea7c9"


# ######################  'uc', '--uppercase'  and 'lc', '--lowercase' ###################### #
uc_hashes = ["52e74a09c305d031fc5263d1751e265d", "34eefeafabfc55811a5c9fe958b61490", "6e5542f41d17ff33afb530b4d07408a3",
             "b82538a4630810c004dc8a4c2d5165ce", "8b6737fe33058121fd99d2deee2f9a76", "b804b3c0077f342f8a5e8c36b8af627f",
             "747ca137dc659f302a07b0c39e989e54", "f35cbc6e929c51481e4ec31e95671638", "73e3da29aa78f4abb4bc6392b81cd279",
             "46e049a1be235d17f8379c293e1e393f", "6f3f234d796520c521cb85c66a3e239a"]

lc_hashes = ["cb1169c2dd357771a97a02ae2160935d", "f59e28493949f78637691caeb617ab50", "52c23bd793c9761b7c0f897d3d757c12",
             "228e36a30e8433e4ee2cd78c3290fa6b", "17ff1b919cac899c5f918ce8d71904f6", "5af1cf061f003d3351417458c0d23811",
             "f3e98897f1bbb3d3d6c5507afa9f814e", "c0dce60745515b31a27de1f919083fe9", "e4d6766b7544557b9ddbdcbf0cde0c16",
             "12716bad78b2f7a40882df3ce183735b", "00661f7afb419c6bb8c9ac654af7c976"]

hashes = [(Alb._make_copies(alb_objects[indx]), uc_hash, lc_hashes[indx]) for indx, uc_hash in enumerate(uc_hashes)]


@pytest.mark.parametrize("alignbuddy,uc_hash,lc_hash", hashes)
def test_cases(alignbuddy, uc_hash, lc_hash):
    tester = Alb.uppercase(alignbuddy)
    assert align_to_hash(tester) == uc_hash
    tester = Alb.lowercase(tester)
    assert align_to_hash(tester) == lc_hash

# ###########################################  'ca', '--condon_alignment' ############################################ #
hashes = ["c907d29434fe2b45db60f1a9b70f110d", "f150b94234e93f354839d7c2ca8dae24", "6a7a5416f2ce1b3161c8b5b8b4b9e901",
          "54d412fbca5baa60e4c31305d35dd79a", "3ddc2109b15655ef0eed3908713510de", "f728ab606602ed67357f78194e500664"]

hashes = [(Alb._make_copies(alb_objects[nucl_indices[indx]]), next_hash) for indx, next_hash in enumerate(hashes)]


@pytest.mark.parametrize("alignbuddy,next_hash", hashes)
def test_codon_alignment1(alignbuddy, next_hash):
    tester = Alb.codon_alignment(alignbuddy)
    assert align_to_hash(tester) == next_hash

    if next_hash == "f728ab606602ed67357f78194e500664":
        with pytest.raises(TypeError):
            Alb.codon_alignment(alb_objects[8])


def test_codon_alignment2():
    with pytest.raises(TypeError):
        tester = Alb._make_copies(alb_objects[3])
        tester.alignments[0][0].seq = Seq("MLDILSKFKGVTPFKGITIDDGWDQLNRSFMFVLLVVMGTTVTVRQYTGSVISCDGFKKFGSTFAEDYCWTQGLY",
                                          alphabet=IUPAC.protein)
        Alb.translate_cds(tester)


# ##############################################  'cs', '--clean_seqs' ############################################### #
def test_clean_seqs():
    # Test an amino acid file
    tester = Alb._make_copies(alb_objects[8])
    Alb.clean_seq(tester)

    with pytest.raises(ValueError):
        str(tester)

    tester.out_format = "fasta"
    with pytest.raises(ValueError):
        str(tester)

    tester.out_format = "genbank"
    assert align_to_hash(tester) == "b613060f43f66248cda0088c06de0949"

    # Test nucleotide files, but skip the errors
    tester = Alb._make_copies(alb_objects[11])
    Alb.clean_seq(tester, skip_list="RYWSMKHBVDNXrywsmkhbvdnx")
    tester.out_format = "genbank"
    assert align_to_hash(tester) == "81189bf7962cc2664815dc7fca8cd95d"

    Alb.clean_seq(tester)
    assert align_to_hash(tester) == "2f2cbf227d45aa49d15971ce214d3191"

# ###########################################  'tr', '--translate' ############################################ #
hashes = ["fa915eafb9eb0bfa0ed8563f0fdf0ef9", "5064c1d6ae6192a829972b7ec0f129ed", "ce423d5b99d5917fbef6f3b47df40513",
          "2340addad40e714268d2523cdb17a78c", "6c66f5f63c5fb98f5855fb1c847486ad", "d9527fe1dfd2ea639df267bb8ee836f7"]
hashes = [(Alb._make_copies(alb_objects[nucl_indices[indx]]), next_hash) for indx, next_hash in enumerate(hashes)]


@pytest.mark.parametrize("alignbuddy,next_hash", hashes)
def test_translate1(alignbuddy, next_hash, capsys):
    tester = Alb.translate_cds(alignbuddy)
    assert align_to_hash(tester) == next_hash

    if next_hash == "6c66f5f63c5fb98f5855fb1c847486ad":
        out, err = capsys.readouterr()
        assert err == "Warning: First codon 'GGT' is not a start codon in Ael_PanxβQ___CDS\n"


def test_translate2():
    # Protein input
    with pytest.raises(TypeError):
        Alb.translate_cds(alb_objects[4])

    # Non-standard length
    tester = Alb._make_copies(alb_objects[0])
    tester.alignments[0][0].seq = Seq(re.sub("-$", "t", str(tester.alignments[0][0].seq)),
                                      alphabet=tester.alignments[0][0].seq.alphabet)
    Alb.translate_cds(tester)
    assert align_to_hash(tester) == "fa915eafb9eb0bfa0ed8563f0fdf0ef9"

    # Final codon not stop and stop codon not at end of seq
    tester = Alb._make_copies(alb_objects[0])
    tester.alignments[0][0].seq = Seq(re.sub("---$", "ttt", str(tester.alignments[0][0].seq)),
                                      alphabet=tester.alignments[0][0].seq.alphabet)
    Alb.translate_cds(tester)
    assert align_to_hash(tester) == "2ca5b0bac98226ee6a53e17503f12197"

    # Non-standard codon
    tester = Alb.AlignBuddy(resource("ambiguous_dna_alignment.fa"))
    Alb.translate_cds(tester)
    assert align_to_hash(tester) == "ab8fb45a38a6e5d553a29f3613bbc1a1"