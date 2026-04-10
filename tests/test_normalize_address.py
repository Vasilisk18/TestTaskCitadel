import pytest
from script import normalize_address


class TestNormalizeAddress:
    def test_normalize_address_replace_ul(self):
        result = normalize_address('ул. Пушкина, 26, Москва')
        assert 'улица' in result
        assert 'ул.' not in result

    def test_normalize_address_replace_pr(self):
        result = normalize_address('пр. Невского, 10, Санкт-Петербург')
        assert 'проспект' in result
        assert 'пр.' not in result

    def test_normalize_address_replace_per(self):
        result = normalize_address('пер. Кольцевой, 5, Москва')
        assert 'переулок' in result
        assert 'пер.' not in result


    def test_normalize_address_replace_pl(self):
        result = normalize_address('пл. Красная, 1, Москва')
        assert 'площадь' in result
        assert 'пл.' not in result

    def test_normalize_address_city_first_reorder(self):
        result = normalize_address('Казань, улица Советская, 33')
        assert result == 'улица Советская, 33, Казань'

    def test_normalize_address_city_first_moscow(self):
        result = normalize_address('Москва, улица Арбат, 42')
        assert result == 'улица Арбат, 42, Москва'

    def test_normalize_address_city_first_spb(self):
        result = normalize_address('Санкт-Петербург, улица Невского, 10')
        assert result == 'улица Невского, 10, Санкт-Петербург'

    def test_normalize_address_city_at_end_no_change(self):
        result = normalize_address('улица Пушкина, 26, Екатеринбург')
        assert result == 'улица Пушкина, 26, Екатеринбург'

    def test_normalize_address_unknown_city(self):
        result = normalize_address('Воронеж, улица Степана, 5')
        assert result == 'Воронеж, улица Степана, 5'

    def test_normalize_address_no_abbreviations(self):
        result = normalize_address('улица Пушкина, 26, Москва')
        assert result == 'улица Пушкина, 26, Москва'

    def test_normalize_address_multiple_abbreviations(self):
        result = normalize_address('ул. Садовая, 10, Санкт-Петербург')
        assert 'улица' in result
        assert 'ул.' not in result


class TestNormalizeAddressEdgeCases:
    def test_normalize_address_empty_string(self):
        result = normalize_address('')
        assert result == ''

    def test_normalize_address_only_city(self):
        result = normalize_address('Москва')
        assert result == 'Москва'

    def test_normalize_address_city_comma_street(self):
        result = normalize_address('Новосибирск, улица Ленина, 60')
        assert result == 'улица Ленина, 60, Новосибирск'