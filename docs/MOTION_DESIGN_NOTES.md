# Motion design in Bloom

A short case study of how Bloom uses motion as **interface language**, not decoration.

The utilities live in `static/css/bloom-pro.css` (the “Motion / interaction utilities” block). Timing tokens sit on `:root`. Templates opt in by adding classes; nothing is animated just because a card exists.

This note is written for someone learning UI/UX with Bloom as the example. The goal is to see *why* a hover lift, a staggered list, or a send-button press exists — and why some screens refuse those same effects.

---

## The idea in one sentence

Motion in Bloom answers three questions the user is already asking:

1. **Can I click this?** (affordance)
2. **Did the system hear me?** (feedback)
3. **What just changed?** (state communication)

If a motion does not help with one of those, Bloom generally does not add it.

---

## Timing tokens: a shared vocabulary

Before the classes, there is a small set of CSS custom properties:

| Token | Value | Used for |
|---|---|---|
| `--pro-ease-standard` | `cubic-bezier(0.2, 0, 0, 1)` | Every motion utility |
| `--pro-duration-fast` | `150ms` | Presses / micro feedback |
| `--pro-duration-base` | `220ms` | Hovers / lifts |
| `--pro-duration-slow` | `320ms` | Entrances / toasts |

**Why a shared curve.** `cubic-bezier(0.2, 0, 0, 1)` is a deceleration ease: the motion starts promptly and settles without bounce. That matches how physical objects lose speed as they land. A bouncy or elastic curve would say “playful toy.” Bloom is a school workspace, so the curve is quiet.

**Why three durations, not one.** Pressing a Send button and watching a list of conversations arrive are different jobs. A 320ms press-scale would feel sluggish (“did it register?”). A 150ms list entrance would feel like a flash, not a sequence you can scan. Duration is part of the message.

These tokens are not decorative constants. They keep hover, press, and entrance in the same family so the product does not feel like several apps glued together.

---

## Each motion utility, and the principle it serves

### `.pro-card-interactive` — affordance: “this is a path, not a label”

On hover and `:focus-visible`, the element lifts `2px` and picks up `--pro-shadow-hover`. Transform, shadow, and border-color all transition over `--pro-duration-base`.

**Principle: affordance signaling.** An affordance is a cue that an object can be used in a certain way. A paper card on a desk does not rise when you look at it. A *clickable* card that stays visually identical to a static summary card forces the user to guess: is this a heading, or a door?

The lift is small on purpose. It is not a bounce or a glow. It says “this surface will take you somewhere” the same way a slightly raised physical button says “press me.” Keyboard users get the same cue on `:focus-visible`, so the affordance is not mouse-only.

**What it is not.** It is not “make the UI feel premium.” Applying this class to a non-clickable card would be a lie: the surface would invite a click that does nothing.

Used today on:

- Teacher Home pending items (`templates/teacher_home.html`) — each `hub-card` is a next action.
- Staff review panels (`templates/staff_page.html`) — each card is a decision.
- Messages inbox rows (`templates/messages_inbox.html`) — each row is a conversation you open.

### `.pro-stagger-in` — perceived structure: “this is a list you can scan”

Put this class on a **parent**. Direct children fade in and rise `4px` over `--pro-duration-slow`, with `nth-child` delays of `40ms` (capped at `280ms` from the ninth child onward). `animation-fill-mode: both` holds the starting state so items do not pop in fully opaque before the animation starts.

**Principle: sequential attention, not spectacle.** A page of eight identical cards appearing at once is a wall. Stagger gives the eye a reading order: first item, then the next, then the rest. The delays are short enough that the whole list is settled in well under half a second. After child 8, extra items share the last delay so a long inbox does not take seconds to finish “arriving.”

**Companion: `.pro-stagger-in.is-stagger-done`.** After first paint, JavaScript can freeze children (`animation: none`). That exists because CSS restarts `nth-child` animations when rows are hidden and shown again (`display: none` / filter). Without the freeze, searching Messages would look like the whole inbox was reloading. The stagger is for *arrival*, not for *every DOM change*.

