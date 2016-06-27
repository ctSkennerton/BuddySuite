#!/usr/bin/env python3
# coding=utf-8
""" tests basic functionality of SeqBuddy class """
import pytest
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import IUPAC
from collections import OrderedDict

try:
    from buddysuite import MyFuncs
    from buddysuite.SeqBuddy import SeqBuddy, hash_ids, pull_recs, make_copy,\
        _guess_alphabet, _guess_format, _stdout, _stderr, _feature_rc
    from buddysuite.buddy_resources import GuessError
except ImportError:
    import MyFuncs
    from SeqBuddy import SeqBuddy, hash_ids, pull_recs, make_copy,\
        _guess_alphabet, _guess_format, _stdout, _stderr, _feature_rc
    from buddy_resources import GuessError


def test_instantiate_seqbuddy_from_file(sb_resources):
    for _path in sb_resources.get_list("", mode="paths"):
        assert type(SeqBuddy(_path)) == SeqBuddy


def test_instantiate_seqbuddy_from_handle(sb_resources):
    for _path in sb_resources.get_list("", mode="paths"):
        with open(_path, 'r') as ifile:
            assert type(SeqBuddy(ifile)) == SeqBuddy


def test_instantiate_seqbuddy_from_raw(sb_resources):
    for _path in sb_resources.get_list("", mode="paths"):
        with open(_path, 'r') as ifile:
            assert type(SeqBuddy(ifile.read(), in_format="raw")) == SeqBuddy

        with open(_path, 'r') as ifile:
            assert type(SeqBuddy(ifile, in_format="raw")) == SeqBuddy


def test_instantiate_seqbuddy_from_seqbuddy(sb_resources, sb_helpers):
    for _path in sb_resources.get_list("", mode="paths"):
        input_buddy = SeqBuddy(_path)
        tester = SeqBuddy(input_buddy)
        assert sb_helpers.seqs_to_hash(input_buddy) == sb_helpers.seqs_to_hash(tester)


def test_alpha_arg_dna(sb_resources):
    tester = SeqBuddy(sb_resources.get_one("d f", mode="paths"), alpha='dna')
    assert tester.alpha is IUPAC.ambiguous_dna


def test_alpha_arg_rna(sb_resources):
    tester = SeqBuddy(sb_resources.get_one("r f", mode="paths"), alpha='rna')
    assert tester.alpha is IUPAC.ambiguous_rna


def test_alpha_arg_prot(sb_resources):
    tester = SeqBuddy(sb_resources.get_one("p f", mode="paths"), alpha='prot')
    assert tester.alpha is IUPAC.protein


def test_alpha_arg_guess(sb_resources):
    tester = SeqBuddy(sb_resources.get_one("d f", mode="paths"), alpha='foo')
    assert tester.alpha is IUPAC.ambiguous_dna


def test_seqlist_error():
    with pytest.raises(TypeError):
        SeqBuddy([str, dict])


# ##################### SeqBuddy methods ###################### ##
def test_to_dict(sb_resources, sb_helpers):
    tester = str(sb_resources.get_one("o d f").to_dict())
    assert sb_helpers.string2hash(tester) == '2311d1712d41c5ec9c23ad107c8a06c3'

    with pytest.raises(RuntimeError):
        tester = SeqBuddy(">duplicate_id\nATGCTCGTA\n>duplicate_id\nATGCTCGTCGATGCT\n")
        tester.to_dict()


