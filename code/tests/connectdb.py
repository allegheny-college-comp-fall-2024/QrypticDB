# """This file is for creating and connecting to a database"""

# import unittest
# import psycopg2
# from ... import databaseconnect as db


# import pytest
from unittest.mock import patch
# # Replace with the actual module name


# # Test connecting to existing database
# @patch(
#     "builtins.input",
#     side_effect=["y", "test_host", "5432", "test_user", "test_pass", "test_db"],
# )
# def test_connect_to_existing_db(mock_input):
#     result = db.create_or_connectdb()
#     assert result == ("test_host", "5432", "test_user", "test_pass", "test_db")


# # Test creating new database with custom parameters
# @patch("your_module.create_database")  # Mock database creation function
# @patch(
#     "builtins.input",
#     side_effect=["n", "y", "n", "new_host", "5433", "new_user", "new_pass", "new_db"],
# )
# def test_create_new_db_custom(mock_input, mock_create_db):
#     result = db.create_or_connectdb()
#     assert result == ("new_host", "5433", "new_user", "new_pass", "new_db")
#     mock_create_db.assert_called_once_with(
#         "new_host", "5433", "new_user", "new_pass", "new_db"
#     )


# # Test creating new database with default parameters
# @patch("your_module.create_database")
# @patch("builtins.input", side_effect=["n", "y", "y"])
# def test_create_new_db_default(mock_input, mock_create_db):
#     result = db.create_or_connectdb()
#     assert result == (
#         "localhost",
#         "5432",
#         "postgres",
#         "your_password",
#         "mynewdatabase57",
#     )
#     mock_create_db.assert_called_once()


# # Test declining to create a database
# @patch("builtins.input", side_effect=["n", "n"])
# def test_decline_create_db(mock_input):
#     result = db.create_or_connectdb()
#     assert result == (None, None)


# # Test database creation error
# @patch("your_module.create_database", side_effect=Exception("DB already exists"))
# @patch("builtins.print")
# @patch("builtins.input", side_effect=["n", "y", "y"])
# def test_db_creation_error(mock_input, mock_print, mock_create_db):
#     result = db.create_or_connectdb()
#     assert result == (
#         "localhost",
#         "5432",
#         "postgres",
#         "your_password",
#         "mynewdatabase57",
#     )
#     mock_print.assert_any_call("Error while creating database: DB already exists")


import sys
import os

# Get the parent directory and add it to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import databaseconnect as db


# def test_connect_to_existing_db():
#     result = db.create_or_connectdb()
#     assert result == ("test_host", "5432", "test_user", "test_pass", "test_db")


@patch(
    "builtins.input",
    side_effect=["y", "test_host", "5432", "test_user", "test_pass", "test_db"],
)
def test_connect_to_existing_db(mock_input):
    result = db.create_or_connectdb()
    assert result == ("test_host", "5432", "test_user", "test_pass", "test_db")


# Test creating new database with custom parameters
@patch("databaseconnect.create_database")  # Mock database creation function
@patch(
    "builtins.input",
    side_effect=["n", "y", "n", "new_host", "5433", "new_user", "new_pass", "new_db"],
)
def test_create_new_db_custom(mock_input, mock_create_db):
    result = db.create_or_connectdb()
    assert result == ("new_host", "5433", "new_user", "new_pass", "new_db")
    mock_create_db.assert_called_once_with(
        "new_host", "5433", "new_user", "new_pass", "new_db"
    )


# Test creating new database with default parameters
@patch("databaseconnect.create_database")
@patch("builtins.input", side_effect=["n", "y", "y"])
def test_create_new_db_default(mock_input, mock_create_db):
    result = db.create_or_connectdb()
    assert result == (
        "localhost",
        "5432",
        "postgres",
        "your_password",
        "mynewdatabase57",
    )
    mock_create_db.assert_called_once()


# Test declining to create a database
@patch("builtins.input", side_effect=["n", "n"])
def test_decline_create_db(mock_input):
    result = db.create_or_connectdb()
    assert result == (None, None)


# Test database creation error
@patch("databaseconnect.create_database", side_effect=Exception("DB already exists"))
@patch("builtins.print")
@patch("builtins.input", side_effect=["n", "y", "y"])
def test_db_creation_error(mock_input, mock_print, mock_create_db):
    result = db.create_or_connectdb()
    assert result == (
        "localhost",
        "5432",
        "postgres",
        "your_password",
        "mynewdatabase57",
    )
    mock_print.assert_any_call("Error while creating database: DB already exists")
