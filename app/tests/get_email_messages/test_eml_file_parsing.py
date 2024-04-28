import json
import pytest


from utils.html_messages_parser import get_messages_from_html_file


def load_test_data():
    with open('test_data.json', 'r') as file:
        return json.load(file)


@pytest.fixture
def test_case(request):
    return request.param


def pytest_generate_tests(metafunc):
    if "test_case" in metafunc.fixturenames:
        test_cases = load_test_data()
        metafunc.parametrize("test_case", test_cases, indirect=True)


def detailed_comparison(expected_snippets, actual_messages):
    mismatches = []
    for expected, actual in zip(expected_snippets, actual_messages):
        if expected.lower() not in actual.lower():
            # Shorten the output to the first 100 characters
            short_actual = actual[:100] + '...' if len(actual) > 100 else actual
            mismatches.append(f"Expected: '{expected}'\nFound in: '{short_actual}'\n")
    return mismatches


def test_message_extraction(test_case):
    messages = get_messages_from_html_file(test_case["file_path"])
    expected_count = test_case["expected_count"]
    expected_snippets = test_case["expected_snippets"]

    assert len(messages) == expected_count, f"Expected {expected_count} messages, got {len(messages)}"

    mismatches = detailed_comparison(expected_snippets, messages)
    assert not mismatches, (
        f"Mismatched pairs:\n{''.join(mismatches)}"
    )
