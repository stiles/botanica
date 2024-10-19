
# Botanica 🌿

Botanica is a modern, Python-based automation system for collecting, processing and managing data. It's designed to allow a personal collection of data projects, or bots, to thrive thanks to a shared ecosystem that handles automated scheduling, data wrangling and cloud storage. 

### Key features

- **Unified system:** Manage all your scraper projects in one place without needing separate repositories.
- **Automated scheduling:** Use GitHub Actions to run tasks on a regular basis, from hourly to daily updates.
- **Seamless cloud integration:** Easily upload processed data to AWS S3 or other cloud services.
- **Modular design:** Each scraper is self-contained, allowing for easy addition, removal or modification.
- **Secure handling:** Sensitive information like API keys and credentials are securely managed through GitHub Secrets.
- **Flexible and scalable:** Easily extend Botanica with new scrapers, configurations and data workflows.

### Structure

Botanica’s structure is designed to keep things organized and straightforward. Each scraper lives in its own folder within `bots`, and the utilities and workflows are kept in their own dedicated directories:

```
botanica/
├── bots/
│   └── example/
│       ├── src/
│       │    └── data/               # Where processed data is stored
│       ├── config.example.json      # Template for bot-specific settings
│       ├── requirements.txt         # Dependencies for the bot
│       ├── runbot.sh                # Script to run the bot
│       └── main.py                  # Main script for the bot
├── .github/
│   └── workflows/
│       └── example-scraper.yml      # GitHub Action for automating tasks
├── utils/
│   ├── s3_upload.py                 # Utility script for S3 uploads
│   └── logs/                        # Directory for logs or temp files
└── .env.example                     # Example environment variables template
```

### How it works

1. **Add a new bot:** To create a new bot, add a new folder under `bots`, following the structure of the `example` bot. Include any scripts, configuration files and dependencies it needs.
2. **Set up automation:** Use the GitHub Actions workflow template to schedule your bot. Define when and how often it should run.
3. **Process and upload:** When a bot runs, it processes data and saves it in the `src/data` directory. From there, the utility scripts can help you upload the results to cloud storage like AWS S3.
4. **Manage configurations:** Use `.env` files for sensitive information and `config.json` files for bot-specific settings. Example templates are included to make setup easier.

