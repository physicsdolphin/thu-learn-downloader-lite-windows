from thu_learn_downloader.client.course import Course
from thu_learn_downloader.client.document import Document, DocumentClass
from thu_learn_downloader.client.homework import Attachment, Homework
from thu_learn_downloader.client.semester import Semester


def document(
    semester: Semester,
    course: Course,
    document_class: DocumentClass,
    document_content: Document,
    index: int,
) -> str:
    filename: str = f"{index:02d}-{document_content.title}"
    if document_content.file_type:
        filename += "." + document_content.file_type
    return f"{course.name} > {filename}"


def attachment(
    semester: Semester, course: Course, homework: Homework, attachment_content: Attachment
) -> str:
    return (
        f"{course.name} > {homework.number:02d}-{homework.title} > {attachment_content.type_}"
    )
