# Circuit Breaker & Rate Limit Protection System

**Created**: 2025-10-08 21:55 PDT  
**Priority**: P1 - HIGH (Prevent catastrophic incidents)  
**Status**: 📋 BACKLOG - Planned after incident recovery  
**Trigger**: Catastrophic YouTube incident (2,165 events → IP ban)

---

## 🚨 Motivation: What Could Have Happened

### **Actual Incident**
- File watching loop → 2,165 processing events
- ~1,000 YouTube API calls in hours
- Result: IP ban (recoverable in 24-48 hours)
- Cost: **$0** (free unofficial API)

### **If This Was a Paid API** 💸

**Example: OpenAI GPT-4**
- Cost: $0.03/1K input tokens, $0.06/1K output tokens
- Avg processing: ~2K tokens per call
- 1,000 calls × $0.12 = **$120 in hours** ❌
- No automatic shutoff = **unlimited burn** 🔥

**Example: YouTube Official API**
- 1,000 calls = 10,000 quota units
- Free tier: 10,000 units/day
- Would have consumed entire daily quota in hours
- Additional quota: **$0 but blocked** ❌

**Example: AWS/GCP APIs**
- Could easily rack up **$1,000+** in a loop
- Credit card auto-charged
- No built-in protection

### **The Real Risk**
> **Without protection, a single bug can cause unlimited financial damage**

---

## 🎯 Goals: Universal Protection System

### **Primary Objectives**
1. **Prevent infinite loops** from causing financial damage
2. **Detect abnormal usage patterns** in real-time
3. **Auto-shutdown** before catastrophic cost accumulation
4. **Alert immediately** when thresholds exceeded
5. **Protect ALL external APIs** (not just YouTube)

### **Success Criteria**
- ✅ No single feature can exceed budget limits
- ✅ Automatic circuit breaking within 5 minutes of anomaly
- ✅ Cost ceiling enforcement (<$10/day default)
- ✅ Real-time alerts for unusual patterns
- ✅ Zero manual intervention required

---

## 🏗️ System Architecture

### **Layer 1: Per-Feature Circuit Breakers** 🔌

**Purpose**: Individual feature protection

**Features**:
- Request counting per feature (hourly/daily windows)
- Automatic circuit opening after threshold
- Exponential backoff for retries
- Manual override for emergencies

**Thresholds** (configurable):
```yaml
circuit_breakers:
  youtube_handler:
    max_requests_per_hour: 50
    max_requests_per_day: 200
    cooldown_seconds: 60
    circuit_open_duration: 3600  # 1 hour
  
  openai_handler:
    max_requests_per_hour: 100
    max_requests_per_day: 500
    estimated_cost_per_request: 0.15
    max_daily_cost: 10.00
    circuit_open_duration: 7200  # 2 hours
  
  screenshot_ocr:
    max_requests_per_hour: 30
    max_requests_per_day: 100
```

**States**:
- 🟢 **CLOSED** (normal operation)
- 🟡 **HALF-OPEN** (testing recovery)
- 🔴 **OPEN** (blocking requests)

---

### **Layer 2: Global Budget Enforcer** 💰

**Purpose**: System-wide cost protection

**Features**:
- Track estimated costs across all features
- Hard ceiling on daily spend
- Automatic shutdown at 80% budget
- Alert at 50% budget

**Configuration**:
```yaml
budget_enforcer:
  daily_budget: 10.00  # USD
  alert_threshold: 0.50  # 50%
  shutdown_threshold: 0.80  # 80%
  
  cost_tracking:
    youtube_official_api: 0.00  # Free tier tracking
    openai_gpt4: 0.12  # Per request estimate
    screenshot_ocr: 0.02  # Per image estimate
```

**Behavior**:
- 50% budget → macOS notification
- 80% budget → **AUTOMATIC SHUTDOWN**
- 100% budget → Hard block (unreachable)

---

### **Layer 3: Anomaly Detection** 🚨

**Purpose**: Detect unusual patterns before damage

**Patterns to Detect**:
1. **Burst Detection**
   - >10 requests in 1 minute (any feature)
   - Likely indicates a loop bug
   
2. **Same-File Thrashing**
   - Same file processed >3 times in 5 minutes
   - File watching loop indicator
   
