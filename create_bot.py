import os
import json
import shutil

# Constants
TEMPLATE_BOT_DIR = "template_bot"
BOTS_DIR = "bots"
CONFIG_FILENAME = "config.json"
WORKFLOW_TEMPLATE_PATH = os.path.join(".github", "workflows", "template_workflow.yml")
WORKFLOW_DIR = os.path.join(".github", "workflows")
README_LOG_ENTRY_TEMPLATE = "- Bot '%%BOT_NAME%%' created on %%DATE%%. AWS Profile: %%AWS_PROFILE%%, Users: %%USERS%%, Schedule: %%CRON_SCHEDULE%%\n"
TEMPLATE_CRON_PLACEHOLDER = '0 0 1 1 *' # This is the placeholder in template_workflow.yml

def create_bot():
    print("Welcome to the Botanica Bot Creator!")

    # --- Get Bot Name ---
    while True:
        bot_name = input("Enter a unique name for your new bot (e.g., 'weather_scraper', use underscores for spaces): ").strip().lower().replace(" ", "_")
        new_bot_path = os.path.join(BOTS_DIR, bot_name)
        if not bot_name:
            print("Bot name cannot be empty.")
        elif os.path.exists(new_bot_path):
            print(f"A bot named '{bot_name}' already exists. Please choose a different name.")
        else:
            break

    # --- Get AWS Profile Name ---
    aws_profile_name = input("Enter your AWS profile name (leave blank for default/environment variables): ").strip()
    if not aws_profile_name:
        aws_profile_name = "default (or environment variables)"

    # --- Get Users/Entities ---
    users_input = input("Enter a comma-separated list of users or entities for this bot (e.g., 'user1,user2'): ").strip()
    users_list = [user.strip() for user in users_input.split(',') if user.strip()] if users_input else []

    # --- Get Cron Schedule for GitHub Actions ---
    default_cron = "0 8 * * *"  # Default: 8 AM UTC daily
    cron_schedule = input(f"Enter the cron schedule for GitHub Actions (e.g., '0 8 * * *', default is '{default_cron}' for daily at 8 AM UTC): ").strip()
    if not cron_schedule: # Basic validation, more complex validation could be added
        cron_schedule = default_cron
    elif len(cron_schedule.split()) != 5:
        print(f"Warning: Cron schedule '{cron_schedule}' might not be valid. Using it anyway. A typical cron has 5 parts.")

    # --- Create Bot Directory Structure ---
    try:
        shutil.copytree(TEMPLATE_BOT_DIR, new_bot_path)
        print(f"Successfully copied template from '{TEMPLATE_BOT_DIR}' to '{new_bot_path}'.")
    except Exception as e:
        print(f"Error copying template directory: {e}")
        return

    # --- Update config.json ---
    config_path = os.path.join(new_bot_path, CONFIG_FILENAME)
    if not os.path.exists(config_path):
        # If template_bot/config.json was named config.example.json, rename it
        example_config_path = os.path.join(new_bot_path, "config.example.json")
        if os.path.exists(example_config_path):
            os.rename(example_config_path, config_path)
            print(f"Renamed '{example_config_path}' to '{config_path}'.")
        else:
            print(f"Error: Template config file not found at '{config_path}' or as 'config.example.json'. Please create it manually.")
            # Create a minimal config if missing
            config_data = {}
    else:
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
        except Exception as e:
            print(f"Error reading '{config_path}': {e}. Starting with an empty configuration.")
            config_data = {}

    config_data["bot_name"] = bot_name
    config_data["s3_profile"] = aws_profile_name if aws_profile_name != "default (or environment variables)" else ""
    config_data["users"] = users_list
    # Add or update other default fields if necessary
    config_data.setdefault("output_directory", f"./src/data/{bot_name}")
    config_data.setdefault("archive_url", f"https://stilesdata.com/{bot_name}/{bot_name}.json") # Example, adjust as needed
    config_data.setdefault("timeseries_file", f"./src/data/{bot_name}_timeseries.json")
    config_data.setdefault("retry_attempts", 3)

    try:
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=4)
        print(f"Successfully updated '{config_path}' with bot-specific details.")
    except Exception as e:
        print(f"Error writing to '{config_path}': {e}")

    # --- Create GitHub Actions Workflow File ---
    if not os.path.exists(WORKFLOW_TEMPLATE_PATH):
        print(f"Error: GitHub Actions workflow template not found at '{WORKFLOW_TEMPLATE_PATH}'. Skipping workflow creation.")
    else:
        try:
            with open(WORKFLOW_TEMPLATE_PATH, 'r') as f_template:
                workflow_content = f_template.read()
            
            workflow_content = workflow_content.replace("%%BOT_NAME%%", bot_name)
            # Replace the specific cron placeholder string with the desired cron schedule
            workflow_content = workflow_content.replace(TEMPLATE_CRON_PLACEHOLDER, cron_schedule)

            new_workflow_filename = f"{bot_name}.yml"
            new_workflow_path = os.path.join(WORKFLOW_DIR, new_workflow_filename)
            
            os.makedirs(WORKFLOW_DIR, exist_ok=True)
            with open(new_workflow_path, 'w') as f_new_workflow:
                f_new_workflow.write(workflow_content)
            print(f"Successfully created GitHub Actions workflow at '{new_workflow_path}' with schedule '{cron_schedule}'.")
            print("Remember to set up necessary secrets (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION) in your GitHub repository settings!")

        except Exception as e:
            print(f"Error creating GitHub Actions workflow: {e}")

    # --- Update README.md log (Optional) ---
    try:
        from datetime import datetime
        log_entry = README_LOG_ENTRY_TEMPLATE.replace("%%BOT_NAME%%", bot_name)
        log_entry = log_entry.replace("%%DATE%%", datetime.now().strftime("%Y-%m-%d"))
        log_entry = log_entry.replace("%%AWS_PROFILE%%", aws_profile_name)
        log_entry = log_entry.replace("%%USERS%%", ", ".join(users_list) if users_list else "N/A")
        log_entry = log_entry.replace("%%CRON_SCHEDULE%%", cron_schedule)
        
        # This part assumes a specific structure in README.md, e.g., a line like "<!-- BOT_LOG_START -->"
        # For simplicity, we'll just append to a dedicated log file or print it.
        # print(f"Log Entry: {log_entry}") 
        # If you want to append to README, you'll need more complex file manipulation.
        # For now, let's assume it's appended to a changelog or similar, or just printed.
    except Exception as e:
        print(f"Note: Could not generate README log entry: {e}")

    print(f"\nBot '{bot_name}' created successfully!")
    print("Next steps:")
    print(f"1. Customize the scraping logic in '{os.path.join(new_bot_path, 'main.py')}'.")
    print(f"2. Add any bot-specific dependencies to '{os.path.join(new_bot_path, 'requirements.txt')}' and run 'pip install -r {os.path.join(new_bot_path, 'requirements.txt')}'.")
    print(f"3. Test your bot locally: python {os.path.join(new_bot_path, 'main.py')}")
    print(f"4. Commit the new bot files and the workflow file ('{os.path.join(WORKFLOW_DIR, new_workflow_filename) if 'new_workflow_filename' in locals() else 'workflow file'}') to your repository.")
    print("5. Ensure GitHub Actions secrets (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION) are set in your repository settings.")

if __name__ == "__main__":
    create_bot()
