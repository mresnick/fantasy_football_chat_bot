"""Unit tests for report.py"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath('.'))

from gamedaybot.utils.report import (
    Report, from_text, GOLD, BLUE, FUNCTION_COLORS,
    MAX_EMBED_TOTAL, MAX_FIELD_VALUE, MAX_FIELDS, MAX_TITLE,
)


class TestFromText:
    """Wrapping an existing plain-text report must not change the text platforms."""

    def test_round_trips_exactly(self):
        text = "Score Update\n  AA 120.00 -   98.00 BB\n  CC  95.00 -   94.00 DD"
        assert from_text(text).to_text() == text

    def test_round_trips_a_single_line(self):
        assert from_text("No waiver transactions").to_text() == "No waiver transactions"

    def test_round_trips_blank_lines(self):
        text = "Playoff Picture\n\n 1: AA (9-2)\n\n 2: BB (8-3)"
        assert from_text(text).to_text() == text

    def test_empty_text_gives_no_report(self):
        assert from_text('') is None
        assert from_text(None) is None

    def test_first_line_becomes_the_title(self):
        embed = from_text("Score Update\n  AA 120.00").to_embed()
        assert embed['title'] == 'Score Update'
        assert 'AA 120.00' in embed['description']

    def test_body_is_fenced_so_columns_stay_aligned(self):
        embed = from_text("Standings\n 1: AA\n 2: BB").to_embed()
        assert embed['description'].startswith('```')
        assert embed['description'].endswith('```')

    def test_monospace_can_be_turned_off(self):
        embed = from_text("Title\nprose line", monospace=False).to_embed()
        assert '```' not in embed['description']


class TestReportRendering:
    """Fields render as name/value line pairs in text and as fields in the embed."""

    def _report(self):
        return Report(title='Trophies of the week:',
                      fields=[('High score', 'Alpha with 120.00 points'),
                              ('Low score', 'Bravo with 80.00 points')],
                      color=GOLD, footer='Week 4')

    def test_text_matches_the_legacy_shape(self):
        assert self._report().to_text() == (
            'Trophies of the week:\n'
            'High score\n'
            'Alpha with 120.00 points\n'
            'Low score\n'
            'Bravo with 80.00 points')

    def test_footer_is_omitted_from_text(self):
        # Text has nowhere sensible to put small print.
        assert 'Week 4' not in self._report().to_text()

    def test_embed_carries_fields_colour_and_footer(self):
        embed = self._report().to_embed()
        assert embed['title'] == 'Trophies of the week:'
        assert embed['color'] == GOLD
        assert embed['footer']['text'] == 'Week 4'
        assert [f['name'] for f in embed['fields']] == ['High score', 'Low score']

    def test_embed_is_timestamped(self):
        assert 'timestamp' in self._report().to_embed()

    def test_fields_default_to_inline(self):
        embed = Report(title='t', fields=[('a', 'b')]).to_embed()
        assert embed['fields'][0]['inline'] is True

    def test_inline_can_be_set_per_field(self):
        embed = Report(title='t', fields=[('a', 'b', False)]).to_embed()
        assert embed['fields'][0]['inline'] is False

    def test_empty_fields_are_dropped(self):
        # Discord rejects an embed containing a field with a blank name or value.
        embed = Report(title='t', fields=[('a', ''), ('', 'b'), ('c', 'd')]).to_embed()
        assert len(embed['fields']) == 1


class TestEmbedLimits:
    """Oversized content must fall back to text rather than be rejected by Discord."""

    def test_a_normal_report_fits(self):
        assert from_text("Standings\n 1: AA\n 2: BB").fits_embed() is True

    def test_an_enormous_report_does_not_fit(self):
        assert from_text('Title\n' + 'x' * (MAX_EMBED_TOTAL + 500)).fits_embed() is False

    def test_an_empty_report_does_not_fit(self):
        assert Report().fits_embed() is False

    def test_title_is_truncated_to_the_limit(self):
        embed = Report(title='x' * (MAX_TITLE + 50)).to_embed()
        assert len(embed['title']) == MAX_TITLE

    def test_field_values_are_truncated_to_the_limit(self):
        embed = Report(title='t', fields=[('name', 'v' * (MAX_FIELD_VALUE + 50))]).to_embed()
        assert len(embed['fields'][0]['value']) == MAX_FIELD_VALUE

    def test_field_count_is_capped(self):
        embed = Report(title='t',
                       fields=[('n%d' % i, 'v%d' % i) for i in range(MAX_FIELDS + 10)]).to_embed()
        assert len(embed['fields']) == MAX_FIELDS

    def test_embed_size_counts_title_description_and_fields(self):
        report = Report(title='abcde', fields=[('ab', 'cde')])
        assert report.embed_size() == len('abcde') + len('ab') + len('cde')

    def test_size_is_measured_before_truncation(self):
        # Measuring the clamped render would report every oversized report as
        # fitting, and the content would be silently cut instead of falling back.
        report = from_text('Title' + chr(10) + 'x' * (MAX_EMBED_TOTAL + 500))
        assert report.embed_size() > MAX_EMBED_TOTAL
        assert report.fits_embed() is False

    def test_anything_needing_a_clamp_falls_back(self):
        # Each of these renders only by losing content, so none should be sent
        # as an embed.
        assert Report(title='x' * (MAX_TITLE + 1)).fits_embed() is False
        assert Report(title='t', fields=[('n', 'v' * (MAX_FIELD_VALUE + 1))]
                      ).fits_embed() is False
        assert Report(title='t', fields=[('n%d' % i, 'v') for i in range(MAX_FIELDS + 1)]
                      ).fits_embed() is False


class TestFunctionColors:
    """Every report the bot can send should have an accent colour."""

    def test_scheduled_functions_all_have_a_colour(self):
        for function in ['get_matchups', 'get_monitor', 'get_scoreboard_short',
                         'get_close_scores', 'get_power_rankings', 'get_trophies',
                         'get_standings', 'get_final', 'get_waiver_report',
                         'get_playoff_picture', 'get_draft_report']:
            assert function in FUNCTION_COLORS, function

    def test_related_reports_share_a_colour(self):
        assert FUNCTION_COLORS['get_trophies'] == FUNCTION_COLORS['get_final'] == GOLD
        assert FUNCTION_COLORS['get_standings'] == FUNCTION_COLORS['get_playoff_picture'] == BLUE
