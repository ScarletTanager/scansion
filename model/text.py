import tokenize
import requests
import argparse
import os
import re
from html.parser import HTMLParser

PACKHUM_URL = 'https://latin.packhum.org/dx/text/{}/{}/{}'
ROMAN_NUM = '(?<=\n)[CDILMVX]+(?=\n)'
WORK_NUM = '(?<=\n)[\d\.]+(?=\n)'
WORK_LINE = '[a-z][a-z\?\.\,\!\;\:]*'


class PackhumHTMLParser(HTMLParser):
    def init_regex(self):
        self.lines = []
        self.current_line = 0
        self.rnp = re.compile(ROMAN_NUM)
        self.wnp = re.compile(WORK_NUM)
        self.wlp = re.compile(WORK_LINE)
        self.in_table_data = False

    def handle_starttag(self, tag, attrs):
        if tag == 'td':
            self.in_table_data = True

    def handle_endtag(self, tag):
        if tag == 'td':
            self.in_table_data = False

    def handle_data(self, data):
        if self.in_table_data:
            if self.rnp.search(data):
                return
            if self.wnp.search(data):
                return
            if self.wlp.search(data):
                self.lines.append(data.strip('\n'))

    def readline(self):
        if self.current_line < len(self.lines):
            self.current_line += 1
            return self.lines[self.current_line - 1]
        else:
            return ''


class Text:
    def __init__(self, data):
        op = getattr(data, 'readline', None)
        if callable(op):
            self.linedicts = {}
            self.tokens = tokenize.generate_tokens(data.readline)
            for tok in self.tokens:
                if tok[0] != 1:
                    # We only care about type=1 (NAME)
                    continue
                lineno = tok[2][0]
                if lineno in self.linedicts:
                    # We've seen the line before, add this word with the position within the line as the key
                    self.linedicts[lineno][tok[2][1]] = tok[1]
                else:
                    # Each line is a dict, key is the starting position in the line, value is the word
                    self.linedicts[lineno] = {tok[2][1]: tok[1]}

            self.lines = []
            for lineno in sorted(self.linedicts):
                ld = self.linedicts[lineno]
                linewords = []
                for pos in sorted(ld):
                    linewords.append(ld[pos])
                self.lines.insert(lineno, linewords)

    def print(self):
        for line in self.lines:
            print(line)


def get_text(author, work, chapter):
    headers = {'user-agent': 'curl/7.64.1'}
    request_path = PACKHUM_URL.format(author, work, chapter)
    r = requests.get(request_path, headers=headers)
    if r.status_code != 200:
        return None
    parser = PackhumHTMLParser()
    parser.init_regex()
    parser.feed(r.text)
    return Text(parser)


def main():
    parser = argparse.ArgumentParser(
        description='Download and parse Latin text from packhum.org',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-a', '--author-index',
                        required=True, help='Author index')
    parser.add_argument('-w', '--work-index', required=True, help='Work index')
    parser.add_argument('-c', '--chapter-index',
                        required=False, help='Chapter index')

    args = parser.parse_args()
    chapter_index = args.chapter_index if args.chapter_index else os.environ.get(
        'JOB_INDEX')

    if not chapter_index:
        return -1

    text = get_text(args.author_index, args.work_index, chapter_index)
    text.print()


if __name__ == "__main__":
    exit(main())
