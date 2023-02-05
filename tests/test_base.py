"""Tests for the base class."""


def test_threads(main_class):
    """Tests caluclation of threads."""
    import os

    from czds.base import Base

    assert Base().THREAD_COUNT == os.cpu_count() * 5


def test_chunk(main_class):
    """Tests chunk method."""
    from czds.base import Base

    sample_list = ["1", "2", "3", "4"]
    chunked_lists = Base()._chunk(items=sample_list, chunk_size=1)
    for item in chunked_lists:
        assert isinstance(item, list)
