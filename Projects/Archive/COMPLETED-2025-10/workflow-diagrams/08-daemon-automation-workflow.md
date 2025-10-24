# Daemon Automation Workflow - Flowchart

**Purpose**: Background automation service for continuous knowledge processing  
**Service**: `automation_daemon.py`  
**Handlers**: Feature-specific automation handlers

## Workflow Overview

The Daemon Automation system runs as a background service, watching for file changes and scheduled events to automatically process notes without manual intervention.

---

## Mermaid Flowchart

```mermaid
flowchart TD
    Start([Daemon Start]) --> Init[Initialize Daemon]
    Init --> LoadConfig[Load Configuration]
    LoadConfig --> RegisterHandlers[Register Handlers]
    RegisterHandlers --> StartWatcher[Start File Watcher]
    StartWatcher --> StartScheduler[Start Task Scheduler]
    StartScheduler --> MainLoop[Main Event Loop]
    
    %% Event Processing
    MainLoop --> CheckEvent{Event?}
    
    CheckEvent -->|File Change| FileEvent[File Event]
    CheckEvent -->|Schedule| ScheduledTask[Scheduled Task]
    CheckEvent -->|Health Check| HealthCheck[Health Monitor]
    CheckEvent -->|Shutdown| Shutdown[Stop Daemon]
    
    %% File Event Handler
    FileEvent --> CooldownCheck{Within Cooldown?}
    CooldownCheck -->|Yes| SkipEvent[Skip Event]
    CooldownCheck -->|No| RouteHandler[Route to Handler]
    SkipEvent --> MainLoop
    
    RouteHandler --> HandlerType{Handler Type?}
    HandlerType -->|YouTube| YouTubeProcess[Process YouTube Note]
    HandlerType -->|Screenshot| ScreenshotProcess[Process Screenshot]
    HandlerType -->|SmartLink| SmartLinkProcess[Discover Links]
    
    YouTubeProcess --> Success1{Success?}
    ScreenshotProcess --> Success1
    SmartLinkProcess --> Success1
    
    Success1 -->|Yes| LogSuccess[Log Success]
    Success1 -->|No| LogError[Log Error]
    LogSuccess --> UpdateMetrics[Update Metrics]
    LogError --> UpdateMetrics
    UpdateMetrics --> MainLoop
    
    %% Scheduled Tasks
    ScheduledTask --> TaskType{Task Type?}
    TaskType -->|Weekly Review| RunWeekly[Generate Review]
    TaskType -->|Backup| RunBackup[Create Backup]
    TaskType -->|Cleanup| RunCleanup[Cleanup Files]
    
    RunWeekly --> NotifyUser[Notify User]
    RunBackup --> NotifyUser
    RunCleanup --> NotifyUser
    NotifyUser --> MainLoop
    
    %% Health Check
    HealthCheck --> CheckCPU[Check CPU/Memory]
    CheckCPU --> CheckDisk[Check Disk Space]
    CheckDisk --> CheckErrors[Check Error Rate]
    CheckErrors --> HealthOK{Healthy?}
    HealthOK -->|Yes| LogHealthy[Log OK]
    HealthOK -->|No| AlertUnhealthy[Send Alert]
    LogHealthy --> MainLoop
    AlertUnhealthy --> MainLoop
    
    %% Shutdown
    Shutdown --> StopWatcher[Stop File Watcher]
    StopWatcher --> StopScheduler[Stop Scheduler]
    StopScheduler --> SaveState[Save State]
    SaveState --> End([End])

    %% Styling
    classDef initClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef eventClass fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    classDef processClass fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px
    classDef healthClass fill:#e8f5e9,stroke:#4caf50,stroke-width:2px
    
    class Init,LoadConfig,RegisterHandlers initClass
    class FileEvent,ScheduledTask,HealthCheck eventClass
    class YouTubeProcess,ScreenshotProcess,SmartLinkProcess processClass
    class CheckCPU,CheckDisk,LogHealthy healthClass
```

---

## Feature Handlers

### 1. YouTube Handler
**Trigger**: YouTube note saved  
**Actions**: Fetch transcript → Extract quotes → Update note

### 2. Screenshot Handler
**Trigger**: New screenshot image  
**Actions**: OCR → AI enhancement → Create note

### 3. Smart Link Handler
**Trigger**: Note without links  
**Actions**: Find connections → Suggest/insert links

---

## Configuration

```yaml
daemon:
  log_level: INFO
  
youtube_handler:
  enabled: true
  cooldown_seconds: 60
  
screenshot_handler:
  enabled: true
  auto_enhance: true
  
smartlink_handler:
  enabled: false
  auto_insert: false
```

---

## Management Commands

```bash
# Start daemon
inneros daemon start

# Stop daemon
inneros daemon stop

# Check status
inneros daemon status

# View logs
inneros daemon logs --tail 50
```

---

**Last Updated**: 2025-10-12  
**Status**: Production Ready ✅