3. **Error Rate Spike**
   - >50% error rate in last 10 requests
   - API issues or bad configuration
   
4. **Midnight Activity**
   - Unusual processing between 2am-6am
   - Possible runaway automation

**Actions**:
- Log anomaly with context
- Send alert (macOS notification + log)
- Reduce processing rate (50% throttle)
- If pattern continues 5 min → Circuit break

---

### **Layer 4: Emergency Kill Switch** 🛑

**Purpose**: Manual override for immediate shutdown

**Features**:
- CLI command: `inneros emergency-stop`
- Creates `.automation/EMERGENCY_STOP` file
- All handlers check this file before processing
- Sends notification: "Emergency stop activated"

**Recovery**:
- Manual review required
- Remove stop file manually
- Restart automation with verification

---

## 📊 Implementation Plan

### **Phase 1: Core Circuit Breaker** (P1 - 1 day)

**Deliverables**:
- `CircuitBreaker` base class
- Per-feature request tracking
- State management (CLOSED/HALF-OPEN/OPEN)
- Basic threshold enforcement

**Tests**: 15 unit tests
- State transitions
- Threshold enforcement
- Cooldown behavior
- Manual override

---

### **Phase 2: Budget Enforcer** (P1 - 1 day)

**Deliverables**:
- `BudgetEnforcer` class
- Cost tracking per feature
- Daily budget calculation
- Automatic shutdown logic

**Tests**: 12 unit tests
- Cost accumulation
- Threshold alerts
- Shutdown behavior
- Budget reset logic

---

### **Phase 3: Anomaly Detection** (P2 - 2 days)

**Deliverables**:
- `AnomalyDetector` class
- Burst detection
- Same-file thrashing detection
- Error rate monitoring
- Time-based alerts

**Tests**: 18 unit tests
- Pattern recognition
- False positive prevention
- Alert triggering
- Integration with circuit breaker

---

### **Phase 4: Integration & Monitoring** (P1 - 1 day)

**Deliverables**:
- Integrate with all existing handlers
- Dashboard endpoint: `/budget` (HTTP monitoring)
- CLI: `inneros budget-status`
- macOS notification system
- Emergency stop mechanism

**Tests**: 10 integration tests
- End-to-end protection
- Multi-feature coordination
- Dashboard accuracy
- Emergency stop effectiveness

---

## 🔧 Technical Design

### **CircuitBreaker Class**

```python
class CircuitBreaker:
    """
    Circuit breaker pattern for API call protection.
    
    States:
    - CLOSED: Normal operation, requests allowed
    - OPEN: Circuit tripped, all requests blocked
    - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(
        self,
        name: str,
        max_requests_per_hour: int,
        max_requests_per_day: int,
        cooldown_seconds: int = 60,
        circuit_open_duration: int = 3600
    ):
        self.name = name
        self.state = CircuitState.CLOSED
        self.request_counts = {
            'hour': deque(maxlen=3600),  # Last hour
            'day': deque(maxlen=86400)    # Last day
        }
        self.thresholds = {
            'hour': max_requests_per_hour,
            'day': max_requests_per_day
        }
        self.cooldown = cooldown_seconds
        self.circuit_open_until = None
    
    def allow_request(self) -> tuple[bool, str]:
        """
        Check if request should be allowed.
        
        Returns:
            (allowed: bool, reason: str)
        """
        # Check circuit state
        if self.state == CircuitState.OPEN:
            if time.time() < self.circuit_open_until:
                return False, f"Circuit OPEN (retry in {int(self.circuit_open_until - time.time())}s)"
            else:
                self.state = CircuitState.HALF_OPEN
        
        # Check rate limits
        now = time.time()
        
        # Remove old entries
        self._cleanup_old_entries(now)
        
        # Check hourly limit
        hour_count = len([t for t in self.request_counts['hour'] if now - t < 3600])
        if hour_count >= self.thresholds['hour']:
            self._open_circuit("Hourly limit exceeded")
            return False, f"Hourly limit ({self.thresholds['hour']}) exceeded"
        
        # Check daily limit
        day_count = len([t for t in self.request_counts['day'] if now - t < 86400])
        if day_count >= self.thresholds['day']:
            self._open_circuit("Daily limit exceeded")
            return False, f"Daily limit ({self.thresholds['day']}) exceeded"
        
        # Check cooldown (same as existing cooldown system)
        # ... existing cooldown logic ...
        
        return True, "OK"
    
    def record_request(self, success: bool = True):
        """Record a request for tracking."""
        now = time.time()
        self.request_counts['hour'].append(now)
        self.request_counts['day'].append(now)
        
        if not success and self.state == CircuitState.HALF_OPEN:
            self._open_circuit("Request failed in HALF_OPEN state")
    
    def _open_circuit(self, reason: str):
        """Open circuit breaker."""
        self.state = CircuitState.OPEN
        self.circuit_open_until = time.time() + self.circuit_open_duration
        logger.warning(f"Circuit breaker OPEN: {self.name} - {reason}")
        # Send alert
        self._send_alert(f"🚨 Circuit breaker activated: {self.name}", reason)
    
    def get_status(self) -> dict:
        """Get current circuit breaker status."""
        now = time.time()
        self._cleanup_old_entries(now)
        
        hour_count = len([t for t in self.request_counts['hour'] if now - t < 3600])
        day_count = len([t for t in self.request_counts['day'] if now - t < 86400])
        
        return {
            'name': self.name,
            'state': self.state.name,
            'requests_last_hour': hour_count,
            'requests_last_day': day_count,
            'hourly_limit': self.thresholds['hour'],
            'daily_limit': self.thresholds['day'],
            'hourly_usage_pct': (hour_count / self.thresholds['hour']) * 100,
            'daily_usage_pct': (day_count / self.thresholds['day']) * 100,
            'circuit_open_until': self.circuit_open_until
        }
```

