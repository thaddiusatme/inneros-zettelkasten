# Core Workflow - Flowchart

**Purpose**: Main workflow operations for inbox processing, status checking, and note promotion  
**CLI**: `core_workflow_cli.py`  
**Manager**: `WorkflowManager`

## Workflow Overview

The Core Workflow manages the fundamental operations of the InnerOS Zettelkasten system, handling note lifecycle from inbox to permanent status.

---

## Mermaid Flowchart

```mermaid
flowchart TD
    Start([User Invokes Core Workflow CLI]) --> Command{Select Command}
    
    %% Status Command
    Command -->|status| CheckStatus[Get Workflow Status]
    CheckStatus --> GenerateReport[Generate Workflow Report]
    GenerateReport --> StatusFormat{Output Format?}
    StatusFormat -->|normal| DisplayStatus[Display Status Summary]
    StatusFormat -->|json| OutputJSON[Output JSON]
    DisplayStatus --> ShowInbox[Show Inbox Count]
    ShowInbox --> ShowFleeting[Show Fleeting Count]
    ShowFleeting --> ShowPermanent[Show Permanent Count]
    ShowPermanent --> StatusEnd([End])
    OutputJSON --> StatusEnd
    
    %% Process Inbox Command
    Command -->|process-inbox| LoadInbox[Load All Inbox Notes]
    LoadInbox --> CheckNotes{Any Notes?}
    CheckNotes -->|No| NoNotes[Display: No notes to process]
    CheckNotes -->|Yes| ProcessLoop[Process Each Note]
    NoNotes --> ProcessEnd([End])
    
    ProcessLoop --> ExtractMetadata[Extract Note Metadata]
    ExtractMetadata --> AIEnhancement[AI Enhancement]
    
    AIEnhancement --> GenerateTags[Generate AI Tags]
    GenerateTags --> CalculateQuality[Calculate Quality Score]
    CalculateQuality --> DiscoverLinks[Discover Semantic Links]
    DiscoverLinks --> CreateSummary[Create Summary]
    
    CreateSummary --> UpdateNote[Update Note with AI Data]
    UpdateNote --> CheckMore{More Notes?}
    CheckMore -->|Yes| ProcessLoop
    CheckMore -->|No| ShowResults[Display Processing Results]
    ShowResults --> ProcessEnd
    
    %% Promote Command
    Command -->|promote| GetNotePath[Get Note Path]
    GetNotePath --> ValidateNote{Note Exists?}
    ValidateNote -->|No| ErrorNote[Error: Note not found]
    ValidateNote -->|Yes| CheckType{Target Type?}
    ErrorNote --> PromoteEnd([End])
    
    CheckType -->|permanent| PromoteToPermanent[Move to Permanent Notes]
    CheckType -->|literature| PromoteToLiterature[Move to Literature]
    
    PromoteToPermanent --> UpdateStatus1[Update Status: published]
    PromoteToLiterature --> UpdateStatus2[Update Status: published]
    
    UpdateStatus1 --> UpdateLinks[Update All Backlinks]
    UpdateStatus2 --> UpdateLinks
    
    UpdateLinks --> VerifyMove{Move Successful?}
    VerifyMove -->|Yes| Success[Display: Success]
    VerifyMove -->|No| ErrorMove[Display: Error]
    Success --> PromoteEnd
    ErrorMove --> PromoteEnd
    
    %% Report Command
    Command -->|report| GenerateFullReport[Generate Full Report]
    GenerateFullReport --> CollectMetrics[Collect All Metrics]
    CollectMetrics --> AnalyzeHealth[Analyze Health]
    AnalyzeHealth --> IdentifyIssues[Identify Issues]
    IdentifyIssues --> FormatReport[Format Comprehensive Report]
    FormatReport --> DisplayReport[Display Report]
    DisplayReport --> ReportEnd([End])

    %% Styling
    classDef processClass fill:#e1f5ff,stroke:#0288d1,stroke-width:2px
    classDef aiClass fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    classDef decisionClass fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px
    classDef successClass fill:#e8f5e9,stroke:#4caf50,stroke-width:2px
    classDef errorClass fill:#ffebee,stroke:#f44336,stroke-width:2px
    
    class ProcessLoop,ExtractMetadata,UpdateNote processClass
    class AIEnhancement,GenerateTags,CalculateQuality,DiscoverLinks,CreateSummary aiClass
    class Command,StatusFormat,CheckNotes,CheckType,VerifyMove decisionClass
    class Success successClass
    class ErrorNote,ErrorMove errorClass
```

