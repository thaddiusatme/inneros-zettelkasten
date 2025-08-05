# Knowledge Directory

## 📚 InnerOS Zettelkasten - Knowledge Base

This directory contains the complete Zettelkasten knowledge management system - all notes, templates, and Obsidian configuration.

## 📁 Directory Structure

```
knowledge/
├── Inbox/                  # 📥 Staging area for new notes
├── Fleeting Notes/         # 📝 Quick captures and temporary notes
├── Permanent Notes/        # 🏛️ Evergreen, atomic knowledge
├── Archive/               # 📦 Old/deprecated content
├── Templates/             # 📋 Obsidian templates and Templater scripts
└── .obsidian/            # ⚙️ Obsidian configuration and plugins
```

## 🎯 Getting Started

### For Knowledge Workers
1. **Open in Obsidian**: Use this directory as your vault
2. **Create Notes**: Start in `Inbox/` with `status: inbox`
3. **Process Notes**: Use AI workflows to promote quality content
4. **Link Everything**: Connect ideas using `[[wiki-links]]`

### For AI Integration
```bash
# Process inbox with AI
python3 ../development/src/cli/workflow_demo.py . --process-inbox

# Analyze knowledge base
python3 ../development/src/cli/analytics_demo.py . --interactive

# Weekly review automation
python3 ../development/src/cli/workflow_demo.py . --weekly-review
```

## 🔗 Key Files

- **Home Note.md** - Main navigation hub
- **MOC files** - Maps of Content for organized discovery
- **Templates/** - Pre-configured note templates

## 🛡️ Data Protection

- **Local AI Only**: All processing happens on-device
- **Privacy First**: Default `visibility: private` for all notes
- **Audit Trail**: Complete change history maintained
- **Backup Ready**: Easy export/import capabilities

## 📊 Quality Standards

- **Atomic Notes**: One idea per note
- **Evergreen Content**: Timeless, reusable knowledge
- **Rich Linking**: Dense internal connections
- **AI Enhanced**: Quality scoring and improvement suggestions

## 🎨 Obsidian Integration

This directory is designed as a complete Obsidian vault with:
- Pre-configured templates
- AI-enhanced workflows
- Knowledge graph visualization
- Cross-platform compatibility