Used today on Teacher Home’s pending list, staff panel lists, the Messages inbox, and the chat thread’s first paint.

### `.pro-skeleton` — perceived performance: “work is happening; the layout is already here”

A soft gradient that shimmers left-to-right (`1.2s`, infinite). Text is hidden, clicks are disabled (`pointer-events: none`).

**Principle: perceived performance.** Users judge speed by whether the screen looks *alive and structured*, not only by when the network returns. A blank hole says “broken or empty.” A skeleton says “the shape of this section is known; the data is still coming.” That is a different emotional state than a spinner in the middle of nowhere.

This class is defined and reduced-motion-safe, but **not yet applied** in the templates listed below. It is there for async regions (polling, generating, summarizing) when a placeholder needs to occupy real space. Until a template opts in, long operations use the full-page `#qol-overlay` fade instead.

### `.pro-toast-in` / `.pro-toast-out` — state communication: “this message just appeared / is leaving”

Toast-in: fade up `8px` over `--pro-duration-slow`. Toast-out: fade down `6px` over `--pro-duration-base` (exit is slightly faster than enter — people are done reading and want the chrome gone).

**Principle: motion as change-of-state, not as ornament.** A confirmation that is already sitting in the layout when the page paints can be missed (“did Approve work?”). A status line that appears with no motion can look like it was always there. A short rise draws the eye to *new* information without a modal.

`.pro-toast-out` is defined for a clean dismissal. Current templates use toast-in on enter; they have not wired toast-out yet. The pair is still the contract: enter slower, leave faster, same curve.

Used today on staff flash messages, Messages empty states, chat empty copy, and the live `chat-status` line.

### Button `active: scale(0.98)` — feedback: “the press counted”

`.btn`, `.pro-btn`, `.btn-primary`, `.today-action`, and `.chat-send-btn` shrink slightly on `:active`, over `--pro-duration-fast`.

**Principle: input confirmation.** On a physical keyboard, the key travels. On a glass screen or a mouse click, nothing moves unless we make it. A 2% scale-down is the digital equivalent of the button depressing. It is especially important when the *result* of the click is delayed (network send, “Generating HOTS questions…”, overlay). The press-scale says “we registered the click” *before* the slower result arrives.

This rule is global for those button classes. A Generate button on HOTS and a Send button in chat share it, even when the surrounding list is not animated.

### Related: notification dropdown and `#qol-overlay`

Not utility classes, but they use the same tokens:

- The announcement bell panel (`#notify-dropdown`) fades and lifts `4px` when it opens — state: closed vs open.
- The loading overlay fades opacity over `--pro-duration-base`. `topbar.js` skips the fade entirely when reduced motion is on, so a “Generating…” message is not trapped waiting for a transition.

---

## Four real screens, and why that motion is there

### 1. Teacher Home — the “Open items” queue

In `templates/teacher_home.html`, pending work is a `hub-list` with `pro-stagger-in`. Each item is a `hub-card pro-card-interactive` with a specific action link (“Review”, “Open”, and so on).

A teacher opening Bloom in the morning is not browsing. They need to see *what still needs them* and start the first one. Two problems without this motion:

- **Which cards are work, and which are scenery?** Home also has pulse chips and stat cards. The lift on the queue cards marks them as the actionable list — the thing you process, not the thing you merely read.
- **How big is the pile?** A simultaneous pop-in of five pending cards feels like a dump. The 40ms stagger is a scan path: first item is the likely next click; the rest are the rest of the day.

The empty state on the same page is a single static `hub-card` with **no** `pro-stagger-in` and **no** `pro-card-interactive`. That is deliberate. When there is nothing pending, there is no queue to parse and the card is a calm “you’re clear,” not a stack of doors.

### 2. Staff page — flash after Approve / Reject

`templates/staff_page.html` puts `pro-toast-in` on each flash `<li>`. Staff workflows are POST-then-redirect: you approve an upload, the page comes back, and a one-line result appears at the top.

The problem this solves is **confirmation blindness**. After a high-stakes action (“Students will be able to practice from this”), the staff member needs to know the server accepted it. A flash that is already fully painted can blend into the heading. The 320ms rise is a tap on the shoulder: “read this first, then look at the remaining queue.”

