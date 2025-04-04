from pathlib import Path

from thu_learn_downloader.client.course import Course
from thu_learn_downloader.client.document import Document, DocumentClass
from thu_learn_downloader.client.homework import Attachment, Homework
from thu_learn_downloader.client.semester import Semester


def document(
    prefix: Path,
    semester: Semester,
    course: Course,
    document_class: DocumentClass,
    document_content: Document,
    index: int,
) -> Path:
    filename: Path = (
        prefix
        / semester.id
        / course.name
        / "docs"
        / document_class.title
        / f"{index:02d}-{document_content.title}".replace("/", "-slash-")
    )
    if document_content.file_type:
        filename = filename.with_suffix("." + document_content.file_type)
    return filename


def homework(
    prefix: Path, semester: Semester, course: Course, homework_content: Homework
) -> Path:
    return (
        prefix
        / semester.id
        / course.name
        / "work"
        / f"{homework_content.number:02d}-{homework_content.title}".replace("/", "-slash-")
        / "README.md"
    )


def attachment(
    prefix: Path,
    semester: Semester,
    course: Course,
    homework_content: Homework,
    attachment_content: Attachment,
) -> Path:
    filename: Path = Path(attachment_content.name)
    filename = filename.with_stem(
        f"{homework_content.number:02d}-{homework_content.title}-{attachment_content.type_}".replace(
            "/", "-slash-"
        )
    )
    return (
        prefix
        / semester.id
        / course.name
        / "work"
        / f"{homework_content.number:02d}-{homework_content.title}".replace("/", "-slash-")
        / filename
    )
