# TRACE-X --- Prototype Master README

## AI-Powered City-Wide Vehicle Intelligence & Traffic Analytics

> **Project purpose:** This document is the single source of truth for
> building the TRACE-X prototype for Smart India Hackathon 2026 problem
> statement **SIH26127 --- City-Wide AI Engine for Multi-Camera ANPR
> Trajectory Tracking and Urban Traffic Analytics**.

------------------------------------------------------------------------

# 1. Executive Summary

TRACE-X is a software platform that converts city-wide CCTV/ANPR camera
feeds into structured, searchable vehicle intelligence.

The prototype is designed around three core SIH requirements:

1.  **High-Accuracy ANPR/OCR**
    -   Detect vehicles and license plates.
    -   Handle difficult real-world conditions such as blur, low light,
        rain, angled plates, dirt, damage and partial obstruction.
    -   Use image-quality checks, enhancement, multi-frame fusion and
        confidence scoring.
    -   Never invent a plate when the evidence is insufficient.
2.  **Single-Plate Trajectory Tracking**
    -   Given an authorized vehicle plate, search previously generated
        vehicle events.
    -   Connect observations from geographically distributed cameras.
    -   Use plate similarity, vehicle appearance, timestamp, location,
        direction, road connectivity and travel-time feasibility.
    -   Distinguish **Confirmed**, **Probable** and **Unknown** links.
    -   Visualize the reconstructed journey on a GIS map.
3.  **Macro Traffic Flow & Movement Analytics**
    -   Aggregate vehicle events and movements across the camera
        network.
    -   Calculate traffic counts/density, movement flows,
        origin-destination patterns, average/estimated speed, congestion
        and trends.
    -   Display city-wide heatmaps and traffic intelligence on a GIS
        dashboard.

A supporting **Alert System** provides authorized
watchlist/blacklisted-vehicle alerts, suspicious route anomaly
indicators and automated reports.

### Core philosophy

> **See → Connect → Understand → Act**

-   **See:** robustly extract vehicle information from imperfect camera
    imagery.
-   **Connect:** connect observations of the same vehicle across
    cameras.
-   **Understand:** aggregate movements into city-wide traffic
    intelligence.
-   **Act:** provide alerts, GIS visualization and investigation reports
    to authorized users.

------------------------------------------------------------------------

# 2. Problem Statement

## Official problem focus

Modern urban centers deploy large networks of CCTV and ANPR cameras for
traffic management, enforcement and public security. The SIH problem
identifies a lack of effective integration across camera feeds, which
limits:

-   city-wide vehicle trajectory reconstruction,
-   tracking of high-interest vehicles across sectors,
-   macro-level traffic movement analytics,
-   centralized GIS visualization,
-   real-time alerts for blacklisted vehicles and suspicious route
    anomalies.

The expected platform must provide:

-   90% ANPR/OCR accuracy in diverse real-world conditions,

-   single-plate spatial-temporal trajectory reconstruction,

-   city-wide traffic density and movement analytics,

-   GIS-integrated visualization,

-   real-time alerts,

-   scalable enterprise-grade architecture.

### TRACE-X positioning

TRACE-X should **not claim that ANPR, vehicle Re-ID, GIS traffic
analytics or city-wide tracking are invented by the project**. These
technologies and commercial/government systems already exist.

The defensible contribution is the proposed **resilience-oriented
integration**:

> **TRACE-X focuses on what happens when camera evidence is imperfect.**

The system combines uncertain observations using multiple signals and
explicitly represents evidence confidence rather than forcing false
matches.

------------------------------------------------------------------------

# 3. What TRACE-X Is --- and Is Not

## TRACE-X IS

-   A vehicle intelligence layer over CCTV/ANPR infrastructure.
-   A structured vehicle-event generation system.
-   A robust ANPR/OCR pipeline.
-   A cross-camera vehicle matching and trajectory reconstruction
    engine.
-   A city-wide traffic analytics engine.
-   A GIS-based investigation and traffic dashboard.
-   A confidence-aware evidence system.
-   A report and alert generation platform.

## TRACE-X IS NOT

-   A replacement for all existing CCTV/NVR infrastructure.
-   A system that must permanently store every vehicle's video.
-   A system that should automatically accuse or identify a person as a
    criminal.
-   A magical predictor of a vehicle's future location.
-   A claim that all vehicles can always be tracked without gaps.
-   A guarantee that poor camera images can always be recovered
    perfectly.

------------------------------------------------------------------------

# 4. Critical Storage Decision

## Do not design TRACE-X around permanent video duplication

The key architecture decision is:

> **TRACE-X does not require continuous storage of all raw CCTV video
> inside its own platform.**

Existing camera/NVR infrastructure may independently retain raw footage
according to its operational and legal policies.

TRACE-X processes live or recorded streams and creates compact **Vehicle
Events**.

### Concept

``` text
CCTV / ANPR Camera
        |
        v
TRACE-X AI Processing
        |
        v
Vehicle Event
        |
        v
Vehicle Event Database
        |
        +----> Trajectory Tracking
        |
        +----> Traffic Analytics
        |
        +----> Alerts
        |
        +----> Reports
```

### Example vehicle event

``` json
{
  "event_id": "evt_000123",
  "camera_id": "C17",
  "timestamp": "2026-09-10T19:42:15+05:30",
  "plate_text": "TS09AB1234",
  "plate_confidence": 0.96,
  "vehicle_type": "motorcycle",
  "vehicle_color": "black",
  "vehicle_make_model": "Yamaha R15",
  "direction": "north",
  "latitude": 17.4123,
  "longitude": 78.4071,
  "image_quality_score": 0.91,
  "observation_status": "confirmed"
}
```

The exact fields can evolve during implementation.

### Important distinction

For the prototype:

-   Store structured vehicle events.
-   Store metadata.
-   Store compact evidence references or selected snapshots only if
    needed for demonstration/evaluation.
-   Do not build an unnecessary giant video archive.

For production:

-   Raw footage retention remains subject to the camera owner's
    policies, legal requirements and evidence-preservation rules.
-   TRACE-X should support a reference back to authorized source footage
    when required, rather than assuming TRACE-X owns the raw archive.

------------------------------------------------------------------------

# 5. Complete TRACE-X Architecture

``` text
                    CITY CCTV / ANPR CAMERAS
                              |
                              v
                     VIDEO INGESTION LAYER
                              |
                              v
                    VEHICLE DETECTION
                              |
                              v
                     PLATE DETECTION
                              |
                              v
                   IMAGE QUALITY CHECK
                              |
               +--------------+--------------+
               |                             |
            GOOD                          POOR
               |                             |
               |                  Enhancement / Multi-frame
               |                             |
               +--------------+--------------+
                              |
                              v
                         OCR / ANPR
                              |
                              v
                    CONFIDENCE SCORING
                              |
                  +-----------+-----------+
                  |                       |
               Reliable               Uncertain
                  |                       |
                  |                Partial / unknown
                  |                   observation
                  +-----------+-----------+
                              |
                              v
                     VEHICLE EVENT
                              |
                    +---------+---------+
                    |                   |
                    v                   v
            TRAJECTORY ENGINE     TRAFFIC ANALYTICS
                    |                   |
                    v                   v
                 GIS MAP          Density / Flow / OD
                    |              Congestion / Trends
                    +---------+---------+
                              |
                              v
                     ALERT & REPORTING
```

