# Fuzzy Booth
# Search a document for a substring, but with Levenshtein edit distance fuzzy-matching.

import logging
from nltk.metrics.distance import edit_distance

def scale_criterion (criterion, scale, denominator=50):
    '''Give more leeway for longer search terms.'''
    return criterion + (scale ** 1/denominator)


def search_for_term (Text='', SearchTerm = '', Transpositions = True, SubstitutionCost = 0.9, Criterion = 2.5, CriterionScale = False):
    '''For a search term phrase (could be single- or multi-word), find whether or not it's present within the text, subject to fuzziness of Levenshtein edit distance. If it's present then for each instance found: return the text that was found, the word index of its first word, and the Levenshtein edit distance.'''
    resultTemplate={'SearchTerm' : SearchTerm, 'Found' : False, 'Index' : None, 'Distance' : None}
    results = []
    SearchTermlen = len(SearchTerm)
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
        if len(Text) < SearchTermlen:
            results.append(resultTemplate)
            return results
        # Loop through the text
        for txt in range(0, len(Text) - (SearchTermlen-1)):
            # Examine the text item against the search term
            dist = edit_distance(SearchTerm[0], Text[txt], substitution_cost=SubstitutionCost, transpositions=Transpositions)
            # if the distance of the current word to the phrase's first word is acceptable, 
            if dist <= scaledCrit:
                # Start saving the text in case we want to return it as a result
                thisText = Text[txt]
                # see if the subsequent SearchTerm words match the following text words 
                for subseqSearchTerm in range(1, SearchTermlen):
                    thisText = thisText + Text[txt + subseqSearchTerm]
                    # JIC the last word checked just happened to be at the end of the text
                    dist += edit_distance(SearchTerm[subseqSearchTerm], Text[txt + subseqSearchTerm], substitution_cost=SubstitutionCost, transpositions=Transpositions)
                # The first SearchTerm met criterion and we've measured edit distances of the subsequent words. Does the phrase meet criterion?
                # If we've reached the end of comparing the search term to the text
                # and dist is still <= scaledCriterion
                if dist <= ScaledCriterion:
                    # The phrase meets criterion
                    thisResult = resultTemplate
                    # Verbiage found
                    thisResult['Found'] = thisText
                    # index of verbiage found
                    thisResult['Index'] = txt
                    # distance of verbiage found
                    thisResult['Distance'] = dist
                    results.append(thisResult)
        # We've run to the end of the text, so return negative result
        else:
            results.append(resultTemplate)
            return results
    except Exception as exc:
        msg = "Error in search_for_term: " + str(exc) + ", Search Term: " + str(SearchTerm) + ", Search Term Length: " + str(SearchTermlen) + ", Search Term Iterator Value: " + str(subseqSearchTerm) + ", Text Length: " + str(len(Text))
        logging.error(msg)
    return results



