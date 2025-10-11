# Architecture Decision Record: Circuit Breaker & Rate Limit Protection System

**ADR**: 002  
**Date**: 2025-10-08  
**Status**: 📋 PROPOSED (Awaiting Implementation)  
**Context**: Catastrophic incident (2,165 events → IP ban) revealed vulnerability to infinite loops with external APIs  
**Decision**: Implement multi-layer protection system (circuit breakers + budget enforcement + anomaly detection)  
**Trigger**: YouTube incident could have cost $120-1,000+ with paid APIs  

---

## Executive Summary

The catastrophic YouTube incident (Oct 8, 2025) exposed a critical vulnerability: **infinite loops with external APIs can cause unlimited financial damage**. While the actual incident only resulted in an IP ban (free API), the same bug with paid APIs (OpenAI GPT-4, AWS, GCP) would have caused $120-1,000+ in uncontrolled charges.

**This ADR proposes a defense-in-depth protection system** that prevents infinite loops, enforces budget ceilings, and auto-shuts down before catastrophic cost accumulation.

---

## Decision Drivers

### **Incident Analysis: What Happened**
- **File watching loop bug** → 2,165 processing events in hours
- **No cooldown** → Same file processed 758 times (should be 1-2)
- **No caching** → ~1,000 YouTube API calls made
- **Result**: Network-wide YouTube IP ban

### **Risk Analysis: What COULD Have Happened**
- **YouTube**: Free API → IP ban (recoverable in 24-48h)
- **OpenAI GPT-4**: 1,000 calls × $0.12 = **$120+ in hours**
- **AWS/GCP APIs**: Could easily rack up **$1,000+ in hours**
- **No Protection**: Bug continues until manually discovered

### **Strategic Drivers**
1. **Paid API Integration Planned**: OpenAI, AWS transcription, premium services
2. **24/7 Automation**: Daemon runs continuously, no human oversight
3. **Financial Risk**: Single bug can cause unlimited charges
4. **User Trust**: System must be safe by default
5. **Compliance**: Budget controls required for production deployment

### **Technical Drivers**
1. **Cooldown alone insufficient**: Prevents loops but not cost overruns
2. **Caching alone insufficient**: Doesn't catch new infinite loops
3. **Need defense-in-depth**: Multiple protection layers
4. **Real-time detection**: Must catch anomalies within minutes, not hours
5. **Zero-config protection**: Should work by default, no user action required

---

## Considered Options

### Option 1: Manual Monitoring Only
**Description**: Rely on users to manually monitor logs and costs

**Pros**:
- No development effort required
- Users maintain full control
- Simple to understand

**Cons**:
- ❌ **Completely reactive**: Damage happens before detection
- ❌ **Requires constant vigilance**: Users must monitor 24/7
- ❌ **No protection during sleep/weekends**: Incident happened overnight
- ❌ **Violates fail-safe principle**: System should be safe by default
- ❌ **Unlimited financial exposure**: No ceiling on damage

**Verdict**: REJECTED - Unacceptable risk for production system

---

### Option 2: Simple Request Counting
**Description**: Add basic per-feature request counters with hard limits

**Pros**:
- Simple to implement (1-2 days)
- Low overhead
- Prevents runaway requests

**Cons**:
- ❌ **No cost awareness**: Doesn't prevent budget overruns
- ❌ **No anomaly detection**: Doesn't catch burst patterns
- ❌ **No emergency override**: Can't manually stop if needed
- ❌ **Binary enforcement**: Either works or completely blocks
- ❌ **Per-feature only**: No system-wide budget protection

**Verdict**: REJECTED - Insufficient protection for paid APIs

---

### Option 3: Cloud-Based Monitoring Service
**Description**: Use external service (DataDog, New Relic) for monitoring and alerts

**Pros**:
- Professional-grade monitoring
- Advanced analytics and dashboards
- SMS/email alerting included

**Cons**:
- ❌ **Monthly cost**: $50-200/month ongoing
- ❌ **External dependency**: Requires internet connectivity
- ❌ **Reactive only**: Alerts after damage, doesn't prevent
- ❌ **No automatic shutdown**: Still requires manual intervention
- ❌ **Overkill for single user**: Enterprise solution for personal system

