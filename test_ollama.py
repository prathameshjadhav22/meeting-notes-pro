import ollama

test_transcript = """
We discussed the Q4 marketing budget. Sarah proposed increasing 
social media spend by 30%. John agreed but suggested we need 
better ROI tracking. Action items: Sarah will prepare detailed 
proposal by Friday. Marketing team meets again next Monday.
"""

print("🤖 Generating meeting notes with AI...")

response = ollama.chat(model='llama3.2', messages=[
    {
        'role': 'user',
        'content': f"""You are a meeting notes assistant. Analyze this transcript and create structured notes.

Transcript:
{test_transcript}

Generate notes in this format:
📋 SUMMARY: (2-3 sentences)

🔑 KEY POINTS:
- Point 1
- Point 2

✅ DECISIONS MADE:
- Decision 1

📝 ACTION ITEMS:
- Task 1 (Owner: Name, Due: Date)

➡️ NEXT STEPS:
- Next step 1

Be concise and clear."""
    }
])

print("\n" + "="*60)
print(response['message']['content'])
print("="*60)