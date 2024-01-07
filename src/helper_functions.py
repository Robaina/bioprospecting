from __future__ import annotations
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


def parse_metadata(metadata_path: Path) -> dict:
    """
    Parses the metadata information from a file.
    Returns a dictionary mapping seq_id to a dictionary of metadata.
    """
    metadata = {}
    with metadata_path.open("r") as file:
        next(file)  # Skip the header line
        for line in file:
            parts = line.strip().split("\t")
            seq_id = parts[0]
            metadata[seq_id] = {
                "function": parts[1],
                "taxonomy": parts[2],
                "novelty": float(parts[3]),
                "gcf_id": int(parts[4]),
            }
    return metadata


def parse_correspondence(correspondence_path: Path) -> dict[str, str]:
    """
    Parses the correspondence information from a file.
    Returns a dictionary mapping old identifiers to new identifiers.
    """
    correspondence = {}
    with correspondence_path.open("r") as file:
        for line in file:
            old_id, new_id = line.strip().split("\t")
            correspondence[old_id] = new_id
    return correspondence


def assign_metadata_to_bgcs(
    bgcs_with_activity: list[str],
    metadata: dict[str, dict[str, str]],
    correspondence: dict[str, str],
) -> pd.DataFrame:
    """
    Assigns metadata to BGCs based on their new identifiers provided in a list.
    Returns a pandas DataFrame with metadata entries for the BGCs with activity,
    with the 'new_id' as the index of the DataFrame.
    """
    # Prepare a list to collect metadata entries
    metadata_entries = []

    # Invert the correspondence dictionary to map new identifiers to old identifiers
    inv_correspondence = {v: k for k, v in correspondence.items()}

    # Iterate over the list of BGC identifiers with activity
    for bgc_id in bgcs_with_activity:
        bgc_id_cleaned = bgc_id.split(".")[0]  # Remove the '.region001' part
        old_id = inv_correspondence.get(bgc_id_cleaned)

        if old_id and old_id in metadata:
            # Append a new dictionary that combines the metadata with the new_id
            metadata_entries.append({**metadata[old_id], "new_id": bgc_id_cleaned})
        else:
            metadata_entries.append(
                {"error": "Identifier not found", "new_id": bgc_id_cleaned}
            )

    df = pd.DataFrame(metadata_entries)
    df.set_index("new_id", inplace=True)

    return df
