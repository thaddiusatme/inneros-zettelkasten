# 🚀 InnerOS Zettelkasten - Installation Guide

**Time to Complete**: ~15 minutes  
**Difficulty**: Beginner-friendly

This guide walks you through setting up InnerOS Zettelkasten from scratch. By the end, you'll have a fully functional personal knowledge management system.

---

## 📋 Prerequisites

Before starting, ensure you have:

### **Required**
- [ ] **Git** (2.0 or later) - [Download](https://git-scm.com/downloads)
- [ ] **Obsidian** (1.0 or later) - [Download](https://obsidian.md/)
- [ ] **macOS, Linux, or Windows** - All supported

### **Optional (for AI features)**
- [ ] **Python 3.9+** - [Download](https://www.python.org/downloads/)
- [ ] **pip** (Python package manager) - Usually included with Python

### **Check Your Setup**
```bash
# Verify Git installation
git --version

# Verify Python installation (optional)
python3 --version

# Verify pip installation (optional)
pip3 --version
```

---

## 🎯 Quick Start (3 Steps)

### **Step 1: Clone the Repository**

```bash
# Clone to your preferred location
git clone https://github.com/yourusername/inneros-zettelkasten.git

# Navigate to the directory
cd inneros-zettelkasten
```

**Expected Result**: You should see the repository files in your current directory.

---

### **Step 2: Open in Obsidian**

1. **Launch Obsidian**
2. Click **"Open folder as vault"** (or "Open" on some versions)
3. Navigate to the `inneros-zettelkasten` directory
4. Click **"Open"**

**Expected Result**: Obsidian loads the vault with the knowledge-starter-pack visible.

---

### **Step 3: Explore the Starter Pack**

1. Open `knowledge-starter-pack/README.md` in Obsidian
2. Read the overview and workflow guide
3. Open `knowledge-starter-pack/zettelkasten-moc.md` to see navigation
4. Explore the example permanent notes

**🎉 You're ready to use InnerOS Zettelkasten!**

---

## 🔧 Optional: AI Features Setup

If you want to use AI-powered features (auto-tagging, connection discovery, quality assessment):

### **Step 1: Install Python Dependencies**

```bash
# Create virtual environment (recommended)
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip3 install -r requirements.txt
```

### **Step 2: Configure AI Provider**

Choose one of these options:

#### **Option A: Local LLM (Privacy-First)**
```bash
# Install Ollama
# macOS:
brew install ollama

# Start Ollama service
ollama serve

# Pull a model (e.g., llama2)
ollama pull llama2
```

#### **Option B: OpenAI API (Cloud-Based)**
```bash
# Set your API key
export OPENAI_API_KEY='your-api-key-here'

# Or create a .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### **Step 3: Test AI Features**

```bash
# Run a simple test
python3 development/demos/connections_demo.py knowledge/
```

**Expected Result**: AI analyzes notes and suggests connections.

---

## 📁 Understanding the Directory Structure

After installation, your vault will look like this:

```
inneros-zettelkasten/
├── knowledge/                    # Your personal knowledge base
│   ├── Inbox/                   # Fleeting notes (quick captures)
│   ├── Permanent Notes/         # Processed, permanent ideas
│   ├── Literature Notes/        # Summaries of external sources
│   └── [Various MOCs]           # Maps of Content for navigation
│
├── knowledge-starter-pack/      # Example notes (read-only reference)
│   ├── README.md               
│   ├── zettelkasten-moc.md
│   └── [4 example notes]
│
├── development/                  # Python automation tools (optional)
├── scripts/                      # Distribution and utility scripts
├── README.md                     # Project overview
└── INSTALLATION.md              # This file
```

**Key Principle**: The `knowledge/` directory is your workspace. The starter pack is for reference only.

---

## ✅ Verification Steps

### **1. Obsidian Loads Successfully**
- [ ] Vault opens without errors
- [ ] You can see `knowledge-starter-pack/` folder
- [ ] Links between notes work (click `[[zettelkasten-moc]]` to test)

### **2. Basic Note Creation**
```bash
# Try creating your first fleeting note
1. In Obsidian, press Cmd/Ctrl + N (new note)
2. Name it: "fleeting-2025-10-09-test"
3. Add some text
4. Save (Cmd/Ctrl + S)
```

### **3. Template Support (Optional)**
- [ ] Install Templater plugin in Obsidian
- [ ] Configure template folder (if you want automation)
- [ ] Test template insertion

### **4. AI Features (If Installed)**
```bash
# Test AI connection discovery
cd inneros-zettelkasten
python3 development/demos/connections_demo.py knowledge/

# Expected: AI suggests connections between notes
```

---

## 🐛 Troubleshooting

### **Obsidian Won't Open Vault**
**Symptom**: Error message when opening folder  
**Solution**: 
- Ensure you selected the root `inneros-zettelkasten` folder, not a subfolder
- Check that `.obsidian` folder exists (it's hidden by default)
- Try closing Obsidian completely and reopening

---

### **Python Dependencies Won't Install**
**Symptom**: `pip install` fails with errors  
**Solution**:
```bash
# Upgrade pip first
pip3 install --upgrade pip

# Try installing again
pip3 install -r requirements.txt

# If still failing, install individually
pip3 install openai anthropic python-dotenv pyyaml
```

---

### **AI Features Not Working**
**Symptom**: Python scripts fail with API errors  
**Solution**:

1. **Check API Key**: Ensure `OPENAI_API_KEY` is set correctly
2. **Check Network**: Some networks block AI API calls
3. **Check Balance**: Verify your OpenAI account has credits
4. **Use Local LLM**: Switch to Ollama for offline operation

---

### **Git Clone Fails**
**Symptom**: Permission denied or network error  
**Solution**:
```bash
# Try HTTPS instead of SSH
git clone https://github.com/yourusername/inneros-zettelkasten.git

# Or use SSH with proper key setup
git clone git@github.com:yourusername/inneros-zettelkasten.git
```

---

## 🎓 Next Steps

### **Learn the Workflow**
1. Read `knowledge-starter-pack/README.md` for methodology overview
2. Review example permanent notes to understand structure
3. Create your first fleeting note in `knowledge/Inbox/`
4. Practice promoting a fleeting note to permanent

### **Customize Your Setup**
1. Configure Obsidian plugins (Templater, Dataview, etc.)
2. Adjust folder structure to your preferences
3. Create topic-specific MOCs for your interests
4. Set up automation scripts (if using AI features)

### **Join the Community**
- **GitHub Issues**: Report bugs or request features
- **Discussions**: Share workflows and ask questions
- **Contributing**: See `CONTRIBUTING.md` for guidelines

---

## 📚 Additional Resources

### **Zettelkasten Method**
- [Zettelkasten.de](https://zettelkasten.de/overview/) - Comprehensive guide
- "How to Take Smart Notes" by Sönke Ahrens - Foundational book
- [Obsidian Forum](https://forum.obsidian.md/) - Community discussions

### **Obsidian Documentation**
- [Official Help Docs](https://help.obsidian.md/)
- [Plugin Directory](https://obsidian.md/plugins)
- [Theme Gallery](https://obsidian.md/themes)

### **AI Integration**
- [Ollama Documentation](https://ollama.ai/docs) - Local LLM setup
- [OpenAI API Docs](https://platform.openai.com/docs) - Cloud AI
- [Anthropic Claude](https://www.anthropic.com/api) - Alternative AI provider

---

## 🆘 Getting Help

### **Quick Help**
1. Check `knowledge-starter-pack/README.md` for workflow guidance
2. Search [GitHub Issues](https://github.com/yourusername/inneros-zettelkasten/issues)
3. Review troubleshooting section above

### **Report Issues**
If you encounter bugs or problems:
1. Check if issue already exists in GitHub Issues
2. Create new issue with:
   - Operating system and version
   - Obsidian version
   - Python version (if using AI features)
   - Error messages (full text)
   - Steps to reproduce

### **Feature Requests**
Have ideas for improvements?
1. Open a GitHub Discussion
2. Describe the feature and use case
3. Explain how it benefits the workflow

---

## 🎉 You're All Set!

You now have a fully functional Zettelkasten system. Start capturing ideas and let your knowledge garden grow!

**First Actions**:
- [ ] Create your first fleeting note
- [ ] Explore the starter pack examples
- [ ] Set up weekly review habit
- [ ] Join the community

**Happy note-taking!** 🌱

---

**Installation Guide Version**: 1.0.0  
**Last Updated**: October 2025  
**Compatible With**: v0.1.0-alpha and later
