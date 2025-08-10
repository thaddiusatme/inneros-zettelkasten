# Content Standards & Note Types

> **Purpose**: Note quality standards, types, and content requirements  
> **Updated**: 2025-08-10  

## 📝 Content Standards

### Literature Notes (NEW)
- Must include source URL and saved_at timestamp
- Require minimum 2 claims or 1 substantial quote
- Link liberally to related permanent and fleeting notes
- Include summary for quick reference
- Use structured template with claims/quotes sections
- Quality score target: >0.7 for promotion to permanent

### Permanent Notes
- Should be atomic and evergreen
- Include minimum 2 relevant tags
- Link liberally using `[[double-brackets]]`
- Never delete without explicit user permission
- Quality score target: >0.7 for promotion
- Can be promoted from fleeting OR literature notes

### Fleeting Notes
- Capture raw ideas quickly
- Include promotion pathway in template
- Preserve original context and timestamp
- Status: inbox until processed
- Can be imported from external sources via Reading Intake Pipeline

### MOCs (Maps of Content)
- Serve as navigation hubs for related topics
- Update regularly as content grows
- Include both structural and contextual links
- Provide entry points to knowledge networks

## 🔍 Validation Rules

### Required on Creation
- Valid YAML frontmatter with all required fields
- Proper status field (inbox|promoted|draft|published|archived)
- Valid type field (permanent|fleeting|literature|MOC)
- Created timestamp present in ISO format

### Required on Modification
- Preserve existing metadata unless explicitly changing
- Update modification timestamps
- Maintain link integrity
- Log changes in appropriate tracking mechanisms
