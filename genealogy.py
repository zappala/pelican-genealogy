# -*- coding: utf-8 -*-
'''
Genealogy Generator
-------

The genealogy plugin generates surname and people lists from the metadata
in each article
'''


from pelican import signals
from pelican.generators import ArticlesGenerator
from pelican.urlwrappers import (URLWrapper)

from collections import defaultdict
from functools import partial
from operator import attrgetter

class Surname(URLWrapper):
    def __init__(self, name, *args, **kwargs):
        super(Surname, self).__init__(name.strip(), *args, **kwargs)


class GenealogyGenerator(ArticlesGenerator):

    def __init__(self, *args, **kwargs):
        self.surnames = defaultdict(list)
        self.people = defaultdict(list)
        super(GenealogyGenerator, self).__init__(*args, **kwargs)

    def generate_context(self):
        super(GenealogyGenerator,self).generate_context()
        for article in self.articles:
            if hasattr(article,'surnames'):
                surnames = article.surnames.split(',')
                for surname in surnames:
                    surname = Surname(surname,self.settings)
                    self.surnames[surname].append(article)
            if hasattr(article, 'people'):
                people = article.people.split(',')
                for person in people:
                    self.people[person].append(article)

        # self.surnames = list(self.surnames.items())
        # self.surnames.sort()

        self.people = list(self.people.items())
        self.people.sort()
        print self.tags,self.surnames

        self._update_context(('surnames','people'))
        # self.save_cache()
        
    def generate_output(self, writer):
        write = partial(writer.write_file,
                        relative_urls=self.settings['RELATIVE_URLS'])

        # Generate surname pages
        surname_template = self.get_template('surname')
        for surname, articles in self.surnames.items():
            articles.sort(key=attrgetter('date'), reverse=True)
            dates = [article for article in self.dates if article in articles]
            write(surname.save_as, surname_template, self.context, surname=surname,
                  articles=articles, dates=dates,
                  paginated={'articles': articles, 'dates': dates},
                  page_name=surname.page_name, all_articles=self.articles)
        # Generate person pages


def get_generators(generators):
    return GenealogyGenerator


def register():
    signals.get_generators.connect(get_generators)
