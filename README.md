
# Botanica 🌿

Botanica is a Python-based automation system for collecting, processing and managing data. It's designed to help cultivate a personal collection of data scrapers, or bots, with a shared ecosystem for scheduling, collection and cloud storage. This is a new project and very much a work in progress. 

### Key features

- **Unified system:** Manage all your scraper projects in one place without needing separate repositories.
- **Automated scheduling:** Use GitHub Actions to run tasks on a regular basis, from hourly to daily updates.
- **Cloud integration:** Easily upload processed data to AWS S3 or other cloud services.
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

1. **Add a new bot:** To create a new bot, run the `create_bot.py` script and follow the instructions below for customizing the scripts, configuration files and dependencies it needs.
2. **Set up automation:** Use the GitHub Actions workflow template to schedule your bot. Define when and how often it should run.
3. **Process and upload:** When a bot runs, it processes data and saves it in the `src/data` directory. From there, the utility scripts can help you upload the results to cloud storage like AWS S3.
4. **Manage configurations:** Use your local environment or `.env` files and Github Actions secrets for sensitive information and `config.json` files for bot-specific settings. Example templates are included to make setup easier.


## How to create and deploy a new bot

Creating and deploying a new bot in Botanica is designed to be quick and easy. Follow the steps below to get your new data scraper up and running.

### Step 1: Set up your environment
Before creating a new bot, ensure your environment is set up:
- Python 3.9+ installed
- Required packages installed (`pip install -r requirements.txt`)
- AWS credentials configured if using cloud uploads

### Step 2: Use the automated bot setup script
1. **Run `create_bot.py`:**
    From the root of the project, run the following command:
    ```bash
    python create_bot.py
    ```
2. **Follow the prompts:**
    - **Bot name:** Enter a unique name for your new bot (e.g., `weather_scraper`).
    - **AWS profile name:** Specify an AWS profile if you want to use a specific one (optional). Otherwise, press enter to use default environment credentials.
    - **Users/entities:** Provide a list of entities or usernames separated by commas. This can be customized later.

**What this does:**
- Copies the `template_bot` directory and sets up a new bot in `./bots/<your_bot_name>`.
- Updates `config.json` with your specified details.
- Appends a log entry to the `README.md` with your new bot.

### Step 3: Customize the bot’s scraping logic
Navigate to the new bot directory:
```bash
cd bots/<your_bot_name>
```
1. **Edit `main.py`:**
   - Replace the placeholder scraping logic with your specific data extraction code. Modify the section marked `CUSTOM SCRAPING LOGIC STARTS HERE`.
   - Use the existing structure for data processing, storage, and upload, so you don’t need to worry about file handling or cloud integration.

2. **Edit `config.json` (Optional):**
   - Modify any parameters such as `output_directory`, `timeseries_file`, or `retry_attempts` as needed.
   - Update other settings like query parameters, API endpoints, or user lists.

### Step 4: Test the bot locally
1. **Navigate to the bot’s directory:**
    ```bash
    cd bots/<your_bot_name>
    ```
2. **Install any additional dependencies:**
    If your bot requires packages not included in the main project’s `requirements.txt`, add them to the bot’s `requirements.txt` file and install:
    ```bash
    pip install -r requirements.txt
    ```
3. **Run the bot:**
    Test your bot locally to ensure everything is working as expected:
    ```bash
    python main.py
    ```

### Step 5: Set up the GitHub actions workflow
1. **Create a workflow file:**
    - Copy the `template_bot.yml` file from `.github/workflows/` or duplicate an existing bot’s `.yml` file.
    - Rename it to `<your_bot_name>.yml`.

2. **Customize the workflow:**
    Update the new `.yml` file:
    - **Name:** Change the name to match your bot, e.g., `name: weather_scraper`.
    - **Paths and environment variables:** Ensure that `BOT_NAME`, `BOT_PATH`, and other environment variables reflect your new bot.
    - **Schedule:** Adjust the cron schedule to determine when your bot should run (e.g., daily, hourly).

3. **Push changes to GitHub:**
    After setting up the workflow, commit and push your changes:
    ```bash
    git add .
    git commit -m "Add new bot: <your_bot_name>"
    git push origin main
    ```

### Step 6: Verify the bot deployment
1. **Check GitHub Actions:**
    - Navigate to the **Actions** tab in your GitHub repository.
    - Confirm that your new bot’s workflow is listed and has successfully run. If there are any errors, check the logs for troubleshooting.

2. **Check the output:**
    - Verify that the processed data is correctly stored in the output directory you specified.
    - Ensure the data has been uploaded to S3 (or your cloud storage), and confirm accessibility if needed.

### Example workflow file (`.github/workflows/weather_scraper.yml`)
```yaml
name: example

on:
  workflow_dispatch:
  schedule:
    - cron: '0 6 * * *'  # Runs daily at 6 AM UTC

jobs:
  build:
    runs-on: ubuntu-latest

    env:
      BOT_NAME: "example"
      BOT_PATH: "./bots/example"
      PYTHONPATH: "${{ github.workspace }}"

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r ${{ env.BOT_PATH }}/requirements.txt

      - name: Run the scraper
        run: |
          python ${{ env.BOT_PATH }}/main.py
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_DEFAULT_REGION: 'us-east-1'

      - name: Pull latest changes
        run: |
          git config pull.rebase false
          git pull origin main

      - name: Commit updated data
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add ${{ env.BOT_PATH }}/src/data/
          git commit -m "Updated data" -a --allow-empty --author="stiles <stiles@users.noreply.github.com>"

      - name: Push changes to main branch
        run: |
          git push origin main
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Step 7: Updating the inventory
After creating a new bot, `create_bot.py` will automatically add an entry to the **bots inventory** section in the `README.md`. Here’s an example of what this section might look like:

```markdown
#### Bots inventory
- **tiktok_followers**: Outputs to `./src/data/tiktok_followers`
- **tsla_stock**: Outputs to `./src/data/tsla_stock`
```

### Future enhancements:
- **Automated cleanup**: Add a feature to automatically archive or delete old files from S3.
- **Comprehensive error handling**: Improve the bot’s codebase to handle more specific errors and retry failed requests.
- **Bot monitoring**: Consider setting up a monitoring system that alerts you if any bot encounters repeated failures.