------------------------------------------------------------------------

# 6. System Modules

## Module 1 --- Camera Network

Each camera is represented with metadata.

### Camera fields

-   camera_id
-   camera name
-   latitude
-   longitude
-   road name
-   direction
-   lane information if available
-   camera type
-   stream source
-   active/offline status
-   quality/reliability score

### Example

``` json
{
  "camera_id": "C101",
  "name": "Main Road Camera",
  "latitude": 17.4100,
  "longitude": 78.4000,
  "road": "Main Road",
  "direction": "north",
  "status": "online"
}
```

### Prototype

Use recorded videos or publicly available datasets and assign simulated
camera metadata.

Do not claim access to government camera feeds unless such access has
actually been provided.

------------------------------------------------------------------------

# 7. Module 2 --- Video Ingestion

The ingestion layer accepts:

-   MP4/video files for prototype,
-   webcam input if useful,
-   RTSP/ONVIF/IP streams for a future deployment architecture.

### Processing sequence

``` text
Video Input
   ↓
Frame Sampling
   ↓
Vehicle Detection Trigger
   ↓
Selected Frames
   ↓
AI Processing
```

Do not run expensive OCR on every video frame unnecessarily.

Use vehicle detection/tracking to identify useful frames.

### Responsibilities

-   read video,
-   maintain timestamps,
-   associate frames with camera_id,
-   sample frames,
-   reconnect to live streams,
-   detect camera offline conditions,
-   pass selected frames to the perception pipeline.

------------------------------------------------------------------------

# 8. Module 3 --- Vehicle Detection

Use a modern object detector such as YOLO.

### Vehicle classes

At minimum:

-   car,
-   motorcycle,
-   bus,
-   truck.

Optional:

-   auto-rickshaw,
-   bicycle,
-   van,
-   other.

### Output

``` json
{
  "track_local_id": 12,
  "class": "motorcycle",
  "bbox": [x1, y1, x2, y2],
  "detection_confidence": 0.94
}
```

The local tracking ID is not a city-wide identity. It only helps
associate frames from the same local camera sequence.

------------------------------------------------------------------------

# 9. Module 4 --- Plate Detection

After vehicle detection:

``` text
Vehicle Bounding Box
        ↓
Plate Detector
        ↓
Plate Crop
```

The plate detector should output:

-   plate bounding box,
-   detection confidence,
-   cropped plate image.

The plate crop is then passed to quality assessment and OCR.

------------------------------------------------------------------------

# 10. Module 5 --- Robust ANPR/OCR

This solves **Problem 1**.

## Difficult conditions

TRACE-X must explicitly test:

-   motion blur,
-   low light/night,
-   rain/wet scenes,
-   glare,
-   angled plates,
-   dirty plates,
-   damaged plates,
-   partial obstruction,
-   low resolution,
-   compression artifacts,
-   small plate size.

## Pipeline

``` text
Plate Crop
    ↓
Quality Assessment
    ↓
+--------------------------+
| Blur?                    |
| Low light?               |
| Rain/glare?              |
| Angle/perspective?       |
| Occlusion?               |
| Plate too small?         |
+--------------------------+
    ↓
Image Enhancement
    ↓
Multi-Frame Fusion
    ↓
OCR
    ↓
Format/Character Validation
    ↓
Confidence Score
```

------------------------------------------------------------------------

# 11. Image Quality Assessment

Create a quality score, e.g. 0--100.

Potential indicators:

### Blur

Variance of Laplacian or a learned blur classifier.

### Brightness

Mean intensity and low-light threshold.

### Contrast

Contrast statistics.

### Plate size

Number of pixels covering the plate.

### Angle

Perspective/plate geometry estimation.

### Occlusion

Percentage of plate region that is blocked.

### Rain/glare

Optional learned or rule-based indicators.

### Important

Image enhancement cannot recover information that was never captured.

If the plate contains no usable information, the system must not
hallucinate characters.

------------------------------------------------------------------------

# 12. Image Enhancement

Potential operations:

-   denoising,
-   deblurring,
-   brightness adjustment,
-   contrast enhancement,
-   perspective correction,
-   super-resolution,
-   glare reduction where feasible.

The enhancement pipeline should be conditional.

Do not blindly apply every enhancement to every image.

Example:

``` text
Quality Check
     |
     +-- good --> OCR
     |
     +-- blur --> deblur + OCR
     |
     +-- dark --> low-light enhancement + OCR
     |
     +-- angle --> perspective correction + OCR
     |
     +-- multiple frames --> multi-frame fusion + OCR
```

------------------------------------------------------------------------

# 13. Multi-Frame OCR Fusion

This is one of the most important robustness mechanisms.

A moving vehicle normally appears across several consecutive frames.

Instead of relying on one frame:

``` text
Frame 1: TS09A?1234
Frame 2: TS09AB1234
Frame 3: TS09AB12?4
Frame 4: TS09AB1234
```

Combine character evidence across frames.

### Concept

For each character position:

``` text
Position 1:
T T T T

Position 2:
S S S S

...

Position 6:
A B A B
```

Use OCR probabilities and temporal consistency to select the most
reliable result.

The actual fusion algorithm can use:

-   per-character confidence,
-   majority voting,
-   probability averaging,
-   temporal consistency,
-   frame quality weighting.

------------------------------------------------------------------------

# 14. OCR Confidence

The system must produce a confidence value.

Example:

``` text
Plate: TS09AB1234
Confidence: 0.96
Status: CONFIRMED
```

Another:

``` text
Plate: TS09A?1234
Confidence: 0.61
Status: PARTIAL / PROBABLE
```

Another:

``` text
Plate: UNKNOWN
Confidence: 0.28
Status: UNREADABLE
```

### Rule

> **Never force a plate number from weak evidence.**

A wrong plate can create a false trajectory and a dangerous false alert.

------------------------------------------------------------------------

# 15. Fallback Handling

When OCR fails:

### Level 1 --- Try additional frames

Search consecutive frames from the same local vehicle track.

### Level 2 --- Improve the crop

Re-detect plate and use better-quality frame.

### Level 3 --- Use vehicle appearance

Store:

-   vehicle type,
-   color,
-   make/model if reliable,
-   visual embedding,
-   distinctive appearance features.

### Level 4 --- Cross-camera matching

Use:

-   partial plate,
-   appearance,
-   time,
-   location,
-   direction,
-   road connectivity.

### Level 5 --- Unknown

If evidence remains insufficient:

``` text
plate_text = null
observation_status = "unknown"
```

