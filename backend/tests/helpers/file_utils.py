"""File handling utilities for testing."""

import io
import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, BinaryIO, Dict, Generator, List, Optional, Tuple, Union

from fastapi import UploadFile
from fastapi.datastructures import Headers
from starlette.datastructures import UploadFile as StarletteUploadFile


class TestFile:
    """A test file that can be used for file upload testing."""

    def __init__(
        self,
        content: Union[bytes, str],
        filename: str = "test.txt",
        content_type: str = "text/plain",
    ):
        """Initialize a test file.

        Args:
            content: File content as bytes or string
            filename: Name of the file
            content_type: MIME type of the file
        """
        self.filename = filename
        self.content_type = content_type

        if isinstance(content, str):
            self.content = content.encode("utf-8")
        else:
            self.content = content

    @property
    def size(self) -> int:
        """Get the size of the file content in bytes."""
        return len(self.content)

    def to_upload_file(self) -> UploadFile:
        """Convert to a FastAPI UploadFile."""
        file = io.BytesIO(self.content)

        # Create a Starlette UploadFile
        upload_file = StarletteUploadFile(
            filename=self.filename,
            file=file,
            headers=Headers({"content-type": self.content_type}),
        )

        # Convert to FastAPI UploadFile
        return UploadFile(
            filename=upload_file.filename,
            file=upload_file.file,
            headers=upload_file.headers,
        )

    def to_dict(self, field_name: str = "file") -> Dict[str, Any]:
        """Convert to a dictionary for use with TestClient."""
        return {field_name: (self.filename, self.content, self.content_type)}

    def save(self, path: Union[str, Path]) -> None:
        """Save the file to the specified path."""
        with open(path, "wb") as f:
            f.write(self.content)

    @classmethod
    def from_file(cls, path: Union[str, Path], **kwargs) -> "TestFile":
        """Create a TestFile from a file on disk.

        Args:
            path: Path to the file
            **kwargs: Additional arguments to pass to TestFile

        Returns:
            A TestFile instance
        """
        path = Path(path)
        with open(path, "rb") as f:
            content = f.read()

        if "filename" not in kwargs:
            kwargs["filename"] = path.name

        return cls(content, **kwargs)

    def __eq__(self, other: Any) -> bool:
        """Check if two TestFiles are equal."""
        if not isinstance(other, TestFile):
            return False

        return (
            self.filename == other.filename
            and self.content == other.content
            and self.content_type == other.content_type
        )


@contextmanager
def temp_directory() -> Generator[Path, None, None]:
    """Create a temporary directory that is automatically cleaned up.

    Yields:
        Path to the temporary directory
    """
    temp_dir = tempfile.mkdtemp()
    try:
        yield Path(temp_dir)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def create_test_file(
    content: Union[bytes, str],
    filename: str = "test.txt",
    content_type: str = "text/plain",
) -> TestFile:
    """Create a test file.

    Args:
        content: File content as bytes or string
        filename: Name of the file
        content_type: MIME type of the file

    Returns:
        A TestFile instance
    """
    return TestFile(content, filename, content_type)


def create_test_image(
    width: int = 100,
    height: int = 100,
    format: str = "png",
    filename: Optional[str] = None,
) -> TestFile:
    """Create a test image file.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        format: Image format (png, jpg, gif)
        filename: Optional filename (defaults to 'test.{format}')

    Returns:
        A TestFile instance with the image data
    """
    from PIL import Image, ImageDraw

    # Create a simple image
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Draw a simple pattern
    for x in range(0, width, 10):
        draw.line([(x, 0), (x, height)], fill="#f0f0f0")
    for y in range(0, height, 10):
        draw.line([(0, y), (width, y)], fill="#f0f0f0")

    # Add some text
    draw.text((10, 10), "Test Image", fill="black")

    # Save to bytes
    buffer = io.BytesIO()
    image.save(buffer, format=format.upper())

    # Determine content type
    content_type = f"image/{format}"

    # Set filename if not provided
    if filename is None:
        filename = f"test.{format}"

    return TestFile(
        content=buffer.getvalue(), filename=filename, content_type=content_type
    )


