# Mihon Local Source Manga Metadata Fetcher

This script automatically fetches metadata and cover images for your manga collection to work with Mihon's local source feature.

## Features

- 🔍 Automatically searches for manga metadata using the Jikan API (MyAnimeList)
- 📝 Creates `details.json` files with manga information (title, author, description, genres, status)
- 🖼️ Downloads `cover.jpg` images for each manga
- ✅ Skips manga that already have metadata
- 📊 Provides detailed logging and summary statistics
- ⏱️ Respects API rate limits

## Requirements

- Python 3.6 or higher
- `requests` library

## Installation

1. Install the required Python package:
```bash
pip install requests
```

## Usage

Simply run the script from the manga directory:

```bash
python fetch_metadata.py
```

The script will:
1. Scan all subdirectories in the current folder
2. Search for each manga on MyAnimeList via Jikan API
3. Download metadata and cover images
4. Create `details.json` and `cover.jpg` in each manga folder

## Output Format

### details.json
```json
{
  "title": "20th Century Boys",
  "author": "Urasawa, Naoki",
  "artist": "Urasawa, Naoki",
  "description": "Humanity, having faced extinction at the end of the 20th century...",
  "genre": ["Mystery", "Drama", "Psychological", "Sci-Fi"],
  "status": 2,
  "_status values": [
    "0 = Unknown",
    "1 = Ongoing",
    "2 = Completed",
    "3 = Licensed",
    "4 = Publishing paused",
    "5 = Cancelled",
    "6 = On hiatus"
  ]
}
```

### cover.jpg
High-quality cover image downloaded from MyAnimeList.

## Mihon Compatibility

This script follows the Mihon local source advanced format:
- Reference: https://mihon.app/docs/guides/local-source/advanced

The generated files are compatible with Mihon's local manga reader.

## Data Source

**Jikan API v4** (Unofficial MyAnimeList API)
- Free and open-source
- No authentication required
- Comprehensive manga database
- Rate limit: 3 requests/second, 60 requests/minute
- Website: https://jikan.moe/

## Troubleshooting

### "No results found for: [manga name]"
The manga might not be in MyAnimeList database, or the folder name doesn't match the official title. Try renaming the folder to match the official English or Japanese title.

### Rate Limit Errors
The script includes built-in delays (1 second between requests). If you still encounter rate limits, the script will log the error and continue with the next manga.

### Missing Dependencies
If you get `ModuleNotFoundError: No module named 'requests'`, install it with:
```bash
pip install requests
```

## Customization

You can modify the script to:
- Change the API source (edit `JIKAN_API_BASE`)
- Adjust rate limiting (edit `REQUEST_DELAY`)
- Modify the metadata format (edit `create_details_json` method)
- Add additional fields to details.json

## Example Directory Structure

Before running:
```
manga/
├── fetch_metadata.py
├── 20th Century Boys/
│   ├── Vol.01 Ch.001.cbz
│   └── Vol.01 Ch.002.cbz
└── Berserk/
    ├── Vol.01 Ch.001.cbz
    └── Vol.01 Ch.002.cbz
```

After running:
```
manga/
├── fetch_metadata.py
├── 20th Century Boys/
│   ├── details.json          ← Created
│   ├── cover.jpg             ← Created
│   ├── Vol.01 Ch.001.cbz
│   └── Vol.01 Ch.002.cbz
└── Berserk/
    ├── details.json          ← Created
    ├── cover.jpg             ← Created
    ├── Vol.01 Ch.001.cbz
    └── Vol.01 Ch.002.cbz
```

## License

This script is provided as-is for personal use. Please respect MyAnimeList's terms of service and Jikan API's usage guidelines.

