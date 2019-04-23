import pandas
from collections import defaultdict, Counter

def compute_stats_about(le_objs, attributes, verbose=0):
    """
    compute stats about the provided attributes
    
    :param list le_objs: list of rbn_classes.LE object
    :param set attributes: set of attributes to use in descriptive statistics
    :param
    :rtype: dict
    :return: {
     'count': number of observations
     '# of unique observations' : number of unique observations,
     'freq_dist': frequency distribution,
     'freq_dist_df' : frequency distribution as pandas dataframe
    }
    """
    observations = []
    
    for le_obj in le_objs:
        observation = [getattr(le_obj, attr)
                       for attr in attributes]
        observations.append(tuple(observation))
        

    
    freq_dist = Counter(observations)
    
    headers = ['-'.join(attributes), 
               'frequency']
    list_of_lists = [[key, freq]
                     for key, freq  in freq_dist.items()]
    df = pandas.DataFrame(list_of_lists, columns=headers)
    
    
    if verbose:
        print(f'chosen attributes: {attributes}')

        
    stats = {
        'count' : len(observations),
        '# of unique observations' : len(set(observations)),
        'freq_dist' : freq_dist,
        'freq_dist_df' : df.sort_values('frequency', ascending=False)
    }
    return stats


def load_mapping(path):
    
    df = pandas.read_excel(path, sheet_name='the_mapping')
    
    rbn_featureset2frames = dict()
    for index, row in df.iterrows():
        rbn_info = row['RBN feature set']
        frames = row['English FrameNet frames']
        frames = frames.split(',')

        rbn_featureset2frames[rbn_info] = frames

    return rbn_featureset2frames


def get_translations_from_wiktionary(path, verbose=0):
    """
    path to translations in csv
    (resources/wiktionary/translations.tsv)

    :param str path: the path to translations

    :rtype: tuple
    :return: (en to nl, nl to en)
    """
    path = 'resources/wiktionary/translations.tsv'
    df = pandas.read_csv(path, sep='\t', usecols=['ID', 'Concept_ID', 'Concept', 'Languoid', 'Language_name', 'Form'])

    if verbose:
        print()
        print(f'number of available languages: {len(set(df.Language_name))}')

    if verbose:
        print()
        print('languages that have Dutch in the name')
        for language in set(df.Language_name):
            if 'Dutch' in language:
                print(language)
        print('we use only: "Dutch; Flemish"')

    df = df[df.Language_name == 'Dutch; Flemish']

    english_lemmas = []
    english_definitions = []

    for index, row in df.iterrows():
        concept = row['Concept']
        lemma, *definitions = concept.split('/')
        english_lemmas.append(lemma)
        english_definitions.append('/'.join(definitions))
    df['English_lemma'] = english_lemmas

    dutch2english = defaultdict(set)
    english2dutch = defaultdict(set)

    for index, row in df.iterrows():
        english_lemma = row['English_lemma']
        dutch_lemma = row['Form']
        dutch2english[dutch_lemma].add(english_lemma)
        english2dutch[english_lemma].add(dutch_lemma)

    return dutch2english, english2dutch