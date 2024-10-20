import os
import shutil
import json

def create_bot():
    # Prompt user for basic details
    bot_name = input("Enter the name of the new bot (e.g., tiktok_followers): ")
    s3_profile = input("Enter the AWS profile name (leave blank to use environment credentials): ") or None
    users = input("Enter usernames separated by commas (e.g., user1,user2): ").split(',')

    # Paths
    template_dir = "./template_bot"
    new_bot_dir = f"./bots/{bot_name}"

    # Copy the template directory to create a new bot directory
    if os.path.exists(new_bot_dir):
        print(f"Error: The bot '{bot_name}' already exists.")
        return

    shutil.copytree(template_dir, new_bot_dir)

    # Update `config.json`
    config_path = os.path.join(new_bot_dir, "config.json")
    with open(config_path, "r") as config_file:
        config = json.load(config_file)

    config["bot_name"] = bot_name
    config["s3_profile"] = s3_profile
    config["users"] = [user.strip() for user in users]
    config["output_directory"] = f"./src/data/{bot_name}"
    config["archive_url"] = f"https://stilesdata.com/{bot_name}/{bot_name}.json"
    config["timeseries_file"] = f"./src/data/{bot_name}_timeseries.json"

    with open(config_path, "w") as config_file:
        json.dump(config, config_file, indent=4)

    # Inform user of success
    print(f"Successfully created new bot '{bot_name}' at '{new_bot_dir}'")

    # Optional: Add to README
    update_readme(bot_name, config["output_directory"])

def update_readme(bot_name, output_directory):
    readme_path = "./README.md"
    log_entry = f"- **{bot_name}**: Outputs to `{output_directory}`\n"

    with open(readme_path, "a") as readme_file:
        readme_file.write(log_entry)

if __name__ == "__main__":
    create_bot()
