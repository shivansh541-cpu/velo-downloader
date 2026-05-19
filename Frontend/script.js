// ══════════════════════════════════════════════════
//  CONFIG - Backend URL
// ══════════════════════════════════════════════════
const BACKEND_URL = "https://velo-downloader.onrender.com";
// Jab deploy karo tab yeh change karo:
// const BACKEND_URL = "https://your-app.onrender.com";


// ══════════════════════════════════════════════════
//  UI HELPERS
// ══════════════════════════════════════════════════

function showLoading(show) {
    const el = document.getElementById("loadingSection");
    show ? el.classList.remove("hidden") : el.classList.add("hidden");
}

function showError(msg) {
    const sec = document.getElementById("errorSection");
    const msgEl = document.getElementById("errorMessage");
    msgEl.textContent = msg;
    sec.classList.remove("hidden");
    setTimeout(() => sec.classList.add("hidden"), 6000);
}

function hideError() {
    document.getElementById("errorSection").classList.add("hidden");
}

function hideResults() {
    document.getElementById("resultsSection").classList.add("hidden");
    document.getElementById("videoFormats").innerHTML = "";
    document.getElementById("audioFormats").innerHTML = "";
    document.getElementById("musicSection").classList.add("hidden");
    document.getElementById("videoSection").classList.remove("hidden");
}

function setButtonLoading(loading) {
    const btn = document.getElementById("downloadBtn");
    if (loading) {
        btn.innerHTML = `<div class="btn-spinner"></div> Fetching...`;
        btn.disabled = true;
        btn.style.opacity = "0.7";
    } else {
        btn.innerHTML = `
            <svg width="9" height="9" viewBox="0 0 12 12" fill="none">
                <path d="M6 1v7M3 5.5l3 3 3-3M1 10h10" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Downloader`;
        btn.disabled = false;
        btn.style.opacity = "1";
    }
}


// ══════════════════════════════════════════════════
//  BUILD FORMAT ROW
// ══════════════════════════════════════════════════

function buildFormatRow(fmt, url) {
    const isVideo = fmt.format === "MP4";
    const quality = fmt.quality || "";
    const size = fmt.size_mb ? `${fmt.size_mb} MB` : "";
    const formatType = isVideo ? "mp4" : "mp3";
    const qualityParam = quality.replace("p", "");

    return `
    <div class="format-row flex items-center justify-between gap-2 py-1">
        <span class="format-badge text-white font-normal text-center flex-shrink-0"
              style="background:#D4920A; font-size:7px; padding:3px 8px; border-radius:4px; min-width:32px;">
            ${fmt.format}
        </span>
        <div class="flex-1 flex items-center gap-2">
            <span class="text-black font-medium" style="font-size:10px;">${quality}</span>
            <span style="font-size:9px; color:rgba(0,0,0,0.5);">${size}</span>
        </div>
        <button
            onclick="startDownload('${encodeURIComponent(url)}', '${formatType}', '${qualityParam}', this)"
            class="download-btn text-white font-normal transition-all duration-150 flex-shrink-0"
            style="background:#7B7FC4; font-size:7px; padding:4px 10px; border-radius:5px; border:none; cursor:pointer;"
        >
            Download
        </button>
    </div>`;
}


// ══════════════════════════════════════════════════
//  FETCH VIDEO INFO
// ══════════════════════════════════════════════════

async function fetchVideoInfo() {
    const urlInput = document.getElementById("videoUrl");
    const url = urlInput.value.trim();

    if (!url) {
        showError("Please paste a video URL first.");
        urlInput.focus();
        return;
    }

    if (!url.startsWith("http://") && !url.startsWith("https://")) {
        showError("Please enter a valid URL starting with http:// or https://");
        return;
    }

    hideError();
    hideResults();
    showLoading(true);
    setButtonLoading(true);

    try {
        const res = await fetch(`${BACKEND_URL}/api/info`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        });

        if (!res.ok) {
            throw new Error(`Server error: ${res.status}`);
        }

        const data = await res.json();

        showLoading(false);
        setButtonLoading(false);

        if (data.error) {
            showError("Error: " + data.error);
            return;
        }

        // Set title
        const titleEl = document.getElementById("videoTitle");
        titleEl.textContent = data.title || "Video";

        // Set thumbnail
        if (data.thumbnail) {
            const thumb = document.getElementById("videoThumb");
            thumb.src = data.thumbnail;
            thumb.style.display = "block";
        }

        // Build video formats
        const videoContainer = document.getElementById("videoFormats");
        if (data.video_formats && data.video_formats.length > 0) {
            data.video_formats.forEach(fmt => {
                videoContainer.innerHTML += buildFormatRow(fmt, url);
            });
        } else {
            document.getElementById("videoSection").innerHTML = `
                <p style="font-size:9px; color:rgba(0,0,0,0.4); text-align:center; padding:8px 0;">
                    No video formats available.
                </p>`;
        }

        // Build audio formats
        const audioContainer = document.getElementById("audioFormats");
        if (data.audio_formats && data.audio_formats.length > 0) {
            document.getElementById("musicSection").classList.remove("hidden");
            data.audio_formats.forEach(fmt => {
                audioContainer.innerHTML += buildFormatRow(fmt, url);
            });
        }

        // Show results
        const resultsSection = document.getElementById("resultsSection");
        resultsSection.classList.remove("hidden");

        // Smooth scroll to results
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
        }, 100);

    } catch (err) {
        showLoading(false);
        setButtonLoading(false);
        if (err.message.includes("Failed to fetch")) {
            showError("Server se connect nahi ho saka. Backend chal raha hai?");
        } else {
            showError("Something went wrong: " + err.message);
        }
    }
}


// ══════════════════════════════════════════════════
//  START DOWNLOAD
// ══════════════════════════════════════════════════

async function startDownload(encodedUrl, formatType, quality, btn) {
    const url = decodeURIComponent(encodedUrl);

    // Button loading state
    const originalText = btn.textContent;
    btn.textContent = "...";
    btn.disabled = true;
    btn.style.opacity = "0.6";

    try {
        const downloadUrl = `${BACKEND_URL}/api/download?url=${encodeURIComponent(url)}&format=${formatType}&quality=${quality}`;

        const response = await fetch(downloadUrl);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || "Download failed");
        }

        // Get filename from header
        const disposition = response.headers.get("Content-Disposition");
        let filename = `velo_download.${formatType}`;
        if (disposition && disposition.includes("filename=")) {
            filename = disposition.split("filename=")[1].replace(/"/g, "").trim();
        }

        // Create blob and trigger download
        const blob = await response.blob();
        const blobUrl = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = blobUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(blobUrl);

        btn.textContent = "Done ✓";
        btn.style.background = "#22c55e";
        btn.style.opacity = "1";

        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = "#7B7FC4";
            btn.disabled = false;
        }, 3000);

    } catch (err) {
        btn.textContent = originalText;
        btn.disabled = false;
        btn.style.opacity = "1";
        showError("Download error: " + err.message);
    }
}


// ══════════════════════════════════════════════════
//  EVENT LISTENERS
// ══════════════════════════════════════════════════

document.addEventListener("DOMContentLoaded", () => {
    // Enter key support
    document.getElementById("videoUrl").addEventListener("keydown", (e) => {
        if (e.key === "Enter") fetchVideoInfo();
    });

    // Paste event - auto fetch
    document.getElementById("videoUrl").addEventListener("paste", () => {
        setTimeout(() => {
            const val = document.getElementById("videoUrl").value.trim();
            if (val.startsWith("http")) {
                fetchVideoInfo();
            }
        }, 100);
    });
});