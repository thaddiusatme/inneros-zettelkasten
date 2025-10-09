# 📚 Knowledge Starter Pack

Welcome to the InnerOS Zettelkasten! This starter pack contains example notes to help you understand how the system works.

## 🎯 What's Inside

This starter pack demonstrates core Zettelkasten concepts with real examples:

### **Navigation Hub**
- `zettelkasten-moc.md` - Map of Content showing how to organize and navigate notes

### **Permanent Notes** (Atomic Ideas)
- `principles-for-zettelkasten-entry-and-promotion.md` - Core workflow principles
- `printing-paper-metaphor-for-llm-context.md` - Mental model for understanding AI
- `strategy-for-ai-augmented-zettelkasten.md` - Integration strategy example

### **Literature Note** (Source Material)
- `example-literature-note.md` - Shows how to capture ideas from external sources

## 📖 How to Use These Examples

### **1. Understanding Note Types**

**Permanent Notes (Zettel)**:
- Express a single, atomic idea
- Written in your own words
- Heavily linked to related concepts
- Filename: `zettel-YYYYMMDDHHSS-descriptive-title.md`

**Literature Notes**:
- Summarize external sources (articles, books, videos)
- Include source attribution
- Bridge between raw content and permanent notes
- Filename: `lit-YYYYMMDD-HHMM-source-description.md`

**Maps of Content (MOC)**:
- Navigate collections of related notes
- Not comprehensive (no need to link everything)
- Evolve organically as knowledge grows
- Filename: `Topic Name MOC.md`

### **2. The Zettelkasten Workflow**

```
Capture → Process → Connect → Discover

1. CAPTURE: Quick ideas go to Inbox as fleeting notes
2. PROCESS: Review fleeting notes, promote valuable ones to permanent
3. CONNECT: Link new permanent notes to existing knowledge
4. DISCOVER: Use MOCs and links to explore your knowledge network
```

### **3. Key Principles Demonstrated**

**Atomicity**: Each permanent note contains one clear idea  
**Connectivity**: Notes link to related concepts using `[[wiki-links]]`  
**Emergence**: Knowledge structure emerges from connections, not rigid hierarchy  
**Your Voice**: Notes are written in your own words, not copied verbatim

## 🚀 Getting Started

1. **Read the MOC** (`zettelkasten-moc.md`) to see how navigation works
2. **Explore permanent notes** to understand atomic ideas
3. **Check frontmatter** to see required metadata structure
4. **Follow the links** to understand connection patterns
5. **Create your own notes** using these as templates

## 📝 Note Metadata Structure

All notes use YAML frontmatter for consistency:

```yaml
---
type: permanent           # or: literature, fleeting, MOC
created: 2025-01-15 14:30
status: published         # or: draft, inbox, archived
tags: [topic, concept]
visibility: private       # or: public
---
```

## 🔗 Understanding Wiki-Links

Links use double bracket syntax: `[[note-title]]`

- **Outgoing links**: Connections you create in your note
- **Incoming links** (backlinks): Shown automatically by Obsidian
- **Bidirectional**: Creating `[[Note A]]` in Note B automatically creates backlink

## 💡 Tips for Your Knowledge Garden

1. **Start small**: Don't worry about having "enough" notes initially
2. **Write for yourself**: Use language that makes sense to you
3. **Link liberally**: More connections = more discovery opportunities
4. **Review regularly**: Weekly reviews help identify promotion opportunities
5. **Let it grow**: Your system will evolve naturally over time

## 🎨 Customization

Feel free to:
- Modify these examples to fit your needs
- Add your own topics and interests
- Adjust metadata fields
- Create additional note types
- Develop your own tagging system

## 📚 Further Reading

- [Zettelkasten Method Overview](https://zettelkasten.de/overview/)
- [How to Take Smart Notes](https://www.goodreads.com/book/show/34507927-how-to-take-smart-notes)
- [Obsidian Documentation](https://help.obsidian.md/)

---

**Ready to build your knowledge garden!** 🌱

Start by creating your first fleeting note in the Inbox, then use these examples as templates for promoting it to a permanent note.