Do not create a fake plate.

------------------------------------------------------------------------

# 16. Vehicle Event Data Model

Every recognized observation becomes a normalized event.

## Suggested schema

``` text
VehicleEvent
------------
event_id
camera_id
timestamp
plate_text
plate_confidence
plate_status
vehicle_type
vehicle_color
vehicle_make
vehicle_model
appearance_embedding
direction
latitude
longitude
road_id
image_quality_score
vehicle_detection_confidence
source_frame_reference
created_at
```

Optional fields:

``` text
lane_id
speed_estimate
weather_condition
occlusion_score
blur_score
brightness_score
```

------------------------------------------------------------------------

# 17. Problem 2 --- Cross-Camera Trajectory Tracking

The second core SIH requirement is:

> Given a specific plate, reconstruct its historical journey across
> geographically distributed cameras.

## Example

``` text
C101 — 10:05
TS09AB1234
      ↓
C107 — 10:11
TS09A?1234
      ↓
C115 — 10:18
No readable plate
      ↓
C123 — 10:25
TS09AB1234
```

TRACE-X should determine whether these observations belong to the same
vehicle.

------------------------------------------------------------------------

# 18. Cross-Camera Evidence Fusion

Do not match only on exact plate.

Use multiple signals.

## Evidence signals

1.  Plate similarity
2.  Vehicle appearance
3.  Vehicle type
4.  Vehicle color
5.  Make/model when available
6.  Visual Re-ID embedding similarity
7.  Timestamp consistency
8.  Location consistency
9.  Direction consistency
10. Road network connectivity
11. Travel-time feasibility

### Conceptual scoring model

``` text
MatchScore =
    w1 * PlateSimilarity
  + w2 * AppearanceSimilarity
  + w3 * TimeFeasibility
  + w4 * DirectionConsistency
  + w5 * RoadConnectivity
  + w6 * ReIDSimilarity
```

The weights should be calibrated experimentally.

Do not present arbitrary example weights as scientifically validated
until measured.

------------------------------------------------------------------------

# 19. Candidate Camera Generation

Do not search every camera equally.

After a vehicle is observed at C101:

``` text
C101
  |
  +--> nearby reachable cameras
  |
  +--> road-connected cameras
  |
  +--> direction-compatible cameras
  |
  +--> cameras reachable within expected time window
```

This reduces unnecessary search.

### Candidate filters

-   road connectivity,
-   geographic distance,
-   direction,
-   expected travel time,
-   camera coverage,
-   time window.

------------------------------------------------------------------------

# 20. Road- and Time-Constrained Matching

Example:

``` text
Camera A
10:00
      |
      | 3 km
      |
Camera B
10:05
```

If 3 km can reasonably be travelled in 5 minutes, the match is
plausible.

If:

``` text
Camera A: 10:00
Camera B: 10:02
Distance: 80 km
```

the match is physically implausible for normal road travel.

Therefore:

> **A visually similar plate is not sufficient if the route/time is
> impossible.**

------------------------------------------------------------------------

# 21. Direction Validation

If Camera A reports northbound and Camera B is reachable only through a
southbound road, the candidate should be penalized or rejected.

Direction can be derived from:

-   camera configuration,
-   lane direction,
-   vehicle motion,
-   road graph.

------------------------------------------------------------------------

# 22. Match Classification

Use three evidence levels.

## CONFIRMED

Strong evidence.

Example:

-   high-confidence plate match,
-   compatible time,
-   compatible road,
-   appearance consistent.

## PROBABLE

Some evidence is missing or uncertain.

Example:

-   partial plate,
-   good appearance match,
-   feasible time,
-   correct road direction.

## UNKNOWN

Insufficient evidence.

Do not include as a confirmed trajectory.

### Important

A probable route is an inference, not a direct observation.

------------------------------------------------------------------------

# 23. Missing Camera / Offline Camera Handling

Example:

``` text
C101
10:05
   |
   |
C107
OFFLINE
   |
   |
C123
10:25
```

If C101 and C123 are compatible by:

-   time,
-   distance,
-   direction,
-   road network,
-   vehicle appearance,

TRACE-X can represent a probable route through the gap.

But it must not claim:

> "Vehicle was definitely detected at C107."

Instead:

> **Camera gap --- probable continuation**

This is a central resilience principle.

------------------------------------------------------------------------

# 24. Conflicting Detections

Example:

``` text
C101: TS09AB1234 — 96%
C107: TS09AX1234 — 52%
C123: TS09AB1234 — 94%
```

Do not immediately split the trajectory.

Use confidence-aware matching.

The low-confidence observation can be retained as supporting evidence.

Another example:

``` text
C101: black motorcycle
C107: white sedan
C123: black motorcycle
```

The appearance conflict should reduce the match score substantially.

If evidence becomes impossible, break the trajectory.

------------------------------------------------------------------------

# 25. Vehicle Re-Identification

Vehicle Re-ID provides visual similarity independent of exact plate OCR.

Possible features:

-   vehicle shape,
-   color,
-   make/model,
-   rear/front appearance,
-   distinctive visible features,
-   learned image embedding.

### Important limitation

Vehicle Re-ID is difficult because the same vehicle changes appearance
across:

-   viewpoint,
-   lighting,
-   distance,
-   occlusion,
-   weather,
-   camera quality.

Therefore Re-ID is **supporting evidence**, not absolute identity proof.

------------------------------------------------------------------------

# 26. Trajectory Graph

Represent the journey as a graph:

``` text
        C101
        10:05
         |
      CONFIRMED
         |
        C107
        10:11
         |
       PROBABLE
         |
        C115
        10:18
         |
      CONFIRMED
         |
        C123
        10:25
```

Every edge should preserve:

-   source observations,
-   matching signals,
-   score,
-   confidence,
-   reason.

This creates an **evidence graph**.

------------------------------------------------------------------------

# 27. Vehicle Search

Input:

``` text
TS09AB1234
```

The search system should support:

-   exact plate,
-   partial plate where authorized,
-   time range,
-   camera,
-   area,
-   vehicle type,
-   confidence.

### Historical search

Returns past observations available in the event database.

### Live status

If live streams are connected, the system can show:

> Last detected at Camera C123, 10:25.

It cannot know the exact current location if no camera is currently
detecting the vehicle.

### Future route

TRACE-X may optionally predict a **probable next corridor**, but this
must be labeled as prediction and never as confirmed location.

------------------------------------------------------------------------

# 28. Vehicle Journey Report

Example:

``` text
TRACE-X VEHICLE JOURNEY REPORT

Vehicle:
TS09AB1234

Type:
Motorcycle

Color:
Black

First detected:
C101 — 10:05

Last detected:
C123 — 10:25

Journey:
C101 → C107 → C115 → C123

Evidence:
C101 — Confirmed
C107 — Confirmed
C115 — Probable / low plate confidence
C123 — Confirmed

Overall confidence:
High

Route:
Displayed on GIS

Notes:
One low-confidence observation occurred at C115.
No direct plate evidence was available at that point.
```

