import unittest
import syllable
import os


class DefaultWordsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        me = os.path.realpath(__file__)
        cls.test_text_file = os.path.join(
            os.path.dirname(me),
            '..',
            'texts/test/43.words'
        )

    def setUp(self):
        self.words = syllable.Words(DefaultWordsTestCase.test_text_file)

    def test_lines(self):
        found = False
        for l in self.words.lines():
            for w in l:
                if w == 'elegante':
                    found = True
        self.assertTrue(found)


# Lowercase, no dipthongs
class DefaultWordTestCase(unittest.TestCase):
    def setUp(self):
        self.word = syllable.Word('elegante')

    def test_to_syllables(self):
        self.assertEqual(len(self.word.to_syllables()), 4)


class WordWithDiphthongTestCase(unittest.TestCase):
    def setUp(self):
        self.word = syllable.Word('caedo')

    def test_to_syllables(self):
        self.assertEqual(len(self.word.to_syllables()), 2)


class WordWithQUTestCase(unittest.TestCase):
    def setUp(self):
        self.word = syllable.Word('qua')

    def test_to_syllables(self):
        self.assertEqual(len(self.word.to_syllables()), 1)


class DefaultSyllableTestCase(unittest.TestCase):
    def setUp(self):
        self.syl = syllable.Syllable('ten')

    def test_slots(self):
        self.assertEqual(self.syl.slots, ['C', 'V', 'C'])

    def test_mark_final(self):
        self.assertFalse(self.syl.is_final())
        self.syl.mark_final()
        self.assertTrue(self.syl.is_final())

    def test_mark_initial(self):
        self.assertFalse(self.syl.is_initial())
        self.syl.mark_initial()
        self.assertTrue(self.syl.is_initial())


class SyllableWithDiphthongTestCase(unittest.TestCase):
    def setUp(self):
        self.syl = syllable.Syllable('lae')

    def test_slots(self):
        self.assertEqual(self.syl.slots, ['C', 'D'])


if __name__ == '__main__':
    unittest.main()
