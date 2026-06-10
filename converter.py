import csv
import io
import json

IGNORED_EMAILS = {"", "***************************************"}


def convert_ff_to_listmonk(content: str) -> tuple[str, int]:
    reader = csv.DictReader(io.StringIO(content), delimiter=";")

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)
    writer.writerow(["email", "name", "attributes"])

    count = 0
    for row in reader:
        active = row.get("ACTIVE", "").strip().strip('"')
        if active != "JA":
            continue

        email = row.get("EMAIL", "").strip().strip('"')
        if not email or email in IGNORED_EMAILS or email.startswith("*"):
            continue

        firstname = row.get("FIRSTNAME", "").strip().strip('"')
        lastname = row.get("LASTNAME", "").strip().strip('"')
        name = f"{firstname} {lastname}".strip()

        einheitsfuehrer_key = next(
            (k for k in row if "Einheitsf" in k and "COMMENT" not in k), None
        )
        einheitsfuehrer = (
            row[einheitsfuehrer_key].strip().strip('"') == "JA"
            if einheitsfuehrer_key
            else False
        )

        gruppenfuehrer_key = next(
            (k for k in row if "Gruppenf" in k and "COMMENT" not in k), None
        )
        gruppenfuehrer = (
            row[gruppenfuehrer_key].strip().strip('"') == "JA"
            if gruppenfuehrer_key
            else False
        )

        birthdate_raw = row.get("BIRTHDATE", "").strip().strip('"')
        birthdate = birthdate_raw if "*" not in birthdate_raw else ""

        attributes = {
            "firstname": firstname,
            "birthdate": birthdate,
            "einheitsfuehrer": einheitsfuehrer,
            "gruppenfuehrer": gruppenfuehrer,
        }
        attributes = {k: v for k, v in attributes.items() if v != "" and v is not False}

        writer.writerow([email, name, json.dumps(attributes, ensure_ascii=False)])
        count += 1

    return output.getvalue(), count


def _safe_int(value: str) -> int:
    try:
        return int(value.strip().strip('"'))
    except (ValueError, AttributeError):
        return 0