------------------------------------------------------------------------

# 29. Problem 3 --- Macro Traffic Analytics

Problem 3 asks a different question.

### Problem 2

> Where did **this vehicle** travel?

### Problem 3

> What is **the city's traffic doing**?

Example:

``` text
Problem 2:
TS09AB1234
C1 → C5 → C8

Problem 3:
C1 → C5
4,820 vehicle movements/hour

C5 → C8
5,130 vehicle movements/hour
```

Problem 3 aggregates many observations and movements.

------------------------------------------------------------------------

# 30. Traffic Metrics

## Vehicle count

Count unique vehicle movements/observations according to the chosen
metric.

Be careful not to double-count the same vehicle unnecessarily.

## Density

Vehicles per:

-   camera,
-   road segment,
-   zone,
-   time window.

## Average/estimated speed

Estimate from:

-   known camera distance,
-   detection timestamps,
-   matched vehicle movement.

Example:

``` text
Camera A
10:00

Camera B
10:06

Distance = 3 km

Estimated speed ≈ 30 km/h
```

Label this as an estimate and account for route length.

## Traffic flow

Vehicles moving between road segments/cameras per time window.

## Origin-Destination

Aggregate movement between defined zones.

## Bottlenecks

Combine:

-   high volume,
-   reduced speed,
-   increased travel time,
-   persistent congestion.

------------------------------------------------------------------------

# 31. Traffic Heatmap

The GIS dashboard should show:

``` text
GREEN = Free flow
YELLOW = Moderate
RED = Congested
```

The map can display:

-   camera points,
-   road segments,
-   vehicle density,
-   traffic flow,
-   congestion hotspots,
-   major movement corridors.

Do not put every individual vehicle on the city map in the macro
analytics view.

------------------------------------------------------------------------

# 32. Origin-Destination Matrix

Define zones:

``` text
A
B
C
D
```

Example:

``` text
From \ To | A | B | C | D
-----------+---+---+---+---
A          | - |800|1200|400
B          |600| - |1500|300
C          |300|700| - |900
D          |200|400|1100| -
```

This helps traffic authorities understand major movement corridors.

------------------------------------------------------------------------

# 33. Congestion Detection

A simple prototype can use thresholds.

Example:

``` text
IF
vehicle_volume > volume_threshold
AND
average_speed < speed_threshold
THEN
congestion = HIGH
```

A better implementation can combine:

-   current volume,
-   current speed,
-   historical baseline,
-   travel time,
-   persistence over several windows.

### Example

``` text
Normal:
40 km/h

Current:
14 km/h

Volume:
2,400 vehicles/hour

Result:
HIGH CONGESTION
```

------------------------------------------------------------------------

# 34. Alert System

Alerts are outputs of the intelligence layer.

## Watchlist alert

``` text
WATCHLIST VEHICLE DETECTED

Plate:
TS09AB1234

Camera:
C123

Time:
10:25

Confidence:
96%
```

## Suspicious route anomaly

A route can be flagged when it is significantly inconsistent with
expected patterns or configured rules.

The system should explain the reason.

Example:

``` text
Route anomaly:
Vehicle deviated from expected corridor
Confidence: 0.78
Reason:
Unexpected direction + unusual travel-time pattern
```

Do not automatically label a person as suspicious solely because of a
route.

------------------------------------------------------------------------

# 35. Human-in-the-Loop

TRACE-X is an intelligence support system.

Final operational decisions remain with authorized human personnel.

### Recommended dashboard actions

-   View evidence
-   Review trajectory
-   Confirm/reject probable link
-   Add case
-   Export report
-   Acknowledge alert

Do not implement automatic accusation.

------------------------------------------------------------------------

# 36. Privacy and Security

Privacy is a core architectural requirement.

## Access control

Use RBAC:

-   Administrator
-   Traffic operator
-   Investigator
-   Viewer

## Security

-   HTTPS/TLS
-   encrypted database/storage where appropriate,
-   authentication,
-   authorization,
-   audit logging,
-   evidence access logging.

## Evidence integrity

For important evidence artifacts:

``` text
Evidence file
    ↓
SHA-256 hash
    ↓
Stored with metadata
```

This allows integrity verification.

## Retention

Implement configurable retention for structured events.

Example configuration:

``` text
EVENT_RETENTION_DAYS = 30
```

The actual production value must be determined by the deploying
authority's legal and operational policy.

## Privacy principle

> Collect and retain what is necessary for the authorized purpose.

For macro traffic analytics, use aggregated outputs where possible
rather than unnecessarily exposing individual vehicle identities.

------------------------------------------------------------------------

# 37. Recommended Technology Stack

## Core

-   **Python** --- AI and backend
-   **OpenCV** --- image/video processing
-   **YOLO** --- vehicle and plate detection
-   **OCR engine** --- PaddleOCR/EasyOCR or a suitable trained OCR
    pipeline
-   **Vehicle Re-ID model** --- embedding-based vehicle similarity
-   **FastAPI** --- backend APIs
-   **PostgreSQL** --- structured data
-   **PostGIS** --- geospatial queries
-   **React.js** --- dashboard
-   **Leaflet + OpenStreetMap** --- prototype GIS
-   **Docker** --- deployment

## Optional production-scale components

-   Kafka for event streaming,
-   Redis for caching,
-   object storage for authorized evidence,
-   GPU inference,
-   Kubernetes for large deployments.

Do not add production-scale components until the basic prototype works.

------------------------------------------------------------------------

# 38. Prototype Hardware

A practical prototype can run on:

### Minimum

-   normal laptop/desktop,
-   webcam or recorded videos,
-   CPU inference for demonstration.

### Recommended

-   NVIDIA GPU,
-   8+ GB VRAM if possible,
-   16--32 GB system RAM,
-   SSD storage.

The prototype does not need a government-grade server.

------------------------------------------------------------------------

# 39. Prototype Data Strategy

Use three types of data.

## Dataset A --- ANPR

Used for:

-   plate detection,
-   OCR,
-   adverse-condition testing.

Conditions should include:

-   day,
-   night,
-   rain,
-   blur,
-   angle,
-   low resolution,
-   dirty/obstructed plates.

## Dataset B --- Multi-Camera Journey

Use several recorded camera views where the same vehicles appear at
different locations.

If a suitable public multi-camera dataset is unavailable, construct a
controlled prototype dataset:

``` text
Camera C1 video
Camera C2 video
Camera C3 video
Camera C4 video
Camera C5 video
```

Assign timestamps and GPS metadata.

## Dataset C --- Investigation/Watchlist

Use synthetic records.

Example:

``` text
TS09AB1234 = STOLEN
TS09CD5678 = WATCHLIST
```

Do not use real sensitive police data for the prototype unless properly
authorized.

------------------------------------------------------------------------

# 40. Prototype Camera Simulation

