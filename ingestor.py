import argparse
from config.settings import SOLR_COLLECTION, SOLR_URL
import copy
import solr
import os
import xml.etree.ElementTree as ET


def rreplace(s, old, new):
    li = s.rsplit(old, 1) #Split only once
    return new.join(li)


class SolrIngestor:

    solr_doc_template = {
        "id": "",
        "name": "",
        "title": "",
        "abstract": "",
        "author": "",
        "author_s": "",
        "citation": "",
        "published": "",
        "journal": "",
        "content": "",
        "content_str": "",
        "doi": "",
    }

    def find_and_get_text_single(self, el, xpath):

        for child_el in el.findall(xpath):
            return child_el.text

        return ''

    def populate_fields_and_citation(self, root):

        author_names = []

        article_meta = root.find("./front/article-meta")

        self.current_solr_template['title'] = \
            self.find_and_get_text_single(article_meta, ".//title-group/article-title")
        self.current_solr_template['doi'] \
            = self.find_and_get_text_single(article_meta, ".//article-id[@pub-id-type='doi']")
        self.current_solr_template['abstract'] = self.find_and_get_text_single(article_meta, ".//abstract/p")

        self.current_solr_template['journal'] = \
            self.find_and_get_text_single(root, "./front/journal-meta/journal-title-group/journal-title")

        if article_meta is not None:
            for author in article_meta.findall(".//contrib-group/contrib[@contrib-type='author']"):
                last_name = self.find_and_get_text_single(author, './/name/surname')
                first_name = self.find_and_get_text_single(author, './/name/given-names')
                author_names.append('%s, %s' % (last_name, first_name))

        author_names = ", & ".join(author_names)
        self.current_solr_template['author'] = author_names
        self.current_solr_template['author_s'] = author_names

        publish_element = article_meta.find(".//pub-date[@pub-type='ppub']")

        if publish_element is not None:
            pub_year = self.find_and_get_text_single(publish_element, ".//year")
            pub_day = self.find_and_get_text_single(publish_element, ".//day")
            pub_month = self.find_and_get_text_single(publish_element, ".//month")
            self.current_solr_template['published'] = "%s-%s-%sT00:00:00Z" % (pub_year, pub_month, pub_day)

            citation = "%s (%s). %s. <span class=\"journal-title\">%s</span>" % \
                (author_names, pub_year, self.current_solr_template['title'], self.current_solr_template['journal'])

        volume = self.find_and_get_text_single(article_meta, ".//volume")
        issue = self.find_and_get_text_single(article_meta, ".//issue")
        fpage = self.find_and_get_text_single(article_meta, ".//fpage")
        lpage = self.find_and_get_text_single(article_meta, ".//lpage")
        self.current_solr_template['citation'] = "%s, %s(%s), %s-%s" % (citation, volume, issue, fpage, lpage)

    def traverse_sections(self, root):

        return None

    def ingest(self, file):

        tree = ET.parse(file)
        root = tree.getroot()
        self.current_solr_template = copy.deepcopy(self.solr_doc_template)
        self.populate_fields_and_citation(root)
        print(self.current_solr_template)

    def __init__(self):
        solr_url = "%s/%s" % (SOLR_URL, SOLR_COLLECTION)
        self.solr_conn = solr.SolrConnection(solr_url)


def main(args):

    x = 0
    ingestor = SolrIngestor()

    print("Scanning directory %s" % args.dir)
    if (os.path.isdir(args.dir)):
        for filename in os.listdir(args.dir):
            if (filename.endswith(".xml")):
                x = x + 1
                print("Attempting to ingest %s" % filename)
                ingestor.ingest(os.path.join(args.dir, filename))
            if (x > 12):
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", help="directory to scour for journal XML files")
    args = parser.parse_args()
    main(args)