def test_to_string(capsys, sb_resources, sb_helpers):
    tester = sb_resources.get_one("o d f")
    assert sb_helpers.string2hash(str(tester)) == "b831e901d8b6b1ba52bad797bad92d14"

    tester = sb_resources.get_one("o d g")
    assert sb_helpers.string2hash(str(tester)) == "2e02a8e079267bd9add3c39f759b252c"

    tester.out_format = "raw"
    assert sb_helpers.string2hash(str(tester)) == "5d00d481e586e287f32d2d29916374ca"

    tester = sb_resources.get_one("o d n")
    pull_recs(tester, "α[2-9]")

    tester.out_format = "phylip"
    assert sb_helpers.string2hash(str(tester)) == "6a4d62e1ee130b324cce48323c6d1d41"

    tester.out_format = "phylip-relaxed"
    assert sb_helpers.string2hash(str(tester)) == "4c2c5900a57aad343cfdb8b35a8f8442"

    tester.out_format = "phylipss"
    assert sb_helpers.string2hash(str(tester)) == "089cfb52076e63570597a74b2b000660"

    tester.out_format = "phylipsr"
    assert sb_helpers.string2hash(str(tester)) == "58a74f5e08afa0335ccfed0bdd94d3f2"

    tester.records = []
    assert str(tester) == "Error: No sequences in object.\n"


def test_print_hashmap(sb_resources, sb_helpers):
    tester = sb_resources.get_one("o d f")
    hash_ids(tester)
    test_hashes = ["FEhFs96uVr", "5dOVoJsEaC", "muOhKHqlRK", "99id32X9JY", "hflijfeJXB", "0m9x7xeSqC", "qwgaHU3fms",
                   "uD7zXF2uEp", "btvnHXOJbc", "GiHvUV1n55", "dJm5uViNsC", "to4ctKvNG7", "VN579cevl3"]
    orig_ids = [rec_id for _hash, rec_id in tester.hash_map.items()]
    tester.hash_map = OrderedDict(zip(test_hashes, orig_ids))
    assert sb_helpers.string2hash(tester.print_hashmap()) == "cdb9fdf429108404be7b93d2ea201d6f"


# ################################################# HELPER FUNCTIONS ################################################# #
# ######################  'GuessError' ###################### #
def test_guesserror_raw_seq():
    with pytest.raises(GuessError):
        SeqBuddy("JSKHGLHGLSDKFLSDYUIGJVSBDVHJSDKGIUSUEWUIOIFUBCVVVBVNNJS{QF(*&#@$(*@#@*(*(%")
    try:
        SeqBuddy("JSKHGLHGLSDKFLSDYUIGJVSBDVHJSDKGIUSUEWUIOIFUBCVVVBVNNJS{QF(*&#@$(*@#@*(*(%")
    except GuessError as e:
        assert "File not found, or could not determine format from raw input" in str(e)


def test_guesserror_infile(sb_odd_resources):
    with pytest.raises(GuessError):
        SeqBuddy(sb_odd_resources["gibberish"])


def test_guesserror_in_handle(sb_odd_resources):
    with pytest.raises(GuessError):
        with open(sb_odd_resources["gibberish"], "r") as ifile:
            SeqBuddy(ifile)


def test_no__input():
    with pytest.raises(TypeError):
        # noinspection PyArgumentList
        SeqBuddy()


# ######################  'make_copy' ###################### #
def test_make_copy(sb_resources, sb_helpers):
    tester = SeqBuddy(sb_resources.get_one("d f", mode="paths"))
    tester_copy = make_copy(tester)
    assert sb_helpers.seqs_to_hash(tester) == sb_helpers.seqs_to_hash(tester_copy)