Because the SIH team may not have access to real city cameras:

``` text
Recorded Video 1
      ↓
Camera C1

Recorded Video 2
      ↓
Camera C2

Recorded Video 3
      ↓
Camera C3

Recorded Video 4
      ↓
Camera C4
```

The software treats them as geographically distributed cameras.

This demonstrates the architecture without falsely claiming government
feed access.

------------------------------------------------------------------------

# 41. Recommended Prototype Scenario

Use one motorcycle as the primary demonstration.

Example:

``` text
Plate:
TS09AB1234

Vehicle:
Black motorcycle
```

### Camera sequence

``` text
C101 → C107 → C115 → C123
```

### Test

C101: - clear plate, - 96% confidence.

C107: - partially readable plate, - 61% confidence.

C115: - plate unreadable, - appearance match only.

C123: - clear plate, - 95% confidence.

TRACE-X should reconstruct:

``` text
C101
 CONFIRMED
    ↓
C107
 PROBABLE/CONFIRMED depending on evidence
    ↓
C115
 PROBABLE
    ↓
C123
 CONFIRMED
```

The exact classification should be generated from the implemented
scoring rules, not hard-coded just for the demo.

------------------------------------------------------------------------

# 42. Prototype Demo Story

## Scene 1 --- Difficult image

Show a rainy/night/blurred vehicle.

TRACE-X:

``` text
Image quality: LOW
```

Then:

``` text
Enhancement
+
Multi-frame fusion
+
OCR
```

Result:

``` text
TS09AB1234
Confidence: 94%
```

## Scene 2 --- Cross-camera tracking

Show:

``` text
C101 → C107 → C115 → C123
```

## Scene 3 --- Camera gap

Simulate C115 being offline or unreadable.

TRACE-X:

``` text
Camera gap detected
↓
Road + time + appearance reasoning
↓
Probable continuation
```

## Scene 4 --- GIS

Display the reconstructed route.

## Scene 5 --- Vehicle report

Search:

``` text
TS09AB1234
```

Generate the journey report.

## Scene 6 --- Traffic analytics

Switch to city traffic dashboard:

-   vehicle count,
-   traffic density,
-   heatmap,
-   congestion,
-   OD flow.

## Scene 7 --- Alert

Trigger a synthetic watchlist record:

``` text
TS09AB1234
WATCHLIST
```

Show the alert.

------------------------------------------------------------------------

# 43. Dashboard Design

The dashboard should have four main views.

## View 1 --- Live City Map

Show:

-   camera locations,
-   road status,
-   congestion heatmap,
-   active alerts.

## View 2 --- Vehicle Search

Search box:

``` text
Enter plate number
[ TS09AB1234 ]
[ SEARCH ]
```

Results:

-   first detected,
-   last detected,
-   camera timeline,
-   journey map,
-   confidence.

## View 3 --- Traffic Analytics

Cards:

``` text
Vehicles Today
Average Speed
Congested Areas
Active Alerts
```

Charts:

-   hourly traffic,
-   vehicle classes,
-   movement flows,
-   OD matrix.

## View 4 --- Alerts/Reports

Show:

-   watchlist alerts,
-   anomaly alerts,
-   congestion alerts,
-   journey report export.

------------------------------------------------------------------------

# 44. Suggested UI Journey

``` text
LOGIN
  ↓
DASHBOARD
  ├── LIVE MAP
  ├── VEHICLE SEARCH
  ├── TRAFFIC ANALYTICS
  ├── ALERTS
  └── REPORTS
```

------------------------------------------------------------------------

# 45. Backend API Design

Suggested API structure:

## Camera APIs

``` http
GET /api/cameras
GET /api/cameras/{camera_id}
POST /api/cameras
PATCH /api/cameras/{camera_id}
```

## Vehicle event APIs

``` http
GET /api/events
GET /api/events/{event_id}
POST /api/events
```

Filters:

``` text
plate
camera_id
start_time
end_time
vehicle_type
min_confidence
area
```

## Vehicle search

``` http
GET /api/vehicles/{plate}/history
```

Example response:

``` json
{
  "plate": "TS09AB1234",
  "first_detected": "...",
  "last_detected": "...",
  "observations": [],
  "trajectory": [],
  "overall_confidence": 0.91
}
```

## Traffic analytics

``` http
GET /api/traffic/summary
GET /api/traffic/heatmap
GET /api/traffic/flow
GET /api/traffic/od
GET /api/traffic/congestion
```

## Alerts

``` http
GET /api/alerts
POST /api/alerts/watchlist
PATCH /api/alerts/{alert_id}/acknowledge
```

## Reports

``` http
GET /api/reports/vehicle/{plate}
GET /api/reports/{report_id}
```

------------------------------------------------------------------------

# 46. Suggested Database Tables

## cameras

``` text
id
camera_id
name
latitude
longitude
road_id
direction
status
quality_score
created_at
```

## vehicle_events

``` text
id
event_id
camera_id
timestamp
plate_text
plate_confidence
plate_status
vehicle_type
vehicle_color
make
model
appearance_embedding
direction
latitude
longitude
road_id
image_quality_score
detection_confidence
```

## trajectories

``` text
id
trajectory_id
plate_text
created_at
overall_confidence
status
```

## trajectory_links

``` text
id
trajectory_id
from_event_id
to_event_id
match_score
match_status
reason
```

## watchlist

``` text
id
plate_text
category
status
created_at
```

## alerts

``` text
id
alert_type
plate_text
camera_id
timestamp
confidence
reason
status
created_at
```

## users

``` text
id
username
role
password_hash
created_at
```

## audit_logs

``` text
id
user_id
action
resource
timestamp
metadata
```

------------------------------------------------------------------------

# 47. Suggested Project Folder Structure

``` text
trace-x/
│
├── README.md
├── .env.example
├── docker-compose.yml
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   │
│   │   ├── api/
│   │   │   ├── cameras.py
│   │   │   ├── events.py
│   │   │   ├── vehicles.py
│   │   │   ├── traffic.py
│   │   │   ├── alerts.py
│   │   │   └── reports.py
│   │   │
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── ingestion/
│   │   │   ├── detection/
│   │   │   ├── anpr/
│   │   │   ├── reid/
│   │   │   ├── trajectory/
│   │   │   ├── traffic/
│   │   │   └── alerts/
│   │   │
│   │   └── utils/
│   │
│   ├── tests/
│   └── requirements.txt
│
├── ai/
│   ├── vehicle_detector/
│   ├── plate_detector/
│   ├── ocr/
│   ├── enhancement/
│   ├── reid/
│   └── quality/
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── maps/
│   │   ├── charts/
│   │   └── services/
│   └── package.json
│
├── data/
│   ├── videos/
│   ├── cameras/
│   ├── events/
│   ├── watchlists/
│   └── sample/
│
├── scripts/
│   ├── ingest_video.py
│   ├── generate_events.py
│   ├── seed_database.py
│   └── run_demo.py
│
└── docs/
    ├── architecture.md
    ├── api.md
    ├── testing.md
    └── demo.md
```

