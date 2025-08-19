#!/usr/bin/env python3
import argparse
import csv
import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path

# Try pandas - fall back gracefully if unavailable
try:
    import pandas as pd
except Exception:
    pd = None

HTML_STYLE = """
body{font-family:system-ui,Arial,sans-serif;max-width:1100px;margin:24px auto;padding:0 12px}
h1{font-size:22px}
h2{font-size:18px;margin-top:24px}
.summary{padding:10px 12px;border:1px solid #ddd;border-radius:10px;background:#fafafa}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}
section.card{border:1px solid #e4e4e4;border-radius:14px;padding:12px 14px;background:#fff;box-shadow:0 1px 2px rgba(0,0,0,.04)}
/* grid-based list instead of CSS columns */
ul.cols{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(220px,1fr));
  gap:10px;
  list-style:none;
  padding:0;
  margin:0;
}
ul.cols li{
  direction:ltr;               /* keep @user left-to-right */
  white-space:nowrap;          /* single clean line per user */
  overflow:hidden;             /* no ugly wrapping */
  text-overflow:ellipsis;      /* show … if too long */
  line-height:1.35;
  padding:6px 8px;
  border-radius:8px;
  background:#f9f9f9;
  border:1px solid #eee;
}
ul.cols li a{
  text-decoration:none;
}
.badge{display:inline-block;font-size:12px;padding:2px 8px;border-radius:999px;border:1px solid #ddd;background:#fff;margin-right:6px}
.search{margin:10px 0}
input[type="search"]{width:100%;padding:8px 10px;border:1px solid #ccc;border-radius:10px}
.hidden{display:none}
.small{color:#666;font-size:12px}
"""

HTML_SCRIPT = """
<script>
function setupFilter(sectionId){
  const input = document.querySelector('#'+sectionId+' input[type=search]');
  const lis = document.querySelectorAll('#'+sectionId+' li');
  input.addEventListener('input', function(){
    const q = this.value.toLowerCase();
    let shown = 0;
    lis.forEach(li => {
      const u = (li.getAttribute('data-u') || '').toLowerCase();
      const show = u.includes(q);
      li.style.display = show ? '' : 'none';
      if(show) shown++;
    });
    const count = document.querySelector('#'+sectionId+' .count');
    if(count) count.innerText = shown;
  });
}

['you_follow_they_do_not','they_follow_you_only','mutual'].forEach(setupFilter);
</script>
"""

def safe_get(entry, key, idx=0, field="value"):
    try:
        return entry.get("string_list_data", [])[idx].get(field)
    except Exception:
        return None

def load_from_zip(zip_path: Path, work_dir: Path):
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(work_dir)
    base = work_dir / "connections" / "followers_and_following"
    if not base.exists():
        raise FileNotFoundError("Could not find connections/followers_and_following in the ZIP")
    followers_files = sorted(base.glob("followers_*.json"))
    following_file = base / "following.json"
    if not following_file.exists():
        raise FileNotFoundError("following.json not found in the ZIP at connections/followers_and_following")
    followers = set()
    followers_rows = []
    for fpath in followers_files:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            for entry in data:
                username = safe_get(entry, "string_list_data")
                ts = safe_get(entry, "string_list_data", field="timestamp")
                if username:
                    followers.add(username)
                    followers_rows.append({"username": username, "follow_ts": ts})

    with open(following_file, "r", encoding="utf-8") as f:
        following_json = json.load(f)

    following = set()
    following_rows = []
    for entry in following_json.get("relationships_following", []):
        username = safe_get(entry, "string_list_data")
        ts = safe_get(entry, "string_list_data", field="timestamp")
        if username:
            following.add(username)
            following_rows.append({"username": username, "follow_ts": ts})

    return followers, followers_rows, following, following_rows

def write_csv_rows(path: Path, rows, headers=("username","follow_ts")):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for r in rows:
            w.writerow({h: r.get(h) for h in headers})

def build_relation_rows(followers: set, following: set):
    all_users = sorted(followers.union(following))
    rows = []
    for u in all_users:
        fy = u in followers
        yf = u in following
        if fy and yf:
            rel = "mutual"
        elif yf and not fy:
            rel = "you_follow_they_do_not"
        elif fy and not yf:
            rel = "they_follow_you_only"
        else:
            rel = "unknown"
        rows.append({
            "username": u,
            "follows_you": fy,
            "you_follow": yf,
            "relation": rel,
            "profile_url": f"https://instagram.com/{u}"
        })
    return rows

def subset(rows, relation):
    return [r for r in rows if r["relation"] == relation]