The remaining review cards then stagger in with `pro-card-interactive`. Same principle as Teacher Home: this list is a decision queue. The toast is “what just happened”; the stagger is “what is still left.”

Teacher-facing flashes in `templates/partials/flash.html` do not currently use `pro-toast-in`. The staff page is where that entrance is wired, because that screen *is* a queue of irreversible approvals.

### 3. Messages inbox — conversations you open, filters that must not “reload”

`templates/messages_inbox.html` is the densest use of the system:

- The list is `pro-stagger-in`.
- Each row is an `<a class="message-row pro-card-interactive">`.
- Filter/search empty states use `pro-toast-in`.
- `static/js/messages_inbox.js` adds `is-stagger-done` after 650ms, and retriggers `pro-toast-in` when the empty card becomes visible.

**Hover-lift on the row.** A message row looks a lot like a chat preview (avatar, snippet, time). Without a lift, it is easy to treat it as a readout. It is actually navigation into a private thread. The lift is the “this opens” cue — the same job as underlining a link, but for a large hit target.

**Stagger on first load, freeze after.** Students and teachers often have many threads. Stagger helps the first glance. Then filters hide rows with `hidden` / `display` changes, which would restart CSS animations. `is-stagger-done` is the UX fix: filtering Unread or Science must feel like *sorting what you already have*, not like the inbox fetched again. Replaying entrance on every chip click would train people not to use filters.

**Toast-in on the empty card.** When a search or subject filter matches nothing, a card appears in place of the list. Instant appearance reads as “the app deleted your conversations.” A short rise says “this is a result of the filter you just chose.” The JS remove/re-add of the class is so the animation can play *again* the next time you hit an empty filter — otherwise CSS would not restart.

### 4. Messages thread — Send press, then a new bubble

`templates/messages_thread.html` + `static/js/messages.js`:

- `#chat-thread` is `pro-stagger-in` so existing history eases in once.
- `.chat-send-btn` gets the global `active: scale(0.98)`.
- `#chat-status` and the empty state use `pro-toast-in`.
- After 650ms the thread is frozen (`is-stagger-done`). New bubbles from send or the 4-second poll get `pro-toast-in` instead of inheriting a list stagger.

**Why the Send button scales.** Sending is asynchronous. The optimistic bubble is labeled “Sending…”, then “Sent” or “Failed.” Between mouse-down and that stamp, there is a gap. The 150ms press-scale fills that gap: the control itself acknowledges the click. Without it, on a slow network, people double-send. (The JS also disables the button while `pending` is true — motion is the *felt* lock; disable is the *actual* lock.)

**Why new bubbles toast-in instead of restaggering.** The thread is polled every 4 seconds. If every append reused `nth-child` stagger, a newly arrived teacher reply could make *older* bubbles twitch, or a single new message could sit on a 280ms delay as “child 9.” After first paint, a new bubble is one piece of new state. `pro-toast-in` is the right verb: this message just entered the conversation.

**Why `#chat-status` animates.** “Sending…”, send errors, and poll errors appear in a `role="status"` live region. Motion plus the live region is belt and braces: assistive tech hears the change; sighted users see the line arrive. The class is retriggered when the status goes from hidden to visible so a second error is visible as a new event, not a stale sentence.

---

## Why `prefers-reduced-motion` is respected — and what breaks if it is not

Bloom listens in two places:

1. **The OS / browser setting:** `@media (prefers-reduced-motion: reduce)` in `bloom-pro.css` turns off transforms and keyframe animations on these utilities. Interactive cards may still change shadow/border (no movement). Skeletons become a flat placeholder. Toasts appear without a rise. Buttons do not scale. The notify dropdown and overlay skip motion too.
2. **An in-app preference:** `html.pref-reduce-motion`, set from `localStorage` in `templates/partials/prefs_boot.html` and toggled in `topbar.js`. `style.css` then disables animation and transition on all elements. `topbar.js` also skips overlay fade if either the media query **or** this class is on.

