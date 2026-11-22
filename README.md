# Batik Air Flight Tracker

A small Python automation project that tracks direct flight prices between Kuala Lumpur (KUL) and Karachi (KHI), publishes the latest results to a GitHub Gist, and supplies a KWGT Android widget with the current prices.

The project is designed around a scheduled GitHub Actions workflow:

```text
GitHub Actions
      |
      v
Apify Google/Kayak flight scraper
      |
      v
Python price normalisation
      |
      v
GitHub Gist: flight_price.json
      |
      v
KWGT widget on Android
```

## Features

- Scrapes outbound and inbound flight prices through the Apify API.
- Uses the Apify actor `p8tZlhUqCGtzZXHzj`.
- Searches economy flights in Malaysian ringgit (MYR).
- Separates direct-flight pricing from the cheapest available flight.
- Publishes one JSON document to a GitHub Gist.
- Sends an email when a direct outbound or inbound lowest price changes.
- Runs automatically every six hours through GitHub Actions.
- Can also be started manually from the Actions tab.
- Generates a `.kwgt` preset for a KUL/KHI boarding-pass-style KWGT widget.

## Current Route Configuration

The route and dates are currently defined in `backend/main.py`:

| Leg | Route | Date | Comment |
|---|---|---|---|
| Outbound | KUL -> KHI | 2027-02-27 | Batik Air OD135 in the source comments |
| Inbound | KHI -> KUL | 2027-03-13 | Batik Air OD136 in the source comments |

To track a different route or date, update `OUTBOUND_DATE`, `RETURN_DATE`, and the corresponding airport codes in `backend/main.py`. Update the labels and expressions in `kwgt_generator.py` as well if the widget should display different airport codes or dates.

## Repository Layout

```text
.
├── .env.example
├── .github/
│   └── workflows/
│       └── scrape.yaml          # Scheduled GitHub Actions job
├── backend/
│   ├── main.py                  # Apify scrape and Gist update logic
│   └── requirements.txt         # Python dependencies
├── batik_flight_tracker.kwgt    # Generated KWGT preset
├── kwgt_generator.py            # Creates the KWGT preset archive
├── manual_test.py               # Legacy test script for an older backend API
└── README.md
```

## Prerequisites

You need:

- Python 3.10 or newer. GitHub Actions currently uses Python 3.11.
- An Apify account and API token.
- A GitHub account with permission to update a Gist.
- An existing GitHub Gist containing a file named `flight_price.json`.
- A Gmail account and Gmail App Password if you want fare-change email notifications.
- KWGT/Kustom Widget Maker on Android if you want to use the widget.

The Apify actor may incur usage charges according to your Apify plan. The scraper is limited to 10 results per leg to keep the request small.

## Configuration

### Local `.env`

Copy the example file and fill in the values:

```powershell
Copy-Item .env.example .env
```

Set the following variables in `.env`:

```dotenv
APIFY_API_TOKEN=your_apify_api_token
GIST_ID=your_github_gist_id
GIST_TOKEN=your_github_personal_access_token
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password
```

`GITHUB_TOKEN` may be used instead of `GIST_TOKEN`; the code checks `GITHUB_TOKEN` first and falls back to `GIST_TOKEN`.

`GMAIL_USER` and `GMAIL_APP_PASSWORD` are optional. When both are set, the script compares the current Gist prices with the newly fetched prices and sends a Gmail SMTP message if the outbound or inbound `lowest_price` changed. Use a Gmail App Password, not your regular Google account password.

Do not commit `.env`. It is ignored by `.gitignore`. Never put a real token or App Password in `README.md`, source code, a public Gist, or a GitHub Actions workflow file.

### Python dependencies

Install the backend dependencies from the repository root:

```powershell
python -m pip install -r backend/requirements.txt
```

For local `.env` loading, install `python-dotenv` if it is not already available in your environment:

```powershell
python -m pip install python-dotenv
```

GitHub Actions receives secrets as environment variables, so it does not depend on `.env` loading.

## Create the GitHub Gist

1. Create a GitHub Gist containing a file named `flight_price.json`.
2. The initial content can be `{}`.
3. Copy the Gist ID from the Gist URL. For example, the ID is the final path segment in `https://gist.github.com/username/GIST_ID`.
4. Put that ID in `GIST_ID` locally and in the GitHub Actions secret.
5. Make the Gist public if KWGT must read the raw file without authentication.

The widget reads this URL pattern:

```text
https://gist.githubusercontent.com/ahmednaeem786/GIST_ID/raw/flight_price.json
```

The username and placeholder Gist ID are currently defined in `kwgt_generator.py`. Replace `GITHUB_USERNAME` and `GIST_ID` before generating a preset for another account or Gist.

## Run the Scraper Locally

From the repository root:

```powershell
python backend/main.py
```

The script starts one Apify actor run for each leg, selects the cheapest direct flight when one is available, and patches the Gist with the combined result.

A successful run prints JSON similar to:

```text
Updated Gist: {
  "updated_at": "21 Nov, 04:00 PM",
  "outbound": {
    "route": "KUL -> KHI",
    "date": "2027-02-27",
    "airline": "Batik Air",
    "lowest_price": "RM 850",
    "cheapest_any": "RM 850 (Batik Air)"
  },
  "inbound": {
    "route": "KHI -> KUL",
    "date": "2027-03-13",
    "airline": "No Direct",
    "lowest_price": "N/A",
    "cheapest_any": "RM 920 (Example Airline)"
  }
}
```

