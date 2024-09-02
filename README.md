# Mail Project

A Python-based email sending system using AWS SES.

## Features

- AWS SES integration
- Rate limiting
- HTML templating
- Confirmation codes
- Logging

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up `.env` file with AWS credentials and settings

## Usage

```python
from src.mail.mail import Mail

mail = Mail()
mail.send("recipient@example.com", "Subject", "Message")
```

## Environment Variables

- Setup boto3 creds
- In .env, set SES_REGION and SES_SENDER

## License

This project is released under CC0 1.0 Universal (CC0 1.0). Do whatever you want.
