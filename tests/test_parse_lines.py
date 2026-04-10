import pytest
from script import parse_lines


class TestParseLines:
    def test_parse_lines_single_line(self):
        text = 'Иванов Иван Иванович\t30\tулица Пушкина, 10, Москва\t2022-11-24 17:07:20'
        rows = parse_lines(text)
        assert len(rows) == 1
        assert rows[0][0] == 'Иванов Иван Иванович'
        assert rows[0][1] == '30'
        assert 'Пушкина' in rows[0][2]
        assert rows[0][3] == '2022-11-24 17:07:20'

    def test_parse_lines_multiple_lines(self):
        text = '''Иванов Иван Иванович\t30\tулица Пушкина, 10, Москва\t2022-11-24 17:07:20
Петров Петр Петрович\t25\tулица Тверская, 5, Санкт-Петербург\t2021-06-09 20:59:18'''
        rows = parse_lines(text)
        assert len(rows) == 2
        assert rows[0][0] == 'Иванов Иван Иванович'
        assert rows[1][0] == 'Петров Петр Петрович'

    def test_parse_lines_skip_empty_lines(self):
        text = '''Иванов Иван Иванович\t30\tулица Пушкина, 10, Москва\t2022-11-24 17:07:20
Петров Петр Петрович\t25\tулица Тверская, 5, Санкт-Петербург\t2021-06-09 20:59:18'''
        rows = parse_lines(text)
        assert len(rows) == 2

    def test_parse_lines_with_age_in_second_part(self):
        text = 'Сидоров Петр Андреевич\t53   улица Пушкина, 26, Екатеринбург\t2022-11-24 17:07:20'
        rows = parse_lines(text)
        assert len(rows) == 1
        assert rows[0][0] == 'Сидоров Петр Андреевич'
        assert rows[0][1] == '53'
        assert 'Пушкина' in rows[0][2]

    def test_parse_lines_with_date_formats(self):
        text = 'Иванов Иван\t30\tулица Пушкина, 10\t20220605 060755'
        rows = parse_lines(text)
        assert len(rows) == 1
        assert '2022-06-05' in rows[0][3]

    def test_parse_lines_abbreviations_replaced(self):
        text = 'Иванов Иван\t30\tул. Пушкина, 10, Москва\t2022-11-24 17:07:20'
        rows = parse_lines(text)
        assert 'улица' in rows[0][2]
        assert 'ул.' not in rows[0][2]

    def test_parse_lines_city_reorder(self):
        text = 'Соколов Андрей\t38\tКазань, ул. Советская, 33\t2027-02-23 05:39:57'
        rows = parse_lines(text)
        assert len(rows) == 1
        assert rows[0][2].startswith('улица')
        assert 'Казань' in rows[0][2]

    def test_parse_lines_carriage_return(self):
        text = 'Иванов Иван\t30\tулица Пушкина, 10\t2022-11-24 17:07:20\r\nПетров Петр\t25\tулица Тверская, 5\t2021-06-09 20:59:18'
        rows = parse_lines(text)
        assert len(rows) == 2


class TestParseLinesEdgeCases:
    def test_parse_lines_empty_text(self):
        rows = parse_lines('')
        assert len(rows) == 0

    def test_parse_lines_only_empty_lines(self):
        text = '\n\n\n'
        rows = parse_lines(text)
        assert len(rows) == 0

    def test_parse_lines_missing_date(self):
        text = 'Иванов Иван\t30\tулица Пушкина, 10, Москва'
        rows = parse_lines(text)
        assert len(rows) == 1
        assert rows[0][3] == '—'

    def test_parse_lines_missing_age(self):
        text = 'Иванов Иван\tулица Пушкина, 10, Москва\t2022-11-24 17:07:20'
        rows = parse_lines(text)
        assert len(rows) == 1
        assert rows[0][0] == 'Иванов Иван'