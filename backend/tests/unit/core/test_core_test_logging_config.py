"""Tests for logging_config module."""

import sys
import logging
import logging.config
from unittest.mock import patch, MagicMock

from app.core import logging_config as logging_module
from app.core.config import settings


# Test cases
@patch("app.core.logging_config.Path")
@patch("app.core.logging_config.logging.config.dictConfig")
@patch.dict("app.core.logging_config.settings.__dict__", {"DEBUG": False, "LOG_TO_FILE": False})
def test_setup_logging_creates_log_dir(mock_dict_config, mock_path):
    """Test that setup_logging creates the log directory if it doesn't exist."""
    # Setup mock for Path
    mock_path_instance = MagicMock()
    mock_path.return_value = mock_path_instance

    # Mock the dictConfig to avoid actual logging configuration
    mock_dict_config.return_value = None

    # Call the function
    logging_module.setup_logging()

    # Check if Path was called with the correct directory
    mock_path.assert_called_once_with("logs")
    # Check if mkdir was called with exist_ok=True
    mock_path_instance.mkdir.assert_called_once_with(exist_ok=True)

    # Check that dictConfig was called with the expected config
    assert mock_dict_config.called
    config = mock_dict_config.call_args[0][0]
    assert "handlers" in config
    assert "error_file" in config["handlers"]
    assert "file" in config["handlers"]
    assert "console" in config["handlers"]


@patch("app.core.logging_config.logging.config.dictConfig")
@patch("app.core.logging_config.logging.getLogger")
def test_setup_logging_debug_mode(mock_get_logger, mock_dict_config, monkeypatch):
    """Test logging configuration in debug mode."""
    # Setup
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    # Set DEBUG=True in settings
    with patch.object(settings, "DEBUG", True):
        # Call the function
        logging_module.setup_logging()

    # Verify dictConfig was called with the right config
    args, _ = mock_dict_config.call_args
    config = args[0]

    # Check root logger level
    assert config["root"]["level"] == "DEBUG"
    # Check console formatter
    assert config["handlers"]["console"]["formatter"] == "verbose"


@patch("app.core.logging_config.logging.config.dictConfig")
@patch("app.core.logging_config.logging.getLogger")
def test_setup_logging_production_mode(mock_get_logger, mock_dict_config, monkeypatch):
    """Test logging configuration in production mode."""
    # Setup
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    # Set DEBUG=False in settings
    with patch.object(settings, "DEBUG", False):
        # Call the function
        logging_module.setup_logging()

    # Verify dictConfig was called with the right config
    args, _ = mock_dict_config.call_args
    config = args[0]

    # Check root logger level
    assert config["root"]["level"] == "INFO"
    # Check console formatter
    assert config["handlers"]["console"]["formatter"] == "simple"


@patch("app.core.logging_config.logging.config.dictConfig")
@patch("app.core.logging_config.logging.getLogger")
def test_setup_logging_log_to_file(mock_get_logger, mock_dict_config, monkeypatch):
    """Test logging configuration when LOG_TO_FILE is True."""
    # Setup
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    # Set LOG_TO_FILE=True in settings
    with patch.object(settings, "LOG_TO_FILE", True):
        # Call the function
        logging_module.setup_logging()

    # Verify dictConfig was called with the right config
    args, _ = mock_dict_config.call_args
    config = args[0]

    # Check file handlers are included
    assert "file" in config["handlers"]
    assert "error_file" in config["handlers"]
    assert "file" in config["root"]["handlers"]
    assert "error_file" in config["root"]["handlers"]


@patch("app.core.logging_config.logging.config.dictConfig")
@patch("app.core.logging_config.logging.getLogger")
def test_setup_logging_unhandled_exception(mock_get_logger, mock_dict_config, monkeypatch):
    """Test that unhandled exceptions are logged."""
    # Setup
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    # Call the function to set up the exception hook
    logging_module.setup_logging()

    # Get the exception hook
    excepthook = sys.excepthook

    # Call the exception hook with a test exception
    test_exc_type = ValueError
    test_exc_value = ValueError("Test error")
    test_traceback = None

    excepthook(test_exc_type, test_exc_value, test_traceback)

    # Verify the logger was called with the exception
    mock_logger.critical.assert_called_once()
    assert "Uncaught exception" in mock_logger.critical.call_args[0][0]
    assert mock_logger.critical.call_args[1]["exc_info"] == (
        test_exc_type,
        test_exc_value,
        test_traceback,
    )


@patch("app.core.logging_config.logging.config.dictConfig")
@patch("app.core.logging_config.logging.getLogger")
def test_setup_logging_keyboard_interrupt(mock_get_logger, mock_dict_config, monkeypatch):
    """Test that KeyboardInterrupt is not logged by the exception hook."""
    # Setup
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    # Mock the original excepthook
    original_excepthook = MagicMock()
    monkeypatch.setattr(sys, "__excepthook__", original_excepthook)

    # Call the function to set up the exception hook
    logging_module.setup_logging()

    # Get the exception hook
    excepthook = sys.excepthook

    # Call the exception hook with KeyboardInterrupt
    test_exc_type = KeyboardInterrupt
    test_exc_value = KeyboardInterrupt()
    test_traceback = None

    excepthook(test_exc_type, test_exc_value, test_traceback)

    # Verify the original excepthook was called
    original_excepthook.assert_called_once_with(test_exc_type, test_exc_value, test_traceback)

    # Verify the logger was not called
    mock_logger.critical.assert_not_called()


@patch("app.core.logging_config.logging.config.dictConfig")
@patch("app.core.logging_config.logging.getLogger")
def test_setup_logging_logger_levels(mock_get_logger, mock_dict_config, monkeypatch):
    """Test that logger levels are set correctly."""
    # Setup
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    # Call the function
    logging_module.setup_logging()

    # Verify dictConfig was called with the right config
    args, _ = mock_dict_config.call_args
    config = args[0]

    # Check logger levels
    assert config["loggers"]["uvicorn"]["level"] == "INFO"
    assert config["loggers"]["sqlalchemy.engine"]["level"] == "WARNING"
    assert config["loggers"]["app"]["level"] == "DEBUG" if settings.DEBUG else "INFO"


@patch("app.core.logging_config.logging.config.dictConfig")
@patch("app.core.logging_config.logging.getLogger")
def test_setup_logging_third_party_loggers(mock_get_logger, mock_dict_config, monkeypatch):
    """Test that third-party loggers are configured with appropriate levels."""
    # Setup
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    # Mock the getLogger function to track which loggers are configured
    logger_instances = {}

    def mock_get_logger(name=None):
        if name not in logger_instances:
            logger_instances[name] = MagicMock()
        return logger_instances[name]

    with patch("logging.getLogger", side_effect=mock_get_logger):
        # Call the function
        logging_module.setup_logging()

        # Check that third-party loggers were configured with WARNING level
        for logger_name in ["asyncio", "httpx", "httpcore"]:
            assert logger_name in logger_instances
            logger_instances[logger_name].setLevel.assert_called_with(logging.WARNING)
