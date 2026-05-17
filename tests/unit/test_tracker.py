from unittest.mock import MagicMock

from wiki_cli.tracker import (
    TokenTracker,
    effective_input_tokens,
    get_tracker,
)


def make_usage(input_tokens=100, output_tokens=50, cache_create=0, cache_read=0):
    """Helper to create a mock usage object."""
    return MagicMock(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_creation_input_tokens=cache_create,
        cache_read_input_tokens=cache_read,
    )


class TestEffectiveInputTokens:
    def test_normal_input(self):
        usage = make_usage(input_tokens=500)
        assert effective_input_tokens(usage) == 500

    def test_zero_input_from_cache(self):
        usage = make_usage(input_tokens=0, cache_create=100, cache_read=400)
        assert effective_input_tokens(usage) == 500

    def test_all_fields_zero(self):
        usage = make_usage(input_tokens=0, cache_create=0, cache_read=0)
        assert effective_input_tokens(usage) == 0

    def test_input_takes_priority_over_cache(self):
        usage = make_usage(input_tokens=300, cache_create=100, cache_read=200)
        assert effective_input_tokens(usage) == 300

    def test_missing_input_attr(self):
        usage = MagicMock(spec=[])  # no attributes
        assert effective_input_tokens(usage) == 0

    def test_none_values(self):
        usage = make_usage(input_tokens=None, output_tokens=50)
        # getattr with None → 0 per the `or 0` logic
        assert effective_input_tokens(usage) == 0


class TestTokenTracker:
    def test_record_single_usage(self):
        t = TokenTracker()
        t.record(make_usage(input_tokens=100, output_tokens=50), "claude-sonnet-4-6")
        assert len(t.usages) == 1
        assert t.usages[0].input_tokens == 100
        assert t.usages[0].output_tokens == 50

    def test_record_multiple_usages(self):
        t = TokenTracker()
        t.record(make_usage(100, 50), "claude-sonnet-4-6")
        t.record(make_usage(200, 80), "claude-opus-4-7")
        assert len(t.usages) == 2

    def test_record_preserves_phase(self):
        t = TokenTracker()
        t._current_phase = "test-phase"
        t.record(make_usage(), "claude-sonnet-4-6")
        assert t.usages[0].phase == "test-phase"

    def test_phase_context_manager(self):
        t = TokenTracker()
        with t.phase("convert.extract"):
            assert t._current_phase == "convert.extract"
            t.record(make_usage(), "claude-sonnet-4-6")
        assert t._current_phase == "unknown"
        assert t.usages[0].phase == "convert.extract"

    def test_phase_restores_on_exception(self):
        t = TokenTracker()
        try:
            with t.phase("risky-phase"):
                t._current_phase = "inner-change"
                raise ValueError("oops")
        except ValueError:
            pass
        assert t._current_phase == "unknown"

    def test_nested_phase(self):
        t = TokenTracker()
        with t.phase("outer"):
            assert t._current_phase == "outer"
            with t.phase("inner"):
                assert t._current_phase == "inner"
            assert t._current_phase == "outer"
        assert t._current_phase == "unknown"

    def test_usages_returns_copy(self):
        t = TokenTracker()
        t.record(make_usage(), "claude-sonnet-4-6")
        copy1 = t.usages
        copy1.clear()
        assert len(t.usages) == 1  # original unaffected

    def test_reset(self):
        t = TokenTracker()
        t.record(make_usage(), "claude-sonnet-4-6")
        t.reset()
        assert len(t.usages) == 0

    def test_report_empty(self):
        t = TokenTracker()
        assert "No token usage recorded" in t.report()

    def test_report_with_data(self):
        t = TokenTracker()
        with t.phase("test"):
            t.record(make_usage(100, 50), "claude-sonnet-4-6")
        report = t.report()
        assert "Token Usage Report" in report
        assert "test" in report
        assert "100" in report
        assert "50" in report

    def test_aggregate_correctness(self):
        t = TokenTracker()
        with t.phase("phase-a"):
            t.record(make_usage(100, 50), "claude-sonnet-4-6")
            t.record(make_usage(200, 60), "claude-sonnet-4-6")
        with t.phase("phase-b"):
            t.record(make_usage(300, 70), "claude-opus-4-7")

        phase_agg, totals = t._aggregate()
        assert phase_agg["phase-a"]["calls"] == 2
        assert phase_agg["phase-a"]["input"] == 300
        assert phase_agg["phase-a"]["output"] == 110
        assert phase_agg["phase-b"]["calls"] == 1
        assert phase_agg["phase-b"]["input"] == 300
        assert totals["calls"] == 3
        assert totals["input"] == 600
        assert totals["output"] == 180

    def test_cost_calculation_sonnet(self):
        t = TokenTracker()
        with t.phase("test"):
            t.record(make_usage(1_000_000, 1_000_000), "claude-sonnet-4-6")
        _, totals = t._aggregate()
        # Sonnet: $3.0/M input, $15.0/M output
        assert abs(totals["cost"] - 18.0) < 0.01

    def test_cost_calculation_opus(self):
        t = TokenTracker()
        with t.phase("test"):
            t.record(make_usage(1_000_000, 1_000_000), "claude-opus-4-7")
        _, totals = t._aggregate()
        # Opus 4.7: $15.0/M input, $75.0/M output
        assert abs(totals["cost"] - 90.0) < 0.01

    def test_cache_token_capping(self):
        t = TokenTracker()
        t.record(
            make_usage(input_tokens=100, cache_create=200, cache_read=200),
            "claude-sonnet-4-6",
        )
        u = t.usages[0]
        assert u.cache_creation_input_tokens <= 100
        assert u.cache_read_input_tokens + u.cache_creation_input_tokens <= 100

    def test_html_report_has_structure(self):
        t = TokenTracker()
        with t.phase("test"):
            t.record(make_usage(100, 50), "claude-sonnet-4-6")
        html = t.html_report()
        assert "<html" in html
        assert "<table" in html
        assert "test" in html
        assert "100" in html

    def test_html_report_empty(self):
        t = TokenTracker()
        assert "No token usage recorded" in t.html_report()

    def test_save_report_md(self, tmp_path):
        t = TokenTracker()
        t.record(make_usage(100, 50), "claude-sonnet-4-6")
        path = t.save_report(str(tmp_path / "report.md"))
        assert path.exists()
        content = path.read_text()
        assert "Token Usage Report" in content

    def test_save_report_html(self, tmp_path):
        t = TokenTracker()
        t.record(make_usage(100, 50), "claude-sonnet-4-6")
        path = t.save_report(str(tmp_path / "report.html"))
        assert path.exists()
        content = path.read_text()
        assert "<html" in content

    def test_thread_safety(self):
        import threading

        t = TokenTracker()
        errors = []

        def record_batch(start: int):
            try:
                for i in range(start, start + 100):
                    t.record(make_usage(i, 10), "claude-sonnet-4-6")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=record_batch, args=(i * 100,)) for i in range(10)]
        for th in threads:
            th.start()
        for th in threads:
            th.join()

        assert not errors
        assert len(t.usages) == 1000


class TestGetTracker:
    def test_singleton(self):
        t1 = get_tracker()
        t2 = get_tracker()
        assert t1 is t2

    def test_returns_token_tracker(self):
        t = get_tracker()
        assert isinstance(t, TokenTracker)
