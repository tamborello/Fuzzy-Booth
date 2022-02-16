# Fuzzy Booth
# Search a document for a substring, but with Levenshtein edit distance fuzzy-matching.

# To do:
# Splitting's all well and good, but I should probably do a bit more processing on Text and SearchTerm, such as to use a generally accepted tokenizer and work on the tokens.

import logging
from nltk.metrics.distance import edit_distance
from nltk.tokenize import word_tokenize

def scale_criterion (criterion, scale, denominator=50):
    '''Give more leeway for longer search terms.'''
    return criterion + (scale ** 1/denominator)


def search_for_term (Text='', SearchTerm='', Transpositions=True, SubstitutionCost=0.9, Criterion=2.5, CriterionScale=False):
    '''For a search term phrase (could be single- or multi-word), find whether or not it's present within the text, subject to fuzziness of Levenshtein edit distance. If it's present then for each instance found: return the text that was found, the word index of its first word, and the Levenshtein edit distance.'''
    resultTemplate={'SearchTerm' : SearchTerm, 'Found' : False, 'Index' : None, 'Edit Distance' : None}
    results = []
    SearchTerm = word_tokenize(SearchTerm)
    SearchTermlen = len(SearchTerm)
    Text = word_tokenize(Text)
    TextLen = len(Text)
    # Maybe scale scoring to the number of words in the search term
    # if it's false then skip the next statement
    if not CriterionScale:
        ScaledCriterion = Criterion
    elif isinstance(CriterionScale, int):
        # larger numbers mean less leniency for longer queries
        ScaledCriterion = scale_criterion(Criterion, SearchTermlen)
    # A phrase could be multiword. If the first word is a single letter, then it might not matter much to the overall score of the phrase. So search for each word of the SearchTerm.
    try: 
        # If the search term is much longer than the text then punt
        if TextLen < SearchTermlen:
            results.append(resultTemplate)
            return results
        # Loop through the text
        for txt in range(0, TextLen - (SearchTermlen-1)):
            # Start saving the text in case we want to return it as a result
            thisText = Text[txt]
            # Examine the text item against the search term
            dist = edit_distance(SearchTerm[0], thisText, substitution_cost=SubstitutionCost, transpositions=Transpositions)
            # if the distance of the current word to the phrase's first word is acceptable, 
            if dist <= ScaledCriterion:
                # see if the subsequent SearchTerm words match the following text words 
                for subseqSearchTerm in range(1, SearchTermlen):
                    subseqText = Text[txt + subseqSearchTerm]
                    thisText = thisText + subseqText
                    # JIC the last word checked just happened to be at the end of the text
                    dist += edit_distance(SearchTerm[subseqSearchTerm], subseqText, substitution_cost=SubstitutionCost, transpositions=Transpositions)
                # The first SearchTerm met criterion and we've measured edit distances of the subsequent words. Does the phrase meet criterion?
                # If we've reached the end of comparing the search term to the text
                # and dist is still <= scaledCriterion
                if dist <= ScaledCriterion:
                    # The phrase meets criterion
                    thisResult = resultTemplate.copy()
                    # Verbiage found
                    thisResult['Found'] = thisText
                    # index of verbiage found
                    thisResult['Index'] = txt
                    # distance of verbiage found
                    thisResult['Edit Distance'] = dist
                    results.append(thisResult)
        # We've run to the end of the text, 
        else:
            # If we have any results already then return those,
            if len(results) > 0:
                return results
            # Else we never found the search term, so return the negative case
            else:
                results.append(resultTemplate)
                return results
    except Exception as exc:
        msg = "Error in search_for_term: " + str(exc) + ", Search Term: " + str(SearchTerm) + ", Search Term Length: " + str(SearchTermlen) + ", Search Term Iterator Value: " + str(subseqSearchTerm) + ", Text Length: " + str(TextLen)
        logging.error(msg)
    return results



