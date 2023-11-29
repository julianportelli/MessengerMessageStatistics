import os
import json
import pandas as pd
from zipfile import ZipFile


def extract_messages_from_folder(folder_path):
    total_message_count = 0
    title = None

    for file_name in os.listdir(folder_path):
        if file_name.startswith("message_") and file_name.endswith(".json"):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                title = data.get("title", None)
                total_message_count += len(data.get("messages", []))

    return title, total_message_count


def process_folder(folder_path):
    chat_data = []

    for folder_name in os.listdir(folder_path):
        folder_path_full = os.path.join(folder_path, folder_name)

        if os.path.isdir(folder_path_full):
            title, message_count = extract_messages_from_folder(folder_path_full)
            if title:
                chat_data.append({"ChatName": title, "MessageCount": message_count})

    return pd.DataFrame(chat_data)


def process_zip(zip_path):
    chat_data = []

    with ZipFile(zip_path, "r") as zip_file:
        for file_info in zip_file.infolist():
            if file_info.filename.startswith(
                "message_"
            ) and file_info.filename.endswith(".json"):
                with zip_file.open(file_info) as file:
                    data = json.load(file)
                    title = data.get("title", None)
                    message_count = len(data.get("messages", []))
                    if title:
                        chat_data.append(
                            {"ChatName": title, "MessageCount": message_count}
                        )

    return pd.DataFrame(chat_data)


def main(folder_path, output_file="output.csv"):
    if not os.path.exists(folder_path) or not os.access(folder_path, os.R_OK):
        print(
            f"Error: The specified folder path '{folder_path}' is either invalid or inaccessible."
        )
        return

    if folder_path.endswith(".zip"):
        df = process_zip(folder_path)
    else:
        inbox_path = os.path.join(
            folder_path, "your_activity_across_facebook/messages/inbox"
        )

        if not os.path.exists(inbox_path) or not os.access(inbox_path, os.R_OK):
            print(
                f"Error: The inbox path '{inbox_path}' is either invalid or inaccessible."
            )
            return

        df = process_folder(inbox_path)

    order_by = input(
        "Do you want to order by 'name' or 'message count'? (Enter 'name', 'message count', or press Enter to skip): "
    ).lower()

    if order_by == "name":
        df = df.sort_values(by="ChatName")
    elif order_by == "message count":
        df = df.sort_values(by="MessageCount")

    # Save DataFrame to a CSV file, overwriting if it already exists
    output_file_path = os.path.join(folder_path, output_file)
    df.to_csv(output_file_path, index=False, mode="w")  # 'w' stands for write mode

    print(f"DataFrame saved to: {output_file_path}")


if __name__ == "__main__":
    folder_path = input("Enter the folder path or zip file path: ")
    main(folder_path)