**Verdict**: REJECTED - Cost doesn't justify value for personal system

---

### Option 4: Multi-Layer Protection System ✅ **SELECTED**
**Description**: Defense-in-depth with circuit breakers, budget enforcement, anomaly detection, and emergency controls

**Pros**:
- ✅ **Prevents damage before it happens**: Proactive protection
- ✅ **Multiple protection layers**: Defense-in-depth approach
- ✅ **Budget ceiling enforcement**: Hard $10/day limit (configurable)
- ✅ **Automatic shutdown**: No manual intervention required
- ✅ **Anomaly detection**: Catches loops within minutes
- ✅ **Universal application**: Protects ALL external APIs automatically
- ✅ **Emergency override**: Manual kill switch available
- ✅ **Zero ongoing cost**: Self-contained, no external services
- ✅ **Production-ready**: Monitoring, alerts, health checks included

**Cons**:
- ⚠️ **4-5 days development**: Not trivial implementation
- ⚠️ **Adds complexity**: New protection layer to maintain
- ⚠️ **Requires integration**: All handlers must use protection system
- ⚠️ **False positives possible**: May block legitimate high-volume usage

**Impact**:
- **Development**: 4-5 days initial implementation
- **Integration**: All existing handlers require protection integration
- **Performance**: <1ms overhead per request (negligible)
- **Maintenance**: Minimal (self-monitoring system)

**Verdict**: SELECTED - Only option providing adequate protection for paid APIs

---

## Detailed Design

### **Layer 1: Per-Feature Circuit Breakers** 🔌

**Purpose**: Individual feature protection with automatic circuit breaking

**Implementation**:
```python
class CircuitBreaker:
    - State machine: CLOSED → HALF_OPEN → OPEN
    - Request counting: hourly/daily windows
    - Automatic tripping: threshold exceeded → circuit opens
    - Cooldown period: configurable recovery time
    - Manual override: force open/close capability
```

**Configuration** (per feature):
```yaml
youtube_handler:
  max_requests_per_hour: 50
  max_requests_per_day: 200
  cooldown_seconds: 60
  circuit_open_duration: 3600  # 1 hour
```

**States**:
- 🟢 **CLOSED**: Normal operation, requests allowed
- 🟡 **HALF_OPEN**: Testing recovery, limited requests
- 🔴 **OPEN**: Circuit tripped, all requests blocked

---

### **Layer 2: Global Budget Enforcer** 💰

**Purpose**: System-wide cost protection with hard ceiling

**Implementation**:
```python
class BudgetEnforcer:
    - Daily budget tracking: accumulate estimated costs
    - Alert thresholds: 50% (warning), 80% (shutdown)
    - Cost estimation: per-feature cost models
    - Automatic shutdown: at 80% budget consumption
    - Emergency stop file: .automation/BUDGET_EXCEEDED
```

**Configuration**:
```yaml
budget_enforcer:
  daily_budget: 10.00  # USD
  alert_threshold: 0.50  # 50%
  shutdown_threshold: 0.80  # 80%
  
  cost_tracking:
    openai_gpt4: 0.12  # Per request estimate
    screenshot_ocr: 0.02  # Per image estimate
```

**Behavior**:
- **50% budget** → macOS notification + log alert
- **80% budget** → **AUTOMATIC SHUTDOWN** + emergency file
- **100% budget** → Unreachable (system stops at 80%)

---

### **Layer 3: Anomaly Detection** 🚨

**Purpose**: Detect unusual patterns before damage occurs

**Patterns Detected**:

1. **Burst Detection**
   - Trigger: >10 requests in 1 minute
   - Likely cause: File watching loop
   - Action: Throttle to 50% rate, alert user

2. **File Thrashing**
   - Trigger: Same file processed >3 times in 5 minutes
   - Likely cause: File watching loop
   - Action: Circuit break for that file, alert

3. **Error Rate Spike**
   - Trigger: >50% errors in last 10 requests
   - Likely cause: API down or bad config
   - Action: Alert user, increase retry delays

