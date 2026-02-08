# Morning Briefing System - Setup Guide

This guide will walk you through setting up the morning briefing system from scratch on Ubuntu (or similar Linux distributions). The setup should take about 30-45 minutes.

## Prerequisites

Before you begin, ensure you have:

- A computer running Ubuntu 20.04 or later (or similar Linux distribution)
- Internet connection
- A valid email address for receiving briefings
- Credit card for API sign-ups (most services have free tiers, but require payment method on file)

## Step 1: Get API Keys

You'll need to sign up for several services and obtain API keys. This is the most time-consuming part of the setup.

### 1.1 OpenWeatherMap API Key

1. Go to [https://openweathermap.org/api](https://openweathermap.org/api)
2. Click "Sign Up" and create a free account
3. Navigate to "API keys" in your account dashboard
4. Copy your API key (starts with a long alphanumeric string)
5. **Free tier**: 1,000 calls/day, 60 calls/minute - more than enough for daily briefings

### 1.2 OpenAI API Key

1. Go to [https://platform.openai.com/](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to "API keys" (or visit [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys))
4. Click "Create new secret key"
5. Name it "morning-briefing" and copy the key (starts with `sk-`)
6. **Important**: Store this key securely - you won't be able to see it again
7. **Pricing**: GPT-3.5-turbo costs ~$0.0015 per request (10 articles), ~$0.60-0.90/month for daily use

### 1.3 SparkPost API Key

1. Go to [https://www.sparkpost.com/](https://www.sparkpost.com/)
2. Sign up for a free account (500 emails/month)
3. Verify your email address
4. Navigate to "Account" → "API Keys"
5. Create a new API key with "Transmissions: Read/Write" permission
6. Copy the API key (starts with a long alphanumeric string)
7. **Important**: You'll also need to verify a sending domain or use SparkPost's sandbox domain for testing

### 1.4 Google Calendar API (Optional)

If you want calendar integration:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   - Navigate to "APIs & Services" → "Library"
   - Search for "Google Calendar API"
   - Click "Enable"
4. Create credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Desktop app" as application type
   - Name it "morning-briefing"
   - Download the credentials JSON file
5. Save the downloaded file as `credentials.json` in the project directory
6. **Note**: The first time you run the script, it will open a browser for you to authorize access

## Step 2: Install on Ubuntu

### 2.1 Install System Dependencies

```bash
# Update package list
sudo apt update

# Install Python 3 and pip (if not already installed)
sudo apt install python3 python3-pip python3-venv git -y

# Verify Python version (should be 3.8 or higher)
python3 --version
```

### 2.2 Clone or Download the Project

If using Git:

```bash
# Navigate to your preferred directory
cd ~/Documents

# Clone the repository (replace with your actual repository URL)
git clone <repository-url> morning-news-summary
cd morning-news-summary
```

Or, if you have the files already, just navigate to the project directory:

```bash
cd /path/to/morning-news-summary
```

### 2.3 Create Python Virtual Environment

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

### 2.4 Install Python Dependencies

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

This will install:
- requests (HTTP requests)
- feedparser (RSS feed parsing)
- newspaper4k (Article extraction)
- beautifulsoup4 (HTML parsing)
- openai (OpenAI API client)
- google-api-python-client (Google Calendar)
- pyyaml (YAML configuration)
- sparkpost (Email delivery)
- pytest (Testing framework)

## Step 3: Configure the System

### 3.1 Create Configuration File

```bash
# Copy the example configuration
cp config.example.yaml config.yaml

# Edit the configuration file
nano config.yaml
```

### 3.2 Edit Configuration

Update `config.yaml` with your API keys and preferences:

```yaml
apis:
  openweather_key: "YOUR_OPENWEATHER_API_KEY_HERE"
  openai_key: "sk-YOUR_OPENAI_API_KEY_HERE"
  sparkpost_key: "YOUR_SPARKPOST_API_KEY_HERE"

location:
  city: "San Francisco"  # Your city
  country_code: "US"     # Your country code (ISO 3166)

email:
  recipient: "your.email@example.com"           # Your email address
  from_address: "briefing@yourdomain.com"       # Sender address (must be verified in SparkPost)
  subject: "Your Morning Briefing - {date}"     # Email subject ({date} will be replaced with current date)

news:
  rss_feeds:
    - "https://feeds.bbci.co.uk/news/rss.xml"
    - "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
    - "https://feeds.reuters.com/reuters/topNews"
    # Add or remove feeds as desired
  max_articles: 10         # Maximum number of articles to fetch
  summary_sentences: 3     # Number of sentences in each AI summary

logging:
  level: "INFO"           # Log level: DEBUG, INFO, WARNING, ERROR
  retain_days: 30         # Number of days to keep old logs
```

**Important Configuration Notes:**

- **SparkPost from_address**: Must be a verified domain in SparkPost. For testing, you can use their sandbox domain (check SparkPost docs)
- **City names**: Use proper capitalization (e.g., "New York", "Los Angeles")
- **Country codes**: Use ISO 3166-1 alpha-2 codes (US, GB, CA, etc.)
- **RSS feeds**: You can add any valid RSS feed URL

Save the file (in nano: Ctrl+X, then Y, then Enter)

### 3.3 Secure Your Configuration

```bash
# Restrict access to config file (contains sensitive API keys)
chmod 600 config.yaml

# Add config.yaml to .gitignore if using version control
echo "config.yaml" >> .gitignore
```

## Step 4: First Run - Authenticate Google Calendar (Optional)

If you're using Google Calendar integration:

```bash
# Ensure credentials.json is in the project directory
ls -l credentials.json

# Run the briefing in dry-run mode to trigger OAuth flow
python morning_briefing.py --dry-run
```

This will:
1. Open a browser window
2. Ask you to log in to Google
3. Request permission to read your calendar
4. Save a `token.pickle` file for future authentication

**Note**: If you're setting up on a headless server (no GUI), you'll need to authenticate on your local machine first, then copy the `token.pickle` file to the server.

## Step 5: Test Run

Test the system before scheduling it:

```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate

# Run in dry-run mode (saves to output/ directory instead of sending email)
python morning_briefing.py --dry-run

# Check the output
ls -l output/
```

You should see:
1. A new HTML file in the `output/` directory
2. Log messages showing each step of the process
3. No errors in the console

Open the HTML file in a browser to preview the email:

```bash
# Open in default browser (on Ubuntu with GUI)
xdg-open output/briefing_*.html

# Or view the file path and open manually
ls output/
```

### 5.1 Verify the Output

Check that the HTML email contains:
- Weather information for your city
- Calendar events (if configured)
- News articles with AI-generated summaries
- Proper formatting and styling

### 5.2 Check Logs

```bash
# View the log file
cat logs/morning_briefing.log

# Or tail the last 50 lines
tail -n 50 logs/morning_briefing.log
```

Look for:
- "Starting morning briefing process"
- "Weather fetched"
- "Found X calendar events"
- "Fetched X news articles"
- "Generated summaries for X articles"
- "Email HTML built successfully"
- "Dry run: Email saved to output/..."

## Step 6: Schedule with Cron

Once you've verified the system works, schedule it to run automatically every morning.

### 6.1 Create Cron Job

```bash
# Open crontab editor
crontab -e
```

### 6.2 Add Cron Entry

Add the following line to run the briefing at 7:30 AM every day:

```bash
30 7 * * * cd /home/yourusername/morning-news-summary && /home/yourusername/morning-news-summary/venv/bin/python /home/yourusername/morning-news-summary/morning_briefing.py >> /home/yourusername/morning-news-summary/logs/cron.log 2>&1
```

**Important**: Replace `/home/yourusername/morning-news-summary` with the actual path to your project directory.

To find the full path:
```bash
cd ~/morning-news-summary
pwd  # This shows the full path
```

### 6.3 Cron Schedule Examples

```bash
# Every day at 7:30 AM
30 7 * * * cd /path/to/project && venv/bin/python morning_briefing.py

# Every weekday at 6:00 AM
0 6 * * 1-5 cd /path/to/project && venv/bin/python morning_briefing.py

# Every day at 8:00 AM with custom config
0 8 * * * cd /path/to/project && venv/bin/python morning_briefing.py --config custom.yaml
```

### 6.4 Test Cron Job

To verify your cron job is scheduled:

```bash
# List all cron jobs
crontab -l
```

You can test if cron can run it by temporarily setting it to run in a few minutes:

```bash
# Edit crontab
crontab -e

# Add a test entry (e.g., if current time is 10:45, set it for 10:47)
47 10 * * * cd /path/to/project && venv/bin/python morning_briefing.py --dry-run

# Wait for the scheduled time and check output
ls -l output/

# Remove test entry after verification
crontab -e
```

## Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError: No module named 'X'"

**Solution**: Ensure you're using the virtual environment's Python:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. "ConfigError: Configuration file not found"

**Solution**: Ensure `config.yaml` exists in the project directory:
```bash
ls -l config.yaml
# If missing:
cp config.example.yaml config.yaml
```

#### 3. "WeatherError: Invalid API key"

**Solution**: Verify your OpenWeatherMap API key in `config.yaml`. Note that new API keys can take 10-15 minutes to activate.

#### 4. "CalendarError: credentials.json not found"

**Solution**:
- If using Google Calendar: Download `credentials.json` from Google Cloud Console
- If not using Calendar: This warning is normal and can be ignored

#### 5. "EmailError: Invalid recipient address"

**Solution**:
- Verify SparkPost API key
- Ensure sender domain is verified in SparkPost
- Check recipient email address is valid

#### 6. "RateLimitError" from OpenAI

**Solution**:
- You may have exceeded your API quota
- Check your OpenAI account usage at https://platform.openai.com/usage
- Add billing information if needed

#### 7. Cron job not running

**Solution**:
```bash
# Check cron service is running
sudo systemctl status cron

# Check system logs for cron errors
grep CRON /var/log/syslog

# Verify cron has correct paths (use absolute paths)
crontab -l
```

#### 8. Articles not being summarized

**Solution**:
- Check OpenAI API key is valid
- Verify you have sufficient API credits
- Look in logs for specific error messages
- Try with `--debug` flag for more details

### Checking Logs

```bash
# View main application log
cat logs/morning_briefing.log

# View cron execution log
cat logs/cron.log

# Watch logs in real-time
tail -f logs/morning_briefing.log

# Search for errors
grep ERROR logs/morning_briefing.log
```

## Monitoring

### View Logs

```bash
# Check today's activity
grep "$(date +%Y-%m-%d)" logs/morning_briefing.log

# Check for errors
grep ERROR logs/morning_briefing.log

# Monitor in real-time
tail -f logs/morning_briefing.log
```

### Check API Costs

- **OpenAI**: [https://platform.openai.com/usage](https://platform.openai.com/usage)
- **SparkPost**: Check your account dashboard for email usage
- **OpenWeatherMap**: Check API usage in your account

### Log Rotation

Logs are automatically managed:
- Each run appends to `logs/morning_briefing.log`
- Logs older than `retain_days` (default: 30) are automatically deleted
- You can manually clear logs: `rm logs/*.log`

## Customization

### Add RSS Feeds

Edit `config.yaml` and add feeds to the `news.rss_feeds` list:

```yaml
news:
  rss_feeds:
    - "https://feeds.bbci.co.uk/news/rss.xml"
    - "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
    - "https://techcrunch.com/feed/"          # Tech news
    - "https://www.reddit.com/r/news/.rss"    # Reddit news
    # Add any valid RSS feed URL
```

### Change Briefing Time

Edit your crontab to change the schedule:

```bash
crontab -e

# Change from 7:30 AM to 6:00 AM
0 6 * * * cd /path/to/project && venv/bin/python morning_briefing.py
```

### Customize Email Template

The email template is generated in `modules/email_builder.py`. You can modify:
- Colors and styling (CSS in the `build_email_html` function)
- Layout and sections
- Content formatting

After making changes, test with:
```bash
python morning_briefing.py --dry-run
```

### Adjust Article Count and Summary Length

Edit `config.yaml`:

```yaml
news:
  max_articles: 15        # Fetch more articles (increases cost slightly)
  summary_sentences: 2    # Shorter summaries (reduces cost)
```

## Uninstall

To completely remove the morning briefing system:

```bash
# Remove cron job
crontab -e
# Delete the morning briefing line, save and exit

# Remove project directory
rm -rf /path/to/morning-news-summary

# Optional: Revoke API access
# - OpenAI: Delete API key at https://platform.openai.com/api-keys
# - SparkPost: Delete API key in account settings
# - Google Calendar: Revoke access at https://myaccount.google.com/permissions
# - OpenWeatherMap: Delete API key in account settings
```

## Next Steps

After successful setup:

1. Monitor the first few days to ensure everything works smoothly
2. Adjust RSS feeds to match your interests
3. Fine-tune the number of articles and summary length
4. Consider adding more data sources (stocks, weather alerts, etc.)
5. Customize the email template to your preferences

## Getting Help

If you encounter issues not covered in this guide:

1. Check the logs for detailed error messages
2. Verify all API keys are correct and active
3. Ensure all dependencies are installed
4. Test each component individually (weather, news, email)
5. Run with `--debug` flag for verbose output

For more information, see:
- [README.md](README.md) - Project overview and quick start
- [Design Document](docs/plans/2026-02-06-morning-news-briefing-design.md) - System architecture

Enjoy your automated morning briefings!
