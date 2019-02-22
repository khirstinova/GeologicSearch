import argparse
from config.settings import SOLR_COLLECTION, SOLR_URL
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

    def get_apa_citation(self, root):

        author_names = []

        article_meta = root.find("./front/article-meta")
        if article_meta is not None:
            for author in article_meta.findall(".//contrib-group/contrib[@contrib-type='author']"):
                last_name = self.find_and_get_text_single(author, './/name/surname')
                first_name = self.find_and_get_text_single(author, './/name/given-names')
                author_names.append('%s, %s' % (last_name, first_name))

        return ", & ".join(author_names)

    def ingest(self, file):
        tree = ET.parse(file)
        root = tree.getroot()
        citation = self.get_apa_citation(root)
        print("File has citation: " + citation)

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
