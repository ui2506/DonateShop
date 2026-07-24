# DonateShop

> [!WARNING]
> The frontend of this project is relatively basic, as development was primarily focused on backend functionality. A frontend redesign is recommended for long-term or production use.

DonateShop is a universal Django-based web platform for selling digital donations across multiple game servers. It is designed to be game-independent, allowing any server or application to integrate through a simple REST API.

The platform includes:

* Digital donation purchases
* User balance and transaction history
* Steam authentication
* Support for multiple game servers
* Donation expiration management
* REST API for retrieving active donations
* REST API for extending donation durations
* IP and API key protection for server-to-server communication

Any game server can integrate with DonateShop by using the provided API to verify whether a player owns a donation, retrieve donation details, or manage donation durations without requiring direct access to the website's database.

This project is no longer actively maintained by the original developer. You may use, modify, and continue developing it according to the repository license.

## Requirements

Before installing the project, make sure the following software is available:

* [Python](https://www.python.org/downloads/)
* [Nginx](https://nginx.org/en/download.html)
* [MySQL Community Server](https://dev.mysql.com/downloads/mysql/) or [PostgreSQL](https://www.postgresql.org/download/)
* Git
* pip
* Gunicorn

The production instructions below are primarily intended for Linux servers.

## 1. Clone the repository

```bash
git clone <repository-url>
cd DonateShop
```

Replace `<repository-url>` with the URL of this repository.

## 2. Install Python

Download and install a supported Python version:

https://www.python.org/downloads/

Verify the installation:

```bash
python --version
```

On some Linux distributions, use:

```bash
python3 --version
```

## 3. Create a virtual environment

Creating a virtual environment is strongly recommended.

### Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

## 4. Install the Python dependencies

Install all dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Install Gunicorn if it is not included in `requirements.txt`:

```bash
pip install gunicorn
```

> Gunicorn is intended for Linux and other Unix-like systems. For local testing on Windows, use Django's development server.

## 5. Install and configure a database

The website requires either MySQL or PostgreSQL.

### MySQL

Download MySQL Community Server:

https://dev.mysql.com/downloads/mysql/

Create a database and a separate database user for the website.

Example:

```sql
CREATE DATABASE donateshop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER 'donateshop'@'localhost' IDENTIFIED BY 'replace-with-a-strong-password';

GRANT ALL PRIVILEGES ON donateshop.* TO 'donateshop'@'localhost';

FLUSH PRIVILEGES;
```

### PostgreSQL

Download PostgreSQL:

https://www.postgresql.org/download/

Create a database and user:

```sql
CREATE USER donateshop WITH PASSWORD 'replace-with-a-strong-password';

CREATE DATABASE donateshop OWNER donateshop;
```

Only one database engine is required.

## 6. Configure Django

Open:

```text
DonateShop/settings.py
```

Configure the following settings.

### `ALLOWED_HOSTS`

Add the domains and IP addresses from which the website may be accessed:

```python
ALLOWED_HOSTS = [
    "example.com",
    "www.example.com",
    "127.0.0.1",
]
```

Do not use `"*"` in production unless you fully understand the security implications.

### `CSRF_TRUSTED_ORIGINS`

Add every trusted HTTPS origin:

```python
CSRF_TRUSTED_ORIGINS = [
    "https://example.com",
    "https://www.example.com",
]
```

Each value must include the protocol, such as `https://`.

### `DATABASES`

Configure the selected database engine.

#### MySQL example

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "donateshop",
        "USER": "donateshop",
        "PASSWORD": "replace-with-a-strong-password",
        "HOST": "127.0.0.1",
        "PORT": "3306",
    }
}
```

#### PostgreSQL example

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "donateshop",
        "USER": "donateshop",
        "PASSWORD": "replace-with-a-strong-password",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}
```

### `API_KEY`

`API_KEY` protects the website API from unauthorized requests.

Generate a long random value:

```python
API_KEY = "replace-with-a-long-random-secret"
```

Clients accessing protected API endpoints must send this value in the `X-API-KEY` HTTP header.

Example:

```http
X-API-KEY: replace-with-a-long-random-secret
```

Example request:

```bash
curl -X POST "https://example.com/api/endpoint" \
    -H "X-API-KEY: replace-with-a-long-random-secret" \
    -H "Content-Type: application/json" \
    -d '{"user_id":"76561198000000000@steam"}'
```

Replace the URL, endpoint, and request body with the values expected by the API.

### `API_IP`

`API_IP` is the allowlist of IP addresses permitted to access protected API endpoints.

Example:

```python
API_IP = [
    "127.0.0.1",
    "203.0.113.10",
]
```

Add the public IP addresses of the game servers or services that will access the API.

Be aware that requests passing through a reverse proxy may appear to come from the proxy address unless forwarded IP headers are configured and validated correctly.

### `SOCIAL_AUTH_STEAM_API_KEY`

Obtain a Steam Web API key here:

https://steamcommunity.com/dev/apikey

Then add it to the configuration:

```python
SOCIAL_AUTH_STEAM_API_KEY = "replace-with-your-steam-api-key"
```

A Steam account is required to create an API key.

### `SECRET_KEY`

Generate and configure a unique Django secret key:

```python
SECRET_KEY = "replace-with-a-long-random-secret-key"
```

Never reuse the development key on a public production server.

## 7. Apply database migrations

Run the following commands from the directory containing `manage.py`:

```bash
python manage.py makemigrations
python manage.py migrate
```

On systems where Python 3 is invoked as `python3`, use:

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

Normally, migrations included in the repository should be applied with `migrate`. Running `makemigrations` is only necessary when the models have changed or migration files are missing.

## 8. Collect static files

The generated `staticfiles` directory is not included in the repository and must be created during deployment:

```bash
python manage.py collectstatic --noinput
```

Make sure `STATIC_ROOT` is correctly configured in `DonateShop/settings.py`.

## 9. Test the website

Temporarily make sure development mode is enabled:

```python
DEBUG = True
```

Start Django's development server:

```bash
python manage.py runserver
```

By default, the website will be available at:

```text
http://127.0.0.1:8000/
```

To make the test server accessible from another device:

```bash
python manage.py runserver 0.0.0.0:8000
```

Django's development server must not be used in production.

## 10. Configure production mode

After confirming that the website works, open:

```text
DonateShop/settings.py
```

Disable debug mode:

```python
DEBUG = False
```

Check that the following settings are configured correctly:

```python
ALLOWED_HOSTS = [
    "example.com",
    "www.example.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://example.com",
    "https://www.example.com",
]
```

Run Django's deployment checks:

```bash
python manage.py check --deploy
```

## 11. Start Gunicorn

Create the log directory if it does not exist:

```bash
sudo mkdir -p /var/www/DonateShop
```

Make sure the current user is allowed to write to it, or change the log path to an appropriate location.

Start Gunicorn:

```bash
gunicorn \
    DonateShop.wsgi:application \
    --bind 127.0.0.1:8000 \
    --log-level error \
    --access-logfile /dev/null \
    --error-logfile /var/www/DonateShop/error.log
```

Gunicorn will listen locally on:

```text
127.0.0.1:8000
```

For a permanent deployment, run Gunicorn through a process manager such as `systemd`. Running it directly in a terminal means it will stop when the terminal session closes.

## 12. Install and configure Nginx

Download or install Nginx:

https://nginx.org/en/download.html

On Debian or Ubuntu:

```bash
sudo apt update
sudo apt install nginx
```

Nginx should normally listen on ports `80` and `443`, while forwarding requests to Gunicorn on `127.0.0.1:8000`.

Create a configuration file:

```bash
sudo nano /etc/nginx/sites-available/donateshop
```

Example configuration:

```nginx
server {
    listen 80;
    listen [::]:80;

    server_name example.com www.example.com;

    client_max_body_size 20M;

    location /static/ {
        alias /path/to/DonateShop/staticfiles/;
    }

    location /media/ {
        alias /path/to/DonateShop/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Replace:

```text
example.com
www.example.com
/path/to/DonateShop/
```

with the real domain and project path.

Enable the configuration:

```bash
sudo ln -s /etc/nginx/sites-available/donateshop /etc/nginx/sites-enabled/donateshop
```

Check the configuration:

```bash
sudo nginx -t
```

Reload Nginx:

```bash
sudo systemctl reload nginx
```

## 13. Configure HTTPS

A production website should use HTTPS.

For Debian or Ubuntu, Certbot can be installed with:

```bash
sudo apt install certbot python3-certbot-nginx
```

Request a certificate:

```bash
sudo certbot --nginx -d example.com -d www.example.com
```

After HTTPS is enabled, make sure the HTTPS domains are present in `CSRF_TRUSTED_ORIGINS`.

## Security warning

Before publishing or deploying the project, verify that the repository does not contain:

* Database passwords
* Django `SECRET_KEY`
* `API_KEY`
* Steam API keys
* Payment provider credentials
* SMTP passwords
* Private certificates
* Production `.env` files
* User-uploaded media
* Database backups

Secrets should preferably be loaded from environment variables instead of being written directly in `settings.py`.

Example:

```python
import os

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
API_KEY = os.environ["DONATESHOP_API_KEY"]
SOCIAL_AUTH_STEAM_API_KEY = os.environ["STEAM_API_KEY"]
```

Never commit real production credentials to Git. Removing them from the latest commit is not enough if they were included in an earlier commit, because they may remain in the Git history.

## Updating the project

After pulling new changes, activate the virtual environment and run:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then restart Gunicorn and reload Nginx.

## Troubleshooting

### `ModuleNotFoundError`

Make sure the virtual environment is active and reinstall the dependencies:

```bash
pip install -r requirements.txt
```

### Database connection errors

Check:

* Database server status
* Database name
* Username and password
* Host and port
* Database user permissions
* Firewall rules

### Static files are missing

Run:

```bash
python manage.py collectstatic --noinput
```

Then verify that the Nginx `alias` path points to the generated `staticfiles` directory.

### `DisallowedHost`

Add the requested domain or IP address to `ALLOWED_HOSTS`.

### CSRF verification errors

Check that the complete origin, including `https://`, is present in `CSRF_TRUSTED_ORIGINS`.

### Nginx returns `502 Bad Gateway`

Verify that Gunicorn is running and listening on:

```text
127.0.0.1:8000
```

You can check the port with:

```bash
ss -ltnp | grep 8000
```

## API

The website provides an HTTP API for retrieving active donations and extending their expiration dates.

All API requests must use the `POST` method and include the following header:

```http
X-Api-Key: your-api-key
```

The client IP address must also be included in the `API_IP` allowlist configured in:

```text
DonateShop/settings.py
```

Example configuration:

```python
API_KEY = "replace-with-a-secure-random-key"

API_IP = [
    "127.0.0.1",
    "203.0.113.10",
]
```

When `API_KEY` is stored as a single string, the authorization check should use exact comparison:

```python
if api_key != settings.API_KEY or ip not in settings.API_IP:
    return Response({"error": "permission denied"}, status=403)
```

## Retrieve donations

### Endpoint

```http
POST /api/donators/
```

This endpoint returns active donation purchases.

Only purchases matching all of the following conditions are returned:

* The purchase is not hidden.
* The purchase is not disabled.
* The expiration date is later than the current time.

### Request headers

```http
Content-Type: application/json
X-Api-Key: your-api-key
```

### Request parameters

All parameters are optional.

| Parameter     |   Type | Description                                                             |
| ------------- | -----: | ----------------------------------------------------------------------- |
| `user_id`     | string | Filters purchases by the player's exact user ID.                        |
| `server_name` | string | Filters purchases by server name. The comparison is case-insensitive.   |
| `donate_name` | string | Filters purchases by donation name. The comparison is case-insensitive. |

When no filters are provided, the endpoint returns all active and visible purchases.

### Example request

```bash
curl -X POST "https://example.com/api/donators/" \
    -H "Content-Type: application/json" \
    -H "X-Api-Key: replace-with-your-api-key" \
    -d '{
        "user_id": "76561198000000000@steam",
        "server_name": "RU Classic",
        "donate_name": "VIP"
    }'
```

### Example Python request

```python
import requests

url = "https://example.com/api/donators/"

headers = {
    "Content-Type": "application/json",
    "X-Api-Key": "replace-with-your-api-key",
}

payload = {
    "user_id": "76561198000000000@steam",
    "server_name": "RU Classic",
    "donate_name": "VIP",
}

response = requests.post(
    url,
    headers=headers,
    json=payload,
    timeout=10,
)

response.raise_for_status()

data = response.json()
print(data)
```

### Successful response

```json
{
    "count": 1,
    "results": [
        {
            "user_id": "76561198000000000@steam",
            "prefix": {
                "text": "Supporter",
                "color": ""
            },
            "donate": {
                "donate_name": "VIP",
                "server_name": "RU Classic",
                "date_purchased": "2026-07-01 15:30:00",
                "expires_at": "2026-08-01 15:30:00",
                "is_active": true
            }
        }
    ]
}
```

### Response fields

#### Root object

| Field     |    Type | Description                   |
| --------- | ------: | ----------------------------- |
| `count`   | integer | Number of matching purchases. |
| `results` |   array | List of matching purchases.   |

#### Purchase object

| Field     |   Type | Description                                  |
| --------- | -----: | -------------------------------------------- |
| `user_id` | string | Player user ID associated with the purchase. |
| `prefix`  | object | Player prefix information.                   |
| `donate`  | object | Donation and purchase information.           |

#### Prefix object

| Field   |           Type | Description                                          |
| ------- | -------------: | ---------------------------------------------------- |
| `text`  | string or null | Prefix assigned to the player.                       |
| `color` |         string | Prefix color. Currently returned as an empty string. |

#### Donate object

| Field            |    Type | Description                                         |
| ---------------- | ------: | --------------------------------------------------- |
| `donate_name`    |  string | Name of the purchased donation.                     |
| `server_name`    |  string | Name of the server associated with the purchase.    |
| `date_purchased` |  string | Purchase date in `YYYY-MM-DD HH:MM:SS` format.      |
| `expires_at`     |  string | Expiration date in `YYYY-MM-DD HH:MM:SS` format.    |
| `is_active`      | boolean | Indicates whether the purchase is currently active. |

### Empty response

When no matching purchases are found:

```json
{
    "count": 0,
    "results": []
}
```

## Extend donation expiration dates

### Endpoint

```http
POST /api/donators/give_days/
```

This endpoint adds a specified number of days to the expiration date of all matching active purchases.

> [!CAUTION]
> This endpoint modifies database records. It should only be accessible to trusted internal services.

### Request headers

```http
Content-Type: application/json
X-Api-Key: your-api-key
```

### Request parameters

| Parameter     | Required |                      Type | Description                                                             |
| ------------- | -------: | ------------------------: | ----------------------------------------------------------------------- |
| `days`        |      Yes | integer or numeric string | Number of days to add to each matching purchase.                        |
| `user_id`     |       No |                    string | Filters purchases by the player's exact user ID.                        |
| `server_name` |       No |                    string | Filters purchases by server name. The comparison is case-insensitive.   |
| `donate_name` |       No |                    string | Filters purchases by donation name. The comparison is case-insensitive. |

### Example request

```bash
curl -X POST "https://example.com/api/donators/give_days/" \
    -H "Content-Type: application/json" \
    -H "X-Api-Key: replace-with-your-api-key" \
    -d '{
        "days": 7,
        "user_id": "76561198000000000@steam",
        "server_name": "RU Classic",
        "donate_name": "VIP"
    }'
```

This request adds seven days to every active `VIP` purchase belonging to the specified player on the `RU Classic` server.

### Example Python request

```python
import requests

url = "https://example.com/api/donators/give_days/"

headers = {
    "Content-Type": "application/json",
    "X-Api-Key": "replace-with-your-api-key",
}

payload = {
    "days": 7,
    "user_id": "76561198000000000@steam",
    "server_name": "RU Classic",
    "donate_name": "VIP",
}

response = requests.post(
    url,
    headers=headers,
    json=payload,
    timeout=10,
)

response.raise_for_status()

print(response.json())
```

### Successful response

```json
{
    "status": "ok",
    "count": 1
}
```

### Response fields

| Field    |    Type | Description                                             |
| -------- | ------: | ------------------------------------------------------- |
| `status` |  string | Returns `ok` when the operation completes successfully. |
| `count`  | integer | Number of purchases whose expiration date was extended. |

### No matching purchases

The endpoint still returns a successful response when no matching purchases are found:

```json
{
    "status": "ok",
    "count": 0
}
```

## Error responses

### Permission denied

Returned when the API key is invalid or the client IP address is not included in `API_IP`.

```json
{
    "error": "permission denied"
}
```

HTTP status:

```http
403 Forbidden
```

### Invalid JSON

Returned when the request body does not contain valid JSON.

```json
{
    "error": "Invalid JSON"
}
```

HTTP status:

```http
400 Bad Request
```

### Invalid days value

Returned by `/api/donators/give_days/` when `days` is missing or is not a positive numeric value.

```json
{
    "error": "Invalid days value"
}
```

HTTP status:

```http
400 Bad Request
```