------------------------------------------------------------------------

# 48. Implementation Order

Do not build everything simultaneously.

## Phase 1 --- Basic ANPR

Goal:

``` text
Video
 ↓
Vehicle Detection
 ↓
Plate Detection
 ↓
OCR
 ↓
Vehicle Event
```

First make this reliable.

## Phase 2 --- Robust ANPR

Add:

-   quality checks,
-   enhancement,
-   multi-frame OCR,
-   confidence,
-   fallback handling.

## Phase 3 --- Event Database

Create PostgreSQL/PostGIS storage.

Implement:

``` text
camera
vehicle_event
```

## Phase 4 --- Vehicle Search

Implement:

``` text
plate → historical observations
```

## Phase 5 --- Cross-Camera Tracking

Add:

-   candidate generation,
-   plate similarity,
-   Re-ID,
-   time,
-   direction,
-   road graph,
-   evidence fusion.

## Phase 6 --- GIS Trajectory

Display:

``` text
C1 → C2 → C3 → C4
```

with confidence levels.

## Phase 7 --- Traffic Analytics

Add:

-   counts,
-   density,
-   speed,
-   flow,
-   OD,
-   congestion.

## Phase 8 --- Alerts and Reports

Add:

-   watchlist,
-   anomaly,
-   congestion,
-   report generation.

## Phase 9 --- Security

Add:

-   login,
-   RBAC,
-   audit logs,
-   evidence integrity,
-   configurable retention.

## Phase 10 --- Demo Polish

Create one reliable end-to-end demonstration.

------------------------------------------------------------------------

# 49. Testing Strategy

Do not claim \>90% accuracy without measurement.

Create separate test groups.

## ANPR tests

  Condition             Metric
  --------------------- ----------------------------
  Day                   Plate recognition accuracy
  Night                 Plate recognition accuracy
  Rain                  Plate recognition accuracy
  Blur                  Plate recognition accuracy
  Angle                 Plate recognition accuracy
  Dirty plate           Plate recognition accuracy
  Partial obstruction   Plate recognition accuracy
  Low resolution        Plate recognition accuracy

Track:

-   plate detection precision,
-   plate detection recall,
-   character accuracy,
-   full-plate exact-match accuracy,
-   confidence calibration.

------------------------------------------------------------------------

# 50. Trajectory Tests

Test:

### Test A --- Normal

``` text
C1 → C2 → C3 → C4
```

Expected:

> Confirmed trajectory.

### Test B --- Partial plate

``` text
C1 → C2(partial) → C3
```

Expected:

> C2 can be probable if supporting evidence is strong.

### Test C --- Unreadable plate

``` text
C1 → C2(no plate) → C3
```

Expected:

> Appearance + time + road reasoning may produce probable link.

### Test D --- Offline camera

``` text
C1 → C2(offline) → C3
```

Expected:

> Gap/inferred route, not confirmed C2 detection.

### Test E --- False similarity

Two black motorcycles appear.

Expected:

> Do not match based only on color/type.

### Test F --- Impossible travel time

Expected:

> Reject/strongly penalize candidate.

------------------------------------------------------------------------

# 51. Traffic Analytics Tests

Validate:

-   vehicle counts,
-   movement counts,
-   density,
-   speed estimates,
-   congestion status,
-   OD flows.

Compare against manually labeled ground truth for the prototype.

------------------------------------------------------------------------

# 52. Camera Reliability

This is a potential TRACE-X differentiator.

Create a camera reliability score based on:

-   resolution,
-   plate pixel size,
-   FPS,
-   blur,
-   brightness,
-   angle,
-   occlusion,
-   detection success rate,
-   OCR success rate,
-   online/offline status.

Example:

``` text
Camera C1
Reliability: 92%
Status: GOOD

Camera C2
Reliability: 58%
Status: DEGRADED

Camera C3
Reliability: OFFLINE
```

The trajectory engine can reduce reliance on degraded cameras.

This is a proposed resilience feature and should be demonstrated rather
than merely claimed.

------------------------------------------------------------------------

# 53. Camera Self-Healing Concept

If C2 becomes unreliable:

``` text
C1
 ↓
C2  ← degraded
 ↓
C3
```

TRACE-X can:

-   lower C2's evidence weight,
-   search neighboring cameras,
-   widen the candidate window carefully,
-   use road-network reasoning,
-   mark the resulting link as probable if needed.

This is better described as **resilience/camera-aware matching**, not
magical self-healing.

------------------------------------------------------------------------

# 54. Why TRACE-X Can Outperform a Basic System

Do not say:

> "Existing systems cannot do this."

Instead say:

> **"Existing systems solve important parts of ANPR, vehicle
> intelligence and traffic analytics. TRACE-X focuses on making the
> end-to-end workflow resilient when individual observations are
> imperfect."**

Differentiating design principles:

1.  **Confidence-aware evidence**
2.  **Multi-frame OCR**
3.  **Multi-signal cross-camera matching**
4.  **Road-constrained trajectory reasoning**
5.  **Camera reliability awareness**
6.  **Explicit confirmed/probable/unknown states**
7.  **Unified vehicle-event layer**
8.  **Investigation-oriented search and reporting**
9.  **Traffic analytics from the same event infrastructure**
10. **Privacy-by-design and human-in-the-loop operation**

These are system design differentiators, not claims of globally unique
invention.

------------------------------------------------------------------------

# 55. Unified Vehicle Event Layer

This is an important architecture decision.

Instead of creating separate systems for:

-   ANPR,
-   tracking,
-   traffic analytics,
-   alerts,

all modules consume the same normalized **Vehicle Event**.

``` text
                VEHICLE EVENT
                     |
       +-------------+-------------+
       |             |             |
       v             v             v
   Trajectory     Traffic        Alerts
     Engine      Analytics       Engine
       |             |             |
       +-------------+-------------+
                     |
                     v
                  GIS/UI
```

This reduces duplicated logic and makes the system easier to scale.

------------------------------------------------------------------------

# 56. Scalability Architecture

For the prototype:

``` text
Cameras
   ↓
Python AI
   ↓
FastAPI
   ↓
PostgreSQL/PostGIS
   ↓
React
```

For production:

``` text
Camera Network
      ↓
Edge AI
      ↓
Event Streaming
      ↓
Distributed Event Processing
      ↓
Scalable Event Store
      ↓
Trajectory / Traffic / Alert Services
      ↓
GIS / Command Center
```

Potential production components:

-   edge GPUs,
-   Kafka,
-   Redis,
-   distributed PostgreSQL or appropriate event storage,
-   object storage,
-   Kubernetes,
-   monitoring,
-   high availability.

------------------------------------------------------------------------

# 57. Interoperability

Real deployments may contain cameras from different vendors.

TRACE-X should normalize inputs into one internal event format.

