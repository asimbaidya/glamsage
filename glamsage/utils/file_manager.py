import os
import uuid
from datetime import datetime


def generate_unique_filename(original_filename):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_string = str(uuid.uuid4().hex)[
        :6
    ]  # Use the first 6 characters of a random UUID
    _, file_extension = os.path.splitext(original_filename)
    unique_filename = f"{timestamp}_{random_string}{file_extension}"
    return unique_filename
