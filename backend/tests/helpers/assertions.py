"""Assertion helpers for API response validation."""
import json
from typing import Any, Dict, List, Optional, Type, Union

from fastapi.testclient import TestClient
from httpx import Response
from pydantic import BaseModel


def assert_status_code(
    response: Response,
    expected_status: int,
    message: Optional[str] = None
) -> None:
    """Assert that the response has the expected status code.
    
    Args:
        response: HTTP response
        expected_status: Expected status code
        message: Optional custom error message
        
    Raises:
        AssertionError: If the status code doesn't match
    """
    __tracebackhide__ = True  # Hide this function from tracebacks
    
    if response.status_code != expected_status:
        msg = (
            f"Expected status code {expected_status}, but got {response.status_code}. "
            f"Response: {response.text}"
        )
        if message:
            msg = f"{message}: {msg}"
        raise AssertionError(msg)


def assert_response_json(
    response: Response,
    expected: Optional[Union[Dict, List]] = None,
    contains: Optional[Union[Dict, List, str]] = None,
    message: Optional[str] = None
) -> Any:
    """Assert that the response contains the expected JSON data.
    
    Args:
        response: HTTP response
        expected: Expected JSON data (exact match)
        contains: Expected JSON data (partial match)
        message: Optional custom error message
        
    Returns:
        The parsed JSON data
        
    Raises:
        AssertionError: If the response doesn't match the expected data
    """
    __tracebackhide__ = True  # Hide this function from tracebacks
    
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        raise AssertionError(f"Response is not valid JSON: {response.text}") from e
    
    if expected is not None:
        if data != expected:
            msg = f"Expected {expected}, but got {data}"
            if message:
                msg = f"{message}: {msg}"
            raise AssertionError(msg)
    
    if contains is not None:
        if isinstance(contains, dict):
            for key, value in contains.items():
                if key not in data:
                    msg = f"Key '{key}' not found in response: {data}"
                    if message:
                        msg = f"{message}: {msg}"
                    raise AssertionError(msg)
                if data[key] != value:
                    msg = f"Expected {key}={value}, but got {key}={data[key]}"
                    if message:
                        msg = f"{message}: {msg}"
                    raise AssertionError(msg)
        elif isinstance(contains, list):
            for item in contains:
                if item not in data:
                    msg = f"Item {item} not found in response: {data}"
                    if message:
                        msg = f"{message}: {msg}"
                    raise AssertionError(msg)
        elif isinstance(contains, str):
            if contains not in json.dumps(data):
                msg = f"String '{contains}' not found in response: {data}"
                if message:
                    msg = f"{message}: {msg}"
                raise AssertionError(msg)
    
    return data


def assert_response_model(
    response: Response,
    model: Type[BaseModel],
    expected_status: int = 200,
    message: Optional[str] = None
) -> BaseModel:
    """Assert that the response matches a Pydantic model.
    
    Args:
        response: HTTP response
        model: Pydantic model class
        expected_status: Expected status code
        message: Optional custom error message
        
    Returns:
        The parsed model instance
        
    Raises:
        AssertionError: If the response doesn't match the model
    """
    __tracebackhide__ = True  # Hide this function from tracebacks
    
    assert_status_code(response, expected_status, message)
    
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        raise AssertionError(f"Response is not valid JSON: {response.text}") from e
    
    try:
        return model.parse_obj(data)
    except Exception as e:
        msg = f"Response does not match model {model.__name__}: {e}"
        if message:
            msg = f"{message}: {msg}"
        raise AssertionError(msg) from e


