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
        "citation": "",
        "published": "",
        "journal": "",
        "journal_art_id": "",
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
        self.current_abstract = self.find_and_get_text_single(article_meta, ".//abstract/p")

        self.current_solr_template['journal'] = \
            self.find_and_get_text_single(root, "./front/journal-meta/journal-title-group/journal-title")

        self.current_journal_id = \
            self.find_and_get_text_single(root, "./front/journal-meta/journal-id[@journal-id-type='publisher-id']")
        self.current_article_id = \
            self.find_and_get_text_single(article_meta, ".//article-id[@pub-id-type='publisher-id']")
        self.current_solr_template['journal_art_id'] = "%s---%s" % \
                                                       (self.current_solr_template['journal'], self.current_article_id)

        if article_meta is not None:
            for author in article_meta.findall(".//contrib-group/contrib[@contrib-type='author']"):
                last_name = self.find_and_get_text_single(author, './/name/surname')
                first_name = self.find_and_get_text_single(author, './/name/given-names')
                author_names.append('%s, %s' % (last_name, first_name))

        author_names = ", & ".join(author_names)
        self.current_solr_template['author'] = author_names

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


    def get_child_sections(self, el, prefix):

        return_val = []

        text_collector = {'item_text': '', 'id': ''}
        return_val.append(text_collector)
        if 'id' not in el.attrib:
            sec_id = prefix
            text_collector['id'] = "%s_%s_%s" % (self.current_journal_id, self.current_article_id, sec_id)
        else:
            text_collector['id'] = "%s_%s_%s" % (self.current_journal_id, self.current_article_id, el.attrib['id'])

        for item in el.findall('*'):
            if item.tag == "sec":
                it_str = ET.tostring(item).decode().replace(" xmlns:ns0=\"http://www.w3.org/1999/xlink\"", "")
                return_val.append({'item': item, 'item_str': it_str})
            else:
                for text in item.itertext():
                    text_collector['item_text'] += (" " + text.strip())

        return return_val

    def traverse_section(self, section, prefix):
        direct_children = self.get_child_sections(section, prefix)
        section_solr_template = copy.deepcopy(self.current_solr_template)
        section_solr_template['id'] = direct_children[0]['id']
        section_solr_template['content'] = direct_children[0]['item_text']
        section_solr_template['content_str'] = direct_children[0]['item_text']
        self.documents.append(section_solr_template)

        for x in range(1, len(direct_children)):
            self.traverse_section(direct_children[x]['item'], prefix + "_" + str(x))

    def traverse_sections(self, root):

        has_sections = False
        top_level_sections = root.findall("./body/sec")

        pos = 1

        for section in top_level_sections:
            has_sections = True
            self.traverse_section(section, 'sec' + str(pos))
            pos = pos + 1

        return has_sections

    def ingest(self, file):

        tree = ET.parse(file)
        root = tree.getroot()
        self.documents = []
        self.current_solr_template = copy.deepcopy(self.solr_doc_template)
        self.populate_fields_and_citation(root)
        if self.traverse_sections(root):
            self.solr_conn.add_many(self.documents, _commit=True)

        if self.current_abstract:
            abstract_entry = copy.deepcopy(self.current_solr_template)
            abstract_entry['id'] = "%s_%s_%s" % (self.current_journal_id, self.current_article_id, 'abstract')
            abstract_entry["abstract"] = self.current_abstract
            self.solr_conn.add_many([abstract_entry], _commit=True)

    def __init__(self):
        solr_url = "%s/%s" % (SOLR_URL, SOLR_COLLECTION)
        self.solr_conn = solr.SolrConnection(solr_url)


def main(args):

    ingestor = SolrIngestor()

    print("Scanning directory %s" % args.dir)
    if (os.path.isdir(args.dir)):
        for filename in os.listdir(args.dir):
            if (filename.endswith(".xml")):
                print("Attempting to ingest %s" % filename)
                ingestor.ingest(os.path.join(args.dir, filename))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", help="directory to scour for journal XML files")
    args = parser.parse_args()
    main(args)
