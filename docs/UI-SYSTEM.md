# UI System

This product will use `assistant-ui` as the core conversation library, with a custom visual system layered on top so the app feels clean, calm, and premium instead of generic.

## 1. UI Direction

### Design Goals
- voice-first, but never visually noisy
- obvious primary action
- large readable conversation area
- clean approval moments for risky actions
- strong status feedback during listening, thinking, and speaking

### Core Principle
We are not building a flashy dashboard.

We are building a focused assistant experience:
- one main thread
- one main voice control
- one clear status at a time

## 2. Library Choice

### Primary UI Library
- `assistant-ui`

### Why
- strong conversation primitives
- built-in tool call rendering patterns
- good fit for streaming assistant responses
- faster path to a polished assistant product than building chat primitives from scratch

### Implementation Rule
Use `assistant-ui` primitives and customize them with our own:
- theme tokens
- spacing system
- status components
- approval cards
- voice controls

Do not ship the default look unchanged.

## 3. Visual System

### Color Palette
- Background: warm off-white
- Surface: soft stone
- Primary text: deep charcoal
- Secondary text: muted slate
- Accent: restrained amber
- Success: natural green
- Error: clear red without neon saturation

### Typography
- Primary font: `Manrope`
- Monospace font: `JetBrains Mono`

### Spacing
- generous vertical rhythm
- compact but readable message grouping
- no cramped composer or dense settings screens

### Shape
- rounded cards
- soft corners on bubbles and sheets
- no harsh borders unless required for clarity

## 4. Core Screens

### Conversation Screen
- sticky compact header
- workspace connection indicator
- thread viewport
- voice-aware composer
- floating or anchored hold-to-talk control

### Approval Sheet
- full-width bottom sheet on mobile
- plain-language summary of what will happen
- explicit confirm and cancel actions
- scope details hidden behind expanders

### Integration Screen
- Google and Microsoft sections
- connection status pills
- reconnect and disconnect actions
- minimal explanation text

### Settings Screen
- voice selection
- transcript preferences
- notification and playback settings
- privacy and data controls

## 5. Conversation Components

### Built With `assistant-ui`
- thread container
- message primitives
- composer primitives
- tool-call primitives
- streaming message rendering

### Custom Components
- `VoiceStatusBar`
- `HoldToTalkButton`
- `ApprovalCard`
- `WorkspaceActionCard`
- `ConnectionStatusPill`
- `TranscriptConfidenceHint`

## 6. Voice States

These states must be visually distinct:
- Idle
- Listening
- Transcribing
- Thinking
- Waiting for approval
- Speaking
- Error

Each state should include:
- icon or motion cue
- short label
- accessible text
- optional haptic feedback on enter/exit

## 7. Clean Interaction Rules

- one accent color, not many
- animation only when it explains state
- do not animate everything
- keep tool cards collapsed by default
- show the result first, raw payload second
- keep destructive actions visually separated

## 8. Mobile Layout Rules

- thumb-friendly hit targets
- avoid tiny icon-only controls for critical actions
- composer should stay stable when keyboard opens
- voice button must remain discoverable in every thread state
- long tool results should expand inline, not take over the whole screen

## 9. Accessibility

- support dynamic text sizing
- never rely on color alone
- spoken responses must also appear as text
- approval screens must be readable by screen readers
- loading states must have labels, not only animation

## 10. Implementation Notes

### Theme Tokens
Create a single source of truth for:
- colors
- typography
- spacing
- radius
- elevation
- animation timing

### Component Strategy
- compose from `assistant-ui` primitives
- wrap primitives in app-specific components
- keep design tokens outside component files

### Quality Bar
Before calling the UI complete:
- voice flow must feel smooth
- approvals must be obvious
- error states must look intentional
- nothing should feel like a default template
