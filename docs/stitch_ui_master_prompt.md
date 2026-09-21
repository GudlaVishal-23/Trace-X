# TRACE-X: Stitch AI Master Prompt & Design System Specification

**Target Tool:** Google Stitch AI / StitchMCP / AI UI Generators  
**Platform:** TRACE-X (Smart City ANPR Trajectory & Traffic Analytics Command Center)  
**Problem Statement ID:** SIH26127  
**Theme:** Traffic Signal Palette — Vibrant Signal Orange, Crisp High-Contrast White, and Glowing Signal Green  
**Format:** Desktop Web Application (1440px / 1920px Wide Display)  

---

## 🎨 Design System & Visual Identity

### Color Tokens (Traffic Signal / Tricolor Identity)
- **Signal Orange / Amber (`#FF6D00`, `#FF8C00`):**
  - Use for: Active alerts, camera gap warnings, priority notifications, bottleneck indicators, search buttons, and interactive hover outlines.
  - Glow filter: `box-shadow: 0 0 16px rgba(255, 109, 0, 0.45)`.
- **Pure White / Crisp Monospace (`#FFFFFF`, `#F8FAFC` on `#080C16`):**
  - Use for: Primary headers, high-contrast license plate text, prominent metric digits, card divider lines, and clean modern glass containers.
- **Signal Green / Emerald (`#00E676`, `#10B981`):**
  - Use for: Free-flow traffic corridors, verified `CONFIRMED` trajectory paths, online camera health indicators, and high confidence ratings ($\ge 90\%$).
  - Glow filter: `box-shadow: 0 0 16px rgba(0, 230, 118, 0.45)`.
- **Deep Obsidian Slate Base (`#080C16`, Surface: `#0E1526`, Card: `#141C33`):**
  - Ultra-deep, anti-glare dark background that makes the orange, white, and green signals pop with extreme clarity.

---

## 📋 The Master Prompt for Stitch AI

Copy and paste the exact prompt block below into **Stitch AI**:

