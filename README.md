# Speechma-API

This repository provides a Python program that uses the Speechma API to convert text into speech. It allows users to select from multiple voices, dialects, and languages, and bypasses the 2000-character limit by splitting the input text into manageable chunks. The program sanitizes the text, handles punctuation for better speech flow, and saves the resulting audio in MP3 format.

## Features

- **Multiple Voice Options:** The program supports multiple voices, genders, and dialects, offering flexibility in audio output.
- **Text Chunking:** The input text is split into chunks to bypass the 2000-character limit imposed by the Speechma API.
- **Input Sanitization:** Non-ASCII characters are removed from the input to ensure compatibility with the API.
- **Punctuation Handling:** Punctuation marks like full stops and commas are handled properly for clearer, more natural speech.
- **Audio Download:** The generated audio is saved as an MP3 file for offline use.
- **Customizable Voice Selection:** Users can choose from a list of available voices, including gender and regional dialect options.
- **Retry Logic:** If an error occurs when processing a chunk, the program automatically retries up to three times.

## Installation

### Prerequisites

- Python 3.x
- `requests` library

### Steps to Install

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/fairy-root/Speechma-API.git
   cd Speechma-API
   ```

2. Install the required dependencies:

   ```bash
   pip install requests
   ```

3. Ensure that the `voices.json` file is present in the root directory. If it's missing or corrupted, you will see an error.

4. Run the script:

   ```bash
   python main.py
   ```

## Usage

- The program will prompt you to enter the text you wish to convert to speech. You can input multiline text by pressing Enter after each line. To finish, type `END` and press Enter.
- You will then be asked to choose the voice you want to use from the available options.
- The program will process the input text, split it into chunks if needed, and send the chunks to the Speechma API for conversion into speech.
- The resulting audio will be saved in MP3 format in the current directory with filenames like `audio_1.mp3`, `audio_2.mp3`, etc.

### Example

```bash
Enter your text (press Enter on an empty line to finish):
This is an example text.
END
Available voices:
1- English UK female Sonia
2- English UK female Maisie
Enter the number of the voice you want to use (1-2):
```

The audio will be saved as `audio_1.mp3`, `audio_2.mp3`, etc.

## Files

- `main.py`: The main script that handles text input, API interaction, and audio saving.
- `voices.json`: A JSON file that contains the available voices and their IDs. Example:

  ```json
  {
    "English": {
      "UK": {
        "female": {
          "Sonia": "voice-35",
          "Maisie": "voice-30"
        }
      }
    }
  }
  ```

## Donation

Your support is appreciated:

- USDt (TRC20): `TGCVbSSJbwL5nyXqMuKY839LJ5q5ygn2uS`
- BTC: `13GS1ixn2uQAmFQkte6qA5p1MQtMXre6MT`
- ETH (ERC20): `0xdbc7a7dafbb333773a5866ccf7a74da15ee654cc`
- LTC: `Ldb6SDxUMEdYQQfRhSA3zi4dCUtfUdsPou`

## Author

- GitHub: [FairyRoot](https://github.com/fairy-root)
- Telegram: [@FairyRoot](https://t.me/FairyRoot)

## Contributing

If you would like to contribute to this project, feel free to fork the repository and submit pull requests. Ensure that your code follows the existing structure, and test it thoroughly.

### TODO

- [ ] Add more voices to the `voices.json` file for additional languages, dialects, and genders.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