---

### **BudgetEnforcer Class**

```python
class BudgetEnforcer:
    """
    Enforces daily budget limits across all features.
    """
    
    def __init__(self, daily_budget: float = 10.00):
        self.daily_budget = daily_budget
        self.alert_threshold = daily_budget * 0.50
        self.shutdown_threshold = daily_budget * 0.80
        self.costs = []  # List of (timestamp, feature, cost) tuples
        self.shutdown_active = False
    
    def record_cost(self, feature: str, estimated_cost: float) -> bool:
        """
        Record a cost and check if budget exceeded.
        
        Returns:
            True if request allowed, False if budget exceeded
        """
        if self.shutdown_active:
            return False
        
        now = time.time()
        self.costs.append((now, feature, estimated_cost))
        
        # Calculate today's costs
        today_cost = self._get_daily_cost()
        
        # Check thresholds
        if today_cost >= self.shutdown_threshold:
            self._activate_shutdown(today_cost)
            return False
        elif today_cost >= self.alert_threshold:
            self._send_budget_alert(today_cost)
        
        return True
    
    def _get_daily_cost(self) -> float:
        """Calculate costs in last 24 hours."""
        now = time.time()
        day_ago = now - 86400
        return sum(cost for ts, _, cost in self.costs if ts > day_ago)
    
    def _activate_shutdown(self, current_cost: float):
        """Activate emergency shutdown."""
        self.shutdown_active = True
        
        # Create emergency stop file
        Path('.automation/BUDGET_EXCEEDED').write_text(
            f"Budget exceeded: ${current_cost:.2f} / ${self.daily_budget:.2f}\n"
            f"Timestamp: {datetime.now()}\n"
        )
        
        logger.critical(f"🚨 BUDGET EXCEEDED: ${current_cost:.2f} / ${self.daily_budget:.2f}")
        
        # Send critical alert
        self._send_alert(
            "🚨 BUDGET EXCEEDED - AUTOMATION STOPPED",
            f"Daily budget (${self.daily_budget:.2f}) exceeded.\n"
            f"Current spend: ${current_cost:.2f}\n"
            f"All automation has been stopped.\n"
            f"Review costs and remove .automation/BUDGET_EXCEEDED to restart."
        )
    
    def get_status(self) -> dict:
        """Get current budget status."""
        daily_cost = self._get_daily_cost()
        
        return {
            'daily_budget': self.daily_budget,
            'current_spend': daily_cost,
            'remaining': self.daily_budget - daily_cost,
            'usage_pct': (daily_cost / self.daily_budget) * 100,
            'shutdown_active': self.shutdown_active,
            'alert_threshold': self.alert_threshold,
            'shutdown_threshold': self.shutdown_threshold
        }
```

---

