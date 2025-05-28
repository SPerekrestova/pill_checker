# Test Credentials Generator

This script generates test usernames, emails, and passwords that meet the security criteria for the Pill Checker application.

## Features

- Generates usernames between 3-50 characters
- Generates passwords between 8-72 characters that contain at least one letter and one number
- Ensures passwords match the required regex pattern
- Generates valid email addresses
- Supports multiple output formats (text, JSON, env variables)
- Can generate multiple sets of credentials at once
- Can save credentials to a file

## Security Criteria

The generated credentials meet the following security criteria:

- **Username**: Between 3-50 characters
- **Password**:
  - Between 8-72 characters
  - Contains at least one letter
  - Contains at least one number
  - Matches the regex pattern: `^[A-Za-z0-9@$!%*#?&]*[A-Za-z][A-Za-z0-9@$!%*#?&]*[0-9][A-Za-z0-9@$!%*#?&]*$|^[A-Za-z0-9@$!%*#?&]*[0-9][A-Za-z0-9@$!%*#?&]*[A-Za-z][A-Za-z0-9@$!%*#?&]*$`
- **Email**: Valid email format

## Usage

```bash
# Generate a single set of credentials
python src/pill_checker/scripts/generate_test_credentials.py

# Generate multiple sets of credentials
python src/pill_checker/scripts/generate_test_credentials.py --num 5

# Generate credentials in JSON format
python src/pill_checker/scripts/generate_test_credentials.py --format json

# Generate credentials in environment variable format
python src/pill_checker/scripts/generate_test_credentials.py --format env

# Save credentials to a file
python src/pill_checker/scripts/generate_test_credentials.py --output credentials.txt

# Generate multiple sets of credentials in JSON format and save to a file
python src/pill_checker/scripts/generate_test_credentials.py --num 3 --format json --output credentials.json
```

## Command-line Options

- `-n, --num`: Number of credential sets to generate (default: 1)
- `-f, --format`: Output format (text, json, or env) (default: text)
- `-o, --output`: Output file to save credentials

## Examples

### Text Format (Default)

```
=== TEST CREDENTIALS 1/1 ===
Username: exampleUser
Email: exampleUser@example.com
Password: p@ssw0rd123
------------------------
Password Validation:
✓ Length between 8-72: True
✓ Contains at least one letter: True
✓ Contains at least one number: True
✓ Matches required pattern: True
========================
```

### JSON Format

```json
[
  {
    "username": "exampleUser",
    "email": "exampleUser@example.com",
    "password": "p@ssw0rd123"
  }
]
```

### Environment Variable Format

```
# Test credentials generated on 2025-05-28 22:43:06
TEST_USERNAME="exampleUser"
TEST_EMAIL="exampleUser@example.com"
TEST_PASSWORD="p@ssw0rd123"
```