---

## Command Details

### 1. **Status** (`--status`)
**Purpose**: Display current workflow state and note counts

**Flow**:
1. Call `WorkflowManager.generate_workflow_report()`
2. Extract workflow status section
3. Display counts for: inbox, fleeting, permanent, archived
4. Show recent activity metrics

**Output**:
```
WORKFLOW STATUS REPORT
=====================
Inbox: 15 notes
Fleeting: 42 notes
Permanent: 128 notes
Archived: 89 notes
```

---

### 2. **Process Inbox** (`--process-inbox`)
**Purpose**: AI-enhance all notes in the inbox directory

**Flow**:
1. Scan `knowledge/Inbox/` for all markdown files
2. For each note:
   - Extract frontmatter metadata
   - Generate AI tags (3-8 contextual tags)
   - Calculate quality score (0.0-1.0)
   - Discover semantic connections to existing notes
   - Create abstractive summary
   - Update note with AI enhancements
3. Display processing summary with counts

**AI Processing Per Note**:
- **Tags**: Context-aware semantic tagging
- **Quality**: Multi-factor scoring (structure, depth, clarity)
- **Links**: Embedding-based similarity search
- **Summary**: Abstractive summarization with key points

**Performance**: <10s per note average

---

### 3. **Promote** (`--promote <path> <type>`)
**Purpose**: Promote a note from fleeting to permanent or literature

**Flow**:
1. Validate note exists and is eligible for promotion
2. Determine target directory based on type:
   - `permanent` → `knowledge/Permanent Notes/`
   - `literature` → `knowledge/Literature/`
3. Update frontmatter:
   - Change `status: inbox` → `status: published`
   - Add promotion timestamp
4. Move file to target directory
5. Update all backlinks in referencing notes
6. Verify integrity of move operation

**Safeguards**:
- Backup created before move
- Link rewriting for all references
- Validation of successful move
- Rollback capability on error

---

### 4. **Report** (`--report`)
**Purpose**: Generate comprehensive workflow health report

**Flow**:
1. Collect metrics from all note directories
2. Analyze workflow health indicators:
   - Inbox accumulation rate
   - Fleeting note aging
   - Promotion rate
   - Quality score distribution
3. Identify issues:
   - Stale notes (>30 days old)
   - Low-quality notes (score <0.5)
   - Orphaned notes (no links)
4. Format comprehensive report with recommendations

**Report Sections**:
- Workflow Status
- Health Indicators
- Issues & Recommendations
- Recent Activity
- Performance Metrics

---

## Architecture

```
CoreWorkflowCLI
    ↓
WorkflowManager
    ↓
CoreWorkflowManager (orchestration)
    ↓
    ├─→ AnalyticsManager (metrics)
    ├─→ AIEnhancementManager (AI processing)
    └─→ ConnectionManager (link discovery)
```

**Key Classes**:
- `CoreWorkflowCLI`: Command-line interface layer
- `WorkflowManager`: Facade/adapter for all managers
- `CoreWorkflowManager`: Core workflow orchestration
- `AnalyticsManager`: Metrics and reporting
- `AIEnhancementManager`: AI processing pipeline
- `ConnectionManager`: Semantic link discovery

---

## Success Metrics

- **Processing Speed**: <10s per note
- **AI Enhancement**: 100% coverage
- **Quality Target**: Average score >0.75
- **Connection Rate**: >3 links per note
- **Error Rate**: <1% failures

---

**Last Updated**: 2025-10-12  
**Status**: Production Ready ✅
