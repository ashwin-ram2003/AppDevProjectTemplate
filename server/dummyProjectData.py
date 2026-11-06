"""Temporary project storage used until the shared MongoDB is available."""

from copy import deepcopy
from types import SimpleNamespace


DUMMY_PROJECTS = [
    {
        "projectName": "Demo Project",
        "projectId": "demo-project",
        "description": "Sample project for local development.",
        "hwSets": {},
        "users": [],
    },
]


class InMemoryProjectCollection:
    """Small writable subset of the PyMongo collection API.

    Data lives only as long as the server process, so restarting Flask resets
    it to DUMMY_PROJECTS.
    """

    def __init__(self, documents):
        self._documents = deepcopy(documents)

    @staticmethod
    def _field_matches(actual, expected):
        """Match one field the way MongoDB does for the operators we use."""
        if isinstance(expected, dict) and "$ne" in expected:
            target = expected["$ne"]
            # For lists, {"$ne": x} means "x is not in the list".
            if isinstance(actual, list):
                return target not in actual
            return actual != target
        # For lists, a plain value means "x is in the list", like MongoDB.
        if isinstance(actual, list) and not isinstance(expected, (list, dict)):
            return expected in actual

        return actual == expected

    def _matches(self, document, query):
        """True if every field in the query matches this document."""
        return all(
            self._field_matches(document.get(key), value)
            for key, value in query.items()
        )
    
    def find(self, query):
        return [
            deepcopy(document)
            for document in self._documents
                if self._matches(document, query)
        ]

    def find_one(self, query):
        matches = self.find(query)
        return matches[0] if matches else None

    def insert_one(self, document):
        self._documents.append(deepcopy(document))

    def update_one(self, query, update):
        """Apply a $addToSet update to the first matching document.
        
        Return as object with matched_count and modified_count, like
        PyMongo's UpdateResult, so caller can tell what happened."""

        for document in self._documents:
            if self._matches(document, query):
                modified = 0
                for field, value in update.get("$addToSet", {}).items():
                    values = document.setdefault(field, [])
                    if value not in values:
                        values.append(value)
                        modified = 1
                return SimpleNamespace(matched_count=1, modified_count=modified)
        return SimpleNamespace(matched_count=0, modified_count=0)
        