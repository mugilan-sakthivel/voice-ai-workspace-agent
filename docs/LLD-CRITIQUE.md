# LLD Critical Review - Voice AI Workspace Agent

## Summary

The LLD covers most areas but has **gaps in specific technical integrations** and some **ambiguities** that need resolution before implementation.

---

## ✅ WHAT'S WELL COVERED

| Area | Status | Notes |
|------|--------|-------|
| System Architecture | ✅ Good | Clear component diagram |
| UI Components (assistant-ui) | ✅ Good | Detailed with code examples |
| AI Agent (LangGraph) | ✅ Good | Using pre-built, not custom |
| CLI Tool Wrappers | ✅ Good | gws & m365 commands mapped |
| OAuth Flow | ✅ Good | Detailed with encryption |
| Database Schema | ✅ Good | Supabase Postgres + durable app tables |
| API Contracts | ✅ Good | REST + WebSocket defined |
| Security | ✅ Good | Token management clear |

---

## ❌ GAPS & MISSING DETAILS

### 1. **Voice/Wake Word - CRITICAL GAPS**

| Issue | What's Missing |
|-------|---------------|
| **Background execution on iOS** | iOS kills background audio after ~30 seconds. Need to explain how wake word works when app is "closed" |
| **Wake word model** | Picovoice Porcupine needs a custom wake word model. How do we create/train "Hey Agent"? Cost? |
| **Battery impact** | Always-on listening drains battery. What's the mitigation strategy? |
| **Permissions UX** | iOS 15+ has strict microphone permissions. Flow for "always allow"? |

**Action Required:**
- Research iOS background audio limitations
- Decide: Custom wake word vs pre-built (Alexa, Hey Google alternatives)
- Consider: Push-to-talk as simpler alternative for v1?

---

### 2. **Gemini Voice API - GAPS**

| Issue | What's Missing |
|-------|---------------|
| **STT not clearly documented** | LLD mentions Gemini STT but Gemini TTS docs don't show STT. Using multimodal? |
| **Streaming STT** | Real-time transcription while speaking - how? Gemini doesn't have streaming STT |
| **Latency** | No benchmarks. Voice → STT → Agent → TTS → Audio could be 3-5 seconds |
| **Fallback** | What if Gemini is down? Alternative STT/TTS? |

**Action Required:**
- Clarify: Use Gemini multimodal for STT OR use Deepgram/Whisper?
- Add latency estimates and optimization strategies
- Define fallback services

---

### 3. **LangGraph Integration - NEEDS MORE DETAIL**

| Issue | What's Missing |
|-------|---------------|
| **Exact LangGraph setup** | No code showing actual LangGraph graph definition |
| **Tool definition format** | How do our CLI wrappers become LangGraph tools? |
| **Streaming to frontend** | How does LangGraph stream → FastAPI → WebSocket → assistant-ui? |
| **Error handling** | What if a tool fails mid-execution? Retry? Rollback? |
| **Checkpointer config** | PostgresSaver setup details missing |

**Action Required:**
- Add complete LangGraph graph definition
- Show tool → LangGraph integration code
- Define streaming pipeline end-to-end

---

### 4. **assistant-ui + Backend Integration - GAPS**

| Issue | What's Missing |
|-------|---------------|
| **Runtime connection** | How does assistant-ui runtime connect to our FastAPI? |
| **Auth header passing** | How does JWT get attached to WebSocket? |
| **React Native specifics** | assistant-ui React Native docs are sparse |
| **Offline mode** | What happens when network is unavailable? |

**Action Required:**
- Add assistant-ui runtime configuration for custom backend
- Show WebSocket auth handshake
- Test assistant-ui React Native ourselves

---

### 5. **CLI Authentication Flow - INCOMPLETE**

