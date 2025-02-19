import pandas as pd
import os


def normalize_elements(element):
    """Funkcja normalizuje wartości w kolumnach, obsługując poprawnie puste wartości"""
    if pd.isna(element) or not isinstance(element, str) or element.strip() == "":
        return []  # Zwracamy pustą listę, jeśli wartość jest NaN, None lub pusta

    groups = element.strip().split(
        "\n"
    )  # Usuwamy zbędne spacje i dzielimy po nowej linii
    normalized_groups = [sorted(g.strip().split(", ")) for g in groups if g.strip()]
    return sorted(normalized_groups, key=lambda x: x[0] if x else '')


def calculate_rowwise_common_elements(file_path, column1, column2):
    df = pd.read_csv(
        file_path, delimiter=";", dtype=str
    )  # Wczytujemy wszystko jako stringi
    df = df.fillna("")  # Zamieniamy NaN na pusty string

    df["Normalized1"] = df[column1].apply(normalize_elements)
    df["Normalized2"] = df[column2].apply(normalize_elements)

    df["CountNormalized1"] = df["Normalized1"].apply(
        lambda x: len(x) if isinstance(x, list) else 0
    )
    df["CountNormalized2"] = df["Normalized2"].apply(
        lambda x: len(x) if isinstance(x, list) else 0
    )

    def count_common_groups(groups1, groups2):
        if not groups1 or not groups2:
            return 0
        set_groups1 = set(tuple(g) for g in groups1)
        return sum(1 for g in groups2 if tuple(g) in set_groups1)

    df['CommonElements'] = df.apply(lambda row: count_common_groups(row['Normalized1'], row['Normalized2']), axis=1)
    df["IncorrectlyGenerated"] = df["CountNormalized2"] - df["CommonElements"]

    df["CommonPercentage"] = df.apply(
        lambda row: (
            1
            if row["CountNormalized1"] == 0 and row["CountNormalized2"] == 0
            else (
                row["CommonElements"] / row["CountNormalized1"]
                if row["CountNormalized1"] > 0
                else 0
            )
        ),
        axis=1,
    )

    columns = [col for col in df.columns if col != column2] + [column2]
    df = df[columns]

    return df[
        [
            "CountNormalized1",
            "CountNormalized2",
            "CommonElements",
            "IncorrectlyGenerated",
            "CommonPercentage",
            column2,
        ]
    ]


def process_csv_files_in_directory(input_directory, column1, column2):
    output_directory = os.path.join(input_directory, "formatted")
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    all_dfs = []

    for filename in os.listdir(input_directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(input_directory, filename)
            try:
                result_df = calculate_rowwise_common_elements(
                    file_path, column1, column2
                )

                output_file_path = os.path.join(output_directory, filename)
                result_df.to_csv(
                    output_file_path, sep=";", index=False, decimal=","
                )  # Ustawienie przecinka w CSV
                print(f"Processed file: {filename}")

                all_dfs.append(result_df)
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

    # Merge all processed DataFrames horizontally (side by side)
    final_df = pd.concat(all_dfs, axis=1)

    final_output_path = os.path.join(output_directory, "final_output.csv")
    final_df.to_csv(
        final_output_path, sep=";", index=False, decimal=","
    )  # Zapis końcowego pliku z przecinkiem
    print(f"Final merged file saved at: {final_output_path}")


# Example usage:
input_directory = r"C:\Users\jakto\Desktop\Pulpit\FaultDiagnosis\FaultDiagnosis\results_article\mso_conflicts_diagnoses\csv\MINIMAL_CONFLICTS"
column1 = "Minimal conflicts"
column2 = "Minimal conflicts - GPT"

process_csv_files_in_directory(input_directory, column1, column2)