## 📋 Configuration Example

```yaml
# .automation/protection_config.yaml

# Global budget settings
budget:
  daily_limit_usd: 10.00
  alert_at_percent: 50
  shutdown_at_percent: 80

# Per-feature circuit breakers
circuit_breakers:
  youtube_handler:
    enabled: true
    max_requests_per_hour: 50
    max_requests_per_day: 200
    cooldown_seconds: 60
    circuit_open_duration: 3600
    estimated_cost_per_request: 0.00  # Free API
    
  openai_handler:
    enabled: true
    max_requests_per_hour: 100
    max_requests_per_day: 500
    cooldown_seconds: 30
    circuit_open_duration: 7200
    estimated_cost_per_request: 0.12  # GPT-4 estimate
    
  screenshot_ocr:
    enabled: true
    max_requests_per_hour: 30
    max_requests_per_day: 100
    cooldown_seconds: 10
    circuit_open_duration: 1800
    estimated_cost_per_request: 0.02

# Anomaly detection
anomaly_detection:
  enabled: true
  
  burst_detection:
    max_requests_per_minute: 10
    action: throttle  # or 'circuit_break'
  
  file_thrashing:
    max_processing_count: 3
    window_seconds: 300
    action: circuit_break
  
  error_rate:
    threshold_percent: 50
    min_requests: 10
    action: alert
  
  off_hours:
    quiet_hours_start: "02:00"
    quiet_hours_end: "06:00"
    max_requests_during_quiet: 5
    action: alert

# Notifications
notifications:
  macos_enabled: true
  log_enabled: true
  email_enabled: false  # Future
```

---

## 🚀 Integration with Existing Handlers

### **Before** (Current - Vulnerable)
```python
class YouTubeFeatureHandler:
    def process(self, file_path: Path, event_type: str):
        # Direct processing, no protection
        transcript = self.transcript_cache.get(video_id)
        if not transcript:
            transcript = fetcher.fetch_transcript(video_id)  # ❌ Unlimited calls
            self.transcript_cache.set(video_id, transcript)
```

### **After** (Protected)
```python
class YouTubeFeatureHandler:
    def __init__(self, config: dict):
        # ... existing init ...
        
        # NEW: Circuit breaker integration
        self.circuit_breaker = CircuitBreaker(
            name='youtube_handler',
            max_requests_per_hour=config.get('max_requests_per_hour', 50),
            max_requests_per_day=config.get('max_requests_per_day', 200),
            cooldown_seconds=config.get('cooldown_seconds', 60)
        )
        
        # NEW: Budget enforcer (shared instance)
        self.budget_enforcer = BudgetEnforcer.get_instance()
    
    def process(self, file_path: Path, event_type: str):
        # NEW: Check circuit breaker
        allowed, reason = self.circuit_breaker.allow_request()
        if not allowed:
            logger.warning(f"Request blocked: {reason}")
            return
        
        # Existing cooldown check
        if file_path in self._last_processed:
            # ... cooldown logic ...
            return
        
        # Existing cache check
        transcript = self.transcript_cache.get(video_id)
        if not transcript:
            # NEW: Check budget before API call
            if not self.budget_enforcer.record_cost('youtube_handler', 0.00):
                logger.error("Budget exceeded - API call blocked")
                return
            
            # Make API call
            try:
                transcript = fetcher.fetch_transcript(video_id)
                self.transcript_cache.set(video_id, transcript)
                
                # NEW: Record successful request
                self.circuit_breaker.record_request(success=True)
                
            except Exception as e:
                # NEW: Record failed request
                self.circuit_breaker.record_request(success=False)
                raise
```

---

## 📊 Monitoring & Alerts

### **CLI Commands**

```bash
# Check current protection status
inneros protection-status

# Output:
# ======================================================================
# PROTECTION SYSTEM STATUS
# ======================================================================
# 
# 💰 Budget Status:
#    Daily Budget: $10.00
#    Current Spend: $2.45 (24.5%)
#    Remaining: $7.55
#    Status: 🟢 SAFE
# 
# 🔌 Circuit Breakers:
#    youtube_handler:     🟢 CLOSED  (12/50 hourly, 45/200 daily)
#    openai_handler:      🟢 CLOSED  (25/100 hourly, 120/500 daily)
#    screenshot_ocr:      🟡 HALF_OPEN (Testing recovery)
# 
# 🚨 Anomalies (Last Hour):
#    - 14:32: Burst detected (15 requests/min) - Throttled
#    - 14:45: File thrashing (youtube-note.md) - Circuit breaker opened
# 
# ✅ System Status: PROTECTED

# Emergency stop
inneros emergency-stop

# Reset circuit breaker manually
inneros circuit-reset youtube_handler

# View cost breakdown
inneros cost-report --today
```

