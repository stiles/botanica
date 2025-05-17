# Botanica

Botanica is a Python-based framework designed to help journalists, newsrooms and data enthusiasts build and manage their data pipelines, or bots. It simplifies the data collection by offering a structured, template-driven ecosystem for:

*   Developing and organizing multiple data scrapers.
*   Automating scraper execution using GitHub Actions for scheduled tasks.
*   Streamlining data uploads to cloud storage (e.g., AWS S3).
*   Maintaining a version-controlled and shareable collection of bots.

Botanica aims to lower the technical barriers to creating robust, automated data gathering workflows. *Note: This is a new project and a work in progress.* 

## Getting Started: Using Botanica as a Template

**Botanica is designed to be used as a GitHub template.** This allows you to quickly create your own repository pre-configured with the Botanica framework, ready for you to add your custom bots.

To get started:
1. Click the **"Use this template"** button located at the top of the Botanica GitHub repository page.
2. Choose **"Create a new repository"**.
3. Give your new repository a name (e.g., `my-botanica-scrapers`).
4. Choose whether to include all branches (usually just the main branch is needed).
5. Click **"Create repository from template"**.

You will now have your own copy of Botanica in your GitHub account. You can then clone it to your local machine and follow the steps below to create and deploy your bots.

### Key features

- **Unified system:** Manage all your scraper projects in one place without needing separate repositories.
- **Automated scheduling:** Use GitHub Actions to run tasks on a regular basis, from hourly to daily updates.
- **Cloud integration:** Easily upload processed data to AWS S3 or other cloud services.
- **Modular design:** Each scraper is self-contained, allowing for easy addition, removal or modification.
- **Secure handling:** Sensitive information like API keys and credentials are securely managed through GitHub Secrets.
- **Flexible and scalable:** Easily extend Botanica with new scrapers, configurations and data workflows.

### Structure

Botanica's structure is designed to keep things organized and straightforward. Each scraper lives in its own folder within `bots`, and the utilities and workflows are kept in their own dedicated directories:

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
    - **AWS profile name:** Specify an AWS profile if you want to use a specific one (optional).
    - **Users/entities:** Provide a list of entities or usernames separated by commas (optional).
    - **Cron schedule:** Define the GitHub Actions cron schedule for your bot (e.g., `0 8 * * *` for daily at 8 AM UTC).

**What this does:**
- Copies the `template_bot` directory and sets up a new bot in `./bots/<your_bot_name>`.
- Updates `config.json` with your specified details.
- **Generates a GitHub Actions workflow file** (e.g., `.github/workflows/<your_bot_name>.yml`) pre-configured with your bot's name and schedule, based on `.github/workflows/template_workflow.yml`.
- Appends a log entry to the `README.md` with your new bot (this feature might be simplified in the script).

### Step 3: Customize the bot's scraping logic
Navigate to the new bot directory:
```bash
cd bots/<your_bot_name>
```
1. **Edit `main.py`:**
   - Replace the placeholder scraping logic with your specific data extraction code. Modify the section marked `CUSTOM SCRAPING LOGIC STARTS HERE`.
   - Use the existing structure for data processing, storage, and upload, so you don't need to worry about file handling or cloud integration.

2. **Edit `config.json` (Optional):**
   - Modify any parameters such as `output_directory`, `timeseries_file`, or `retry_attempts` as needed.
   - Update other settings like query parameters, API endpoints, or user lists.

### Step 4: Test the bot locally
1. **Navigate to the bot's directory:**
    ```bash
    cd bots/<your_bot_name>
    ```
2. **Install any additional dependencies:**
    If your bot requires packages not included in the main project's `requirements.txt` or the base `template_bot/requirements.txt`, add them to your bot's `requirements.txt` file and install:
    ```bash
    pip install -r requirements.txt
    ```
3. **Run the bot:**
    Test your bot locally to ensure everything is working as expected:
    ```bash
    python main.py
    ```

### Step 5: Set up the GitHub actions workflow
The `create_bot.py` script (as of recent updates) now automatically generates the initial GitHub Actions workflow file for your bot (e.g., `.github/workflows/<your_bot_name>.yml`) based on the template found at `.github/workflows/template_workflow.yml`.

1. **Verify the generated workflow:**
    - Open the newly created `.github/workflows/<your_bot_name>.yml`.
    - Check if the `BOT_NAME` and `cron` schedule match what you intended.
    - The workflow is designed to use GitHub Secrets for AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`).

2. **Set up GitHub Secrets:**
    For the workflow to run successfully, especially if it involves AWS services like S3 uploads, you **must** configure the necessary secrets in your GitHub repository:
    - Go to your repository on GitHub.
    - Click on **Settings** > **Secrets and variables** > **Actions**.
    - Click **New repository secret** for each of the following (if your bot needs them):
        - `AWS_ACCESS_KEY_ID`: Your AWS access key ID.
        - `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key.
        - `AWS_DEFAULT_REGION`: The AWS region your resources are in (e.g., `us-east-1`).
    - Ensure these secret names match exactly what's used in the workflow file's `env` section for the `Run the scraper` step.

3. **Push changes to GitHub:**
    After customizing your bot and verifying the workflow, commit and push your changes:
    ```bash
    git add .
    git commit -m "Add new bot: <your_bot_name> and its workflow"
    git push origin main # Or your primary branch
    ```

### Step 6: Verify the bot deployment
1. **Check GitHub Actions:**
    - Navigate to the **Actions** tab in your GitHub repository.
    - Confirm that your new bot's workflow is listed and has successfully run. If there are any errors, check the logs for troubleshooting.

2. **Check the output:**
    - Verify that the processed data is correctly stored in the output directory you specified.
    - Ensure the data has been uploaded to S3 (or your cloud storage), and confirm accessibility if needed.

### Example workflow file (`.github/workflows/example.yml`)
The `create_bot.py` script now generates a bot-specific workflow file (e.g., `<your_bot_name>.yml`) in the `.github/workflows/` directory. This generated file is based on `.github/workflows/template_workflow.yml`. Please refer to the `template_workflow.yml` for the current standard structure.

The template includes:
- Manual trigger (`workflow_dispatch`).
- Scheduled execution based on the cron you provide.
- Python setup and dependency installation.
- Execution of the bot's `main.py`.
- Steps to commit and push data changes back to the repository.
- Use of GitHub Secrets for credentials.

```yaml
# Example content of .github/workflows/template_workflow.yml
# (This is a conceptual snippet; the actual template may evolve)

name: "%%BOT_NAME%%" # Placeholder for the bot's name

on:
  workflow_dispatch:
  schedule:
    - cron: '%%CRON_SCHEDULE%%' # Placeholder for the cron schedule

jobs:
  run-bot:
    runs-on: ubuntu-latest
    env:
      BOT_NAME: "%%BOT_NAME%%"
      BOT_PATH: "./bots/%%BOT_NAME%%"
      PYTHONPATH: "${{ github.workspace }}"
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      # ... other steps for python setup, install, run, commit, push ...
      # Refer to the actual .github/workflows/template_workflow.yml for full details.
```

### Future enhancements:
- **Automated cleanup**: Add a feature to automatically archive or delete old files from S3.
- **Comprehensive error handling**: Improve the bot's codebase to handle more specific errors and retry failed requests.
- **Bot monitoring**: A monitoring system that alerts if a bot encounters repeated failures.
- **Automate inventory collection**: Keep an updated list of bots, metadata and output paths. 
