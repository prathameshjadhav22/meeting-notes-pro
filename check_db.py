from database import MeetingDatabase

db = MeetingDatabase()
meetings = db.get_all_meetings()

print("=" * 60)
print(f"Total meetings in database: {len(meetings)}")
print("=" * 60)

for meeting in meetings:
    mid, title, date, duration = meeting
    print(f"\nID: {mid}")
    print(f"Title: {title}")
    print(f"Date: {date}")
    print(f"Duration: {duration}s")
    
    # Get full details
    full = db.get_meeting(mid)
    if full:
        print(f"Has transcript: {len(full[4]) if full[4] else 0} chars")
        print(f"Has notes: {len(full[5]) if full[5] else 0} chars")

print("\n" + "=" * 60)