"""
# ######################  '_check_for_blast_bin' ###################### #
@pytest.mark.internet
@pytest.mark.slow
@pytest.mark.blast
def test_check_blast_bin(capsys):
    for _bin in ["blastn", "blastp", "blastdbcmd", "makeblastdb"]:
        assert _check_for_blast_bin(_bin)

    # noinspection PyUnresolvedReferences
    with mock.patch.dict(os.environ, {"PATH": ""}):
        with mock.patch('MyFuncs.ask', return_value=False):
            assert not _check_for_blast_bin("blastp")

        with mock.patch('MyFuncs.ask', return_value=True):
            with mock.patch("SeqBuddy._download_blast_binaries", return_value=False):
                check = _check_for_blast_bin("foo")
                assert not check
                out, err = capsys.readouterr()
                assert "Failed to download foo" in err

            _check_for_blast_bin("blastp")
            out, err = capsys.readouterr()
            assert "blastp downloaded" in err
            assert os.path.isfile("./blastp")
            os.remove("./blastp")


# ######################  '_download_blast_binaries' ###################### #
@pytest.mark.internet
@pytest.mark.slow
@pytest.mark.blast
@pytest.mark.parametrize("platform", ["darwin", "linux32", "linux64", "win"])
def test_dl_blast_bins(monkeypatch, platform):
    tmp_dir = MyFuncs.TempDir()
    monkeypatch.chdir(tmp_dir.path)
    if platform == "linux32":
        monkeypatch.setattr("sys.maxsize", 2000000000)
    platform = "linux" if "linux" in platform else platform
    _download_blast_binaries(ignore_pre_install=True, system=platform)
    if platform != "win":
        assert os.path.isfile('./blastdbcmd')
        assert os.path.isfile('./blastn')
        assert os.path.isfile('./blastp')
    else:
        assert os.path.isfile('./blastdbcmd.exe')
        assert os.path.isfile('./blastn.exe')
        assert os.path.isfile('./blastp.exe')
"""


# ######################  '_feature_rc' ###################### #
def test_feature_rc(sb_resources, sb_helpers):
    tester = sb_resources.get_one("d g")
    seq1 = tester.records[0]
    hashed = ["dc71a33b64a766da8653c19f22fc4caa", "9ab8296fb3443198674d90abe3311ba6",
              "10018d1b15c7f76a6333ac3bf96d2d07", "273463b9eace12d2eeadbf272692d73e",
              "c452d66d13120cd6eb5f041b7c37dd27", "1811b0695dba1fc3fe431a6ee00ef359"]
    for feature in zip(seq1.features, hashed):
        assert sb_helpers.string2hash(str(_feature_rc(feature[0], 1203))) == feature[1]

    with pytest.raises(TypeError):
        feature = seq1.features[0]
        feature.location = {}
        _feature_rc(feature, 1203)


# ######################  'guess_alphabet' ###################### #
def test_guess_alphabet(sb_resources):
    tester = sb_resources.get_one("d f")
    assert _guess_alphabet(tester) == IUPAC.ambiguous_dna

    tester = sb_resources.get_one("p f")
    assert _guess_alphabet(tester) == IUPAC.protein

    tester = sb_resources.get_one("r f")
    assert _guess_alphabet(tester) == IUPAC.ambiguous_rna

    tester = SeqBuddy(">Seq1", in_format="fasta")
    assert not _guess_alphabet(tester)


# ######################  'guess_format' ###################### #
@pytest.mark.foo
def test_guess_format(sb_resources, sb_odd_resources):
    assert _guess_format(["foo", "bar"]) == "gb"
    assert _guess_format(sb_resources.get_one("d f")) == "fasta"
    assert _guess_format(sb_resources.get_one("d f", mode="paths")) == "fasta"
    assert _guess_format(sb_odd_resources["blank"]) == "empty file"
    with pytest.raises(GuessError):
        _guess_format("foo")

    temp_file = MyFuncs.TempFile()
    temp_file.write('''\
<?xml version="1.0" encoding="ISO-8859-1"?>
<nex:nexml
    version="0.9"
    xsi:schemaLocation="http://www.nexml.org/2009 ../xsd/nexml.xsd"
    xmlns="http://www.nexml.org/2009"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xml="http://www.w3.org/XML/1998/namespace"
    xmlns:nex="http://www.nexml.org/2009"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
''')

    assert not _guess_format(temp_file.path)


# ######################  '_stdout and _stderr' ###################### #
def test_stdout(capsys):
    _stdout("Hello std_out", quiet=False)
    out, err = capsys.readouterr()
    assert out == "Hello std_out"

    _stdout("Hello std_out", quiet=True)
    out, err = capsys.readouterr()
    assert out == ""


def test_stderr(capsys):
    _stderr("Hello std_err", quiet=False)
    out, err = capsys.readouterr()
    assert err == "Hello std_err"

    _stderr("Hello std_err", quiet=True)
    out, err = capsys.readouterr()
    assert err == ""