```text
Design a state-of-the-art, high-clarity Urban Traffic & Vehicle Intelligence Command Center Dashboard called "TRACE-X" for Smart India Hackathon 2026.

THEME & COLOR PALETTE:
- Primary Accents: Traffic Signal Palette.
  * Signal Orange (#FF6D00) for alerts, search CTA buttons, warning indicators, and camera gaps.
  * Crisp White (#FFFFFF / #F8FAFC) for primary data numbers, glass container borders, and high-contrast typography.
  * Signal Green (#00E676) for free-flow traffic, confirmed vehicle trajectory links, and online camera pulses.
- Background: Deep obsidian dark slate (#080C16) with glassmorphic cards (#0E1526 with 1px border rgba(255,255,255,0.1) and subtle backdrop blur).
- Typography: Clean neo-grotesque sans (Inter / Plus Jakarta Sans) paired with monospaced JetBrains Mono for license plates, timestamps, and GPS coordinates.

HEADER / TOP NAVIGATION:
- Left: Glowing dual-tone pulse dot (Orange & Green), bold modern logo "TRACE-X", subtitle "SIH26127 • URBAN VEHICLE INTELLIGENCE".
- Center: 4 segment navigation tabs with clear active indicator:
  1. "Live City Map" (Map icon)
  2. "Trajectory Search" (Search path icon)
  3. "Traffic Analytics" (Bar chart icon)
  4. "Watchlist & Alerts" (Bell icon with glowing Orange badge '3')
- Right: Network Health chip "8 NODES ONLINE" in emerald green + real-time UTC digital clock in monospace.

SCREEN 1 — LIVE CITY MAP VIEW:
- Left / Center: High-contrast Dark Matter GIS map showing city road network (Hyderabad arterial grid).
  * 8 camera pins with glowing halo rings: Green for online, Amber/Orange for offline camera gaps.
  * Dynamic polyline road segments colored Green (Free flow > 40 km/h) and Orange (Congested corridor).
  * Interactive popup on camera click showing Camera ID, Location, FPS, and Image Quality Score (96%).
- Right Panel (380px wide): "Live Event Stream" showing real-time passing vehicles.
  * Cards featuring Indian High-Security License Plate pills (embossed yellow/white pill with bold black monospace font "TS09AB1234").
  * Detection confidence badges, vehicle type tag ("Black Yamaha R15"), and relative timestamps ("2s ago").

SCREEN 2 — TRAJECTORY RECONSTRUCTION WORKSPACE:
- Top Hero Search Bar: Floating glass input box with search icon, glowing orange "TRACK TRAJECTORY" button, and quick-filter pills ("TS09AB1234", "DL01CA9999", "MH12XY7788").
- 4 Sleek KPI Metric Cards:
  1. "Target Vehicle": Plate pill + model name
  2. "Trajectory Status": "CONFIRMED (96% Confidence)" in vibrant Green
  3. "Distance Reconstructed": "10.8 km"
  4. "Average Velocity": "27.0 km/h"
- Center Reconstructed Journey Timeline:
  * Visual interactive breadcrumb sequence connecting Camera C101 -> C107 -> C115 -> C123.
  * Solid Green line connecting C101 to C107 (Confirmed Link).
  * Dashed Orange line between C107 and C115 indicating "CAMERA GAP — C112 Offline along Corridor (Probable Continuation)".
  * "Export Forensic Dossier (SHA-256)" button with cryptographic hash preview.

SCREEN 3 — MACRO TRAFFIC ANALYTICS:
- Top Stat Banners: "248,910 Vehicles Tracked Today", "34.8 km/h City Transit Velocity", "3 Active Congestion Bottlenecks" (in Orange).
- Left: Vehicle Modal Distribution horizontal progress bars (Two-wheelers 42%, Cars 36%, Auto-rickshaws 12%, Commercial 10%) filled with green-to-orange gradient.
- Right: Origin-Destination (OD) Zonal Flow Matrix heatmap table showing trip volumes between North, East, Central, and West zones.

SCREEN 4 — WATCHLIST & OPERATIONAL ALERTS:
- Tactical Watchlist Table: Blacklisted vehicles, category badges (Stolen, Suspect, Reckless), FIR reference, and status.
- Real-Time Alert Grid: High-priority cards with glowing orange/red borders, snapshot preview, explainable reason ("Target vehicle TS09AB1234 detected at C123 PVNR Expressway"), and 2 clear action buttons: "[Confirm Interception]" (Orange) and "[Dismiss]" (Ghost White).

OVERALL FEEL:
Extremely clean, modern, uncluttered, professional command center aesthetics. High visual hierarchy, clear separation of data, zero confusing clutter, optimized for rapid law enforcement and traffic management decision-making.
```

---

## 🎯 Modular Prompts for Individual Screen Generation

If generating one screen at a time in Stitch AI, use these targeted prompts:

### Screen Prompt A: The GIS Map & Live Event Feed
> *"Design a dark-mode GIS Command Center screen for urban traffic surveillance called TRACE-X. Deep obsidian slate background (#080C16). High-contrast dark city map on the left with camera markers glowing in Traffic Green (#00E676) and Warning Orange (#FF6D00). Floating collapsible sidebar on the right displaying real-time recognized Indian vehicle plates in embossed monospace pills, with vehicle class tags and 95% confidence badges. Top navbar with navigation tabs and live UTC clock."*

### Screen Prompt B: Single-Plate Trajectory Breadcrumb View
> *"Design a forensic vehicle tracking interface for TRACE-X. Top prominent search bar for entering license plate 'TS09AB1234' with a glowing Signal Orange CTA button. 4 KPI glass cards showing Target Plate, Reconstructed Status (CONFIRMED in emerald green), Distance (10.8 km), and Speed (27 km/h). An interactive step-by-step route timeline connecting 4 cameras with timestamps, GPS coordinates, and clear visual differentiation between Solid Green (Confirmed Link) and Dashed Orange (Camera Gap Bridged). Include a button to export a cryptographic SHA-256 forensic report."*

### Screen Prompt C: Macro Traffic Analytics & Origin-Destination Matrix
> *"Design a macro urban mobility dashboard for city traffic controllers in TRACE-X. Clean dark UI with traffic signal colors (Orange, White, Green). High-level KPI cards for total daily vehicle volume (248,910) and average transit speed. A vehicle modal split section with gradient progress bars showing percentage breakdown of motorcycles, cars, and autos. An interactive 4x4 Origin-Destination flow matrix grid with color-coded density cells indicating commuter transit corridors."*