``` text
Vendor A Camera ─┐
Vendor B Camera ─┼──> TRACE-X Normalization ──> Vehicle Event
Vendor C Camera ─┘
```

Possible input standards:

-   RTSP,
-   ONVIF,
-   HTTP APIs,
-   existing ANPR event APIs.

Do not assume every camera supports every protocol.

------------------------------------------------------------------------

# 58. Production Readiness Roadmap

## Phase 1 --- SIH Prototype

-   5--20 simulated cameras,
-   recorded videos,
-   ANPR,
-   event database,
-   trajectory,
-   GIS,
-   traffic analytics,
-   watchlist,
-   reports.

## Phase 2 --- Controlled Pilot

-   real cameras in one corridor/zone,
-   camera quality audit,
-   ground-truth labeling,
-   accuracy and latency measurement,
-   operator feedback.

## Phase 3 --- City Deployment

-   hundreds/thousands of cameras,
-   edge inference,
-   scalable event processing,
-   high availability,
-   security,
-   governance,
-   monitoring.

------------------------------------------------------------------------

# 59. Camera Readiness Assessment

Before production deployment, assess every camera.

### Checklist

-   resolution,
-   FPS,
-   plate pixel size,
-   camera height,
-   viewing angle,
-   lane coverage,
-   night visibility,
-   rain performance,
-   motion blur,
-   compression,
-   glare,
-   occlusion,
-   network reliability.

### Classification

``` text
GREEN  = good for ANPR
YELLOW = usable with limitations
RED    = poor for reliable ANPR
```

This prevents unrealistic expectations.

------------------------------------------------------------------------

# 60. Important Limitations to State Honestly

TRACE-X should explicitly acknowledge:

### Camera limitations

If the camera never captures the plate clearly, AI cannot recover
missing information.

### Re-ID limitations

Similar vehicles can produce false matches.

### Camera gaps

A missing camera creates uncertainty.

### Route inference

A probable route is not a direct observation.

### Speed estimation

Camera-to-camera speed is an estimate and depends on actual route length
and timestamps.

### OCR accuracy

> 90% must be experimentally demonstrated under the selected test
> conditions; it should not be claimed merely because a model exists.

### Privacy

Vehicle-level data can be sensitive and requires appropriate governance,
access controls and retention rules.

------------------------------------------------------------------------

# 61. Recommended Evaluation Metrics

## ANPR

-   Plate detection precision
-   Plate detection recall
-   Character accuracy
-   Full-plate exact match
-   OCR confidence calibration
-   Day/night/rain/blur performance

## Tracking

-   Cross-camera matching precision
-   Cross-camera matching recall
-   ID switches
-   trajectory completeness
-   false-link rate
-   confirmed/probable classification quality

## Traffic

-   counting error,
-   speed estimation error,
-   congestion detection precision/recall,
-   OD estimation accuracy.

## System

-   processing latency,
-   events/second,
-   camera throughput,
-   API response time,
-   GPU utilization,
-   failure recovery time.

------------------------------------------------------------------------

# 62. Example End-to-End Data Flow

``` text
CAMERA C101
    |
    v
Vehicle detected
    |
    v
Plate detected
    |
    v
Quality = 78/100
    |
    v
Enhancement
    |
    v
Multi-frame OCR
    |
    v
TS09AB1234 / 96%
    |
    v
Vehicle Event
    |
    v
PostgreSQL/PostGIS
    |
    v
Trajectory Engine
    |
    +----> Candidate C107
    |
    +----> Candidate C115
    |
    v
Evidence Fusion
    |
    v
C107 = confirmed
C115 = probable
    |
    v
Trajectory Graph
    |
    v
GIS
    |
    +----> Vehicle Journey Report
    |
    +----> Traffic Aggregation
                 |
                 +----> Density
                 +----> Flow
                 +----> OD
                 +----> Congestion
                 |
                 v
             Dashboard
```

------------------------------------------------------------------------

# 63. Example of the Three Problems Together

## Problem 1

Camera sees:

``` text
Rain + blur
```

TRACE-X:

``` text
Quality check
→ enhancement
→ multi-frame fusion
→ OCR
→ confidence
```

Output:

``` text
TS09AB1234 — 88%
```

## Problem 2

Another camera sees:

``` text
TS09A?1234
```

TRACE-X:

``` text
plate similarity
+
black motorcycle
+
same direction
+
feasible travel time
+
road connectivity
```

Output:

``` text
Probable match
```

## Problem 3

Thousands of such events are aggregated:

``` text
Road A → 4,820 vehicles/hour
Road B → 5,130 vehicles/hour
Average speed → 14 km/h
```

Output:

``` text
HIGH CONGESTION
```

------------------------------------------------------------------------

# 64. The TRACE-X Value Proposition

### Existing infrastructure

Already has:

> Cameras + video feeds

### TRACE-X adds

> AI recognition + structured events + cross-camera intelligence +
> traffic analytics + GIS + alerts.

### Simple explanation

> **"We don't replace the city's eyes. We add intelligence to them."**

Another strong statement:

> **"TRACE-X converts isolated camera observations into connected
> vehicle intelligence and city-wide traffic understanding."**

------------------------------------------------------------------------

# 65. SIH Presentation Story

Recommended narrative:

## Slide 1 --- Problem

Cameras exist, but information is fragmented.

## Slide 2 --- Proposed Solution

``` text
CCTV
 ↓
AI
 ↓
Vehicle Events
 ↓
Tracking
 ↓
Traffic Intelligence
 ↓
Alerts
```

## Slide 3 --- Technical Approach

Show:

-   robust ANPR,
-   evidence fusion,
-   road reasoning,
-   GIS,
-   traffic analytics.

## Slide 4 --- Feasibility & Viability

Show:

-   existing camera reuse,
-   software-first architecture,
-   prototype using recorded feeds,
-   scalable production roadmap,
-   security/privacy.

## Slide 5 --- Impact

Show:

-   faster vehicle investigations,
-   better traffic visibility,
-   congestion detection,
-   smarter planning,
-   operational efficiency.

## Slide 6 --- Research & References

Show research areas:

-   ANPR/OCR,
-   vehicle Re-ID,
-   multi-camera tracking,
-   GIS traffic analytics,
-   traffic flow,
-   privacy/security.

------------------------------------------------------------------------

# 66. Strong Evaluator Answers

## "ANPR already exists. What is new?"

> "Yes, ANPR is an established technology. We are not claiming to invent
> ANPR. TRACE-X focuses on resilient end-to-end integration: when plate
> recognition is uncertain, we combine multiple observations using
> appearance, time, direction and road constraints, explicitly
> distinguishing confirmed and probable evidence."

## "Why not just search the CCTV footage?"

> "Searching raw video manually is expensive and slow at city scale.
> TRACE-X converts video into structured vehicle events that can be
> searched and analyzed automatically."

## "Are you storing every vehicle's video?"

