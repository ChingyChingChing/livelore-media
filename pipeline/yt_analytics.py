#!/usr/bin/env python3
"""Pull Live Lore per-video stats straight from the YouTube Analytics API.

Needs three environment variables (set in the Claude Code environment settings,
never in the repo): YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN.

Usage:
  python3 pipeline/yt_analytics.py            # since 2026-11-07, writes files below
  python3 pipeline/yt_analytics.py --check    # only test the login

Writes:
  pipeline/yt_stats.json      raw numbers (channel by day, per video, retention curves)
  pipeline/analytics_log.csv  fills views / watch_min / avg_view_s / retention_pct /
                              likes / comments / shares for each Short (matched by video ID)
YouTube data lags ~2 days. Uses only the standard library.
"""
import csv, datetime as dt, json, os, re, sys, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
START = "2026-11-07"


def token():
    missing = [k for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN") if not os.environ.get(k)]
    if missing:
        sys.exit("Missing environment variables: " + ", ".join(missing))
    body = urllib.parse.urlencode({
        "client_id": os.environ["YT_CLIENT_ID"],
        "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }).encode()
    with urllib.request.urlopen("https://oauth2.googleapis.com/token", body, timeout=30) as r:
        return json.load(r)["access_token"]


def get(url, params, tok):
    req = urllib.request.Request(url + "?" + urllib.parse.urlencode(params),
                                 headers={"Authorization": "Bearer " + tok})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{e.code} from {url}: {e.read().decode()[:500]}")


def report(tok, **p):
    p.setdefault("ids", "channel==MINE")
    d = get("https://youtubeanalytics.googleapis.com/v2/reports", p, tok)
    cols = [h["name"] for h in d.get("columnHeaders", [])]
    return [dict(zip(cols, row)) for row in d.get("rows", []) or []]


def iso_seconds(s):
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    return sum(int(x or 0) * k for x, k in zip(m.groups(), (3600, 60, 1))) if m else None


def uploads(tok):
    ch = get("https://www.googleapis.com/youtube/v3/channels", {"part": "contentDetails,snippet,statistics", "mine": "true"}, tok)
    item = ch["items"][0]
    pl = item["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, page = [], None
    while True:
        p = {"part": "contentDetails", "playlistId": pl, "maxResults": 50}
        if page:
            p["pageToken"] = page
        d = get("https://www.googleapis.com/youtube/v3/playlistItems", p, tok)
        ids += [i["contentDetails"]["videoId"] for i in d["items"]]
        page = d.get("nextPageToken")
        if not page:
            break
    vids = {}
    for i in range(0, len(ids), 50):
        d = get("https://www.googleapis.com/youtube/v3/videos",
                {"part": "snippet,contentDetails,statistics", "id": ",".join(ids[i:i + 50])}, tok)
        for v in d["items"]:
            vids[v["id"]] = {"title": v["snippet"]["title"], "published": v["snippet"]["publishedAt"],
                             "length_s": iso_seconds(v["contentDetails"]["duration"]),
                             "public_views": int(v["statistics"].get("viewCount", 0))}
    return item["snippet"]["title"], item["statistics"], vids


def main():
    tok = token()
    name, stats, vids = uploads(tok)
    print(f"Logged in: channel '{name}', {stats.get('subscriberCount')} subs, {len(vids)} uploads")
    if "--check" in sys.argv:
        return
    end = dt.date.today().isoformat()
    by_day = report(tok, startDate=START, endDate=end, dimensions="day", sort="day",
                    metrics="views,engagedViews,estimatedMinutesWatched,subscribersGained,subscribersLost")
    per_video = report(tok, startDate=START, endDate=end, dimensions="video", sort="-views", maxResults=200,
                       metrics="views,engagedViews,estimatedMinutesWatched,averageViewDuration,"
                               "averageViewPercentage,likes,comments,shares,subscribersGained")
    curves = {}
    for vid in vids:
        try:
            rows = report(tok, startDate=START, endDate=end, dimensions="elapsedVideoTimeRatio",
                          metrics="audienceWatchRatio,relativeRetentionPerformance", filters=f"video=={vid}")
            curves[vid] = [[r["elapsedVideoTimeRatio"], r["audienceWatchRatio"], r.get("relativeRetentionPerformance")] for r in rows]
        except SystemExit as e:
            curves[vid] = str(e)
    out = {"pulled_at": dt.datetime.now(dt.timezone.utc).isoformat(), "channel": stats, "videos": vids,
           "by_day": by_day, "per_video": per_video, "retention_curves": curves}
    json.dump(out, open(os.path.join(HERE, "yt_stats.json"), "w"), indent=1, ensure_ascii=False)

    pv = {r["video"]: r for r in per_video}
    path = os.path.join(HERE, "analytics_log.csv")
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    fields = list(rows[0].keys())
    for r in rows:
        m = re.search(r"(?:v=|shorts/)([\w-]{11})", r.get("url") or "")
        if not m or m.group(1) not in pv:
            continue
        v, meta = pv[m.group(1)], vids.get(m.group(1), {})
        length = float(r["length_s"]) if r.get("length_s") else meta.get("length_s")
        r["title"] = r["title"] or meta.get("title", "")
        r["length_s"] = r["length_s"] or (str(length) if length else "")
        r["views"], r["watch_min"] = v["views"], round(v["estimatedMinutesWatched"], 1)
        r["avg_view_s"] = v["averageViewDuration"]
        r["retention_pct"] = round(100 * v["averageViewDuration"] / length, 1) if length else ""
        r["likes"], r["comments"], r["shares"] = v["likes"], v["comments"], v["shares"]
        r["last_updated"] = dt.date.today().isoformat()
        r["note"] = (f"YouTube Analytics API (data lags ~2 days). engaged views {v['engagedViews']}, "
                     f"avg view % (YouTube) {v['averageViewPercentage']}, subs gained {v['subscribersGained']}")
    w = csv.DictWriter(open(path, "w", newline="", encoding="utf-8"), fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
    print(f"Per-video rows: {len(per_video)}; days: {len(by_day)}; wrote yt_stats.json and analytics_log.csv")


if __name__ == "__main__":
    main()
