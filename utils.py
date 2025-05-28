import pickle


def save_object_to_pickle(object: str, file_path: str) -> None:
    """Save transcription object to a pickle file."""
    with open(file_path, "wb") as f:
        pickle.dump(object, f)
    print("pickle file saved")


def load_object_from_pickle(file_path: str) -> any:
    """Load transcription object from a pickle file."""
    with open(file_path, "rb") as f:
        return pickle.load(f)
