from wiki_cli.llint import LintResult, _count_rounds


class TestLintResult:
    def test_initial_state(self):
        r = LintResult()
        assert r.errors == []
        assert r.warnings == []
        assert r.passes == []

    def test_pass_records(self):
        r = LintResult()
        r.pass_("All good")
        assert "All good" in r.passes

    def test_fail_records(self):
        r = LintResult()
        r.fail("Broken link")
        assert "Broken link" in r.errors

    def test_warn_records(self):
        r = LintResult()
        r.warn("Low connectivity")
        assert "Low connectivity" in r.warnings

    def test_format_report_structure(self):
        r = LintResult()
        r.pass_("Check A passed")
        r.fail("Check B failed")
        r.warn("Check C warning")
        report = r.format_report()
        assert "LLM Wiki Lint Report" in report
        assert "[PASS] Check A passed" in report
        assert "[FAIL] Check B failed" in report
        assert "[WARN] Check C warning" in report
        assert "Errors: 1, Warnings: 1, Passes: 1" in report

    def test_format_report_empty(self):
        r = LintResult()
        report = r.format_report()
        assert "Errors: 0, Warnings: 0, Passes: 0" in report

    def test_format_report_only_passes(self):
        r = LintResult()
        r.pass_("A")
        r.pass_("B")
        report = r.format_report()
        assert "Errors: 0, Warnings: 0, Passes: 2" in report

    def test_format_report_only_errors(self):
        r = LintResult()
        r.fail("E1")
        r.fail("E2")
        r.fail("E3")
        report = r.format_report()
        assert "Errors: 3, Warnings: 0, Passes: 0" in report


class TestCountRounds:
    def test_no_file(self, tmp_path):
        assert _count_rounds(tmp_path / "nonexistent.md") == 0

    def test_empty_file(self, tmp_path):
        path = tmp_path / "empty.md"
        path.write_text("")
        assert _count_rounds(path) == 0

    def test_one_round(self, tmp_path):
        path = tmp_path / "report.md"
        path.write_text("## Round 1 -- [2026-05-17]\n")
        assert _count_rounds(path) == 1

    def test_multiple_rounds(self, tmp_path):
        path = tmp_path / "report.md"
        path.write_text("## Round 1 -- [...]\n## Round 2 -- [...]\n## Round 3 -- [...]\n")
        assert _count_rounds(path) == 3

    def test_round_in_body_not_header(self, tmp_path):
        path = tmp_path / "report.md"
        path.write_text(
            "Some text mentioning Round 5 but not as ## header.\n## Round 1 -- [date]\n"
        )
        assert _count_rounds(path) == 1
