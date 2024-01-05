import pandas as pd
import re
from pathlib import Path


def compile_natural_product_data(
    directory: str, classifier_choice: str, classification_cutoff: float = None
) -> pd.DataFrame:
    """
    Compiles data from multiple text files into a single DataFrame. Each file corresponds to a different
    natural product, and the DataFrame contains probabilities for different categories based on the chosen classifier.
    Optionally discretizes the DataFrame based on a classification cutoff.

    :param directory: Directory containing the text files.
    :param classifier_choice: Classifier to use ('tree', 'logistic_regression', 'svm', 'mean').
    :param classification_cutoff: Optional cutoff for discretizing the DataFrame.
    :return: A pandas DataFrame with rows as natural products and columns as categories.
    """
    valid_classifiers = ["tree", "logistic_regression", "svm", "mean"]
    if classifier_choice not in valid_classifiers:
        raise ValueError(
            f"Invalid classifier choice. Must be one of {valid_classifiers}"
        )

    data = {}
    directory_path = Path(directory)

    for file_path in directory_path.glob("*.txt"):
        df = parse_activity_classifier_file(file_path)

        # Extract the classifier's data
        if classifier_choice != "mean":
            classifier_column = f"{classifier_choice}_classifier"
            data[file_path.stem] = df[classifier_column]
        else:
            # Compute the mean across all classifiers
            data[file_path.stem] = df.mean(axis=1)

    result_df = pd.DataFrame(data).transpose()
    if classification_cutoff is not None:
        result_df = (result_df >= classification_cutoff).astype(int)

    return result_df


def parse_activity_classifier_file(file_path: Path) -> pd.DataFrame:
    """
    Parses a text file containing activity and classifier data into a pandas DataFrame.

    The file should have a structure similar to:
    "probabilities of [activity]:
    [classifier]: [probability] [classifier]: [probability] ..."

    :param file_path: Path to the text file to be parsed.
    :return: A pandas DataFrame with the parsed data.
    """
    with open(file_path, "r") as file:
        text = file.read()

    sections = re.split(r"probabilities of ([\w\s-]+) activity:", text)
    sections = [s.strip() for s in sections if s.strip()]

    data = {}
    for i in range(0, len(sections), 2):
        activity = sections[i].replace(" or ", "_").replace(" ", "_").lower()
        classifier_data = sections[i + 1]

        # Extract classifier and its probability
        classifiers = re.findall(r"(\w+ [\w\s]+): ([0-9.]+)", classifier_data)
        for classifier, probability in classifiers:
            classifier = classifier.replace(" ", "_").lower()
            probability = float(probability)

            # Populate the dictionary
            if classifier not in data:
                data[classifier] = {}
            data[classifier][activity] = probability
    return pd.DataFrame(data)


from pathlib import Path
import shutil


def flatten_input_directory(
    src_directory: Path, dest_directory: Path, file_extension: str
) -> None:
    """
    Copy files with a specific extension from a source directory (including subdirectories)
    to a destination directory using pathlib.

    Args:
    src_directory (Path): Source directory to search for files.
    dest_directory (Path): Destination directory to copy files to.
    file_extension (str): File extension to filter files to be copied.
    """
    dest_directory.mkdir(parents=True, exist_ok=True)

    for file_path in src_directory.rglob(f"*{file_extension}"):
        dest_file_path = dest_directory / file_path.name
        shutil.copy2(file_path, dest_file_path)
        # print(f"Copied: {file_path} -> {dest_file_path}")