---

### **HTTP Monitoring Endpoints**

```bash
# Budget status
curl http://localhost:8000/protection/budget

# Circuit breaker status
curl http://localhost:8000/protection/circuits

# Anomaly log
curl http://localhost:8000/protection/anomalies
```

---

## 💰 Cost Savings Analysis

### **Incident Scenarios**

| Scenario | Without Protection | With Protection | Savings |
|----------|-------------------|-----------------|---------|
| **YouTube Loop (Actual)** | IP ban (free API) | Stopped at 50/hr | No IP ban |
| **OpenAI GPT-4 Loop** | $120-1,000+ | Stopped at $10 | $110-990 |
| **Screenshot OCR Loop** | $50-200 | Stopped at $10 | $40-190 |
| **AWS API Loop** | $500-5,000+ | Stopped at $10 | $490-4,990 |

**ROI**: One prevented incident pays for entire development (1 week effort)

---

## 🎯 Success Metrics

### **Technical Metrics**
- ✅ Zero budget overruns (100% enforcement)
- ✅ Circuit breaker activation <5 min after anomaly
- ✅ False positive rate <5% (don't block legitimate usage)
- ✅ Alert delivery <30 seconds
- ✅ Emergency stop <10 seconds

### **Business Metrics**
- ✅ Max daily spend: $10 (configurable)
- ✅ No unexpected charges
- ✅ No IP bans from rate limiting
- ✅ Incident detection before damage

---

## 📅 Timeline & Priority

### **Priority**: P1 (HIGH)
- Prevents catastrophic financial damage
- Learned from real incident
- Applicable to all external APIs
- Low effort, very high value

### **Timeline**: 4-5 days total
- Phase 1: Circuit Breaker (1 day)
- Phase 2: Budget Enforcer (1 day)
- Phase 3: Anomaly Detection (2 days)
- Phase 4: Integration (1 day)

### **Dependencies**: None
- Can implement independently
- Works alongside existing cooldown/caching
- Adds additional protection layer

### **When to Implement**
- **Recommended**: After Distribution System
- **Blocker**: Before adding ANY paid APIs
- **Required**: Before OpenAI integration
- **Nice-to-have**: As standalone protection

---

## 📝 Lessons Learned from Incident

### **What We Learned**
1. ⚠️ **File watching loops are real** - One bug = 2,165 events
2. ⚠️ **Free APIs aren't safe** - IP bans hurt too
3. ⚠️ **Cooldown alone isn't enough** - Need multiple protection layers
4. ⚠️ **Early detection is critical** - 5 min vs 6 hours = huge difference
5. ⚠️ **Cost could have been catastrophic** - With paid API = $120-1,000+

### **Prevention Principles**
1. ✅ **Defense in depth** - Multiple protection layers
2. ✅ **Fail fast** - Detect anomalies within minutes
3. ✅ **Automatic shutdown** - Don't require human intervention
4. ✅ **Budget ceiling** - Hard limit on financial damage
5. ✅ **Universal application** - Protect ALL external APIs

---

## 🔗 Related Documents

- `catastrophic-incident-fix-2025-10-08.md` - Incident that triggered this
- `youtube-rate-limit-investigation-2025-10-08.md` - Forensic analysis
- `daemon-automation-system-current-state-roadmap.md` - Integration point
- `automation-monitoring-requirements.md` - Monitoring standards

---

**Status**: 📋 BACKLOG  
**Next Action**: Implement after Distribution System complete  
**Blocker Status**: BLOCKS any paid API integration  
**Estimated Effort**: 4-5 days (1 week sprint)

---

**Created**: 2025-10-08 21:55 PDT  
**Last Updated**: 2025-10-08 21:55 PDT  
**Priority**: P1 - Prevent catastrophic incidents  
**Value**: CRITICAL - Prevents unlimited financial damage
