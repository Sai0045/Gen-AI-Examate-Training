import calendar
import re
from datetime import date, timedelta

from app.records import load_records


AGE_PATTERN = re.compile(r"(\d+)\s*(weeks?|months?|years?)", re.IGNORECASE)


def parse_date(value):
    """Accept a date object or an ISO date string."""
    if isinstance(value, date):
        return value

    try:
        return date.fromisoformat(str(value))
    except ValueError:
        raise ValueError("Date must use YYYY-MM-DD format.")


def add_months(start_date, months):
    """Add calendar months without creating an invalid date."""
    total_months = start_date.year * 12 + start_date.month - 1 + months

    year = total_months // 12
    month = total_months % 12 + 1

    last_day = calendar.monthrange(year, month)[1]
    day = min(start_date.day, last_day)

    return date(year, month, day)


def add_years(start_date, years):
    """Add years safely, including leap-year birthdays."""
    return add_months(start_date, years * 12)


def age_to_date(dob, amount, unit):
    """Convert an age in weeks, months or years into a calendar date."""
    unit = unit.lower().rstrip("s")

    if unit == "week":
        return dob + timedelta(weeks=amount)

    if unit == "month":
        return add_months(dob, amount)

    if unit == "year":
        return add_years(dob, amount)

    raise ValueError("Unsupported age unit: " + unit)


def extract_due_ages(due_age):
    """
    Extract scheduled ages from a record.

    For a range such as 16-24 months, use 16 months
    as the scheduled due age.
    """
    text = str(due_age).lower()

    # Pregnancy schedules cannot be calculated from a baby's DOB.
    if "pregnancy" in text:
        return []

    # Handle ranges such as 16-24 months.
    range_match = re.search(
        r"(\d+)\s*[-–]\s*\d+\s*(weeks?|months?|years?)",
        text
    )

    if range_match:
        return [(int(range_match.group(1)), range_match.group(2))]

    # Handle ranges such as 9 completed months - 12 months.
    range_match = re.search(
        r"(\d+)\s*(?:completed\s+)?(weeks?|months?|years?)\s*[-–]",
        text
    )

    if range_match:
        return [(int(range_match.group(1)), range_match.group(2))]

    # PCV has two primary doses and a booster at 9 completed months.
    if "booster at 9 completed months" in text:
        return [
            (6, "weeks"),
            (14, "weeks"),
            (9, "months"),
        ]

    # Handle shared units such as 6 & 14 weeks.
    shared_match = re.search(
        r"(\d+)\s*&\s*(\d+)\s*(weeks?|months?|years?)",
        text
    )

    if shared_match:
        return [
            (int(shared_match.group(1)), shared_match.group(3)),
            (int(shared_match.group(2)), shared_match.group(3)),
        ]

    # Handle schedules such as 6 weeks, 10 weeks and 14 weeks.
    matches = AGE_PATTERN.findall(text)

    if matches:
        return [
            (int(amount), unit)
            for amount, unit in matches
        ]

    # Birth vaccines have a due age of zero.
    if "birth" in text:
        return [(0, "days")]

    return []


def calculate_latest_date(dob, latest_age):
    """Convert the latest eligible age into a calendar cutoff date."""
    text = str(latest_age).lower()

    if "pregnancy" in text:
        return None

    # Special limits expressed in hours or days after birth.
    hours_match = re.search(r"within\s+(\d+)\s+hours?", text)

    if hours_match:
        hours = int(hours_match.group(1))
        return dob + timedelta(days=(hours + 23) // 24)

    days_match = re.search(r"first\s+(\d+)\s+days?", text)

    if days_match:
        days = int(days_match.group(1))
        return dob + timedelta(days=days)

    # Handle wording such as "one year of age".
    text = re.sub(r"\bone\b", "1", text)

    matches = AGE_PATTERN.findall(text)

    if not matches:
        return None

    amount, unit = matches[0]

    return age_to_date(dob, int(amount), unit)


def get_status(due_date, latest_date, today):
    """Determine the dose status using its due date and cutoff."""
    if latest_date is not None and today > latest_date:
        return "Too late"

    if due_date - today > timedelta(days=7):
        return "Upcoming"

    if today <= due_date + timedelta(days=7):
        return "Due this week"

    return "Overdue"


def expand_record(record, dob):
    """Expand a schedule record into individual dose entries."""
    # Exclude pregnancy-related records, including TT-2.
    if "pregnancy" in str(record["latest_age"]).lower():
        return []

    due_ages = extract_due_ages(record["due_age"])

    if not due_ages:
        return []

    # Vitamin A doses 2-9: start at 16 months, then every 6 months.
    if "then one dose every 6 months" in record["due_age"].lower():
        due_ages = [
            (month, "months")
            for month in range(16, 59, 6)
        ]

    latest_date = calculate_latest_date(
        dob,
        record["latest_age"]
    )

    doses = []

    for number, (amount, unit) in enumerate(due_ages, start=1):
        if unit == "days":
            due_date = dob
        else:
            due_date = age_to_date(dob, amount, unit)

        doses.append({
            "record_id": record["id"],
            "vaccine": record["vaccine"],
            "dose_number": number,
            "due_age": record["due_age"],
            "due_date": due_date.isoformat(),
            "latest_date": (
                latest_date.isoformat()
                if latest_date else None
            ),
            "status": None,
            "dose": record["dose"],
            "route_site": record["route_site"],
        })

    return doses


def vaccine_due_dates(date_of_birth, today=None):
    """
    Calculate vaccine due dates and statuses for a baby's DOB.

    date_of_birth: YYYY-MM-DD string or date object.
    today: YYYY-MM-DD string or date object.
           Defaults to the system's current date.
    """
    dob = parse_date(date_of_birth)

    if today is None:
        today = date.today()
    else:
        today = parse_date(today)

    if dob > today:
        raise ValueError("Date of birth cannot be in the future.")

    records = load_records()
    all_doses = []

    for record in records:
        doses = expand_record(record, dob)

        for dose in doses:
            due_date = date.fromisoformat(dose["due_date"])

            latest_date = (
                date.fromisoformat(dose["latest_date"])
                if dose["latest_date"] else None
            )

            dose["status"] = get_status(
                due_date,
                latest_date,
                today
            )

            all_doses.append(dose)

    all_doses.sort(
        key=lambda item: (
            item["due_date"],
            item["record_id"],
            item["dose_number"]
        )
    )

    return {
        "date_of_birth": dob.isoformat(),
        "today": today.isoformat(),
        "total_doses": len(all_doses),
        "doses": all_doses,
    }