The exact result depends on the live scraper response. When no direct flight has a price, `lowest_price` is `N/A`; when no priced flight exists at all, `cheapest_any` is also `N/A`. If one leg fails, that leg is marked with `lowest_price: "Error"` while the other leg can still be written.

## GitHub Actions Setup

The workflow is located at `.github/workflows/scrape.yaml`. It runs:

- Every six hours using the cron expression `0 */6 * * *`.
- Manually when `workflow_dispatch` is selected.

Add these repository secrets under **Settings -> Secrets and variables -> Actions**:

| Secret | Purpose |
|---|---|
| `APIFY_API_TOKEN` | Authenticates Apify actor runs |
| `GIST_ID` | Identifies the destination Gist |
| `GIST_TOKEN` | Allows the workflow to update the Gist |
| `GMAIL_USER` | Gmail sender and recipient address |
| `GMAIL_APP_PASSWORD` | Gmail App Password used for SMTP authentication |

Both Gmail secrets are optional. The workflow will skip notifications when either one is missing.

To trigger it manually:

1. Open the repository on GitHub.
2. Open the **Actions** tab.
3. Select **Flight Price Scraper**.
4. Select **Run workflow**.
5. Choose the branch and confirm.

Review the workflow logs for the `Updated Gist` output, per-leg errors, or `No fare change detected; skipping email.` If a notification is sent, the log prints `Email notification sent` with the changed legs.

## Generate the KWGT Preset

After setting the correct GitHub username and Gist ID in `kwgt_generator.py`, run:

```powershell
python kwgt_generator.py
```

The script creates or replaces `batik_flight_tracker.kwgt`. It is a ZIP archive containing `preset.json` in the format expected by Kustom/KWGT.

To install it on Android:

1. Transfer `batik_flight_tracker.kwgt` to the device.
2. Open KWGT and create or edit a widget.
3. Use KWGT's import option to import the preset.
4. Place the widget on the home screen and grant any requested network or storage permissions.
5. Confirm that the Gist URL in the preset points to the correct public `flight_price.json` file.

The generated widget displays:

- The airline label `Batik Air`.
- The route `KUL` to `KHI`.
- The Gist update time.
- The outbound direct-flight price.
- The inbound direct-flight price.

## Data Format

The Gist is updated with a document shaped like this:

```json
{
  "updated_at": "21 Nov, 04:00 PM",
  "outbound": {
    "route": "KUL -> KHI",
    "date": "2027-02-27",
    "airline": "Batik Air",
    "lowest_price": "RM 850",
    "cheapest_any": "RM 850 (Batik Air)"
  },
  "inbound": {
    "route": "KHI -> KUL",
    "date": "2027-03-13",
    "airline": "No Direct",
    "lowest_price": "N/A",
    "cheapest_any": "RM 920 (Example Airline)"
  }
}
```

`lowest_price` is deliberately restricted to direct flights. `cheapest_any` can include flights with stops and is provided as additional information.

## Troubleshooting

### `N/A` for a direct price

`N/A` means the scraper returned no priced nonstop flight for that leg. Check `cheapest_any` to see whether a connecting flight was available.

### `Error` for a leg

The Apify call or response parsing failed for that leg. Open the GitHub Actions log or run the script locally to see the printed exception.

### Fare-change email is not received

Check that:

- `GMAIL_USER` and `GMAIL_APP_PASSWORD` are set locally or as GitHub Actions secrets.
- `GMAIL_APP_PASSWORD` is a Gmail App Password for the configured account.
- Both outbound and inbound `lowest_price` values changed or were initially available as priced values.
- The script can read the existing Gist before the Gist is overwritten.

The script deliberately sends no email when no fare change is detected.

### Gist update fails with an authentication error

Check that:

- `GIST_TOKEN` or `GITHUB_TOKEN` is valid.
- The token has permission to edit Gists.
- `GIST_ID` is the actual Gist ID, not the full URL.
- The target Gist still exists.

### KWGT shows empty values

Check that:

- The Gist is public.
- The file is exactly named `flight_price.json`.
- The raw Gist URL opens in a browser.
- `kwgt_generator.py` contains the correct username and Gist ID.
- The workflow has successfully updated the Gist at least once.

### Apify actor returns no flights

Verify the airport codes, date format (`YYYY-MM-DD`), Apify token, actor availability, and Apify usage limits. Search results can also vary by date, provider, region, and availability.

## Notes on `manual_test.py`

`manual_test.py` was written for an earlier version of the backend that exposed a `get_price()` function. The current backend is a scheduled Gist-updating script and does not currently define that function. Use `python backend/main.py` for the current implementation unless the manual test is updated to call `fetch_leg()` or another intended public interface.

## Security

- Keep `.env` private.
- Store production credentials only in GitHub Actions secrets.
- Use a GitHub token with the smallest practical scope for updating Gists.
- Use a Gmail App Password and never the normal Google account password.
- Do not print tokens or App Passwords in logs or commit them to the repository.
- Rotate tokens immediately if one is exposed.

## License

No license file is currently included. Add a `LICENSE` file before distributing this project if you want to specify reuse and contribution terms.
