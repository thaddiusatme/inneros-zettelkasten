# Directory Context & Organization Guide

**Created**: 2025-10-09  
**Purpose**: Directory structure awareness for AI agents and developers  
**Related**: `adr-003-distribution-architecture.md`, `distribution-productionization-manifest.md`

---

## 🎯 Purpose

This guide ensures all systems (AI agents, automation scripts, developers) maintain awareness of:
1. **Repository Context**: Source vs. Distribution
2. **Directory Structure**: Where files belong
3. **Safety Boundaries**: What content is private vs. public
4. **Organizational Rules**: How to maintain structure

---

## 🏛️ Repository Context Recognition

### **Source Repository** (Current: inneros-zettelkasten)

**Identifiers**:
```python
def is_source_repository():
    """Detect if working in source (personal) repository."""
    indicators = [
        Path('Reviews/').exists(),  # Personal weekly reviews
        Path('knowledge/Content Pipeline/').exists(),  # Personal work
        len(list(Path('knowledge/Permanent Notes/').glob('*.md'))) > 20,  # Many personal notes
        Path('.automation/logs/').exists()  # Processing logs
    ]
    return any(indicators)
```

**AI Agent Behavior**:
- ✅ **Access**: All personal notes for testing and development
- ✅ **Processing**: Generate real insights from personal data
- ✅ **Backups**: Create in `.automation/backups/`
- ✅ **Logging**: Write to `.automation/logs/`
- ❌ **Git**: Never commit personal content (use .gitignore)
- ❌ **Sharing**: Never expose personal information in outputs

**Development Mode**:
```python
context = {
    'repo': 'source',
    'mode': 'development',
    'safety': 'protect_personal_data',
    'test_data': 'use_real_notes',
    'processing': 'full_ai_features',
    'backup_location': '.automation/backups/',
    'log_location': '.automation/logs/'
}
```

---

### **Distribution Repository** (Future: inneros-distribution)

**Identifiers**:
```python
def is_distribution_repository():
    """Detect if working in distribution (public) repository."""
    indicators = [
        Path('DISTRIBUTION-NOTES.md').exists(),  # Distribution marker
        not Path('Reviews/').exists(),  # No personal reviews
        all(f.name.startswith('example-') for f in Path('knowledge/Permanent Notes/').glob('*.md')),  # Only examples
        Path('scripts/create-distribution.sh').exists()  # Distribution script
    ]
    return all(indicators)
```

**AI Agent Behavior**:
- ✅ **Access**: Sample notes only (example-*.md)
- ✅ **Processing**: Generate generic examples
- ✅ **Testing**: Use synthetic/sample data
- ✅ **Documentation**: Create public-facing docs
- ❌ **Personal**: Never reference personal information
- ❌ **Private**: Never create private content

**Production Mode**:
```python
context = {
    'repo': 'distribution',
    'mode': 'production',
    'safety': 'public_ready',
    'test_data': 'use_sample_notes',
    'processing': 'demo_features_only',
    'backup_location': None,  # No backups in distribution
    'log_location': None  # No logging in distribution
}
```

---

## 📁 Directory Structure Standards

### **1. Knowledge Base** (`knowledge/`)

#### **Directory Type Matrix**

| Directory | Source Repo | Distribution Repo | AI Processing |
|-----------|-------------|-------------------|---------------|
| `Inbox/` | Personal captures | Empty + README + 1 example | Full processing |
| `Fleeting Notes/` | 53+ personal notes | 1-2 examples + README | Full processing |
| `Permanent Notes/` | 102+ personal notes | 3-5 examples + README | Full processing |
| `Literature Notes/` | Personal reading notes | 1-2 examples + README | Full processing |
| `Archive/` | Historical personal content | Not included | No processing |
| `Content Pipeline/` | 123 work items | Not included | Limited processing |
| `Templates/` | All templates | All templates (copied) | Template generation |

#### **File Naming Standards**

**Source Repository**:
```
knowledge/Permanent Notes/
├── zettel-202507231648-context-engineering.md  # Real note
├── fleeting-2025-07-28-voice-note.md            # Real capture
└── lit-20250818-1957-prompt.md                  # Real literature note
```

