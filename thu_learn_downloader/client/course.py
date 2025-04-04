from collections.abc import Sequence
from typing import Any

from pydantic import Field
from requests import Response

from . import url
from .client import MAX_SIZE, Client
from .document import Document, DocumentClass
from .homework import Homework
from .model import BaseModel


class Course(BaseModel):
    client: Client = Field(exclude=True)
    id: str = Field(alias="wlkcid")
    chinese_name: str = Field(alias="kcm")
    course_number: str = Field(alias="kch")
    english_name: str = Field(alias="ywkcm")
    name: str = Field(alias="zywkcm")
    teacher_name: str = Field(alias="jsm")
    teacher_number: str = Field(alias="jsh")

    @property
    def document_classes(self) -> Sequence[DocumentClass]:
        
        response = self.client.get_with_token(
        url=url.make_url(path="/b/wlxt/kj/wlkc_kjflb/student/pageList"),
        params={"wlkcid": self.id}
        )

        try:
            data = response.json()
        except ValueError:
            print(f"[ERROR] Invalid JSON response for course {self.id}. Skipping...")
            return []  # Skip if response is not JSON

        if not isinstance(data, dict) or "object" not in data or not data["object"]:
            print(f"[WARNING] Skipping course {self.id}: No document data available.")
            return []  # Skip if 'object' is missing or None

        if data.get("result") == "error":
            print(f"[WARNING] Skipping course {self.id}: {data.get('msg', 'Unknown error')}")
            return []  # Skip if permission denied
        
        return [DocumentClass(client=self.client, **result) for result in data["object"]["rows"]]

    @property
    def documents(self) -> Sequence[Document]:
        try:
            response = self.client.get_with_token(
                url=url.make_url(
                    path="/b/wlxt/kj/wlkc_kjxxb/student/kjxxbByWlkcidAndSizeForStudent"
                ),
                params={"wlkcid": self.id, "size": MAX_SIZE},
            )
            data = response.json()
        except Exception as e:
            print(f"[ERROR] Failed to fetch documents for course {self.id}: {e}")
            return []  # Return empty list to avoid crash

        # Ensure 'object' exists and is iterable
        if not isinstance(data, dict) or "object" not in data or not isinstance(data["object"], list):
            print(f"[WARNING] No valid documents for course {self.id}. Skipping...")
            return []

        # Convert to Document objects and sort
        documents: Sequence[Document] = [
            Document(client=self.client, **result) for result in data["object"]
        ]
        documents.sort(key=lambda document: document.title)
        documents.sort(key=lambda document: document.upload_time)

        return documents


    @property
    def homeworks(self) -> Sequence[Homework]:
        return [
            *self._homeworks_at_url(
                url=url.make_url(
                    path="/b/wlxt/kczy/zy/student/index/zyListWj",
                    query={"wlkcid": self.id, "size": MAX_SIZE},
                ),
            ),
            *self._homeworks_at_url(
                url=url.make_url(
                    path="/b/wlxt/kczy/zy/student/index/zyListYjwg",
                    query={"wlkcid": self.id, "size": MAX_SIZE},
                ),
            ),
            *self._homeworks_at_url(
                url=url.make_url(
                    path="/b/wlxt/kczy/zy/student/index/zyListYpg",
                    query={"wlkcid": self.id, "size": MAX_SIZE},
                ),
            ),
        ]

    def _homeworks_at_url(self, url: str) -> Sequence[Homework]:
        resp: Response = self.client.get_with_token(url=url)
        json: dict[str, Any] = resp.json()
        results: Sequence[dict[str, Any]] = json["object"]["aaData"] or []
        return [
            Homework.from_json(client=self.client, json=result) for result in results
        ]