def create_test_zip(
    files: List[Tuple[str, Union[bytes, str]]], filename: str = "test.zip"
) -> TestFile:
    """Create a test zip file.

    Args:
        files: List of (filename, content) tuples
        filename: Name of the zip file

    Returns:
        A TestFile instance with the zip data
    """
    import zipfile

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        for name, content in files:
            if isinstance(content, str):
                content = content.encode("utf-8")
            zf.writestr(name, content)

    return TestFile(
        content=buffer.getvalue(), filename=filename, content_type="application/zip"
    )


def assert_files_equal(
    file1: Union[str, Path, BinaryIO, bytes],
    file2: Union[str, Path, BinaryIO, bytes],
    msg: Optional[str] = None,
) -> None:
    """Assert that two files have the same content.

    Args:
        file1: First file (path, file-like object, or bytes)
        file2: Second file (path, file-like object, or bytes)
        msg: Optional error message

    Raises:
        AssertionError: If the files are not equal
    """

    def read_file(f):
        if isinstance(f, (str, Path)):
            with open(f, "rb") as fp:
                return fp.read()
        elif hasattr(f, "read"):
            pos = f.tell()
            content = f.read()
            f.seek(pos)
            return content
        elif isinstance(f, bytes):
            return f
        else:
            raise TypeError(f"Unsupported file type: {type(f)}")

    content1 = read_file(file1)
    content2 = read_file(file2)

    if content1 != content2:
        if msg is None:
            msg = "Files are not equal"
        raise AssertionError(msg)


def assert_directories_equal(
    dir1: Union[str, Path], dir2: Union[str, Path], ignore: Optional[List[str]] = None
) -> None:
    """Assert that two directories have the same content.

    Args:
        dir1: Path to first directory
        dir2: Path to second directory
        ignore: Optional list of file patterns to ignore

    Raises:
        AssertionError: If the directories are not equal
    """
    import fnmatch

    dir1 = Path(dir1)
    dir2 = Path(dir2)

    if ignore is None:
        ignore = []

    # Check that both paths are directories
    if not dir1.is_dir() or not dir2.is_dir():
        raise AssertionError(f"Both paths must be directories: {dir1}, {dir2}")

    # Get all files in both directories
    files1 = set()
    for root, _, files in os.walk(dir1):
        rel_root = Path(root).relative_to(dir1)
        for f in files:
            rel_path = rel_root / f
            # Skip ignored files
            if not any(fnmatch.fnmatch(str(rel_path), pattern) for pattern in ignore):
                files1.add(rel_path)

    files2 = set()
    for root, _, files in os.walk(dir2):
        rel_root = Path(root).relative_to(dir2)
        for f in files:
            rel_path = rel_root / f
            # Skip ignored files
            if not any(fnmatch.fnmatch(str(rel_path), pattern) for pattern in ignore):
                files2.add(rel_path)

    # Check for missing files
    missing_in_2 = files1 - files2
    if missing_in_2:
        raise AssertionError(f"Files missing in second directory: {missing_in_2}")

    missing_in_1 = files2 - files1
    if missing_in_1:
        raise AssertionError(f"Extra files in second directory: {missing_in_1}")

    # Check file contents
    for rel_path in files1:
        file1 = dir1 / rel_path
        file2 = dir2 / rel_path

        try:
            assert_files_equal(file1, file2, f"Files differ: {rel_path}")
        except AssertionError as e:
            raise AssertionError(f"Files differ: {rel_path}") from e


def create_temp_file(
    content: Union[bytes, str] = b"",
    suffix: str = "",
    prefix: str = "tmp",
    dir: Optional[Union[str, Path]] = None,
    text: bool = False,
) -> Path:
    """Create a temporary file with the given content.

    Args:
        content: File content as bytes or string
        suffix: File suffix (e.g., '.txt')
        prefix: File prefix
        dir: Directory to create the file in (defaults to system temp dir)
        text: If True, open in text mode

    Returns:
        Path to the created file
    """
    mode = "w" if text else "wb"

    if isinstance(content, str) and not text:
        content = content.encode("utf-8")

    with tempfile.NamedTemporaryFile(
        mode=mode, suffix=suffix, prefix=prefix, dir=dir, delete=False
    ) as f:
        f.write(content)
        return Path(f.name)
