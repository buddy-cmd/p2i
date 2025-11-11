// Backend endpoint — update if your Render URL changes
const API_ENDPOINT = "https://p2i.onrender.com/generate";

const form = document.getElementById("gen-form");
const statusEl = document.getElementById("status");
const progressEl = document.getElementById("progress");
const galleryEl = document.getElementById("gallery");
const generateBtn = document.getElementById("generate-btn");
const clearBtn = document.getElementById("clear-btn");
const downloadAllBtn = document.getElementById("download-all");

function setBusy(isBusy, message = "") {
  statusEl.textContent = message;
  progressEl.hidden = !isBusy;
  generateBtn.disabled = isBusy;
}

function renderImages(urls) {
  if (!urls || !urls.length) return;

  // Enable batch download
  downloadAllBtn.disabled = false;
  downloadAllBtn.onclick = () => downloadZip(urls);

  urls.forEach((url, idx) => {
    const card = document.createElement("div");
    card.className = "card";

    const img = document.createElement("img");
    img.alt = `Generated ${idx + 1}`;
    img.src = url;
    img.onload = () => img.classList.add("loaded");

    const meta = document.createElement("div");
    meta.className = "meta";

    const small = document.createElement("div");
    small.textContent = "Generated";

    const actions = document.createElement("div");
    actions.className = "actions";

    const copyBtn = document.createElement("button");
    copyBtn.className = "btn btn-ghost";
    copyBtn.textContent = "Copy URL";
    copyBtn.onclick = async () => {
      try {
        await navigator.clipboard.writeText(url);
        statusEl.textContent = "Copied image URL to clipboard";
      } catch {
        statusEl.textContent = "Copy failed";
      }
    };

    const dlBtn = document.createElement("button");
    dlBtn.className = "btn btn-ghost";
    dlBtn.textContent = "Download";
    dlBtn.onclick = () => downloadImage(url);

    actions.appendChild(copyBtn);
    actions.appendChild(dlBtn);

    meta.appendChild(small);
    meta.appendChild(actions);

    card.appendChild(img);
    card.appendChild(meta);
    galleryEl.prepend(card); // newest first
  });
}

async function downloadImage(url) {
  try {
    const res = await fetch(url);
    const blob = await res.blob();
    const a = document.createElement("a");
    const objectUrl = URL.createObjectURL(blob);
    a.href = objectUrl;
    a.download = "p2i-image.png";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(objectUrl);
  } catch (e) {
    statusEl.textContent = "Download failed";
  }
}

async function downloadZip(urls) {
  // Lightweight batch: prompt user to save individually
  // For full ZIP, integrate JSZip later if needed (keeps bundle small for now)
  statusEl.textContent = "Tip: Download buttons on each image save files individually.";
}

clearBtn.onclick = () => {
  galleryEl.innerHTML = "";
  downloadAllBtn.disabled = true;
  statusEl.textContent = "Gallery cleared";
};

// Form submit handler
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const prompt = document.getElementById("prompt").value.trim();
  const model = document.getElementById("model").value;
  const aspect = document.getElementById("aspect").value;
  const outputs = parseInt(document.getElementById("outputs").value, 10);
  const imageFile = document.getElementById("image").files[0];

  if (!prompt) {
    statusEl.textContent = "Please enter a prompt.";
    return;
  }

  // Build FormData for optional img2img
  const formData = new FormData();
  formData.append("prompt", prompt);
  formData.append("model", model);
  formData.append("aspect_ratio", aspect);
  formData.append("outputs", outputs);
  if (imageFile) formData.append("image", imageFile, imageFile.name);

  setBusy(true, "Sending request to generator…");
  try {
    const res = await fetch(API_ENDPOINT, {
      method: "POST",
      body: formData
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || `HTTP ${res.status}`);
    }

    const data = await res.json();
    const urls = data?.images || [];

    if (urls.length === 0) {
      setBusy(false, "No images returned. Try a simpler prompt or fewer outputs.");
      return;
    }

    setBusy(false, `Generated ${urls.length} image${urls.length > 1 ? "s" : ""}`);
    renderImages(urls);
  } catch (err) {
    console.error(err);
    setBusy(false, "Generation failed. Please retry after a moment.");
  }
});
