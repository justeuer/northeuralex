# coding=utf-8
from __future__ import unicode_literals, print_function

from clldutils.dsv import NamedTupleReader
import attr

from clldutils.path import Path
from pylexibank.dataset import Metadata, Lexeme
from pylexibank.dataset import Dataset as BaseDataset

from pylexibank.util import pb


@attr.s
class NLLexeme(Lexeme):
    Orthography = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    lexeme_class = NLLexeme

    def cmd_download(self, **kw):
        self.raw.download(
            'http://www.northeuralex.org/static/downloads/northeuralex-cldf.csv',
            "nelex.tsv",
            log=self.log)
        #self.raw.write('sources.bib', getEvoBibAsBibtex('Hamed2006', 'List2015d', **kw))

    def split_forms(self, row, value):
        """
        We make sure to always only yield one form per raw lexeme.
        """
        return BaseDataset.split_forms(self, row, value)[:1]

    def cmd_install(self, **kw):
        ccode = {x.attributes['nelex_id']: x.concepticon_id for x in
                 self.conceptlist.concepts.values()}

        tk = self.get_tokenizer()
        with self.cldf as ds, NamedTupleReader(
                self.raw.posix('nelex.tsv'), delimiter="\t") as reader:
            ds.add_sources(*self.raw.read_bib())

            for row in pb(reader, desc="installing northeuralex"):
                if row.rawIPA:
                    ds.add_language(
                        ID=row.Language_ID,
                        name=row.Language_ID,
                        glottocode=row.Glottocode)
                    ds.add_concept(
                        ID=row.Concept_ID,
                        gloss=row.Concept_ID,
                        conceptset=ccode[row.Concept_ID])
                    ds.add_lexemes(
                        Language_ID=row.Language_ID,
                        Parameter_ID=row.Concept_ID,
                        Value=row.rawIPA,
                        Orthography=row.Word_Form,
                        Source=[],
                        Segments=tk(row.rawIPA, 'IPA'))