4. **Off-Hours Activity**
   - Trigger: Unusual processing between 2am-6am
   - Likely cause: Runaway automation
   - Action: Alert user, reduce rate

**Actions**:
- Log anomaly with full context
- Send macOS notification
- Reduce processing rate (throttle)
- If continues 5 min → Circuit break

---

### **Layer 4: Emergency Kill Switch** 🛑

**Purpose**: Manual override for immediate shutdown

**Implementation**:
```bash
# CLI command
inneros emergency-stop

# Creates file
.automation/EMERGENCY_STOP

# All handlers check before processing
if Path('.automation/EMERGENCY_STOP').exists():
    logger.error("Emergency stop active - processing halted")
    return
```

**Recovery**:
- Manual file removal required
- Forces review before restart
- Clean state verification
- Log review recommended

---

## Integration Pattern

### **Before** (Current - Vulnerable)
```python
class YouTubeFeatureHandler:
    def process(self, file_path: Path, event_type: str):
        # Cooldown check (prevents rapid loops)
        if file_path in self._last_processed:
            # ... cooldown logic ...
            return
        
        # Cache check (prevents redundant calls)
        transcript = self.transcript_cache.get(video_id)
        if not transcript:
            transcript = fetcher.fetch_transcript(video_id)  # ❌ No protection
            self.transcript_cache.set(video_id, transcript)
```

**Vulnerabilities**:
- ❌ No request limit enforcement
- ❌ No cost tracking
- ❌ No anomaly detection
- ❌ No emergency stop capability

---

### **After** (Protected)
```python
class YouTubeFeatureHandler:
    def __init__(self, config: dict):
        # Existing protections
        self.cooldown_seconds = config.get('cooldown_seconds', 60)
        self.transcript_cache = TranscriptCache(...)
        
        # NEW: Circuit breaker integration
        self.circuit_breaker = CircuitBreaker(
            name='youtube_handler',
            max_requests_per_hour=50,
            max_requests_per_day=200
        )
        
        # NEW: Budget enforcer (shared instance)
        self.budget_enforcer = BudgetEnforcer.get_instance()
    
    def process(self, file_path: Path, event_type: str):
        # NEW: Emergency stop check
        if self._check_emergency_stop():
            return
        
        # NEW: Circuit breaker check
        allowed, reason = self.circuit_breaker.allow_request()
        if not allowed:
            logger.warning(f"Request blocked: {reason}")
            return
        
        # Existing: Cooldown check
        if self._check_cooldown(file_path):
            return
        
        # Existing: Cache check
        transcript = self.transcript_cache.get(video_id)
        if not transcript:
            # NEW: Budget check before API call
            estimated_cost = 0.00  # YouTube is free
            if not self.budget_enforcer.record_cost('youtube_handler', estimated_cost):
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

**Protection Layers**:
1. ✅ Emergency stop check (Layer 4)
2. ✅ Circuit breaker limits (Layer 1)
3. ✅ Cooldown prevention (Existing)
4. ✅ Budget enforcement (Layer 2)
5. ✅ Anomaly detection (Layer 3 - background)

---

## Implementation Phases

### **Phase 1: Circuit Breaker Core** (1 day)
**Deliverables**:
- `CircuitBreaker` base class
- State machine (CLOSED/HALF_OPEN/OPEN)
- Request tracking with time windows
- Threshold enforcement
- Manual override capability

**Tests**: 15 unit tests
- State transitions
- Threshold calculations
- Cooldown behavior
- Manual override

---

### **Phase 2: Budget Enforcer** (1 day)
**Deliverables**:
- `BudgetEnforcer` singleton class
- Cost tracking per feature
- Daily budget calculations
- Threshold alerts (50%, 80%)
- Automatic shutdown logic

**Tests**: 12 unit tests
- Cost accumulation
- Threshold detection
- Shutdown behavior
- Budget reset (daily)

---

### **Phase 3: Anomaly Detection** (2 days)
**Deliverables**:
- `AnomalyDetector` class
- Burst detection algorithm
- File thrashing detection
- Error rate monitoring
- Off-hours activity detection
- Alert system integration

**Tests**: 18 unit tests
- Pattern recognition
- False positive prevention
- Alert triggering
- Throttle actions

---

### **Phase 4: Integration & Monitoring** (1 day)
**Deliverables**:
- Integration with all handlers
- CLI: `inneros protection-status`
- HTTP endpoints: `/protection/budget`, `/protection/circuits`
- macOS notification system
- Emergency stop mechanism
- Dashboard UI

**Tests**: 10 integration tests
- End-to-end protection
- Multi-feature coordination
- Dashboard accuracy
- Emergency stop effectiveness

---

## Monitoring & Observability

### **CLI Commands**
```bash
# Check protection status
inneros protection-status