**Distribution Repository**:
```
knowledge/Permanent Notes/
├── README.md                                     # Explains permanent notes
├── example-zettelkasten-method.md                # Demo note
├── example-note-linking.md                       # Demo note
├── example-ai-workflows.md                       # Demo note
└── example-knowledge-management.md               # Demo note
```

**Naming Rules**:
- **Real Notes**: Any filename format (personal preference)
- **Sample Notes**: Must start with `example-` or `EXAMPLE-`
- **Templates**: Kept identical in both repositories
- **Documentation**: README.md in each directory

---

### **2. Projects Directory** (`Projects/`)

#### **Directory Type Matrix**

| Directory | Source Repo | Distribution Repo | Purpose |
|-----------|-------------|-------------------|---------|
| `ACTIVE/` | Personal projects + ADRs | ADRs only | Current work |
| `REFERENCE/` | Core documentation | Core documentation (sanitized) | Essential docs |
| `COMPLETED-2025-XX/` | All lessons learned | Sanitized lessons learned | Historical record |
| `DEPRECATED/` | Old personal projects | Not included | Archive |

#### **File Organization Rules**

**ACTIVE/ Directory** (Source):
```
Projects/ACTIVE/
├── adr-001-workflow-manager-refactoring.md      # ✅ Distribute (architecture)
├── adr-002-circuit-breaker-rate-limit.md        # ✅ Distribute (architecture)
├── adr-003-distribution-architecture.md         # ✅ Distribute (architecture)
├── project-todo-v3.md                           # ❌ Private (personal tasks)
├── current-priorities-summary.md                # ❌ Private (personal priorities)
├── bug-empty-video-id-frontmatter.md            # ❌ Private (personal bug)
└── personal-project-manifest.md                 # ❌ Private (personal work)
```

**ACTIVE/ Directory** (Distribution):
```
Projects/ACTIVE/
├── README-ACTIVE.md                             # ✅ Distribution guidance
├── adr-001-workflow-manager-refactoring.md      # ✅ Architecture decision
├── adr-002-circuit-breaker-rate-limit.md        # ✅ Architecture decision
└── adr-003-distribution-architecture.md         # ✅ Architecture decision
```

**Distribution Rules**:
- **ADRs**: Always distribute (they document architecture)
- **Manifests**: Sanitize and distribute if relevant to public
- **Personal Files**: Never distribute (project-todo, priorities, personal bugs)
- **Completed**: Sanitize lessons learned, keep technical insights

---

### **3. Automation Directory** (`.automation/`)

#### **Directory Type Matrix**

| Directory | Source Repo | Distribution Repo | Purpose |
|-----------|-------------|-------------------|---------|
| `config/` | Personal config | Default config (sanitized) | Configuration |
| `logs/` | Processing logs | Not included | Operational data |
| `review_queue/` | Generated reports | Not included | Workflow outputs |
| `scripts/` | Automation scripts | Automation scripts | Utilities |
| `backups/` | Backup files | Not included | Safety |

#### **Safety Rules**

**Source Repository**:
```python
# AI agents can freely use automation
def process_with_automation(note_path):
    """Process note with full automation."""
    log_to('.automation/logs/processing.log')
    backup_to('.automation/backups/')
    generate_report('.automation/review_queue/')
    return result
```

**Distribution Repository**:
```python
# AI agents use minimal automation
def process_with_automation(note_path):
    """Process note with demo automation."""
    # No logging (privacy)
    # No backups (no personal data)
    # No reports (demo only)
    return demo_result
```

---

## 🔒 Privacy & Security Boundaries

### **Content Classification**

#### **Level 1: Public** (Safe for Distribution)
- ✅ All code in `development/src/`
- ✅ All tests in `development/tests/`
- ✅ Templates in `knowledge/Templates/`
- ✅ ADRs in `Projects/ACTIVE/`
- ✅ Sanitized documentation
- ✅ Generic examples

#### **Level 2: Personal** (NEVER Distribute)
- ❌ Personal notes (200+ files)
- ❌ Weekly reviews (39 files)
- ❌ Media files (screenshots, recordings)
- ❌ Processing logs
- ❌ Backup files
- ❌ Personal project details
- ❌ Work-in-progress content