| Issue | What's Missing |
|-------|---------------|
| **gws CLI setup** | How is gws CLI installed on backend server? |
| **m365 CLI setup** | How is m365 CLI installed and authenticated? |
| **Token injection** | Env var injection shown but not how backend manages multiple users' tokens |
| **Concurrent execution** | Multiple users hitting same server - how to isolate CLI executions? |

**Action Required:**
- Document CLI installation in Docker
- Show multi-tenant token management
- Consider: Subprocess isolation or container-per-request?

---

### 6. **Missing: Onboarding Flow**

**Not documented at all:**
- How does a new user sign up?
- What's the first-time experience?
- How do we guide them to connect Google/Microsoft?
- What if they only want Google OR only Microsoft?

---

### 7. **Missing: Error Handling & Edge Cases**

**Not documented:**
- What if OAuth token refresh fails?
- What if CLI command times out?
- What if user revokes access from Google/Microsoft side?
- Network errors during voice streaming?
- Rate limited by Google/Microsoft APIs?

---

### 8. **Missing: Testing Strategy**

**Not documented:**
- How to test CLI tools without real accounts?
- Mock vs real API testing?
- Voice testing automation?
- Load testing for concurrent users?

---

### 9. **Missing: Cost Estimation**

**Not documented:**
- Gemini API costs (per request)
- Picovoice Porcupine licensing (commercial use)
- Cloud infrastructure costs
- Expected cost per user per month

---

### 10. **Deployment - VAGUE**

**Current:** Just says "GCP / Docker / Cloud Run"

**Missing:**
- Actual deployment architecture diagram
- How many instances? Auto-scaling rules?
- Database hosting (Cloud SQL?)
- Supabase project layout and backup policy?
- Domain, SSL, CDN setup

---

## 🔶 AMBIGUITIES TO RESOLVE

### A. Push-to-Talk vs Always Listening?

**Current LLD assumes:** Always-on wake word detection

**Reality:**
- Very hard on iOS (background restrictions)
- Battery drain concerns
- Privacy concerns

**Decision needed:**
- v1: Push-to-talk button only?
- v2: Add wake word for Android (easier)?
- v3: iOS wake word (if even possible)?

---

### B. Where does AI processing happen?

**Options:**
1. **All on server** - Mobile sends audio, server does everything
2. **Hybrid** - Mobile does STT, server does agent, mobile does TTS
3. **Edge** - Some processing on device

**Current LLD:** Unclear, seems server-side

**Recommendation:** Server-side for v1 (simpler), optimize later

---

### C. Real-time vs Request-Response?

**Voice interaction could be:**
1. **Request-Response** - User finishes speaking, wait for full response
2. **Real-time streaming** - Response starts while user still speaking (like GPT-4o)

**Current LLD:** Seems request-response

**Decision needed:** Start with request-response, streaming is much harder

---

## 📋 RECOMMENDED NEXT STEPS

### Priority 1: Resolve Critical Gaps
1. ❓ Decide on wake word vs push-to-talk for v1
2. ❓ Confirm Gemini STT approach or pick alternative (Deepgram?)
3. ❓ Test assistant-ui React Native with custom backend

### Priority 2: Add Missing Sections
4. 📝 Add onboarding flow design
5. 📝 Add error handling section
6. 📝 Add deployment architecture
7. 📝 Add cost estimation

### Priority 3: Prototype Key Risks
8. 🔬 Prototype: LangGraph + custom tools
9. 🔬 Prototype: assistant-ui + FastAPI WebSocket
10. 🔬 Prototype: gws/m365 CLI in Docker

---

## QUESTIONS FOR YOU

1. **Wake word priority?** Should v1 have wake word or just push-to-talk?

2. **Which workspace first?** Start with Google only, then add Microsoft?

3. **Web app too?** Should there be a web version alongside mobile?

4. **Self-hosted or cloud?** Will users run their own backend or use our cloud?

5. **Monetization?** Free tier limits? Subscription pricing?

---

*Review Date: 2024-01-15*