def html_list(section_id, title, items):
    lis = "\n".join([f"<li data-u=\"{r['username']}\"><a href=\"{r['profile_url']}\" target=\"_blank\">@{r['username']}</a></li>" for r in items])
    return f"""
<section id="{section_id}" class="card">
  <div class="search"><input type="search" placeholder="Search by username..."></div>
  <h2>{title} - <span class="count">{len(items)}</span></h2>
  <ul class="cols">{lis}</ul>
</section>
"""

def write_html(out_html: Path, title: str, followers: set, following: set, rows: list):
    mutual = subset(rows, "mutual")
    you_not = subset(rows, "you_follow_they_do_not")
    they_not = subset(rows, "they_follow_you_only")

    out_html.parent.mkdir(parents=True, exist_ok=True)
    with open(out_html, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>")
        f.write(f"<title>{title}</title>")
        f.write("<style>"+HTML_STYLE+"</style>")
        f.write("</head><body>")
        f.write(f"<h1>{title}</h1>")
        f.write(f"<div class='summary'><span class='badge'>followers: {len(followers)}</span>"
                f"<span class='badge'>following: {len(following)}</span>"
                f"<span class='badge'>mutual: {len(mutual)}</span>"
                f"<span class='badge'>you follow - they do not: {len(you_not)}</span>"
                f"<span class='badge'>they follow you only: {len(they_not)}</span>"
                f"<div class='small'>Click any username to open their profile in a new tab</div>"
                f"</div>")
        f.write("<div class='grid'>")
        f.write(html_list("you_follow_they_do_not", "You follow - they do not", you_not))
        f.write(html_list("they_follow_you_only", "They follow you - you do not follow back", they_not))
        f.write(html_list("mutual", "Mutual follows", mutual))
        f.write("</div>")
        f.write(HTML_SCRIPT)
        f.write("</body></html>")

def main():
    ap = argparse.ArgumentParser(description="Instagram followers vs following audit")
    ap.add_argument("--zip", required=True, help="Path to Instagram Data Download ZIP")
    ap.add_argument("--out", required=False, default="ig_audit_output", help="Output directory")
    ap.add_argument("--title", required=False, default="Instagram followers-following audit", help="Report title")
    ap.add_argument("--open", action="store_true", help="Attempt to open the HTML after generation")
    args = ap.parse_args()

    zip_path = Path(args.zip).expanduser().resolve()
    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpd:
        tmp = Path(tmpd)
        followers, followers_rows, following, following_rows = load_from_zip(zip_path, tmp)

    # Save raw CSVs
    write_csv_rows(out_dir / "followers.csv", followers_rows)
    write_csv_rows(out_dir / "following.csv", following_rows)

    # Relations table
    rows = build_relation_rows(followers, following)

    # CSV for relations - with or without pandas
    rel_csv = out_dir / "relations.csv"
    headers = ["username","follows_you","you_follow","relation","profile_url"]
    if pd is not None:
        df = pd.DataFrame(rows, columns=headers)
        relation_order = {"you_follow_they_do_not": 0, "they_follow_you_only": 1, "mutual": 2, "unknown": 9}
        df["relation_rank"] = df["relation"].map(relation_order).fillna(9)
        df = df.sort_values(["relation_rank","username"]).drop(columns=["relation_rank"])
        df.to_csv(rel_csv, index=False, encoding="utf-8")
        df[df["relation"]=="you_follow_they_do_not"].to_csv(out_dir / "you_follow_they_do_not.csv", index=False, encoding="utf-8")
        df[df["relation"]=="they_follow_you_only"].to_csv(out_dir / "they_follow_you_only.csv", index=False, encoding="utf-8")
        df[df["relation"]=="mutual"].to_csv(out_dir / "mutual.csv", index=False, encoding="utf-8")
    else:
        with open(rel_csv, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=headers)
            w.writeheader()
            for r in rows:
                w.writerow({h: r.get(h) for h in headers})
        for name in ("you_follow_they_do_not","they_follow_you_only","mutual"):
            sub = [r for r in rows if r["relation"]==name]
            with open(out_dir / f"{name}.csv", "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=headers)
                w.writeheader()
                for r in sub:
                    w.writerow({h: r.get(h) for h in headers})

    html_path = out_dir / "instagram_audit_report.html"
    write_html(html_path, args.title, followers, following, rows)

    print("Done")
    print("Output directory:", out_dir)
    print("HTML report:", html_path)
    print("CSV summary:", rel_csv)

    if args.open:
        try:
            import webbrowser
            webbrowser.open(html_path.as_uri())
        except Exception:
            pass

if __name__ == "__main__":
    main()