This is not a polish flag. Reduced motion exists because **motion is a physical stimulus**.

If Bloom ignored it:

- **Vestibular and motion-sensitive users** can get dizziness or nausea from even small `translateY` on large lists. A staggered inbox plus a lifting card plus a toast is several moving layers. That is a medical issue, not a taste issue.
- **Attention and cognitive load.** Entrance animation captures the eye. For some users (including ADHD and certain processing differences), a 320ms rise on every flash and empty state is an interruption they cannot dismiss. The content is the point; the motion is an extra demand.
- **Infinite shimmer (`.pro-skeleton`) is the sharp edge.** A looping gradient is the kind of persistent motion that is hardest to ignore. The reduced-motion rule replaces it with a still fill so a loading region does not keep pulsing.
- **False “nothing loaded yet.”** Stagger starts children at `opacity: 0`. If someone needs the UI still, and you still run the animation, they wait on motion they cannot comfortably watch — or they think the list is empty until child 8 finishes. Reduced motion sets `opacity: 1; transform: none; animation: none` immediately so content is available on the first frame.
- **Keyboard and low-vision use.** Focus already has to be visible. Adding a lift that the user cannot comfortably track makes focus harder to follow, not easier.

Respecting the preference is how Bloom keeps the *meaning* of the motion (this is clickable, this just arrived) without requiring the *movement*. Shadow and copy still work. The overlay still appears; it just does not fade.

---

## What's NOT animated in Bloom, and why

Motion is applied where it answers “can I use this / did that work / what changed.” It is withheld where it would only make the UI fidget.

**HOTS question cards do not stagger or lift.** In `templates/teacher_hots.html`, generated items are `hub-card hub-card-stack` inside a plain `hub-list`. They are **reading surfaces** for review (prompt, options, answer, citation). The card is not a link. A hover-lift here would fake a navigation affordance. A stagger would imply a queue of destinations. The teacher is checking quality before Publish — they need the text still, not the list performing. What *is* animated on this screen is the buttons: Generate, Regenerate, and Publish use `.btn-primary` / `.today-action`, so they press-scale. Those are the actions. The questions are the content.

**Materials pending / deployed cards do not use `.pro-card-interactive`.** In `templates/teacher_materials.html`, each row is a file plus metadata plus a separate “Review” or “View file & summary” control (`today-action`). The card is a record; the button is the affordance. Lifting the whole article would suggest the card itself is the hit target. It is not.

**Monitor student cards and assessment panels stay still.** `templates/teacher_monitor.html` is a dashboard: roster, scores, release state. Student cards are not clickable destinations (Message is a nested link). Assessment panels are status plus forms (Close, Reopen, Release scores). Lifting those panels on hover would compete with the actual buttons and imply the whole card navigates somewhere. Progress meters already communicate state. Extra motion would be noise on a screen whose job is “see who submitted.”

**Chat bubbles do not get hover-lift.** In `messages_thread.html`, bubbles are `.chat-bubble`, not `.pro-card-interactive`. They are messages, not buttons. Lifting them on hover would make a conversation feel like a stack of links and would fight selection/reading. Arrival is handled once (stagger on first paint, toast-in for new ones). After that, bubbles sit. Send is the control that moves.

**Teacher Home’s empty “you’re clear” card does not stagger or lift** — covered above. One static card is a rest state.

**`.pro-skeleton` and `.pro-toast-out` are unused in these templates.** That is a restraint, not a missing animation. Long teacher actions (upload & summarize, generate HOTS) currently use the loading overlay, which is one shared “please wait” object instead of several shimmer blocks. Toast-out can wait until flashes are dismissed in place rather than on navigation.

**Decorative page chrome does not use these utilities.** Ribbons, blobs, and similar background motion live elsewhere and already shut off under reduced motion. The Pro utilities are reserved for *interaction*.

The test Bloom is using, whether or not it was written down before this file:

> If the user cannot click it, if nothing about the system’s state changed, and if the motion is not confirming a press — do not animate it.

That is how a hover-lift stays an affordance, a stagger stays a scan aid, and a toast stays a status change — instead of the product looking busy for its own sake.
