# Instagram Followers vs Following Audit

This project provides a **Python script** to analyze your Instagram Data Download (ZIP) and generate reports showing:

- Who you follow that does not follow you back
- Who follows you but you do not follow back
- Mutual followers (both follow each other)
- Complete CSV and interactive HTML report

## Features

- Input: Instagram Data Download ZIP file (export from Instagram privacy settings)
- Output:
  - `instagram_audit_report.html` – interactive report with search, filters, and links to profiles
  - `relations.csv` – combined summary table
  - `you_follow_they_do_not.csv` – accounts you follow but who do not follow you back
  - `they_follow_you_only.csv` – accounts that follow you but you do not follow them
  - `mutual.csv` – mutual follows
  - Raw `followers.csv` and `following.csv`
- Works with or without `pandas` installed (pandas recommended)

## Requirements

- Python 3.8+
- (Optional but recommended) pandas

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Download your Instagram Data ZIP file from [Instagram Data Download](https://www.instagram.com/download/request/).  
   Make sure to select **JSON format**.

2. Run the script:

```bash
python ig_follow_audit.py --zip path/to/instagram.zip --out ./ig_audit_output
```

Optional arguments:

- `--title "My Instagram Audit"` → set custom title for the HTML report
- `--open` → automatically open the generated HTML report in your browser

Example:

```bash
python ig_follow_audit.py --zip ~/Downloads/instagram-danel.zip --out ./results --title "Danel Instagram Audit" --open
```

## Output

Inside the output directory you will find:

- `instagram_audit_report.html` (interactive clickable report)
- `relations.csv` (full summary)
- `you_follow_they_do_not.csv` (you follow but they don’t follow back)
- `they_follow_you_only.csv` (they follow you but you don’t follow back)
- `mutual.csv` (mutual follows)
- `followers.csv` and `following.csv` (raw parsed data)

## Example Screenshot

*(You can add a screenshot of the HTML report here)*

## Project Structure

```
.
├── ig_follow_audit.py       # Main script
├── requirements.txt         # Dependencies (pandas)
└── README.md                # Documentation
```

## License

This project is released under the MIT License.

---

### Author
Created by **Danel Schwartz**
