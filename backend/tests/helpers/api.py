"""API test helpers."""

from typing import Any, Dict, Optional

from fastapi.testclient import TestClient


def assert_response(
    response,
    status_code: int = 200,
    data: Any = None,
    message: Optional[str] = None,
    error: Optional[str] = None,
    meta: Optional[Dict] = None,
) -> None:
    """Assert that a response matches the expected format.

    Args:
        response: Response object from TestClient
        status_code: Expected HTTP status code
        data: Expected response data
        message: Expected message
        error: Expected error message
        meta: Expected metadata
    """
    # Check status code
    assert response.status_code == status_code, (
        f"Expected status code {status_code}, got {response.status_code}. " f"Response: {response.text}"
    )

    # Parse response JSON
    try:
        response_data = response.json()
    except ValueError:
        response_data = {}

    # Check response structure
    if status_code >= 400:
        assert "detail" in response_data, "Error response missing 'detail' field"
        if error is not None:
            assert response_data["detail"] == error, "Error message does not match"
    else:
        if data is not None:
            if isinstance(data, dict):
                assert "data" in response_data, "Response missing 'data' field"
                _assert_dict_contains(response_data["data"], data)
            elif isinstance(data, list):
                assert "data" in response_data, "Response missing 'data' field"
                assert isinstance(response_data["data"], list), "Expected data to be a list"
                assert len(response_data["data"]) == len(data), "Data length mismatch"
                for i, item in enumerate(data):
                    if isinstance(item, dict):
                        _assert_dict_contains(response_data["data"][i], item)

        if message is not None:
            assert "message" in response_data, "Response missing 'message' field"
            assert response_data["message"] == message, "Message does not match"

        if meta is not None:
            assert "meta" in response_data, "Response missing 'meta' field"
            _assert_dict_contains(response_data["meta"], meta)


def _assert_dict_contains(actual: Dict, expected: Dict) -> None:
    """Assert that the actual dict contains all key-value pairs from expected."""
    for key, value in expected.items():
        assert key in actual, f"Missing key: {key}"
        if isinstance(value, dict):
            _assert_dict_contains(actual[key], value)
        elif isinstance(value, list):
            assert isinstance(actual[key], list), f"Expected {key} to be a list"
            assert len(actual[key]) == len(value), f"Length mismatch for {key}"
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    _assert_dict_contains(actual[key][i], item)
                else:
                    assert actual[key][i] == item, f"Value mismatch for {key}[{i}]"
        else:
            assert actual[key] == value, f"Value mismatch for {key}"


def assert_pagination(response_data: Dict, total: int, page: int, size: int, total_pages: int) -> None:
    """Assert that pagination metadata is correct.

    Args:
        response_data: Response data containing pagination metadata
        total: Expected total number of items
        page: Expected current page number
        size: Expected page size
        total_pages: Expected total number of pages
    """
    assert "meta" in response_data, "Response missing 'meta' field"
    meta = response_data["meta"]

    assert "pagination" in meta, "Response missing 'pagination' field"
    pagination = meta["pagination"]

    assert pagination["total"] == total, "Total count does not match"
    assert pagination["page"] == page, "Page number does not match"
    assert pagination["size"] == size, "Page size does not match"
    assert pagination["total_pages"] == total_pages, "Total pages do not match"


def assert_validation_error(
    response, field: str, message: Optional[str] = None, error_type: str = "value_error"
) -> None:
    """Assert that a validation error occurred for a specific field.

    Args:
        response: Response object from TestClient
        field: Name of the field with validation error
        message: Expected error message (optional)
        error_type: Expected error type (default: "value_error")
    """
    assert response.status_code == 422, "Expected status code 422"

    try:
        response_data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    assert "detail" in response_data, "Error response missing 'detail' field"

    errors = response_data["detail"]
    assert isinstance(errors, list), "Expected 'detail' to be a list"

    field_errors = [e for e in errors if isinstance(e, dict) and e.get("loc") and e["loc"][-1] == field]

    assert len(field_errors) > 0, f"No validation error found for field '{field}'"

    error = field_errors[0]
    if message is not None:
        assert error.get("msg") == message, "Error message does not match"

    if error_type is not None:
        assert error.get("type") == error_type, "Error type does not match"


def assert_unauthorized(response) -> None:
    """Assert that the response indicates an unauthorized error."""
    assert response.status_code == 401, "Expected status code 401"
    assert "Not authenticated" in response.text, "Expected authentication error"


def assert_forbidden(response) -> None:
    """Assert that the response indicates a forbidden error."""
    assert response.status_code == 403, "Expected status code 403"
    assert "Not enough permissions" in response.text, "Expected permission error"


def assert_not_found(response, resource: str = "Resource") -> None:
    """Assert that the response indicates a not found error."""
    assert response.status_code == 404, "Expected status code 404"
    assert resource in response.text, f"Expected {resource} not found error"


def create_test_data(
    client: TestClient,
    endpoint: str,
    data: Dict[str, Any],
    auth_headers: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Helper to create test data via API.

    Args:
        client: Test client
        endpoint: API endpoint
        data: Data to create
        auth_headers: Optional authentication headers

    Returns:
        Created data with ID
    """
    headers = auth_headers or {}
    response = client.post(endpoint, json=data, headers=headers)
    assert response.status_code == 201, f"Failed to create test data: {response.text}"
    return response.json()["data"]