#### **Level 3: Sanitize** (Requires Review)
- ⚠️ Lessons learned documents
- ⚠️ Project manifests
- ⚠️ Documentation with examples
- ⚠️ Configuration files
- ⚠️ Workflow guides

### **AI Agent Safety Rules**

```python
def ai_agent_safety_check(operation, content):
    """Enforce safety boundaries for AI operations."""
    
    repo_context = detect_repository_context()
    
    if repo_context['repo'] == 'distribution':
        # Public repository - strict rules
        if contains_personal_info(content):
            raise SecurityError("Personal information detected in distribution")
        
        if not is_example_file(content):
            raise SecurityError("Non-example content in distribution")
    
    elif repo_context['repo'] == 'source':
        # Private repository - protect from exposure
        if operation == 'commit' and not in_gitignore(content):
            warn("Verify personal content not being committed")
        
        if operation == 'share' or operation == 'publish':
            raise SecurityError("Cannot share from source repository directly")
    
    return True
```

---

## 🔄 Directory Maintenance Rules

### **Weekly Cleanup Tasks**

1. **Projects/ACTIVE/** (Every Monday)
   - Move completed projects to `COMPLETED-2025-XX/`
   - Archive deprecated manifests to `DEPRECATED/`
   - Verify ADRs are up-to-date
   - Limit to 8-10 active files

2. **knowledge/** (Every Sunday)
   - Process inbox notes (status: inbox → promoted)
   - Archive old fleeting notes (>90 days)
   - Validate links in permanent notes
   - Update MOCs with new connections

3. **.automation/** (Daily)
   - Prune old logs (>7 days)
   - Clean review queue (>30 days)
   - Verify backup retention (keep last 5)
   - Monitor disk usage

### **Directory Organization Handler**

**Automated System** (See: `.windsurf/workflows/directory-organization-tdd.md`):

```python
class DirectoryOrganizationHandler:
    """Maintains directory structure and organization."""
    
    def process_directory_health(self, vault_path):
        """Run health checks on directory structure."""
        
        issues = []
        
        # Check 1: Files in wrong directories
        misplaced = self.find_misplaced_files(vault_path)
        if misplaced:
            issues.append(f"Found {len(misplaced)} misplaced files")
        
        # Check 2: Type-directory mismatch
        # Example: type: permanent but still in Inbox/
        mismatches = self.find_type_mismatches(vault_path)
        if mismatches:
            issues.append(f"Found {len(mismatches)} type mismatches")
        
        # Check 3: Orphaned files
        orphaned = self.find_orphaned_files(vault_path)
        if orphaned:
            issues.append(f"Found {len(orphaned)} orphaned files")
        
        # Check 4: Broken links
        broken_links = self.find_broken_links(vault_path)
        if broken_links:
            issues.append(f"Found {len(broken_links)} broken links")
        
        return {
            'health': 'HEALTHY' if not issues else 'NEEDS_ATTENTION',
            'issues': issues,
            'recommendations': self.generate_recommendations(issues)
        }
    
    def auto_organize(self, vault_path, dry_run=True):
        """Automatically organize files based on type field."""
        
        # Safety: Always backup first
        backup_path = self.create_backup(vault_path)
        
        try:
            moves = []
            
            # Find files with type-directory mismatch
            for note_path in self.scan_notes(vault_path):
                metadata = self.parse_metadata(note_path)
                current_dir = note_path.parent.name
                expected_dir = self.get_expected_directory(metadata['type'])
                
                if current_dir != expected_dir:
                    moves.append({
                        'file': note_path,
                        'from': current_dir,
                        'to': expected_dir,
                        'type': metadata['type']
                    })
            
            if dry_run:
                return self.generate_move_plan(moves)
            else:
                return self.execute_moves(moves, backup_path)
        
        except Exception as e:
            # Rollback on any error
            self.rollback_from_backup(backup_path)
            raise
```

---

## 🧭 AI Agent Directory Guidelines

### **Context-Aware File Operations**

```python
def ai_file_operation(operation, file_path, content=None):
    """AI agents should use this for all file operations."""
    
    # Step 1: Detect repository context
    repo_context = detect_repository_context()
    
    # Step 2: Validate operation is allowed
    if repo_context['repo'] == 'distribution':
        # Distribution repo - limit operations
        allowed_dirs = [
            'development/',
            'knowledge/Templates/',
            'Projects/ACTIVE/',  # ADRs only
            'Projects/REFERENCE/'
        ]
        
        if not any(str(file_path).startswith(d) for d in allowed_dirs):
            raise PermissionError(f"Cannot modify {file_path} in distribution")
    
    # Step 3: Execute with safety checks
    if operation == 'write':
        # Check for personal information
        if repo_context['repo'] == 'distribution' and contains_personal_info(content):
            raise SecurityError("Personal info in distribution write")
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write with backup
        if file_path.exists():
            backup_file(file_path)
        
        file_path.write_text(content)
    
    elif operation == 'move':
        # Validate target directory
        target_dir = file_path.parent
        if not is_valid_directory(target_dir, repo_context):
            raise ValueError(f"Invalid target directory: {target_dir}")
        
        # Execute with link preservation
        move_with_link_updates(file_path, target_dir)
    
    # Step 4: Log operation
    log_operation(operation, file_path, repo_context)
```

### **Directory-Aware Note Processing**

```python
def process_notes_by_directory(vault_path):
    """Process notes with directory context awareness."""
    
    repo_context = detect_repository_context()
    
    # Source repository - process all notes
    if repo_context['repo'] == 'source':
        notes = list(Path(vault_path).rglob('*.md'))
        
        # Full AI processing
        for note in notes:
            process_with_ai(note, full_features=True)
    
    # Distribution repository - process examples only
    elif repo_context['repo'] == 'distribution':
        notes = list(Path(vault_path).rglob('example-*.md'))
        
        # Demo processing only
        for note in notes:
            process_with_ai(note, full_features=False, demo_mode=True)
```

---

## 📊 Directory Health Metrics

### **Health Check Dashboard**

```python
def generate_directory_health_report(vault_path):
    """Generate comprehensive directory health metrics."""
    
    return {
        'repository': {
            'type': detect_repository_context()['repo'],
            'total_files': count_files(vault_path),
            'total_notes': count_notes(vault_path),
            'total_size': get_directory_size(vault_path)
        },
        
        'organization': {
            'misplaced_files': find_misplaced_files(vault_path),
            'type_mismatches': find_type_mismatches(vault_path),
            'orphaned_files': find_orphaned_files(vault_path),
            'broken_links': find_broken_links(vault_path)
        },
        
        'safety': {
            'gitignore_violations': check_gitignore_violations(vault_path),
            'personal_info_exposed': scan_for_personal_info(vault_path),
            'backup_status': check_backup_status(vault_path)
        },
        
        'recommendations': generate_health_recommendations(vault_path)
    }
```

---

## ✅ Success Criteria

**Directory organization is healthy when**:
- ✅ All notes in correct directories based on type field
- ✅ Zero type-directory mismatches
- ✅ All links functional (zero broken links)
- ✅ Git ignores personal content properly
- ✅ AI agents respect repository context
- ✅ ACTIVE/ directory has ≤10 files
- ✅ Automation logs cleaned regularly
- ✅ Backups maintained with retention

**AI agents are context-aware when**:
- ✅ Detect repository type automatically
- ✅ Adapt behavior to source vs. distribution
- ✅ Never expose personal data in distribution
- ✅ Use appropriate processing levels
- ✅ Respect directory boundaries
- ✅ Log operations appropriately

---

## 📚 Related Documents

- **Architecture**: `adr-003-distribution-architecture.md`
- **Distribution**: `distribution-productionization-manifest.md`
- **File Organization**: `.windsurf/rules/updated-file-organization.md`
- **Workflow**: `.windsurf/workflows/directory-organization-tdd.md`

---

**Status**: ✅ ACTIVE  
**Next Review**: Weekly (Mondays during cleanup)  
**Automation**: DirectoryOrganizationHandler (planned TDD implementation)  
**Owner**: InnerOS Development Team
