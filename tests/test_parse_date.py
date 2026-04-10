import pytest
from script import parse_date


class TestParseDate:
    def test_parse_date_yyyy_mm_dd_hh_mm_ss(self):
        result = parse_date('2022-11-24 17:07:20')
        assert result == '2022-11-24 17:07:20'

    def test_parse_date_yyyy_mm_dd_t_hh_mm_ss(self):
        result = parse_date('2021-06-09T20:59:18')
        assert result == '2021-06-09 20:59:18'

    def test_parse_date_yyyymmdd_hh_mm_ss(self):
        result = parse_date('20220317 15:49:17')
        assert result == '2022-03-17 15:49:17'

    def test_parse_date_yyyymmddthhmmss(self):
        result = parse_date('19800713T205307')
        assert result == '1980-07-13 20:53:07'

    def test_parse_date_yyyymmdd_hhmmss(self):
        result = parse_date('20220605 060755')
        assert result == '2022-06-05 06:07:55'

    def test_parse_date_empty_string(self):
        result = parse_date('')
        assert result == '—'

    def test_parse_date_invalid_format(self):
        result = parse_date('invalid-date')
        assert result == 'invalid-date'

    def test_parse_date_invalid_date_values(self):
        result = parse_date('2010-30-02 05:56:30')
        assert result == '2010-30-02 05:56:30'

    def test_parse_date_month_day_swap(self):
        result = parse_date('2022-13-01 10:20:30')
        assert result == '2022-01-13 10:20:30'

    def test_parse_date_with_newlines(self):
        result = parse_date('2022-11-24 17:07:20\n')
        assert result == '2022-11-24 17:07:20'


class TestParseDateEdgeCases:
    def test_parse_date_midnight(self):
        result = parse_date('2022-01-01 00:00:00')
        assert result == '2022-01-01 00:00:00'

    def test_parse_date_last_minute_of_day(self):
        result = parse_date('2022-12-31 23:59:59')
        assert result == '2022-12-31 23:59:59'

    def test_parse_date_leap_year(self):
        result = parse_date('2020-02-29 12:00:00')
        assert result == '2020-02-29 12:00:00'