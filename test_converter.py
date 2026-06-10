import csv
import io
import json
import unittest

from converter import convert_ff_to_listmonk, _safe_int

HEADER = (
    '"USERNAME";"PUBLIC_GUID";"FIRSTNAME";"LASTNAME";"P_NUMBER";"MEMBER_SINCE";'
    '"COMMANDER";"ADMIN";"ACTIVE";"AVAILABILITY";"EMAIL";"MOBILE";"BIRTHDATE";'
    '"Einheitsführer";"Einheitsführer_COMMENT";"Gruppenführer";"Gruppenführer_COMMENT";'
    '"MISSIONS";"MISSION_LEADS"'
)


def make_csv(*rows: str) -> str:
    return "\n".join([HEADER] + list(rows))


def parse_output(output: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(output))
    return [
        {**row, "attributes": json.loads(row["attributes"])}
        for row in reader
    ]


def make_row(
    email="max@example.com",
    firstname="Max",
    lastname="Mustermann",
    active="JA",
    birthdate="01.01.1990",
    einheitsfuehrer="NEIN",
    gruppenfuehrer="NEIN",
):
    return (
        f'"user@ff";"guid";"{firstname}";"{lastname}";"";"";"NEIN";"NEIN";"{active}";"JA";'
        f'"{email}";"0151111";"{birthdate}";'
        f'"{einheitsfuehrer}";"";""{gruppenfuehrer}";"";'
        f'"5";"1"'
    )


class TestConvertFFToListmonk(unittest.TestCase):

    def test_basic_row(self):
        csv_in = make_csv(
            '"user1@ff";"guid1";"Max";"Mustermann";"";"";"NEIN";"NEIN";"JA";"JA";'
            '"max@example.com";"0151111";"01.01.1990";"NEIN";"";"NEIN";"";"5";"1"'
        )
        output, count = convert_ff_to_listmonk(csv_in)
        self.assertEqual(count, 1)
        rows = parse_output(output)
        self.assertEqual(rows[0]["email"], "max@example.com")
        self.assertEqual(rows[0]["name"], "Max Mustermann")
        attrs = rows[0]["attributes"]
        self.assertEqual(attrs["firstname"], "Max")
        self.assertEqual(attrs["birthdate"], "01.01.1990")
        self.assertNotIn("einheitsfuehrer", attrs)
        self.assertNotIn("gruppenfuehrer", attrs)

    def test_inactive_skipped(self):
        csv_in = make_csv(
            '"user@ff";"guid";"Hans";"Inaktiv";"";"";"NEIN";"NEIN";"NEIN";"NEIN";'
            '"hans@example.com";"";"";"NEIN";"";"NEIN";"";"0";"0"'
        )
        _, count = convert_ff_to_listmonk(csv_in)
        self.assertEqual(count, 0)

    def test_einheitsfuehrer_true(self):
        csv_in = make_csv(
            '"user@ff";"guid";"Anna";"Chef";"";"";"JA";"JA";"JA";"JA";'
            '"anna@example.com";"";"";"JA";"";"NEIN";"";"0";"0"'
        )
        attrs = parse_output(convert_ff_to_listmonk(csv_in)[0])[0]["attributes"]
        self.assertTrue(attrs["einheitsfuehrer"])
        self.assertNotIn("gruppenfuehrer", attrs)

    def test_gruppenfuehrer_true(self):
        csv_in = make_csv(
            '"user@ff";"guid";"Peter";"Gruppe";"";"";"NEIN";"NEIN";"JA";"JA";'
            '"peter@example.com";"";"";"NEIN";"";"JA";"";"0";"0"'
        )
        attrs = parse_output(convert_ff_to_listmonk(csv_in)[0])[0]["attributes"]
        self.assertTrue(attrs["gruppenfuehrer"])
        self.assertNotIn("einheitsfuehrer", attrs)

    def test_masked_birthdate_omitted(self):
        csv_in = make_csv(
            '"user@ff";"guid";"Klaus";"Anonym";"";"";"NEIN";"NEIN";"JA";"JA";'
            '"klaus@example.com";"";""**********";"NEIN";"";"NEIN";"";"0";"0"'
        )
        # masked birthdate should not appear in attributes
        csv_in = (
            HEADER + "\n"
            '"user@ff";"guid";"Klaus";"Anonym";"";"";"NEIN";"NEIN";"JA";"JA";'
            '"klaus@example.com";"**********";"**********";"NEIN";"";"NEIN";"";"0";"0"'
        )
        attrs = parse_output(convert_ff_to_listmonk(csv_in)[0])[0]["attributes"]
        self.assertNotIn("birthdate", attrs)

    def test_empty_email_skipped(self):
        csv_in = make_csv(
            '"user@ff";"guid";"No";"Mail";"";"";"NEIN";"NEIN";"JA";"JA";'
            '"";"";"";"NEIN";"";"NEIN";"";"0";"0"'
        )
        _, count = convert_ff_to_listmonk(csv_in)
        self.assertEqual(count, 0)

    def test_masked_email_skipped(self):
        csv_in = make_csv(
            '"admin@ff";"guid";"Admin";"User";"";"";"JA";"JA";"JA";"NEIN";'
            '"***************************************";"";"";"NEIN";"";"NEIN";"";"0";"0"'
        )
        _, count = convert_ff_to_listmonk(csv_in)
        self.assertEqual(count, 0)

    def test_starred_email_skipped(self):
        csv_in = make_csv(
            '"user@ff";"guid";"Star";"Man";"";"";"NEIN";"NEIN";"JA";"JA";'
            '"***partial***";"";"";"NEIN";"";"NEIN";"";"0";"0"'
        )
        _, count = convert_ff_to_listmonk(csv_in)
        self.assertEqual(count, 0)

    def test_multiple_rows_count(self):
        csv_in = make_csv(
            '"u1@ff";"g1";"A";"B";"";"";"NEIN";"NEIN";"JA";"JA";"a@x.de";"";"";"NEIN";"";"NEIN";"";"1";"0"',
            '"u2@ff";"g2";"C";"D";"";"";"NEIN";"NEIN";"JA";"JA";"c@x.de";"";"";"NEIN";"";"NEIN";"";"2";"0"',
            '"u3@ff";"g3";"E";"F";"";"";"NEIN";"NEIN";"NEIN";"JA";"";"";"";"NEIN";"";"NEIN";"";"0";"0"',
        )
        _, count = convert_ff_to_listmonk(csv_in)
        self.assertEqual(count, 2)

    def test_output_has_listmonk_header(self):
        csv_in = make_csv()
        output, _ = convert_ff_to_listmonk(csv_in)
        first_line = output.splitlines()[0]
        self.assertEqual(first_line, '"email","name","attributes"')


class TestSafeInt(unittest.TestCase):

    def test_normal(self):
        self.assertEqual(_safe_int("42"), 42)

    def test_quoted(self):
        self.assertEqual(_safe_int('"7"'), 7)

    def test_empty(self):
        self.assertEqual(_safe_int(""), 0)

    def test_non_numeric(self):
        self.assertEqual(_safe_int("abc"), 0)


if __name__ == "__main__":
    unittest.main()