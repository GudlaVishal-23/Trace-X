
    let currentJobId = null;
    let wsConnection = null;
    let playMode = 'LIVE';
    let allDetections = [];
    let reviewDetections = [];
    const activeTrackMap = new Map();
    let lastSelectedPlate = "TS09AB1234";
    let pollInterval = null;
    let lastPolledFrame = 0;

    const videoElem = document.getElementById("stage-video");
    const canvasElem = document.getElementById("stage-canvas");
    const ctx = canvasElem.getContext("2d");

    function syncCanvasDimensions() {
      if (videoElem.clientWidth > 0 && videoElem.clientHeight > 0) {
        if (canvasElem.width !== videoElem.clientWidth || canvasElem.height !== videoElem.clientHeight) {
          canvasElem.width = videoElem.clientWidth;
          canvasElem.height = videoElem.clientHeight;
        }
      }
    }
    window.addEventListener("resize", syncCanvasDimensions);
    videoElem.addEventListener("loadedmetadata", syncCanvasDimensions);

    // Preload default sample clip on load so theatre viewport is never blank
    window.addEventListener("DOMContentLoaded", () => {
      const defaultVal = "5009674-hd_1920_1080_25fps.mp4|CAM_DL_01";
      const [videoFile, camId] = defaultVal.split("|");
      videoElem.src = `/sample_videos/${videoFile}`;
      videoElem.load();
    });

    function getVideoDisplayedRect() {
      const vWidth = videoElem.videoWidth || 1920;
      const vHeight = videoElem.videoHeight || 1080;
      const cWidth = canvasElem.width;
      const cHeight = canvasElem.height;
      if (!cWidth || !cHeight) {
        return { x: 0, y: 0, w: 1920, h: 1080, scaleX: 1, scaleY: 1 };
      }
      const videoRatio = vWidth / vHeight;
      const clientRatio = cWidth / cHeight;
      let renderW, renderH, offsetX, offsetY;
      if (clientRatio > videoRatio) {
        renderH = cHeight; renderW = cHeight * videoRatio;
        offsetX = (cWidth - renderW) / 2; offsetY = 0;
      } else {
        renderW = cWidth; renderH = cWidth / videoRatio;
        offsetX = 0; offsetY = (cHeight - renderH) / 2;
      }
      return { x: offsetX, y: offsetY, w: renderW, h: renderH, scaleX: renderW / vWidth, scaleY: renderH / vHeight };
    }

    setInterval(() => {
      const now = new Date();
      const timeStr = now.toLocaleTimeString('en-IN', { hour12: false, timeZone: 'Asia/Kolkata' });
      const clockEl = document.getElementById("live-ist-clock");
      if (clockEl) clockEl.innerText = `${timeStr} IST`;
    }, 1000);

    function setPlayMode(mode) {
      playMode = mode;
      const liveBtn = document.getElementById("live-mode-btn");
      const revBtn = document.getElementById("review-mode-btn");
      liveBtn.className = mode === 'LIVE'
        ? "flex items-center space-x-1 px-2 py-1 rounded-md bg-emerald-500/15 text-emerald-400 font-semibold border border-emerald-500/20 transition-all"
        : "px-2 py-1 text-slate-400 hover:text-white rounded-md transition-all";
      revBtn.className = mode === 'REVIEW'
        ? "flex items-center space-x-1 px-2 py-1 rounded-md bg-amber-500/15 text-amber-500 font-semibold border border-amber-500/20 transition-all"
        : "px-2 py-1 text-slate-400 hover:text-white rounded-md transition-all";
    }

    function showHUDToast(msg, type = "info") {
      const banner = document.getElementById("alert-banner");
      const bannerText = document.getElementById("banner-text");
      if (banner && bannerText) {
        bannerText.innerText = msg;
        banner.style.background = type === "error" ? "#dc2626" : "#F59E0B";
        banner.classList.remove("hidden");
        setTimeout(() => banner.classList.add("hidden"), 6000);
      }
    }

    function loadPresetSample(val) {
      if (!val) return;
      const [videoFilename, camId] = val.split("|");
      document.getElementById("camera-select").value = camId;
      document.getElementById("hud-cam-title").innerText = `${camId}`;
      videoElem.src = `/sample_videos/${videoFilename}`;
      videoElem.load();
      allDetections = [];
      activeTrackMap.clear();
      document.getElementById("detection-feed-list").innerHTML = "";
      document.getElementById("fused-feed-list").innerHTML = "";
    }

    async function submitPreset(presetFilename, cameraId) {
      const startBtn = document.getElementById("start-scan-btn");
      startBtn.disabled = true;
      document.getElementById("status-pill").innerText = "SCANNING";
      document.getElementById("status-pill").className = "text-emerald-400 font-bold tracking-wide text-[10px] animate-pulse";
      document.getElementById("drop-overlay").classList.add("hidden");
      
      // Ensure video is playing immediately
      videoElem.muted = true;
      videoElem.loop = true;
      if (!videoElem.src || videoElem.src.endsWith("/scan")) {
        videoElem.src = `/sample_videos/${presetFilename}`;
        videoElem.load();
      }
      videoElem.play().catch(e => console.log("Autoplay:", e));

      const formData = new FormData();
      formData.append("preset_filename", presetFilename);
      formData.append("camera_id", cameraId);
      try {
        const res = await fetch("/api/ingest/upload", { method: "POST", body: formData });
        if (!res.ok) { const err = await res.json(); throw new Error(err.detail || "Failed"); }
        const data = await res.json();
        initJobStream(data.job_id, presetFilename);
      } catch (e) {
        showHUDToast("Error: " + e.message, "error");
        startBtn.disabled = false;
        document.getElementById("status-pill").innerText = "ERROR";
      }
    }

    function handleFileSelected(input) {
      if (input.files && input.files.length > 0) {
        document.getElementById("upload-label").innerText = input.files[0].name.slice(0, 14) + "...";
        submitVideoUpload();
      }
    }

    async function submitVideoUpload() {
      const fileInput = document.getElementById("video-file-input");
      const presetSelect = document.getElementById("sample-preset-select");
      if (fileInput.files && fileInput.files.length > 0) {
        const file = fileInput.files[0];
        const cameraId = document.getElementById("camera-select").value;
        const formData = new FormData();
        formData.append("file", file);
        formData.append("camera_id", cameraId);
        document.getElementById("start-scan-btn").disabled = true;
        document.getElementById("status-pill").innerText = "UPLOADING";
        document.getElementById("drop-overlay").classList.add("hidden");
        try {
          const res = await fetch("/api/ingest/upload", { method: "POST", body: formData });
          if (!res.ok) { const err = await res.json(); throw new Error(err.detail || "Failed"); }
          const data = await res.json();
          initJobStream(data.job_id);
        } catch (e) {
          showHUDToast("Upload failed: " + e.message, "error");
          document.getElementById("start-scan-btn").disabled = false;
          document.getElementById("status-pill").innerText = "ERROR";
        }
        return;
      }
      let val = presetSelect.value || "5009674-hd_1920_1080_25fps.mp4|CAM_DL_01";
      const [videoFilename, camId] = val.split("|");
      submitPreset(videoFilename, camId);
    }

    function initJobStream(jobId, presetFilename = null) {
      currentJobId = jobId;
      const statusPill = document.getElementById("status-pill");
      statusPill.innerText = "SCANNING";
      statusPill.className = "text-emerald-400 font-bold tracking-wide text-[10px] animate-pulse";
      document.getElementById("drop-overlay").classList.add("hidden");
      
      // Ensure video is playing
      videoElem.muted = true;
      videoElem.loop = true;
      if (!videoElem.src || videoElem.src === "" || videoElem.paused) {
        videoElem.src = presetFilename ? `/sample_videos/${presetFilename}` : `/api/ingest/jobs/${jobId}/video`;
        videoElem.load();
        videoElem.play().catch(e => console.log("Play:", e));
      } else {
        videoElem.play().catch(e => console.log("Play:", e));
      }

      setPlayMode('LIVE');
      document.getElementById("detection-feed-list").innerHTML = "";
      document.getElementById("fused-feed-list").innerHTML = "";
      allDetections = [];
      activeTrackMap.clear();
      reviewDetections = [];
      lastPolledFrame = 0;
      connectWebSocket(jobId);
      startFallbackPolling(jobId);
    }

    function connectWebSocket(jobId) {
      if (wsConnection) { try { wsConnection.close(); } catch(e) {} }
      const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
      wsConnection = new WebSocket(`${proto}//${window.location.host}/ws/ingest/${jobId}`);
      wsConnection.onopen = () => {
        document.getElementById("sock-status").innerText = "WS CONNECTED";
        document.getElementById("sock-status").className = "text-emerald-400 font-semibold";
      };
      wsConnection.onmessage = (evt) => {
        try {
          handleLiveEvent(JSON.parse(evt.data));
        } catch (e) {
          console.error("WS parse:", e);
        }
      };
      wsConnection.onclose = () => {
        document.getElementById("sock-status").innerText = "POLL ACTIVE";
        document.getElementById("sock-status").className = "text-amber-400 font-semibold";
      };
    }

    function startFallbackPolling(jobId) {
      if (pollInterval) clearInterval(pollInterval);
      pollInterval = setInterval(async () => {
        if (!currentJobId || currentJobId !== jobId) { clearInterval(pollInterval); return; }
        try {
          const jobRes = await fetch(`/api/ingest/jobs/${jobId}`);
          if (jobRes.ok) {
            const job = await jobRes.json();
            if (job.total_frames > 0) {
              const pct = Math.min(100, Math.round((job.done_frames / job.total_frames) * 100));
              document.getElementById("progress-bar-fill").style.width = `${pct}%`;
              document.getElementById("frames-metric").innerText = `#${job.done_frames} / ${job.total_frames}`;
              if (job.stats && job.stats.processing_fps) {
                document.getElementById("fps-metric").innerText = `${job.stats.processing_fps} FPS`;
              }
            }
            if (job.status === "DONE") {
              handleLiveEvent({ type: "done", stats: job.stats });
            }
          }
          const detRes = await fetch(`/api/ingest/jobs/${jobId}/detections?since_frame=${lastPolledFrame}&limit=50`);
          if (detRes.ok) {
            const dets = await detRes.json();
            for (const d of dets) {
              if (d.frame_idx > lastPolledFrame) {
                lastPolledFrame = d.frame_idx;
                handleLiveEvent({
                  type: "detection",
                  frame_idx: d.frame_idx,
                  video_ts: d.video_ts,
                  track_id: d.track_id,
                  bbox: d.bbox,
                  plate_bbox: d.plate_bbox,
                  plate_raw: d.plate_raw,
                  plate_conf: d.plate_conf,
                  blur: d.blur_score,
                  vehicle_class: d.vehicle_class,
                  color: d.color,
                  crop_url: d.crop_path,
                  plate_url: d.plate_crop_path
                });
              }
            }
          }
          const trackRes = await fetch(`/api/ingest/jobs/${jobId}/tracks`);
          if (trackRes.ok) {
            const tracks = await trackRes.json();
            for (const t of tracks) {
              addFusedCard({
                track_id: t.track_id,
                plate: t.fused_plate,
                conf: t.fused_conf,
                n_frames: t.n_frames,
                hit: !!t.watchlist_hit,
                vehicle_class: t.vehicle_class,
                color: t.color
              });
            }
          }
        } catch (e) {
          console.debug("Poll:", e);
        }
      }, 400);
    }

    function handleLiveEvent(msg) {
      if (msg.type === "progress") {
        const pct = Math.min(100, Math.round((msg.done / msg.total) * 100));
        document.getElementById("progress-bar-fill").style.width = `${pct}%`;
        document.getElementById("frames-metric").innerText = `#${msg.done} / ${msg.total}`;
        document.getElementById("fps-metric").innerText = `${msg.fps_proc || 16} FPS`;
        if (msg.eta_s) {
          const etaEl = document.getElementById("eta-metric");
          if (etaEl) etaEl.innerText = `ETA: ${msg.eta_s}s`;
        }
      }
      else if (msg.type === "detection") {
        msg.receivedAt = performance.now();
        activeTrackMap.set(msg.track_id, msg);
        allDetections.push(msg);
        addDetectionCard(msg);
        reviewDetections.push(msg);
      }
      else if (msg.type === "fused") {
        addFusedCard(msg);
      }
      else if (msg.type === "alert") {
        tacticalAudio.alertChirp();
        const banner = document.getElementById("alert-banner");
        document.getElementById("banner-text").innerText = `WATCHLIST HIT: ${msg.category} (${msg.plate}) [${msg.priority}]`;
        banner.classList.remove("hidden");
      }
      else if (msg.type === "done") {
        const statusPill = document.getElementById("status-pill");
        statusPill.innerText = "DONE (100%)";
        statusPill.className = "text-emerald-400 font-bold tracking-wide text-[10px]";
        document.getElementById("start-scan-btn").disabled = false;
        tacticalAudio.radarPing();
        // Seamless transition: keep video looping with real-time canvas overlays
        setPlayMode('REVIEW');
      }
    }

    // Canvas Real-Time Perception Engine
    function renderCanvasLoop() {
      syncCanvasDimensions();
      ctx.clearRect(0, 0, canvasElem.width, canvasElem.height);

      if (canvasElem.width > 0 && canvasElem.height > 0) {
        const rect = getVideoDisplayedRect();
        const curTime = videoElem.currentTime || 0;
        const now = performance.now();

        // Priority 1: Detections matching video playback time
        let detsToDraw = [];
        if (allDetections.length > 0) {
          detsToDraw = allDetections.filter(d => Math.abs(d.video_ts - curTime) <= 0.25);
        }

        // Priority 2: Actively received WebSocket tracks during initial stream
        if (detsToDraw.length === 0 && activeTrackMap.size > 0) {
          for (const [tid, det] of activeTrackMap.entries()) {
            if (now - det.receivedAt < 1800) {
              detsToDraw.push(det);
            }
          }
        }

        const seenTracks = new Set();
        for (const det of detsToDraw) {
          if (seenTracks.has(det.track_id)) continue;
          seenTracks.add(det.track_id);

          const [x1, y1, x2, y2] = det.bbox;
          const sx = rect.x + x1 * rect.scaleX;
          const sy = rect.y + y1 * rect.scaleY;
          const sw = (x2 - x1) * rect.scaleX;
          const sh = (y2 - y1) * rect.scaleY;

          // Vehicle box (Emerald)
          ctx.strokeStyle = "#10B981";
          ctx.lineWidth = 2;
          ctx.strokeRect(sx, sy, sw, sh);

          // Precision HUD Corner Brackets
          const clen = Math.min(10, Math.min(sw, sh) / 3);
          ctx.lineWidth = 2.5;
          ctx.beginPath();
          ctx.moveTo(sx, sy + clen); ctx.lineTo(sx, sy); ctx.lineTo(sx + clen, sy);
          ctx.moveTo(sx + sw - clen, sy); ctx.lineTo(sx + sw, sy); ctx.lineTo(sx + sw, sy + clen);
          ctx.moveTo(sx, sy + sh - clen); ctx.lineTo(sx, sy + sh); ctx.lineTo(sx + clen, sy + sh);
          ctx.moveTo(sx + sw - clen, sy + sh); ctx.lineTo(sx + sw, sy + sh); ctx.lineTo(sx + sw, sy + sh - clen);
          ctx.stroke();

          // Vehicle Tag
          const label = `#${det.track_id} ${det.vehicle_class || 'car'}`;
          const labelW = Math.max(90, label.length * 7 + 8);
          ctx.fillStyle = "rgba(15, 23, 42, 0.90)";
          ctx.fillRect(sx, Math.max(0, sy - 18), labelW, 18);
          ctx.fillStyle = "#10B981";
          ctx.font = "bold 10px Inter, sans-serif";
          ctx.fillText(label, sx + 5, Math.max(12, sy - 5));

          // Plate Box (Amber)
          if (det.plate_bbox && det.plate_bbox.length === 4) {
            const [px1, py1, px2, py2] = det.plate_bbox;
            const psx = rect.x + px1 * rect.scaleX;
            const psy = rect.y + py1 * rect.scaleY;
            const psw = (px2 - px1) * rect.scaleX;
            const psh = (py2 - py1) * rect.scaleY;

            ctx.strokeStyle = "#F59E0B";
            ctx.lineWidth = 2;
            ctx.strokeRect(psx, psy, psw, psh);

            if (det.plate_raw) {
              const ptext = `${det.plate_raw} ${Math.round((det.plate_conf || 0.9) * 100)}%`;
              const ptextW = ptext.length * 7.5 + 8;
              ctx.fillStyle = "rgba(245, 158, 11, 0.95)";
              ctx.fillRect(psx, Math.max(0, psy - 16), ptextW, 16);
              ctx.fillStyle = "#0F172A";
              ctx.font = "bold 10px 'JetBrains Mono', monospace";
              ctx.fillText(ptext, psx + 4, Math.max(11, psy - 3));
            }
          }
        }
      }
      requestAnimationFrame(renderCanvasLoop);
    }
    requestAnimationFrame(renderCanvasLoop);

    // Review mode sync
    videoElem.addEventListener("timeupdate", () => {
      if (videoElem.duration) {
        document.getElementById("scrubber-current-time").innerText = formatTime(videoElem.currentTime);
        document.getElementById("scrubber-duration").innerText = formatTime(videoElem.duration);
        if (playMode === 'REVIEW') {
          document.getElementById("progress-bar-fill").style.width = `${(videoElem.currentTime / videoElem.duration) * 100}%`;
        }
      }
      if (playMode !== 'REVIEW' || reviewDetections.length === 0) return;
      ctx.clearRect(0, 0, canvasElem.width, canvasElem.height);
      const rect = getVideoDisplayedRect();
      const active = reviewDetections.filter(d => Math.abs(d.video_ts - videoElem.currentTime) <= 0.08);
      for (const d of active) {
        const [x1, y1, x2, y2] = d.bbox;
        const sx = rect.x + x1 * rect.scaleX, sy = rect.y + y1 * rect.scaleY;
        const sw = (x2 - x1) * rect.scaleX, sh = (y2 - y1) * rect.scaleY;
        ctx.strokeStyle = "#F59E0B"; ctx.lineWidth = 2;
        ctx.strokeRect(sx, sy, sw, sh);
        ctx.fillStyle = "rgba(245, 158, 11, 0.9)";
        ctx.fillRect(sx, Math.max(0, sy - 16), 120, 16);
        ctx.fillStyle = "#000"; ctx.font = "bold 10px JetBrains Mono";
        ctx.fillText(`${d.plate_raw || '#' + d.track_id}`, sx + 4, Math.max(11, sy - 3));
      }
    });

    function formatTime(s) {
      if (!s || isNaN(s)) return "00:00.00";
      const m = Math.floor(s / 60), sec = Math.floor(s % 60), ms = Math.floor((s % 1) * 100);
      return `${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}.${String(ms).padStart(2,'0')}`;
    }

    function togglePlayPause() {
      if (videoElem.paused) { videoElem.play(); document.getElementById("play-icon").innerText = "pause"; }
      else { videoElem.pause(); document.getElementById("play-icon").innerText = "play_arrow"; }
    }
    function stepFrame(delta) { videoElem.pause(); document.getElementById("play-icon").innerText = "play_arrow"; videoElem.currentTime = Math.max(0, videoElem.currentTime + (delta / 25.0)); }
    function setPlaybackSpeed(spd, btn) {
      videoElem.playbackRate = spd;
      btn.parentElement.querySelectorAll("button").forEach(b => b.className = "hover:text-white px-1");
      btn.className = "text-amber-500 font-bold px-1 bg-white/5 rounded";
    }
    function handleScrubberClick(e) {
      const track = document.getElementById("scrubber-track");
      const rect = track.getBoundingClientRect();
      if (videoElem.duration) videoElem.currentTime = ((e.clientX - rect.left) / rect.width) * videoElem.duration;
    }

    function addDetectionCard(det) {
      const feed = document.getElementById("detection-feed-list");
      if (document.getElementById(`det-card-${det.track_id}-${det.frame_idx}`)) return;
      if (feed.children.length === 1 && feed.children[0].innerText.includes("Click")) feed.innerHTML = "";
      const card = document.createElement("div");
      card.id = `det-card-${det.track_id}-${det.frame_idx}`;
      card.className = "p-2 rounded-lg bg-slate-850 border border-white/[0.06] hover:border-amber-500/30 transition-all cursor-pointer flex items-center justify-between gap-2";
      card.onclick = () => { videoElem.currentTime = det.video_ts; openEvidenceModal(det); };
      const plateText = det.plate_raw || "UNKNOWN";
      const isCommercial = plateText.startsWith("TS09") || plateText.startsWith("WB") || plateText.includes("AUTO");
      card.innerHTML = `
        <div class="flex items-center space-x-2 overflow-hidden">
          <img class="w-10 h-7 object-cover rounded bg-black border border-white/[0.06] shrink-0" src="${det.crop_url}" alt="" onerror="this.src='/static/evidence/vehicle_DL9CAB5561.jpg'">
          <div class="flex flex-col min-w-0">
            <div class="hsrp-plate ${isCommercial ? 'commercial' : ''}"><span class="ind-strip">IND</span><span>${plateText}</span></div>
            <div class="text-[8px] text-slate-400 font-mono truncate mt-0.5">f${det.frame_idx} • ${det.video_ts.toFixed(1)}s • ${det.vehicle_class}</div>
          </div>
        </div>
        <div class="flex flex-col items-end shrink-0">
          <span class="text-[8px] font-mono px-1 py-0.2 rounded font-semibold ${det.plate_conf >= 0.8 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'}">${Math.round(det.plate_conf * 100)}%</span>
          <span class="text-[8px] text-slate-500 font-mono mt-0.5">#${det.track_id}</span>
        </div>`;
      feed.insertBefore(card, feed.firstChild);
      if (feed.children.length > 40) feed.removeChild(feed.lastChild);
      document.getElementById("det-counter").innerText = `${feed.querySelectorAll("[id^='det-card']").length} READS`;
    }

    function addFusedCard(track) {
      const feed = document.getElementById("fused-feed-list");
      if (feed.children.length === 1 && feed.children[0].innerText.includes("Awaiting")) feed.innerHTML = "";
      const existing = document.getElementById(`track-${track.track_id}`);
      const card = existing || document.createElement("div");
      card.id = `track-${track.track_id}`;
      card.className = `p-2 rounded-lg ${track.hit ? 'bg-red-950/30 border border-red-500/30' : 'bg-slate-850 border border-white/[0.06] hover:border-white/10'} transition-all`;
      lastSelectedPlate = track.plate;
      const isCommercial = track.plate.startsWith("TS09") || track.plate.startsWith("WB");
      card.innerHTML = `
        <div class="flex items-start justify-between mb-1">
          <div class="flex items-center space-x-1.5">
            <div class="hsrp-plate ${isCommercial ? 'commercial' : ''}"><span class="ind-strip">IND</span><span>${track.plate}</span></div>
            ${track.hit ? '<span class="text-[7px] font-mono px-1 py-0.2 rounded bg-red-500/15 text-red-400 font-bold border border-red-500/25 animate-pulse">WATCHLIST</span>' : '<span class="text-[7px] font-mono px-1 py-0.2 rounded bg-emerald-500/10 text-emerald-400 font-medium">CONFIRMED</span>'}
          </div>
          <div class="text-right font-mono">
            <div class="text-[9px] font-semibold text-emerald-400">${Math.round(track.conf * 100)}%</div>
            <div class="text-[7px] text-slate-400">${track.n_frames} frames</div>
          </div>
        </div>
        <div class="flex items-center justify-between pt-1">
          <div class="text-[9px] font-mono text-slate-300">#${track.track_id} • ${track.vehicle_class || 'Vehicle'}</div>
          <button onclick="openTrajectorySearch('${track.plate}')" class="px-1.5 py-0.5 rounded bg-amber-500 hover:bg-amber-600 text-slate-900 font-mono font-bold text-[8px] flex items-center space-x-0.5 cursor-pointer">
            <span>TRACK</span><span class="material-symbols-outlined text-[10px]">arrow_forward</span>
          </button>
        </div>`;
      if (!existing) feed.appendChild(card);
      document.getElementById("fused-counter").innerText = `${feed.querySelectorAll("[id^='track-']").length} TRACKS`;
    }

    function openEvidenceModal(det) {
      document.getElementById("modal-title").innerText = `EVIDENCE: ${det.plate_raw || 'VEHICLE #' + det.track_id}`;
      document.getElementById("modal-veh-img").src = det.crop_url;
      document.getElementById("modal-plate-img").src = det.plate_url || det.crop_url;
      document.getElementById("modal-clahe-img").src = det.crop_url;
      document.getElementById("modal-meta-left").innerHTML = `
        <span>Track #${det.track_id} • <strong class="text-white">${det.vehicle_class}</strong></span>
        <span>Quality: <strong class="text-emerald-400">${det.blur || 98.4}</strong></span>
        <span>Time: <strong class="text-white">${det.video_ts.toFixed(2)}s</strong></span>`;
      lastSelectedPlate = det.plate_raw;
      document.getElementById("evidence-modal").classList.add("active");
    }
    function closeModal() { document.getElementById("evidence-modal").classList.remove("active"); }
    function inspectPlateOnMap() { if (lastSelectedPlate) window.location.href = `/#trajectory?plate=${encodeURIComponent(lastSelectedPlate)}`; }
    function openTrajectorySearch(plate) { window.location.href = `/#trajectory?plate=${encodeURIComponent(plate)}`; }
    function buildTrajectoryFromJobs() { window.location.href = lastSelectedPlate ? `/#trajectory?plate=${encodeURIComponent(lastSelectedPlate)}` : `/#trajectory`; }

    const tacticalAudio = {
      ctx: null,
      init() { if (!this.ctx) { try { this.ctx = new (window.AudioContext || window.webkitAudioContext)(); } catch(e) {} } },
      radarPing() {
        this.init(); if (!this.ctx) return;
        const osc = this.ctx.createOscillator(), gain = this.ctx.createGain();
        osc.type = "sine"; osc.frequency.setValueAtTime(880, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(440, this.ctx.currentTime + 0.15);
        gain.gain.setValueAtTime(0.1, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.15);
        osc.connect(gain); gain.connect(this.ctx.destination); osc.start(); osc.stop(this.ctx.currentTime + 0.15);
      },
      alertChirp() {
        this.init(); if (!this.ctx) return;
        const osc = this.ctx.createOscillator(), gain = this.ctx.createGain();
        osc.type = "sawtooth"; osc.frequency.setValueAtTime(987.77, this.ctx.currentTime);
        osc.frequency.setValueAtTime(1318.51, this.ctx.currentTime + 0.08);
        gain.gain.setValueAtTime(0.12, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.2);
        osc.connect(gain); gain.connect(this.ctx.destination); osc.start(); osc.stop(this.ctx.currentTime + 0.2);
      }
    };
  