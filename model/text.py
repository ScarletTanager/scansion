import tokenize


class Text:
    def __init__(self, path):
        with tokenize.open(path) as f:
            self.linedicts = {}
            self.tokens = tokenize.generate_tokens(f.readline)
            for tok in self.tokens:
                if tok[0] == 0:
                    # This is the EOF token, we skip it, continue instead of break
                    # so that we aren't dependent on eating the tokens in order
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


if __name__ == "__main__":
    import sys
    t = Text(sys.argv[1])
    t.print()
