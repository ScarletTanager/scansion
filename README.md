# Scansion

A project to explore analyzing prosody in Latin verse using machine learning.

## Goals

My primary goal is to build a system capable of correctly scanning (analyzing for meter)
Latin poetry.  For example, given a specific poem (e.g. Catullus 43), the system
should be able to scan it correctly.  "Scanning" here includes:
1. Identifying syllable boundaries
1. Identifying long vs. short syllables
1. Identifying the meter used and the foot structure/boundaries for each line (or couplet/quatrain, as the case may be)

## Requirements

1. The system must be capable of analyzing any meter used in classical Latin verse.
1. The system _must not need to know Latin_.  For example, the Latin `mensa` could
be in the Nominative case (with a _short_ -a) or in the Ablative (ending with a _long_ -ā).
It follows then that the deciding factor in determining whether to scan `mensa` as
either `mēnsă` or `mēnsā` cannot depending on the system knowing the grammatical case
of the word - it must derive solely from metrical/prosodic context.

## Other efforts known to me

The use of ML to perform metric analysis is not wholly novel.  There are at least a couple of
previous efforts of which I am aware:
1. Moy, Laney: [Scanning Vergil using a Neural Network](https://community.wolfram.com/groups/-/m/t/1732445) - This is an impressive effort
implemented by a (at the time) rising high school senior.  But...
    1. The ratio of training data to test data is far, far too high - 824 lines of training data to 20 lines of test data.  This means
    that the model produced will inevitably be highly overspecified and not sufficiently general purpose for my purposes.
    1. Simply recognizing a consonant as a consonant is probably insufficient.  Although the author states that she wants to
    avoid simply reproducing the rules of Latin scansion, some rule implementation may be necessary, as in the case of e.g.
    clusters containing liquids.  I think she wanted to offload the decision making to the model to the greatest extent possible
    (which is, I think, the correct impulse), but I'm not convinced this is viable.  (But I'm willing to be proven wrong.)
    1. The model only accounts for dactylic hexameter.  Catullus uses around ten different meters, for example.  Our model
    needs to be able scan a poem in any meter known in classical Latin verse.  (Note: I am not differentiating Republican vs. Imperial, etc. - I am simply differentiating classical from medieval for the nonce.)
1. Agirrezabal, Manex; Alegria, Iñaki; Hulden, Mans: [Machine Learning for Metrical Analysis of English Poetry](https://aclanthology.org/C16-1074.pdf) - I think the authors here are after a similar purpose
to my own, albeit using a different corpus (English poetry) and a stress-based, rather than a quantity-based (as in Latin) system.  I just found this article
recently, though, and it bears a couple of readings.
1. Kim, Hyungrok; Zhao, Yu; Zelalem, Belay: [Automatic Classification of Poetry by Neural Scansion](https://rokrokss.com/assets/cv/aiml.pdf) - Based on my initial reading, I think the authors
here recognize some of the problems with much computational scanning (although she didn't mention it as a problem, the author of the first solution sidestepped this as well by refusing to try to encode actual scansion rules) - namely that "poetic license" can result in a word scanning differently in
verse than one might expect based on its normal (prose) use would indicate, and that wholesale avoidance of knowing the language used is difficult
in a rule based system (e.g. the verb `conVICT` vs. the noun `CONvict`).

## Intended approach

Having done some experimentation, I think that a multiple pass classification approach should serve as a starting point.  By this, I mean that we have two tasks
in front of us.  The first is not to scan each line perfectly - it is just to scan the poem with _enough accuracy that we can identify the meter used_.
This is important because it is not unheard of for the length of a syllable in Latin verse to be ambiguous if one relies solely on phonological clues.
But in such cases, we may mark the syllable as either long or short because "the meter demands it".  E.g. if the syllable in question is in a line
of dactylic hexameter, and it _must_ be the first syllable in a dactyl, then we know that it must therefore be a long syllable, _even if it would otherwise be short in normal prose usage_.

To reach this point, we need a model which can identify with near certainty the meter in question.  Again, this does _not_ require us to achieve
flawless scansion of the entire poem.

Once we have the meter identified, we can then rescan the poem using the meter as a template - within a given meter, there is a fixed number
of ways to scan a line of a given number of syllables (some meters, e.g. hendecasyllabics, require a specific number of syllables to the line,
  while others allow for a variable number of syllables - the well-known dactylic hexameter is an example of this, along with elegiac couplets).

So we can use the meter as a template input to the model when classifying each syllable.

If we cannot scan the poem to fit the meter we believe to have been used, that will be a sign that we have misidentified the meter.

## Syllabic boundaries

Latin orthography can make identifying syllabic boundaries problematic - for example, some texts may use `i` and `u` for `j` (consonantal /y/)
and `v` (consonantal /w/) respectively - such as my own 2nd. Ed. of Quinn's Catullus, which I have owned since high school.  Others may use `i` for /y/ but `v` for /w/ (see [Catullus 1 at the Packard Humanities Institute](https://latin.packhum.org/loc/472/1/0#0) for an example of this), or perhaps vice versa.
This can be especially problematic when analyzing a word such as `iam` vs. `iambus` - the initial `i` in the first is consonantal (it is a monosyllabic word), but `iambus` is actually _trisyllabic_ - accounting for this without "teaching the model Latin" is a key difficulty.  One step is therefore to normalize
the input texts into a standardized orthography, so we will preprocess the texts (using both computation and some amount of human editing)
to render glide consonants solely as `j` and `v`.  

(Moy) handles this problem in part by assigning every character a probabilistic classification of long vowel, short vowel, consonant, punctuation mark, or ignored vowel.  I am not convinced of the general viability of this strategy - for example, a diphthong is an orthographic rendering of what is, metrically, a single long vowel.  And considering punctuation also seems inaccurate to me - for example, commas are not found in the original texts - they are later introductions to match our own sense of sentence/phrase structure - but they are frequently seen in most commonly used editions of classical Latin verse.  My own edition of Catullus (Quinn, 2nd. Ed.) contains not only commas but also parentheses as well.  For the purposes of meter, I would argue that we should omit these entirely from our analysis (at least for now).
