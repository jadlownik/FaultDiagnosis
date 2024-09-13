import pandas as pd


def normalize_elements(element):
    groups = element.split('\n')
    normalized_groups = [sorted(g.strip().split(', ')) for g in groups]
    return sorted(normalized_groups, key=lambda x: x[0] if x else '')


def calculate_rowwise_common_elements(file_path, column1, column2):
    df = pd.read_csv(file_path, delimiter=';')

    df['Normalized1'] = df[column1].astype(str).apply(normalize_elements)
    df['Normalized2'] = df[column2].astype(str).apply(normalize_elements)

    df['CountNormalized1'] = df['Normalized1'].apply(lambda x: len(x))
    df['CountNormalized2'] = df['Normalized2'].apply(lambda x: len(x))

    def count_common_groups(groups1, groups2):
        common_count = 0
        set_groups1 = set(tuple(g) for g in groups1)
        for g in groups2:
            if tuple(g) in set_groups1:
                common_count += 1
        return common_count

    df['CommonElements'] = df.apply(lambda row: count_common_groups(row['Normalized1'], row['Normalized2']), axis=1)
    df['IncorrectlyGenerated'] = df['CountNormalized2'] - df['CommonElements']
    df['CommonPercentage'] = (df['CommonElements'] / df['CountNormalized1']) * 100

    return df[['CountNormalized1', 'CountNormalized2', 'CommonElements', 'IncorrectlyGenerated', 'CommonPercentage']]


file_path = r'.\results\results_minimal_diagnoses_examples_approach_1_attempt_2_overwrite.csv'
column1 = 'Minimal diagnosis'
column2 = 'Minimal diagnosis - GPT'

result_df = calculate_rowwise_common_elements(file_path, column1, column2)
output_file_path = r'.\results\results_analysis222.csv'
result_df.to_csv(output_file_path, sep=';', index=False)
