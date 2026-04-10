import argparse
import re
import shutil
import sys
import urllib.request
from datetime import datetime
import io
from typing import List


def read_source(source: str) -> bytes:
    if source.startswith(('http://', 'https://')):
        with urllib.request.urlopen(source, timeout=30) as resp:
            return resp.read()
    chunks = []
    with open(source, 'rb') as f:
        while chunk := f.read(1024 * 1024):
            chunks.append(chunk)
    return b''.join(chunks)


def parse_date(raw: str) -> str:
    s = raw.strip()
    s = s.replace(r'\r\n', '').replace(r'\n', '').replace(r'\r', '')
    if not s:
        return '—'

    formats = [
        (r'^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})$',
         lambda m: (int(m.group(1)), int(m.group(2)), int(m.group(3)),
                    int(m.group(4)), int(m.group(5)), int(m.group(6)))),
        (r'^(\d{4})(\d{2})(\d{2}) (\d{2}):(\d{2}):(\d{2})$',
         lambda m: (int(m.group(1)), int(m.group(2)), int(m.group(3)),
                    int(m.group(4)), int(m.group(5)), int(m.group(6)))),
        (r'^(\d{4})(\d{2})(\d{2})[ T](\d{2})(\d{2})(\d{2})$',
         lambda m: (int(m.group(1)), int(m.group(2)), int(m.group(3)),
                    int(m.group(4)), int(m.group(5)), int(m.group(6)))),
        (r'^(\d{4})(\d{2})(\d{2}) (\d{6})$',
         lambda m: (int(m.group(1)), int(m.group(2)), int(m.group(3)),
                    int(m.group(4)[:2]), int(m.group(4)[2:4]), int(m.group(4)[4:]))),
    ]

    for pattern, extractor in formats:
        m = re.match(pattern, s)
        if m:
            try:
                yr, mo, dy, hh, mm, ss = extractor(m)
                if mo > 12:
                    mo, dy = dy, mo
                datetime(yr, mo, dy, hh, mm, ss)
                return f'{yr:04d}-{mo:02d}-{dy:02d} {hh:02d}:{mm:02d}:{ss:02d}'
            except ValueError:
                pass
    return s


def normalize_address(addr: str) -> str:
    addr = addr.replace('ул.', 'улица')
    addr = addr.replace('пр.', 'проспект')
    addr = addr.replace('пер.', 'переулок')
    addr = addr.replace('бул.', 'бульвар')
    addr = addr.replace('пл.', 'площадь')

    # Список известных городов
    cities = ['Москва', 'Санкт-Петербург', 'Екатеринбург', 'Новосибирск', 'Казань']

    # Проверяем, начинается ли адрес с города (без улицы перед ним)
    for city in cities:
        if addr.startswith(city + ','):
            # Город в начале, нужно переставить
            # Ищем все части адреса
            parts = [p.strip() for p in addr.split(',')]
            # Первая часть - город, остальное - улица и номер
            city_part = parts[0]
            street_and_number = ', '.join(parts[1:])
            return f'{street_and_number}, {city_part}'

    return addr


def parse_lines(text: str) -> List[List[str]]:
    rows = []
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue

        # Ищем дату
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}',
            r'\d{4}\d{2}\d{2} \d{2}:\d{2}:\d{2}',
            r'\d{4}\d{2}\d{2}[ T]\d{2}\d{2}\d{2}',
            r'\d{4}\d{2}\d{2} \d{6}',
        ]

        date_str = ''
        line_without_date = line

        for pattern in date_patterns:
            date_match = re.search(pattern, line)
            if date_match:
                date_str = date_match.group(0)
                line_without_date = line[:date_match.start()].strip()
                break

        # Разбиваем по табуляциям
        parts = re.split(r'\t+', line_without_date)
        parts = [p.strip() for p in parts]

        fio = ''
        age = ''
        addr = ''

        # Ищем возраст как отдельную часть (только цифры)
        for i, part in enumerate(parts):
            age_match = re.match(r'^(\d+)$', part)
            if age_match:
                # Нашли возраст
                fio = ' '.join(parts[:i])
                age = part
                addr = ' '.join(parts[i + 1:])
                break

        # Если возраст не найден как отдельная часть, ищем его в начале части
        if not age and len(parts) >= 2:
            # Проверяем первую часть после ФИО - может быть "53   улица..."
            age_in_part = re.match(r'^(\d+)\s+(.*)$', parts[1])
            if age_in_part:
                fio = parts[0]
                age = age_in_part.group(1)
                remaining = age_in_part.group(2)
                if len(parts) > 2:
                    addr = remaining + ' ' + ' '.join(parts[2:])
                else:
                    addr = remaining
            else:
                fio = parts[0]
                if len(parts) > 1:
                    age = parts[1]
                if len(parts) > 2:
                    addr = ' '.join(parts[2:])
        elif not age:
            # Не смогли разобраться, берем первую часть как ФИО
            if parts:
                fio = parts[0]
            if len(parts) > 1:
                addr = ' '.join(parts[1:])

        # Очищаем адрес от лишних пробелов
        addr = ' '.join(addr.split())

        # Нормализуем адрес
        addr = normalize_address(addr)

        date = parse_date(date_str)

        rows.append([fio, age, addr, date])
    return rows


def render_table(rows: List[List[str]],
                 title: str = 'Список сотрудников') -> None:
    term_w = shutil.get_terminal_size(fallback=(120, 40)).columns
    headers = ['ФИО', 'Возраст', 'Адрес', 'Дата рождения']

    col_w = [max(len(headers[i]), max(len(r[i]) for r in rows))
             for i in range(4)]

    total = sum(col_w) + 3 * len(col_w) + 1

    if total > term_w:
        overhead = 3 * len(col_w) + 1
        available = term_w - overhead
        ratio = available / sum(col_w)
        col_w = [max(5, int(w * ratio)) for w in col_w]

    def cell(text: str, w: int) -> str:
        if len(text) > w:
            text = text[:w - 1] + '…'
        return text.ljust(w)

    def separator(char='-') -> str:
        return '+' + '+'.join('-' * (w + 2) for w in col_w) + '+'

    line_w = len(separator())

    print(separator().replace('-', '='))
    print('|' + title.center(line_w - 2) + '|')
    print(separator())
    print('| ' + ' | '.join(cell(h, col_w[i]) for i, h in enumerate(headers)) + ' |')
    print(separator())
    for row in rows:
        print('| ' + ' | '.join(cell(row[i], col_w[i]) for i in range(4)) + ' |')
    print(separator())
    print(f'Записей: {len(rows)}')


def main() -> None:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    parser = argparse.ArgumentParser(description='Вывод таблицы из текстового файла')
    parser.add_argument('-i', '--input', required=True,
                        help='Путь к файлу или URL')
    args = parser.parse_args()

    raw_bytes = read_source(args.input)

    text = raw_bytes.decode('utf-8').encode('cp1251', errors='ignore').decode('utf-8', errors='replace')
    text = text.replace('�', 'И')
    rows = parse_lines(text)

    if not rows:
        print('Данные не найдены.', file=sys.stderr)
        sys.exit(1)

    render_table(rows)


if __name__ == '__main__':
    main()