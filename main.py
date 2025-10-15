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

# Load voices from voices.json file
def load_voices():
    """Load voice data from voices.json file"""
    try:
        with open('voices.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print_colored("Error: voices.json file not found!", "red")
        return None
    except json.JSONDecodeError as e:
        print_colored(f"Error parsing voices.json: {e}", "red")
        return None

# Recursively display voices in an enumerated format with enhanced information
def display_voices(voices, prefix="", show_ids=False):
    if not voices:
        print_colored("Error: No voices available.", "red")
        return 0

    index = 0
    for key, value in voices.items():
        if isinstance(value, dict):
            new_prefix = f"{prefix}{key} " if prefix else f"{key} "
            count = display_voices(value, new_prefix, show_ids)
            index += count
        else:
            index += 1
            # Format: "1- English UK female Sonia"
            # Optionally show voice ID: "1- English UK female Sonia (voice-35)"
            if show_ids:
                print(f"{index}- {prefix}{key} \033[90m({value})\033[0m")
            else:
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
def get_audio(url, data, headers, cookies=None):
    try:
        json_data = json.dumps(data)
        response = req.post(url, data=json_data, headers=headers, cookies=cookies)
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
def get_multiline_input(prompt="Enter your text (type END on a new line when finished):"):
    print_colored(prompt, "cyan")
    print_colored("(Type your text, then press Enter and type END to finish)", "yellow")
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

# Helper function to count voices at each level
def count_voices_by_level(voices, level=0):
    """Count voices at different hierarchy levels"""
    counts = {}

    def count_recursive(data, current_level=0):
        for key, value in data.items():
            if isinstance(value, dict):
                if current_level == level:
                    # Count voices under this key
                    voice_count = sum(1 for _ in get_all_voice_ids(value))
                    counts[key] = voice_count
                count_recursive(value, current_level + 1)

    count_recursive(voices)
    return counts

# Helper function to get all voice IDs from a nested dict
def get_all_voice_ids(data):
    """Recursively get all voice IDs from nested structure"""
    for key, value in data.items():
        if isinstance(value, dict):
            yield from get_all_voice_ids(value)
        else:
            yield value

# Interactive voice selection with filtering
def select_voice_interactive(voices):
    """
    Interactive voice selection with hierarchical filtering.
    Returns: (voice_id, voice_name) tuple or (None, None) if cancelled

    Hierarchy: Language → Country → Gender → Voice Name
    Special commands: 'b' (back), 'r' (restart), 'voice-XXX' (direct ID)
    """

    while True:
        # Step 1: Select Language
        print_colored("\n" + "="*60, "blue")
        print_colored("STEP 1: Select Language", "blue")
        print_colored("="*60, "blue")

        lang_counts = count_voices_by_level(voices, level=0)
        languages = sorted(lang_counts.keys())

        for i, lang in enumerate(languages, 1):
            count = lang_counts[lang]
            print(f"{i}. {lang} ({count} voices)")

        print_colored("\nType 'voice-XXX' to directly enter a voice ID, or 'q' to quit", "yellow")

        lang_input = input_colored(f"\nSelect language (1-{len(languages)}): ", "green").strip()

        # Handle special inputs
        if lang_input.lower() == 'q':
            return None, None
        if lang_input.startswith('voice-'):
            return lang_input, f"Direct ID: {lang_input}"

        try:
            lang_choice = int(lang_input)
            if lang_choice < 1 or lang_choice > len(languages):
                print_colored("Invalid choice. Please try again.", "red")
                continue
        except ValueError:
            print_colored("Invalid input. Please enter a number.", "red")
            continue

        selected_language = languages[lang_choice - 1]

        # Step 2: Select Country
        while True:
            print_colored("\n" + "="*60, "blue")
            print_colored(f"STEP 2: Select Country ({selected_language})", "blue")
            print_colored("="*60, "blue")

            country_data = voices[selected_language]
            country_counts = count_voices_by_level({selected_language: country_data}, level=1)
            countries = sorted(country_counts.keys())

            for i, country in enumerate(countries, 1):
                count = country_counts[country]
                print(f"{i}. {country} ({count} voices)")

            print_colored("\nType 'b' to go back, 'r' to restart, or 'q' to quit", "yellow")

            country_input = input_colored(f"\nSelect country (1-{len(countries)}): ", "green").strip()

            if country_input.lower() == 'b':
                break  # Go back to language selection
            if country_input.lower() == 'r':
                return select_voice_interactive(voices)  # Restart
            if country_input.lower() == 'q':
                return None, None

            try:
                country_choice = int(country_input)
                if country_choice < 1 or country_choice > len(countries):
                    print_colored("Invalid choice. Please try again.", "red")
                    continue
            except ValueError:
                print_colored("Invalid input. Please enter a number.", "red")
                continue

            selected_country = countries[country_choice - 1]

            # Step 3: Select Gender
            while True:
                print_colored("\n" + "="*60, "blue")
                print_colored(f"STEP 3: Select Gender ({selected_language} - {selected_country})", "blue")
                print_colored("="*60, "blue")

                gender_data = country_data[selected_country]
                genders = sorted(gender_data.keys())

                for i, gender in enumerate(genders, 1):
                    count = len(gender_data[gender])
                    print(f"{i}. {gender.capitalize()} ({count} voices)")

                print_colored("\nType 'b' to go back, 'r' to restart, or 'q' to quit", "yellow")

                gender_input = input_colored(f"\nSelect gender (1-{len(genders)}): ", "green").strip()

                if gender_input.lower() == 'b':
                    break  # Go back to country selection
                if gender_input.lower() == 'r':
                    return select_voice_interactive(voices)  # Restart
                if gender_input.lower() == 'q':
                    return None, None

                try:
                    gender_choice = int(gender_input)
                    if gender_choice < 1 or gender_choice > len(genders):
                        print_colored("Invalid choice. Please try again.", "red")
                        continue
                except ValueError:
                    print_colored("Invalid input. Please enter a number.", "red")
                    continue

                selected_gender = genders[gender_choice - 1]

                # Step 4: Select Voice Name
                while True:
                    print_colored("\n" + "="*60, "blue")
                    print_colored(f"STEP 4: Select Voice", "blue")
                    print_colored(f"{selected_language} - {selected_country} - {selected_gender.capitalize()}", "cyan")
                    print_colored("="*60, "blue")

                    voice_names = gender_data[selected_gender]
                    sorted_names = sorted(voice_names.keys())

                    # Ask if user wants to see voice IDs
                    show_ids_input = input_colored("\nShow voice IDs? (y/n, default: n): ", "blue").lower().strip()

                    # Handle navigation commands at the ID prompt
                    if show_ids_input == 'b':
                        break  # Go back to gender selection
                    if show_ids_input == 'r':
                        return select_voice_interactive(voices)  # Restart
                    if show_ids_input == 'q':
                        return None, None

                    show_ids = show_ids_input == 'y'

                    print()
                    for i, name in enumerate(sorted_names, 1):
                        voice_id = voice_names[name]
                        if show_ids:
                            print(f"{i}. {name} \033[90m({voice_id})\033[0m")
                        else:
                            print(f"{i}. {name}")

                    print_colored("\nType 'b' to go back, 'r' to restart, or 'q' to quit", "yellow")

                    voice_input = input_colored(f"\nSelect voice (1-{len(sorted_names)}): ", "green").strip()

                    if voice_input.lower() == 'b':
                        break  # Go back to gender selection
                    if voice_input.lower() == 'r':
                        return select_voice_interactive(voices)  # Restart
                    if voice_input.lower() == 'q':
                        return None, None

                    try:
                        voice_choice = int(voice_input)
                        if voice_choice < 1 or voice_choice > len(sorted_names):
                            print_colored("Invalid choice. Please try again.", "red")
                            continue
                    except ValueError:
                        print_colored("Invalid input. Please enter a number.", "red")
                        continue

                    selected_name = sorted_names[voice_choice - 1]
                    selected_voice_id = voice_names[selected_name]

                    # Show final selection
                    print_colored("\n" + "="*60, "green")
                    print_colored("✓ Voice Selected!", "green")
                    print_colored("="*60, "green")
                    print(f"Language: {selected_language}")
                    print(f"Country: {selected_country}")
                    print(f"Gender: {selected_gender.capitalize()}")
                    print(f"Voice: {selected_name}")
                    print(f"Voice ID: {selected_voice_id}")
                    print_colored("="*60, "green")

                    return selected_voice_id, selected_name

# Function to count voices in the hierarchical structure
def count_voice_stats(voices):
    stats = {
        'total': 0,
        'languages': set(),
        'countries': set(),
        'genders': set()
    }

    def count_recursive(data, level=0):
        for key, value in data.items():
            if isinstance(value, dict):
                if level == 0:  # Language level
                    stats['languages'].add(key)
                elif level == 1:  # Country level
                    stats['countries'].add(key)
                elif level == 2:  # Gender level
                    stats['genders'].add(key)
                count_recursive(value, level + 1)
            else:
                stats['total'] += 1

    count_recursive(voices)
    return stats

# Main function
def main():
    voices = load_voices()
    if not voices:
        print_colored("Error: No voices available. Exiting.", "red")
        return

    # Display statistics
    stats = count_voice_stats(voices)
    print_colored("=" * 60, "cyan")
    print_colored("🎤 Speechma Text-to-Speech", "magenta")
    print_colored("=" * 60, "cyan")
    print_colored(f"📊 Voice Library: {stats['total']} voices", "yellow")
    print(f"   • {len(stats['languages'])} languages")
    print(f"   • {len(stats['countries'])} countries")
    print_colored("=" * 60, "cyan")

    # Use interactive voice selection
    voice_id, voice_name = select_voice_interactive(voices)
    if not voice_id:
        print_colored("Voice selection cancelled. Exiting.", "yellow")
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

    # IMPORTANT: You need to get cookies from your browser after visiting speechma.com
    # Instructions:
    # 1. Visit https://speechma.com in your browser
    # 2. Complete any CAPTCHA/bot check
    # 3. Open Developer Tools (F12) > Application tab > Cookies > speechma.com
    # 4. Copy the cookie values and add them here
    # Example: cookies = {'cf_clearance': 'your_token_here', '__cfruid': 'your_token_here'}
    cookies = None  # Set this to a dictionary with your cookies to bypass 403 errors

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
            response = get_audio(url, data, headers, cookies)
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
