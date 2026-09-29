import re
import xml.etree.ElementTree as ET
from pathlib import Path


REPORT_FILE = Path("test-results/pytest-results.xml")


# ============================================================
# TEXT FORMATTING
# ============================================================

BOLD = "\033[1m"
RESET = "\033[0m"


def bold(text):
    return f"{BOLD}{text}{RESET}"


# ============================================================
# CHECK JUNIT REPORT
# ============================================================

if not REPORT_FILE.exists():

    print()
    print("=" * 70)
    print("PLAYWRIGHT PYTEST TEST SUMMARY")
    print("=" * 70)
    print()
    print(f"JUnit report not found: {REPORT_FILE}")

    raise SystemExit(1)


# ============================================================
# READ JUNIT XML
# ============================================================

try:

    tree = ET.parse(REPORT_FILE)
    root = tree.getroot()

except Exception as error:

    print()
    print("=" * 70)
    print("PLAYWRIGHT PYTEST TEST SUMMARY")
    print("=" * 70)
    print()

    print(f"Unable to read JUnit XML: {error}")

    raise SystemExit(1)


# ============================================================
# TEST COUNTS
# ============================================================

total = int(root.attrib.get("tests", 0))

failures = int(root.attrib.get("failures", 0))

errors = int(root.attrib.get("errors", 0))

skipped = int(root.attrib.get("skipped", 0))

passed = total - failures - errors - skipped

failed_count = failures + errors


# ============================================================
# SUMMARY
# ============================================================

print()

print(bold("=" * 70))

print(
    bold(
        "              PLAYWRIGHT PYTEST TEST SUMMARY"
    )
)

print(bold("=" * 70))

print()

print(f"TOTAL   : {total}")
print(f"PASSED  : {passed}")
print(f"FAILED  : {failed_count}")
print(f"SKIPPED : {skipped}")

print()

print(bold("=" * 70))


# ============================================================
# EXTRACT FILE AND LINE FROM TRACEBACK
# ============================================================

def extract_file_and_line(traceback):

    if not traceback:
        return None, None

    patterns = [

        r'([A-Za-z0-9_./\\\-]+\.py):(\d+)',

        r'([A-Za-z]:\\[^:\n]+\.py):(\d+)',

    ]

    for pattern in patterns:

        match = re.search(pattern, traceback)

        if match:

            return match.group(1), match.group(2)

    return None, None


# ============================================================
# FAILED TESTS
# ============================================================

failed_tests = []


for testcase in root.iter("testcase"):

    failure = testcase.find("failure")

    error = testcase.find("error")

    if failure is None and error is None:
        continue

    problem = failure if failure is not None else error

    failed_tests.append({

        "name": testcase.attrib.get(
            "name",
            "Not available"
        ),

        "class": testcase.attrib.get(
            "classname",
            "Not available"
        ),

        "file": testcase.attrib.get(
            "file",
            ""
        ),

        "line": testcase.attrib.get(
            "line",
            ""
        ),

        "error": problem.attrib.get(
            "message",
            "Not available"
        ),

        "traceback": problem.text or ""
    })


# ============================================================
# PRINT FAILED TEST DETAILS
# ============================================================

if failed_tests:

    print()

    print(
        bold(
            "                  FAILED TEST DETAILS"
        )
    )

    print()

    print(bold("=" * 70))

    for index, test in enumerate(
        failed_tests,
        start=1
    ):

        print()

        print(
            bold(
                f"FAILED TEST #{index}"
            )
        )

        print(
            bold("-" * 70)
        )


        # ----------------------------------------------------
        # FILE
        # ----------------------------------------------------

        file_name = test["file"]


        # ----------------------------------------------------
        # LINE
        # ----------------------------------------------------

        line_number = test["line"]


        # ----------------------------------------------------
        # EXTRACT FROM TRACEBACK IF MISSING
        # ----------------------------------------------------

        if not file_name or not line_number:

            extracted_file, extracted_line = (
                extract_file_and_line(
                    test["traceback"]
                )
            )

            if not file_name and extracted_file:

                file_name = extracted_file

            if not line_number and extracted_line:

                line_number = extracted_line


        if not file_name:

            file_name = "Not available"


        if not line_number:

            line_number = "Not available"


        # ----------------------------------------------------
        # TEST
        # ----------------------------------------------------

        print(
            bold("TEST   : ")
            + str(test["name"])
        )


        # ----------------------------------------------------
        # CLASS
        # ----------------------------------------------------

        print(
            bold("CLASS  : ")
            + str(test["class"])
        )


        # ----------------------------------------------------
        # FILE
        # ----------------------------------------------------

        print(
            bold("FILE   : ")
            + str(file_name)
        )


        # ----------------------------------------------------
        # LINE
        # ----------------------------------------------------

        print(
            bold("LINE   : ")
            + str(line_number)
        )


        # ----------------------------------------------------
        # ERROR
        # ----------------------------------------------------

        print()

        print(
            bold("ERROR  : ")
            + str(test["error"])
        )


        # ----------------------------------------------------
        # TRACEBACK
        # ----------------------------------------------------

        print()

        print(
            bold("TRACEBACK:")
        )

        print()

        print(
            test["traceback"]
            if test["traceback"]
            else "Traceback not available."
        )

        print()

        print(
            bold("-" * 70)
        )


else:

    print()

    print(
        bold("ALL TESTS PASSED")
    )

    print()


# ============================================================
# FINAL RESULT
# ============================================================

print()

print(bold("=" * 70))

if failed_count == 0:

    print(
        bold(
            "RESULT : ALL TESTS PASSED"
        )
    )

else:

    print(
        bold(
            f"RESULT : {failed_count} TEST(S) FAILED"
        )
    )

print(bold("=" * 70))

print()