> "No. TRACE-X does not require continuous duplication of the raw video
> archive. It extracts structured vehicle events. Existing camera
> infrastructure can retain source footage according to its own
> policies."

## "Can you track a vehicle if the plate is unreadable?"

> "Not with certainty from the unreadable frame alone. TRACE-X uses
> other frames and supporting evidence such as appearance, time,
> direction and road connectivity to produce a probable match when
> justified. Otherwise it marks the observation unknown."

## "Can you tell where the vehicle will go?"

> "Only if a live camera detects it can we report a current detection.
> We can optionally estimate a probable next route, but that is a
> prediction, not a confirmed location."

## "Can this scale?"

> "The prototype uses recorded feeds and a centralized stack. Production
> architecture moves inference toward the edge and uses distributed
> event processing so the central platform receives compact vehicle
> events rather than all raw video."

## "What if cameras fail?"

> "TRACE-X tracks camera reliability and does not treat a failed camera
> as proof that a vehicle disappeared. It can use neighboring cameras
> and road/time constraints to represent a probable continuation while
> clearly marking uncertainty."

------------------------------------------------------------------------

# 67. Development Priorities

If development time becomes limited, prioritize in this order:

### Must have

1.  Vehicle detection
2.  Plate detection
3.  OCR
4.  Confidence
5.  Vehicle event database
6.  Plate search
7.  Cross-camera trajectory
8.  GIS map
9.  Traffic counts
10. Congestion
11. Watchlist alert
12. Report generation

### Strong differentiators

13. Multi-frame OCR
14. Quality scoring
15. Vehicle Re-ID
16. Road-constrained matching
17. Confirmed/probable/unknown evidence
18. Camera reliability

### Optional advanced features

19. Predictive traffic
20. Advanced route anomaly detection
21. Streaming infrastructure
22. Large-scale distributed deployment

Do not sacrifice the core working demo to build advanced optional
features.

------------------------------------------------------------------------

# 68. Golden Demo

The ideal final demonstration should be one continuous story:

``` text
1. Camera sees vehicle
          ↓
2. Difficult image
          ↓
3. TRACE-X enhances it
          ↓
4. OCR produces plate + confidence
          ↓
5. Vehicle event created
          ↓
6. Same vehicle appears at another camera
          ↓
7. Plate is partial
          ↓
8. TRACE-X uses evidence fusion
          ↓
9. Camera gap occurs
          ↓
10. Road/time reasoning creates probable link
          ↓
11. Next camera confirms vehicle
          ↓
12. GIS reconstructs journey
          ↓
13. Search plate to retrieve journey
          ↓
14. Generate report
          ↓
15. Aggregate events
          ↓
16. Detect congestion
          ↓
17. Display city traffic heatmap
          ↓
18. Trigger watchlist alert
```

This demonstrates all major parts of the SIH problem in one coherent
system.

------------------------------------------------------------------------

# 69. Final Architecture Principle

The entire TRACE-X prototype should follow this principle:

> **Camera → Observation → Confidence → Evidence Fusion → Intelligence →
> Action**

More concretely:

``` text
SEE
CCTV / ANPR
   ↓
RECOGNIZE
Vehicle + Plate + Quality
   ↓
STRUCTURE
Vehicle Event
   ↓
CONNECT
Cross-Camera Matching
   ↓
RECONSTRUCT
Trajectory
   ↓
UNDERSTAND
Traffic Analytics
   ↓
VISUALIZE
GIS Dashboard
   ↓
ACT
Alerts + Reports
```

------------------------------------------------------------------------

# 70. One-Sentence Project Definition

> **TRACE-X is a confidence-aware, city-wide vehicle intelligence
> platform that converts CCTV/ANPR feeds into structured vehicle events,
> robustly connects imperfect observations across cameras, reconstructs
> vehicle journeys, and transforms aggregated movements into GIS-based
> traffic intelligence, alerts and reports.**

------------------------------------------------------------------------

# 71. Final Rules for the Development Team

1.  **Never fabricate plate numbers.**
2.  **Never treat a probable match as confirmed.**
3.  **Never claim future vehicle location as fact.**
4.  **Never claim access to government camera feeds without
    authorization.**
5.  **Never claim \>90% ANPR accuracy without measured testing.**
6.  **Do not duplicate the entire video archive unnecessarily.**
7.  **Use structured vehicle events as the core data layer.**
8.  **Keep raw evidence handling separate from event analytics.**
9.  **Use road/time constraints for cross-camera matching.**
10. **Use Re-ID as supporting evidence, not absolute identity.**
11. **Make camera reliability visible.**
12. **Keep human investigators in the decision loop.**
13. **Use RBAC and audit logs.**
14. **Design retention as configurable and policy-controlled.**
15. **Build the simplest working end-to-end prototype first.**
16. **Demonstrate failure recovery, not just perfect-case detection.**
17. **Make every inference explainable.**
18. **Separate direct observations from inferred/probable routes.**

------------------------------------------------------------------------

# 72. Quick Build Checklist

## AI

-   [ ] Vehicle detector
-   [ ] Plate detector
-   [ ] OCR
-   [ ] Image quality scoring
-   [ ] Enhancement
-   [ ] Multi-frame fusion
-   [ ] Confidence scoring
-   [ ] Vehicle Re-ID

## Backend

-   [ ] FastAPI
-   [ ] PostgreSQL
-   [ ] PostGIS
-   [ ] Vehicle event schema
-   [ ] Search API
-   [ ] Trajectory API
-   [ ] Traffic API
-   [ ] Alert API
-   [ ] Report API

## GIS

-   [ ] Camera map
-   [ ] Vehicle journey map
-   [ ] Traffic heatmap
-   [ ] Congestion map
-   [ ] Flow visualization

## Frontend

-   [ ] Login
-   [ ] Dashboard
-   [ ] Vehicle search
-   [ ] Journey timeline
-   [ ] Traffic analytics
-   [ ] Alerts
-   [ ] Reports

## Security

-   [ ] Authentication
-   [ ] RBAC
-   [ ] Audit logs
-   [ ] HTTPS
-   [ ] Configurable retention
-   [ ] Evidence hash

## Demo

-   [ ] Clear vehicle
-   [ ] Blurry vehicle
-   [ ] Rain/night case
-   [ ] Partial plate
-   [ ] Missing camera
-   [ ] Cross-camera match
-   [ ] GIS trajectory
-   [ ] Traffic heatmap
-   [ ] Congestion alert
-   [ ] Watchlist alert
-   [ ] Journey report

------------------------------------------------------------------------

# 73. Final Mental Model

Whenever a development decision is unclear, return to these four
questions:

### Q1 --- Can we SEE it?

Robust ANPR and vehicle detection.

### Q2 --- Can we CONNECT it?

Evidence fusion and cross-camera trajectory.

### Q3 --- Can we UNDERSTAND it?

Traffic analytics and GIS.

### Q4 --- Can we ACT on it responsibly?

Alerts, reports, security, privacy and human verification.

That is TRACE-X.
