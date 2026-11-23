import pytest
from pydantic import ValidationError

from schemas import IndexRequest, ChatRequest


class TestVideoIdValidation:
    """Test VideoId validation on both request models."""

    VALID_ID = "dQw4w9WgXcQ"
    VALID_IDS = [
        "dQw4w9WgXcQ",
        "abcdefghijk",
        "ABCDEFGHIJK",
        "01234567890",
        "abc_def-ghi",
        "___---___--",
    ]

    INVALID_IDS = [
        ("../x", "path traversal"),
        ("", "empty string"),
        ("short", "too short"),
        ("012345678901", "too long"),
        ("abc def ghi", "space"),
        ("abc/def/ghi", "slash"),
        ("abc.def.ghi", "dot"),
        ("abc@def#ghi", "special chars"),
        ("abcdéfghijk", "unicode"),
        ("a/../../b/c", "11 chars with slashes"),
    ]

    def test_valid_ids_index_request(self):
        """Valid YouTube IDs should be accepted by IndexRequest."""
        for vid in self.VALID_IDS:
            req = IndexRequest(video_id=vid)
            assert req.video_id == vid

    def test_valid_ids_chat_request(self):
        """Valid YouTube IDs should be accepted by ChatRequest."""
        for vid in self.VALID_IDS:
            req = ChatRequest(video_id=vid, query="test")
            assert req.video_id == vid

    def test_invalid_ids_index_request(self):
        """Invalid IDs should raise ValidationError for IndexRequest."""
        for vid, desc in self.INVALID_IDS:
            with pytest.raises(ValidationError) as exc_info:
                IndexRequest(video_id=vid)
            assert "video_id" in str(exc_info.value)

    def test_invalid_ids_chat_request(self):
        """Invalid IDs should raise ValidationError for ChatRequest."""
        for vid, desc in self.INVALID_IDS:
            with pytest.raises(ValidationError) as exc_info:
                ChatRequest(video_id=vid, query="test")
            assert "video_id" in str(exc_info.value)


class TestChatRequestFields:
    """Test other ChatRequest fields still work."""

    def test_optional_fields_default(self):
        req = ChatRequest(video_id="dQw4w9WgXcQ", query="test")
        assert req.current_time is None
        assert req.session_id is None

    def test_optional_fields_provided(self):
        req = ChatRequest(video_id="dQw4w9WgXcQ", query="test", current_time=10.5, session_id="sess123")
        assert req.current_time == 10.5
        assert req.session_id == "sess123"

    def test_session_id_max_length(self):
        with pytest.raises(ValidationError):
            ChatRequest(video_id="dQw4w9WgXcQ", query="test", session_id="x" * 65)

    def test_session_id_max_length_valid(self):
        req = ChatRequest(video_id="dQw4w9WgXcQ", query="test", session_id="x" * 64)
        assert len(req.session_id) == 64