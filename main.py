import requests as req
import json
import sys
import os
from datetime import datetime
from typing import Dict

# Function to print colored text
def print_colored(text: str, color: str) -> None:
    """
    Print colored text.

    Args:
        text: Text to be printed.
        color: Color to be applied to the text.
    """
    colors: Dict[str, str] = {
        "green": "\033[92m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "yellow": "\033[93m",
        "cyan": "\033[96m",
        "magenta": "\033[95m"
    }
    color_code: str = colors.get(color.lower(), "\033[0m")
    colored_text: str = f"{color_code}{text}\033[0m"
    print(colored_text)

# Function to get user input with colored prompt
def input_colored(prompt: str, color: str) -> str:
    """
    Get user input with colored prompt.

    Args:
        prompt: Prompt to be displayed to the user.
        color: Color of the prompt.

    Returns:
        User input.
    """
    colors: Dict[str, str] = {
        "green": "\033[92m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "yellow": "\033[93m",
        "cyan": "\033[96m",
        "magenta": "\033[95m"
    }
    color_code: str = colors.get(color.lower(), "\033[0m")
    colored_prompt: str = f"{color_code}{prompt}\033[0m"
    return input(colored_prompt)

# Load voices from the JSON file
def load_voices():
    try:
        with open('voices.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print_colored("Error: voices.json file not found.", "red")
        return {}
    except json.JSONDecodeError:
        print_colored("Error: voices.json is not a valid JSON file.", "red")
        return {}

# Recursively display voices in an enumerated format
def display_voices(voices, prefix=""):
    if not voices:
        print_colored("Error: No voices available.", "red")
        return 0

    index = 0
    for key, value in voices.items():
        if isinstance(value, dict):
            new_prefix = f"{prefix}{key} " if prefix else f"{key} "
            count = display_voices(value, new_prefix)
            index += count
        else:
            index += 1
            print(f"{index}- {prefix}{key}")
    return index

# Recursively get the selected voice ID based on user input
def get_voice_id(voices, choice, current_index=0):
    for key, value in voices.items():
        if isinstance(value, dict):
            result, current_index = get_voice_id(value, choice, current_index)
            if result:
                return result, current_index
        else:
            current_index += 1
            if current_index == choice:
                return value, current_index
    return None, current_index

# Function to get audio from the server
def get_audio(url, data, headers):
    try:
        json_data = json.dumps(data)
        response = req.post(url, data=json_data, headers=headers)
        response.raise_for_status()
        if response.headers.get('Content-Type') == 'audio/mpeg':
            return response.content
        else:
            print_colored(f"Unexpected response format: {response.headers.get('Content-Type')}", "red")
            return None
    except req.exceptions.RequestException as e:
        if e.response:
            print_colored(f"Server response: {e.response.text}", "red")
        print_colored(f"Request failed: {e}", "red")
        return None
    except Exception as e:
        print_colored(f"An unexpected error occurred: {e}", "red")
        return None

# Function to save audio to a file
def save_audio(response, directory, chunk_num):
    if response:
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, f"audio_chunk_{chunk_num}.mp3")
        try:
            with open(file_path, 'wb') as f:
                f.write(response)
            print_colored(f"Audio saved to {file_path}", "green")
        except IOError as e:
            print_colored(f"Error saving audio: {e}", "red")
    else:
        print_colored("No audio data to save", "red")

# Function to split text into chunks
def split_text(text, chunk_size=1000):
    if not text:
        print_colored("Error: No text provided to split.", "red")
        return []

    chunks = []
    while len(text) > 0:
        if len(text) <= chunk_size:
            chunks.append(text)
            break
        chunk = text[:chunk_size]
        last_full_stop = chunk.rfind('.')
        last_comma = chunk.rfind(',')
        split_index = last_full_stop if last_full_stop != -1 else last_comma
        if split_index == -1:
            split_index = chunk_size
        else:
            split_index += 1
        chunks.append(text[:split_index])
        text = text[split_index:].lstrip()
    return chunks

# Function to validate text
def validate_text(text):
    return ''.join(char for char in text if ord(char) < 128)

# Function to get multiline input
def get_multiline_input(prompt="Enter your text (press Enter on an empty line to finish):"):
    print_colored(prompt, "cyan")
    lines = []
    while True:
        line = input()
        if line == "END":
            break
        lines.append(line)
    return " ".join(lines)

# Function to prompt for graceful exit
def prompt_graceful_exit():
    while True:
        choice = input_colored("\nDo you want to exit? (y/n): ", "blue").lower()
        if choice == "y":
            print_colored("Exiting gracefully...", "magenta")
            sys.exit(0)
        elif choice == "n":
            return
        else:
            print_colored("Invalid choice. Please enter 'y' or 'n'.", "red")

# Main function
def main():
    voices = load_voices()
    if not voices:
        print_colored("Error: No voices available. Exiting.", "red")
        return

    print_colored("Available voices:", "blue")
    total_voices = display_voices(voices)

    try:
        choice = int(input_colored(f"Enter the number of the voice you want to use (1-{total_voices}): ", "green"))
        if choice < 1 or choice > total_voices:
            print_colored("Error: Invalid choice. Please enter a valid number.", "red")
            return
    except ValueError:
        print_colored("Error: Invalid input. Please enter a number.", "red")
        return

    voice_id, _ = get_voice_id(voices, choice)
    if not voice_id:
        print_colored("Error: Invalid voice choice. Exiting.", "red")
        return

    text = get_multiline_input().replace("  ", " ")
    
    if not text:
        print_colored("Error: No text provided. Exiting.", "red")
        return
    elif len(text) <= 9 :
        print_colored("Error: The text must be more than 9 characters. Exiting.", "red")
        return

    text = validate_text(text)

    url = 'https://speechma.com/com.api/tts-api.php'
    headers = {
        'Host': 'speechma.com',
        'Sec-Ch-Ua-Platform': 'Windows',
        'Accept-Language': 'en-US,en;q=0.9',
        'Sec-Ch-Ua': '"Chromium";v="131", "Not_A Brand";v="24"',
        'Content-Type': 'application/json',
        'Sec-Ch-Ua-Mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36',
        'Accept': '*/*',
        'Origin': 'https://speechma.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://speechma.com/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Priority': 'u=1, i'
    }

    chunks = split_text(text, chunk_size=1000)
    if not chunks:
        print_colored("Error: Could not split text into chunks. Exiting.", "red")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    directory = os.path.join("audio", timestamp)
    
    for i, chunk in enumerate(chunks, start=1):
        print_colored(f"\nProcessing chunk {i}...", "yellow")
        data = {
            "text": chunk.replace("'", "").replace('"', '').replace("&", "and"),
            "voice": voice_id
        }

        max_retries = 3
        for retry in range(max_retries):
            response = get_audio(url, data, headers)
            if response:
                save_audio(response, directory, i)
                break
            else:
                print_colored(f"Retry {retry + 1} for chunk {i}...", "yellow")
        else:
            print_colored(f"Failed to process chunk {i} after {max_retries} retries.", "red")

    prompt_graceful_exit()

# Main execution
if __name__ == "__main__":
    try:
        while True:
            main()
    except KeyboardInterrupt:
        print_colored("\nExiting gracefully...", "yellow")
        sys.exit(0)
