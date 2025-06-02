import random
import string
import re
import json
import argparse
import os
from datetime import datetime


def generate_username(min_length=3, max_length=50):
    """Generate a random username between min_length and max_length characters."""
    length = random.randint(min_length, min(15, max_length))  # Using a reasonable max length

    # Start with a letter
    username = random.choice(string.ascii_letters)

    # Add remaining characters (letters, numbers, underscores)
    chars = string.ascii_letters + string.digits + "_"
    username += "".join(random.choice(chars) for _ in range(length - 1))

    return username


def generate_password(min_length=8, max_length=72):
    """
    Generate a password that meets the following criteria:
    - Between min_length and max_length characters
    - Contains at least one letter and one number
    - Matches the regex pattern
    """
    # Define character sets
    letters = string.ascii_letters
    digits = string.digits
    special_chars = "@$!%*#?&"
    all_chars = letters + digits + special_chars

    # Choose a reasonable length (not too long, not too short)
    length = random.randint(min_length, min(16, max_length))

    # Ensure the password has the required pattern (letter-number or number-letter)
    if random.choice([True, False]):
        # Pattern: [chars]*[letter][chars]*[number][chars]*
        password_list = [
            random.choice(letters),  # Ensure at least one letter
            random.choice(digits),  # Ensure at least one number
        ]
    else:
        # Pattern: [chars]*[number][chars]*[letter][chars]*
        password_list = [
            random.choice(digits),  # Ensure at least one number
            random.choice(letters),  # Ensure at least one letter
        ]

    # Add remaining random characters
    password_list.extend(random.choice(all_chars) for _ in range(length - 2))

    # Shuffle the password characters
    random.shuffle(password_list)

    password = "".join(password_list)

    # Verify the password matches the required pattern
    pattern = r"^[A-Za-z0-9@$!%*#?&]*[A-Za-z][A-Za-z0-9@$!%*#?&]*[0-9][A-Za-z0-9@$!%*#?&]*$|^[A-Za-z0-9@$!%*#?&]*[0-9][A-Za-z0-9@$!%*#?&]*[A-Za-z][A-Za-z0-9@$!%*#?&]*$"

    # If the password doesn't match the pattern, generate a new one
    if not re.match(pattern, password):
        return generate_password(min_length, max_length)

    return password


def generate_email(username=None):
    """Generate a random email address."""
    if not username:
        username = generate_username(5, 10)

    domains = ["example.com", "test.org", "demo.net", "sample.io", "testuser.dev"]
    domain = random.choice(domains)

    return f"{username}@{domain}"


def generate_credentials():
    """Generate a set of credentials."""
    username = generate_username()
    password = generate_password()
    email = generate_email(username)

    return {"username": username, "email": email, "password": password}


def validate_password(password):
    """Validate that a password meets all requirements."""
    min_length = 8
    max_length = 72
    pattern = r"^[A-Za-z0-9@$!%*#?&]*[A-Za-z][A-Za-z0-9@$!%*#?&]*[0-9][A-Za-z0-9@$!%*#?&]*$|^[A-Za-z0-9@$!%*#?&]*[0-9][A-Za-z0-9@$!%*#?&]*[A-Za-z][A-Za-z0-9@$!%*#?&]*$"

    validations = {
        "length": min_length <= len(password) <= max_length,
        "has_letter": any(c.isalpha() for c in password),
        "has_number": any(c.isdigit() for c in password),
        "matches_pattern": bool(re.match(pattern, password)),
    }

    return validations


def format_as_env(credentials):
    """Format credentials as environment variables."""
    return f"""
# Test credentials generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
TEST_USERNAME="{credentials['username']}"
TEST_EMAIL="{credentials['email']}"
TEST_PASSWORD="{credentials['password']}"
"""


def format_as_json(credentials_list):
    """Format credentials as JSON."""
    return json.dumps(credentials_list, indent=2)


def save_to_file(content, filename):
    """Save content to a file."""
    with open(filename, "w") as f:
        f.write(content)
    print(f"Credentials saved to {os.path.abspath(filename)}")


def main():
    """Generate and display test credentials."""
    parser = argparse.ArgumentParser(
        description="Generate test credentials that meet security criteria"
    )
    parser.add_argument(
        "-n", "--num", type=int, default=1, help="Number of credential sets to generate"
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["text", "json", "env"],
        default="text",
        help="Output format (text, json, or env variables)",
    )
    parser.add_argument("-o", "--output", help="Output file to save credentials")
    args = parser.parse_args()

    credentials_list = []
    for i in range(args.num):
        credentials = generate_credentials()
        credentials_list.append(credentials)

        # Only print individual validations for text format
        if args.format == "text":
            validations = validate_password(credentials["password"])

            print(f"\n=== TEST CREDENTIALS {i + 1}/{args.num} ===")
            print(f"Username: {credentials['username']}")
            print(f"Email: {credentials['email']}")
            print(f"Password: {credentials['password']}")
            print("------------------------")
            print("Password Validation:")
            print(f"✓ Length between 8-72: {validations['length']}")
            print(f"✓ Contains at least one letter: {validations['has_letter']}")
            print(f"✓ Contains at least one number: {validations['has_number']}")
            print(f"✓ Matches required pattern: {validations['matches_pattern']}")
            print("========================\n")

    # Format output based on user preference
    if args.format == "json":
        output = format_as_json(credentials_list)
        if not args.output:
            print(output)
    elif args.format == "env":
        # For env format, just use the first set if multiple were generated
        output = format_as_env(credentials_list[0])
        if not args.output:
            print(output)

    # Save to file if requested
    if args.output:
        if args.format == "text":
            # Create a simple text summary for file output
            lines = []
            for i, creds in enumerate(credentials_list):
                lines.append(f"=== TEST CREDENTIALS {i + 1}/{args.num} ===")
                lines.append(f"Username: {creds['username']}")
                lines.append(f"Email: {creds['email']}")
                lines.append(f"Password: {creds['password']}")
                lines.append("========================")
            output = "\n".join(lines)
        save_to_file(output, args.output)


if __name__ == "__main__":
    main()
