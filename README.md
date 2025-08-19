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

### Linux / macOS

```bash
python3 ig_follow_audit.py --zip ~/Downloads/instagram_data.zip --out ./ig_audit_output --title "My IG Audit" --open
```

### Windows (CMD / PowerShell)

```cmd
py ig_follow_audit.py --zip "C:\Users\YourName\Downloads\instagram_data.zip" --out ".\ig_audit_output" --title "My IG Audit" --open
```

Optional arguments:

- `--title "My Instagram Audit"` → set custom title for the HTML report
- `--open` → automatically open the generated HTML report in your browser

## Output

Inside the output directory you will find:

- `instagram_audit_report.html` (interactive clickable report)
- `relations.csv` (full summary)
- `you_follow_they_do_not.csv` (you follow but they don’t follow back)
- `they_follow_you_only.csv` (they follow you but you don’t follow back)
- `mutual.csv` (mutual follows)
- `followers.csv` and `following.csv` (raw parsed data)

## Summary to obtain the ZIP file correctly

1. Go to your Instagram profile menu.  
2. Tap **Settings and Activity** (the icon with three horizontal lines in the top right corner).  
3. In the search bar, type **“Download your information”** and select the corresponding option.  
4. Select **“Download or transfer information”**.  
5. Select your Instagram account and press **Next**.  
6. Select **“Some of your information”**.  
7. In the **Connection** section, select **Followers and following** and press **Next**.  
8. Select **“Download to device”** and press **Next**.  
9. Click on **“Date range”** and select **All time** and **Save**.  
10. Click on **“Format”** and select **JSON**.  
11. Click on **“Create files”**.  
12. Wait for the confirmation email from Instagram.  
13. Download the ZIP file from the email or directly from Instagram.

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
