"""Tests for the API key pool: loading, round-robin, load balancing, errors."""

from src.core.api_pool import APIKeyInfo, APIKeyPool


def test_add_key_skips_blank_and_commented():
    pool = APIKeyPool()
    pool.add_key("sk-real")
    pool.add_key("   ")  # blank -> skipped
    pool.add_key("")  # empty -> skipped
    pool.add_key("# commented-out key")  # comment -> skipped
    assert pool.total_count == 1
    assert pool.keys[0].key == "sk-real"


def test_add_key_strips_whitespace():
    pool = APIKeyPool()
    pool.add_key("  sk-padded  ")
    assert pool.keys[0].key == "sk-padded"


def test_round_robin_cycles_through_active_keys():
    pool = APIKeyPool()
    for k in ("a", "b", "c"):
        pool.add_key(k)
    assert [pool.get_next_key().key for _ in range(4)] == ["a", "b", "c", "a"]


def test_get_next_key_returns_none_when_no_active_keys():
    pool = APIKeyPool()
    assert pool.get_next_key() is None
    pool.add_key("a")
    pool.keys[0].is_active = False
    assert pool.get_next_key() is None


def test_key_disabled_after_three_consecutive_errors():
    info = APIKeyInfo(key="sk-x", provider="openai")
    info.mark_error()
    info.mark_error()
    assert info.is_active is True  # only two so far
    info.mark_error()
    assert info.is_active is False  # the third trips the limit


def test_success_resets_consecutive_error_count():
    # The disable rule is documented as "3 consecutive errors", so a success in
    # between must clear the streak: two errors, a success, then two more errors
    # should leave the key active rather than disabling it on a lifetime total.
    info = APIKeyInfo(key="sk-x", provider="openai")
    info.mark_error()
    info.mark_error()
    info.mark_used()  # success clears the streak
    info.mark_error()
    info.mark_error()
    assert info.is_active is True
    assert info.errors == 2


def test_least_used_key_prefers_fewest_calls():
    pool = APIKeyPool()
    pool.add_key("a")
    pool.add_key("b")
    pool.keys[0].mark_used()
    pool.keys[0].mark_used()  # "a" used twice
    pool.keys[1].mark_used()  # "b" used once
    assert pool.get_least_used_key().key == "b"


def test_get_keys_for_parallel_cycles_when_count_exceeds_pool():
    pool = APIKeyPool()
    pool.add_key("a")
    pool.add_key("b")
    keys = pool.get_keys_for_parallel(5)
    assert [k.key for k in keys] == ["a", "b", "a", "b", "a"]


def test_active_and_total_counts():
    pool = APIKeyPool()
    pool.add_key("a")
    pool.add_key("b")
    pool.keys[1].is_active = False
    assert pool.total_count == 2
    assert pool.active_count == 1
