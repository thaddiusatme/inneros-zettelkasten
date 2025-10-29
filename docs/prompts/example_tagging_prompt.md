# Example Tagging Prompt
version: 0.1.0
task: "Suggest tags for a note"
input_contract: "plain text"
output_contract: "json list of tags"

System:
You are a careful assistant. Return valid JSON only.

User:
{{note_text}}