def assert_pagination(
    response: Response,
    total: int,
    page: int,
    size: int,
    pages: int,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """Assert that the response contains pagination metadata.
    
    Args:
        response: HTTP response
        total: Expected total number of items
        page: Expected current page number
        size: Expected page size
        pages: Expected total number of pages
        message: Optional custom error message
        
    Returns:
        The parsed response data
        
    Raises:
        AssertionError: If the pagination metadata doesn't match
    """
    data = assert_response_json(response, message=message)
    
    if "pagination" not in data:
        msg = "Response does not contain pagination metadata"
        if message:
            msg = f"{message}: {msg}"
        raise AssertionError(msg)
    
    pagination = data["pagination"]
    
    if pagination.get("total") != total:
        msg = f"Expected total={total}, but got {pagination.get('total')}"
        if message:
            msg = f"{message}: {msg}"
        raise AssertionError(msg)
    
    if pagination.get("page") != page:
        msg = f"Expected page={page}, but got {pagination.get('page')}"
        if message:
            msg = f"{message}: {msg}"
        raise AssertionError(msg)
    
    if pagination.get("size") != size:
        msg = f"Expected size={size}, but got {pagination.get('size')}"
        if message:
            msg = f"{message}: {msg}"
        raise AssertionError(msg)
    
    if pagination.get("pages") != pages:
        msg = f"Expected pages={pages}, but got {pagination.get('pages')}"
        if message:
            msg = f"{message}: {msg}"
        raise AssertionError(msg)
    
    return data


def assert_error_response(
    response: Response,
    status_code: int,
    detail: Optional[Union[str, Dict]] = None,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """Assert that the response is an error with the expected details.
    
    Args:
        response: HTTP response
        status_code: Expected status code
        detail: Expected error detail (string or dictionary)
        message: Optional custom error message
        
    Returns:
        The parsed error response
        
    Raises:
        AssertionError: If the error response doesn't match
    """
    assert_status_code(response, status_code, message)
    
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        raise AssertionError(f"Response is not valid JSON: {response.text}") from e
    
    if "detail" not in data:
        msg = "Error response does not contain 'detail' field"
        if message:
            msg = f"{message}: {msg}"
        raise AssertionError(msg)
    
    if detail is not None:
        if isinstance(detail, str) and data["detail"] != detail:
            msg = f"Expected error detail '{detail}', but got '{data['detail']}'"
            if message:
                msg = f"{message}: {msg}"
            raise AssertionError(msg)
        elif isinstance(detail, dict) and data["detail"] != detail:
            msg = f"Expected error detail {detail}, but got {data['detail']}"
            if message:
                msg = f"{message}: {msg}"
            raise AssertionError(msg)
    
    return data


def assert_validation_errors(
    response: Response,
    expected_errors: List[Dict[str, Any]],
    message: Optional[str] = None
) -> Dict[str, Any]:
    """Assert that the response contains validation errors.
    
    Args:
        response: HTTP response
        expected_errors: List of expected validation errors
        message: Optional custom error message
        
    Returns:
        The parsed error response
        
    Raises:
        AssertionError: If the validation errors don't match
    """
    data = assert_error_response(
        response=response,
        status_code=422,
        message=message
    )
    
    if "detail" not in data or not isinstance(data["detail"], list):
        msg = "Expected list of validation errors in 'detail' field"
        if message:
            msg = f"{message}: {msg}"
        raise AssertionError(msg)
    
    errors = data["detail"]
    
    if len(errors) != len(expected_errors):
        msg = f"Expected {len(expected_errors)} errors, but got {len(errors)}"
        if message:
            msg = f"{message}: {msg}"
        raise AssertionError(msg)
    
    for i, (error, expected) in enumerate(zip(errors, expected_errors)):
        for key, value in expected.items():
            if key not in error:
                msg = f"Error {i} missing field '{key}'"
                if message:
                    msg = f"{message}: {msg}"
                raise AssertionError(msg)
            
            if error[key] != value:
                msg = (
                    f"Error {i} field '{key}' has value '{error[key]}', "
                    f"expected '{value}'"
                )
                if message:
                    msg = f"{message}: {msg}"
                raise AssertionError(msg)
    
    return data


def assert_unauthorized(
    response: Response,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """Assert that the response indicates an unauthorized error.
    
    Args:
        response: HTTP response
        message: Optional custom error message
        
    Returns:
        The parsed error response
    """
    return assert_error_response(
        response=response,
        status_code=401,
        detail="Not authenticated",
        message=message
    )


def assert_forbidden(
    response: Response,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """Assert that the response indicates a forbidden error.
    
    Args:
        response: HTTP response
        message: Optional custom error message
        
    Returns:
        The parsed error response
    """
    return assert_error_response(
        response=response,
        status_code=403,
        detail="Not enough permissions",
        message=message
    )


def assert_not_found(
    response: Response,
    resource: str = "Resource",
    message: Optional[str] = None
) -> Dict[str, Any]:
    """Assert that the response indicates a not found error.
    
    Args:
        response: HTTP response
        resource: Name of the resource that was not found
        message: Optional custom error message
        
    Returns:
        The parsed error response
    """
    return assert_error_response(
        response=response,
        status_code=404,
        detail=f"{resource} not found",
        message=message
    )
