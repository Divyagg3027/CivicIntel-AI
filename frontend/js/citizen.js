/**
 * Citizen Request Submission & Voice Input Logic
 * CivicIntel AI
 */

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("citizenRequestForm");
    const textarea = document.getElementById("requestText");
    const locationInput = document.getElementById("requestLocation");
    const voiceBtn = document.getElementById("voiceInputBtn");
    const voiceStatus = document.getElementById("voiceStatus");
    const submitBtn = document.getElementById("submitBtn");
    const resultCard = document.getElementById("resultCard");
    const alertBox = document.getElementById("formAlert");

    // Location Chip Clicks
    document.querySelectorAll(".chip[data-loc]").forEach(chip => {
        chip.addEventListener("click", () => {
            locationInput.value = chip.getAttribute("data-loc");
            locationInput.focus();
        });
    });

    // Voice Input Implementation using Web Speech API
    let recognition = null;
    let isRecording = false;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = "en-IN"; // Supports Tamil/Indian English speech

        recognition.onstart = () => {
            isRecording = true;
            voiceBtn.classList.add("recording");
            if (voiceStatus) {
                voiceStatus.textContent = "🎙️ Listening... Speak your civic issue in English, Tamil, or Hindi.";
                voiceStatus.style.display = "block";
            }
        };

        recognition.onresult = (event) => {
            let transcript = "";
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }
            if (transcript) {
                textarea.value = (textarea.value ? textarea.value + " " : "") + transcript;
            }
        };

        recognition.onerror = (event) => {
            console.warn("Speech recognition error:", event.error);
            isRecording = false;
            voiceBtn.classList.remove("recording");
            if (voiceStatus) {
                voiceStatus.textContent = `Speech recognition notification: ${event.error}. You can also type your message directly.`;
            }
        };

        recognition.onend = () => {
            isRecording = false;
            voiceBtn.classList.remove("recording");
            if (voiceStatus) {
                setTimeout(() => { voiceStatus.style.display = "none"; }, 3000);
            }
        };

        voiceBtn.addEventListener("click", () => {
            if (isRecording) {
                recognition.stop();
            } else {
                try {
                    recognition.start();
                } catch (e) {
                    console.error("Speech recognition start failed:", e);
                }
            }
        });
    } else {
        voiceBtn.title = "Voice recognition is not supported in this browser version. Please type your request.";
        voiceBtn.addEventListener("click", () => {
            showAlert("Voice speech-to-text is not supported by your current browser. Please type your request into the text box.", "warning");
        });
    }

    // Form Submission
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        hideAlert();

        const text = textarea.value.trim();
        const loc = locationInput.value.trim();

        if (text.length < 3) {
            showAlert("Please enter a detailed description of the civic problem (at least 3 characters).", "error");
            return;
        }

        if (loc.length < 2) {
            showAlert("Please specify the city, town, or village location.", "error");
            return;
        }

        submitBtn.disabled = true;
        submitBtn.innerHTML = "<span>Analyzing & Structuring Intelligence...</span>";

        try {
            const response = await CivicIntelAPI.submitRequest(text, loc);
            const req = response.request;

            // Populate structured breakdown
            document.getElementById("resCategory").textContent = req.category || "Unassigned";
            
            const sevEl = document.getElementById("resSeverity");
            sevEl.textContent = req.severity || "Low";
            sevEl.className = `badge badge-${(req.severity || 'low').toLowerCase()}`;

            document.getElementById("resPeople").textContent = req.affected_people ? `${req.affected_people.toLocaleString()} residents` : "Not specified";
            document.getElementById("resLanguage").textContent = req.language || "English";
            document.getElementById("resNeed").textContent = req.detected_need || "General Civic Support";
            document.getElementById("resStatus").textContent = req.status || "Analyzed";
            document.getElementById("resLocation").textContent = req.location;

            resultCard.classList.add("visible");
            showAlert("✅ Request successfully registered and transformed into structured intelligence!", "success");

            // Scroll to result
            resultCard.scrollIntoView({ behavior: "smooth" });

        } catch (err) {
            console.error("Submission failed:", err);
            showAlert(`Failed to submit request: ${err.message}. Ensure CivicIntel AI backend is running.`, "error");
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = "Submit Request";
        }
    });

    function showAlert(msg, type = "info") {
        if (!alertBox) return;
        alertBox.textContent = msg;
        alertBox.className = `alert-box alert-${type}`;
        alertBox.style.display = "flex";
    }

    function hideAlert() {
        if (!alertBox) return;
        alertBox.style.display = "none";
    }
});