# Output:
# 💰 Budget Status: $2.45 / $10.00 (24.5%)
# 🔌 Circuit Breakers:
#    youtube_handler:  🟢 CLOSED (12/50 hourly)
#    openai_handler:   🟢 CLOSED (25/100 hourly)
# 🚨 Anomalies: 2 in last hour
# ✅ System Status: PROTECTED

# Emergency stop
inneros emergency-stop

# Reset circuit breaker
inneros circuit-reset youtube_handler

# View cost report
inneros cost-report --today
```

---

### **HTTP Endpoints**
```bash
# Budget status (JSON)
curl http://localhost:8000/protection/budget

# Circuit breaker status
curl http://localhost:8000/protection/circuits

# Anomaly log
curl http://localhost:8000/protection/anomalies

# Health check
curl http://localhost:8000/protection/health
```

---

### **macOS Notifications**
- **50% budget**: "⚠️ Budget Alert: 50% consumed ($5.00 / $10.00)"
- **80% budget**: "🚨 BUDGET EXCEEDED - Automation stopped"
- **Circuit breaker**: "🔴 Circuit breaker activated: youtube_handler"
- **Anomaly detected**: "⚠️ Burst detected: 15 requests/min"

---

## Consequences

### **Positive Consequences**

1. **Financial Protection** 💰
   - **Before**: Unlimited financial exposure
   - **After**: Hard $10/day ceiling (configurable)
   - **Impact**: $120-1,000+ incidents prevented

2. **Automatic Safety** 🛡️
   - **Before**: Manual monitoring required
   - **After**: Zero-config protection
   - **Impact**: Safe by default, no user action needed

3. **Real-Time Detection** ⚡
   - **Before**: Incidents discovered hours later
   - **After**: Anomalies detected within minutes
   - **Impact**: Damage limited to <$1 instead of $100+

4. **Universal Application** 🌐
   - **Before**: Each handler vulnerable
   - **After**: All APIs protected automatically
   - **Impact**: Add new APIs safely

5. **Production Confidence** ✅
   - **Before**: Hesitant to add paid APIs
   - **After**: Confident in system safety
   - **Impact**: Unblocks OpenAI, AWS integrations

---

### **Negative Consequences**

1. **Development Effort** ⏱️
   - **Impact**: 4-5 days implementation time
   - **Mitigation**: One prevented incident = ROI

2. **Added Complexity** 🔧
   - **Impact**: New protection layer to maintain
   - **Mitigation**: Self-monitoring, minimal overhead

3. **False Positives** ⚠️
   - **Impact**: Legitimate high-volume usage may be blocked
   - **Mitigation**: Configurable thresholds, manual override

4. **Integration Requirement** 🔗
   - **Impact**: All handlers must integrate protection
   - **Mitigation**: Template pattern, copy-paste integration

---

### **Risk Assessment**

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| False positive blocks legitimate usage | Medium | Low | Configurable thresholds, manual override |
| Budget too restrictive | Low | Low | User-configurable limits |
| Overhead impacts performance | Very Low | Low | <1ms per request, negligible |
| Users bypass protection | Low | High | Default-on, requires explicit disable |
| Protection layer has bugs | Low | Medium | Comprehensive test suite, gradual rollout |

---

## Success Metrics

### **Technical Metrics**
- ✅ Zero budget overruns (100% enforcement)
- ✅ Circuit breaker activation <5 min after anomaly
- ✅ False positive rate <5%
- ✅ Alert delivery <30 seconds
- ✅ Emergency stop <10 seconds

### **Business Metrics**
- ✅ Max daily spend: $10 (configurable)
- ✅ No unexpected charges
- ✅ No IP bans from rate limiting
- ✅ Incident detection before damage

### **User Experience Metrics**
- ✅ Zero-config protection (works by default)
- ✅ Clear error messages when blocked
- ✅ Easy manual override when needed
- ✅ Transparent cost tracking

---

## Dependencies & Blockers

### **Dependencies**
- **None**: Can implement independently of other work

### **Blockers**
- **BLOCKS**: Any paid API integration (OpenAI, AWS, GCP)
- **BLOCKS**: Production deployment without financial controls

### **Integration Points**
- **YouTubeFeatureHandler**: Already has cooldown + caching
- **ScreenshotHandler**: Will need integration
- **SmartLinkHandler**: Will need integration
- **Future handlers**: Must use protection from day 1

---

## Timeline & Prioritization

### **Recommended Priority**: P1 (HIGH)
**Reasoning**:
- Prevents catastrophic financial damage
- Learned from real incident
- Required before paid API integration
- Low effort (4-5 days), very high value

### **Recommended Timing**
- **After**: Distribution System (2-3 days)
- **Before**: Any paid API integration
- **Blocks**: OpenAI, AWS, premium services

### **Alternative Timing**
- **Immediate**: If planning to add paid APIs soon
- **Deferred**: If only using free APIs indefinitely

---

## Alternatives Considered (Detailed)

### **Alternative A: Rate Limiting Library (e.g., ratelimit, limits)**
**Pros**: Battle-tested, well-documented, simple integration
**Cons**: No budget awareness, no anomaly detection, library dependency
**Verdict**: Insufficient - needs cost tracking

### **Alternative B: Cloud Cost Alerts (AWS Budget Alerts, GCP Billing)**
**Pros**: Professional-grade, provider-native, SMS/email alerts
**Cons**: Reactive only (alerts after spend), no automatic shutdown, cloud-only
**Verdict**: Complementary but not sufficient alone

### **Alternative C: Custom Middleware Pattern**
**Pros**: Flexible, extensible, minimal coupling
**Cons**: More complex implementation, harder to test
**Verdict**: Over-engineering for current needs

---

## Related Documents

- **Trigger Incident**: `youtube-rate-limit-investigation-2025-10-08.md`
- **Incident Fix**: `catastrophic-incident-fix-2025-10-08.md`
- **Implementation Manifest**: `circuit-breaker-rate-limit-protection-manifest.md`
- **Project Tracking**: `project-todo-v3.md`
- **Current State**: `CURRENT-STATE-2025-10-08.md`

---

## Lessons Learned from Incident

1. **File watching loops are real** - One bug caused 2,165 events
2. **Free APIs aren't safe** - IP bans hurt too
3. **Cooldown alone isn't enough** - Need multiple protection layers
4. **Early detection is critical** - 5 min vs 6 hours = huge difference
5. **Cost could have been catastrophic** - With paid API = $120-1,000+

---

## Decision Rationale

**Why Multi-Layer Protection**:
- Defense-in-depth prevents single point of failure
- Different layers catch different failure modes
- Redundancy ensures protection even if one layer fails

**Why Budget Ceiling**:
- Absolute guarantee against runaway costs
- User control over maximum financial exposure
- Peace of mind for production deployment

**Why Anomaly Detection**:
- Proactive vs reactive protection
- Catches patterns before damage
- Enables intelligent throttling vs binary blocking

**Why Emergency Override**:
- Human judgment still valuable
- Edge cases may need manual intervention
- Fail-safe mechanism if automation goes wrong

---

## Approval & Sign-off

**Author**: Cascade AI (InnerOS Development Team)  
**Reviewers**: User (Product Owner)  
**Status**: 📋 PROPOSED - Awaiting approval  
**Implementation**: Planned after Distribution System

---

**ADR**: 002  
**Date**: 2025-10-08  
**Last Updated**: 2025-10-08  
**Status**: 📋 PROPOSED (Awaiting Implementation)
