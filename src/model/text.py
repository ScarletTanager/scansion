import tokenize

#
# Text: a tokenized (by word) representation of a text
#
# Must be instantiated from a type implementing readline(), such
# as a file
#

class Text:
    def __init__(self, data):
        op = getattr(data, 'readline', None)
        self.lines = []
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

            for lineno in sorted(self.linedicts):
                ld = self.linedicts[lineno]
                linewords = []
                for pos in sorted(ld):
                    linewords.append(ld[pos])
                self.lines.insert(lineno, linewords)

    def print(self):
        for line in self.lines:
            print(line)


class ScannedText:
    def __init__(self, data_file):
        self.lines = {}
        with open(data_file) as f:
            for line in f:
                vals = line.strip().split(',')
                lineno = int(vals[0])
                quantity = int(vals[9])
                if lineno not in self.lines:
                    self.lines[lineno] = {}
                self.lines[lineno][int(float(vals[7]))] = {
                    'chars': vals[1],
                    'wordpos': int(float(vals[5])),
                    'quantity': quantity,
                    'certainty': float(vals[10 + quantity])
                }

            # def create_bucket_if_does_not_exist(bucket=None):
