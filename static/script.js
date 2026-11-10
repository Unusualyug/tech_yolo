/* =========================================================
   TRINEXIS FRONTEND
   ========================================================= */

"use strict";


/* =========================================================
   GLOBAL STATE
   ========================================================= */

let pollingTimer = null;

let alertObjects = new Set();

let lastSpeechPreview = "";

let toastTimer = null;


/* =========================================================
   DOM HELPER
   ========================================================= */

function $(id) {

    return document.getElementById(id);

}


/* =========================================================
   ESCAPE HTML
   ========================================================= */

function escapeHtml(value) {

    return String(value ?? "")

        .replaceAll("&", "&amp;")

        .replaceAll("<", "&lt;")

        .replaceAll(">", "&gt;")

        .replaceAll('"', "&quot;")

        .replaceAll("'", "&#039;");

}


/* =========================================================
   TOAST
   ========================================================= */

function showToast(
    message,
    type = "success"
) {

    const toast =
        $("toast");

    const text =
        $("toast-msg");

    if (!toast || !text) {

        return;

    }


    text.textContent =
        message;


    const icon =
        toast.querySelector("i");


    if (icon) {

        if (type === "error") {

            icon.className =
                "fa-solid fa-xmark";

        } else if (type === "warning") {

            icon.className =
                "fa-solid fa-triangle-exclamation";

        } else {

            icon.className =
                "fa-solid fa-check";

        }

    }


    toast.classList.add(
        "show"
    );


    clearTimeout(
        toastTimer
    );


    toastTimer =
        setTimeout(
            () => {

                toast.classList.remove(
                    "show"
                );

            },
            2500
        );

}


/* =========================================================
   POST HELPER
   ========================================================= */

async function post(
    url,
    body = {}
) {

    const response =
        await fetch(
            url,
            {

                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json"

                },

                body:
                    JSON.stringify(
                        body
                    )

            }
        );


    if (!response.ok) {

        throw new Error(
            `HTTP ${response.status}`
        );

    }


    return response.json();

}


/* =========================================================
   DETECTION
   ========================================================= */

async function startDet() {

    try {

        await post(
            "/start_detection"
        );


        setSystemState(
            true
        );


        startPolling();


        showToast(
            "Detection engine started"
        );

    } catch (error) {

        console.error(error);

        showToast(
            "Unable to start detection",
            "error"
        );

    }

}


async function stopDet() {

    try {

        await post(
            "/stop_detection"
        );


        setSystemState(
            false
        );


        stopPolling();


        showToast(
            "Detection paused",
            "warning"
        );

    } catch (error) {

        console.error(error);

        showToast(
            "Unable to stop detection",
            "error"
        );

    }

}


/* =========================================================
   SYSTEM STATUS
   ========================================================= */

function setSystemState(
    active
) {

    const status =
        $("status-chip");


    if (!status) {

        return;

    }


    status.classList.toggle(
        "active",
        active
    );


    $("status-text").textContent =
        active
            ? "DETECTING"
            : "STANDBY";


    $("stage-state").textContent =
        active
            ? "DETECTING"
            : "STANDBY";

}


/* =========================================================
   MODEL
   ========================================================= */

async function setModel() {

    const select =
        $("sel-model");


    if (!select) {

        return;

    }


    const model =
        select.value;


    showToast(
        "Loading model...",
        "warning"
    );


    try {

        const data =
            await post(
                "/set_model",
                {
                    model
                }
            );


        if (
            data.status &&
            data.status !==
                "success"
        ) {

            throw new Error(
                data.message ||
                "Model failed"
            );

        }


        $("model-name")
            .textContent =
            model.replace(
                ".pt",
                ""
            );


        showToast(
            "Model loaded"
        );


    } catch (error) {

        console.error(error);

        showToast(
            "Model could not be loaded",
            "error"
        );

    }

}


/* =========================================================
   LANGUAGE
   ========================================================= */

async function setLang() {

    const select =
        $("sel-lang");


    if (!select) {

        return;

    }


    const language =
        select.value;


    try {

        await post(
            "/set_language",
            {
                language
            }
        );


        showToast(
            `Language: ${language}`
        );


    } catch (error) {

        console.error(error);

        showToast(
            "Language update failed",
            "error"
        );

    }

}


/* =========================================================
   CONFIDENCE
   ========================================================= */

async function setConf() {

    const value =
        $("sel-conf").value;


    try {

        await post(
            "/set_confidence",
            {
                threshold:
                    value
            }
        );


        showToast(
            `Confidence: ${
                Math.round(
                    Number(value) * 100
                )
            }%`
        );


    } catch (error) {

        console.error(error);

        showToast(
            "Confidence update failed",
            "error"
        );

    }

}


/* =========================================================
   INTERVAL
   ========================================================= */

async function setInt() {

    const value =
        $("sel-int").value;


    try {

        await post(
            "/set_interval",
            {
                interval:
                    value
            }
        );


        showToast(
            `Interval: ${value}s`
        );


    } catch (error) {

        console.error(error);

        showToast(
            "Interval update failed",
            "error"
        );

    }

}


/* =========================================================
   RESOLUTION
   ========================================================= */

async function setRes() {

    const value =
        $("sel-res").value;


    const width =
        Number(value);


    const height =
        Math.round(
            width * 9 / 16
        );


    $("camera-meta")
        .textContent =
        `${width} × ${height}`;


    try {

        await post(
            "/set_resolution",
            {
                resolution:
                    value
            }
        );


        showToast(
            `Resolution: ${value}px`
        );


    } catch (error) {

        console.error(error);

        showToast(
            "Resolution update failed",
            "error"
        );

    }

}


/* =========================================================
   SPEECH
   ========================================================= */

async function toggleSpeech() {

    try {

        const data =
            await post(
                "/toggle_speech"
            );


        updateSpeechUI(
            Boolean(
                data.speech_enabled
            )
        );


        showToast(
            data.speech_enabled
                ? "Voice enabled"
                : "Voice muted"
        );


    } catch (error) {

        console.error(error);

        showToast(
            "Voice update failed",
            "error"
        );

    }

}


function updateSpeechUI(
    enabled
) {

    const toggle =
        $("tgl-speech");


    if (toggle) {

        toggle.classList.toggle(
            "active",
            enabled
        );

    }


    if ($("voice-toggle-label")) {

        $("voice-toggle-label")
            .textContent =
            enabled
                ? "Enabled"
                : "Muted";

    }


    if ($("voice-state")) {

        $("voice-state")
            .textContent =
            enabled
                ? "ON"
                : "OFF";

    }

}


/* =========================================================
   PANEL SWITCHING
   ========================================================= */

function switchPanel(
    panelName,
    button
) {

    document
        .querySelectorAll(
            ".tab"
        )
        .forEach(
            tab => {

                tab.classList.remove(
                    "active"
                );

            }
        );


    document
        .querySelectorAll(
            ".panel"
        )
        .forEach(
            panel => {

                panel.classList.remove(
                    "active"
                );

            }
        );


    button.classList.add(
        "active"
    );


    const panel =
        $(`panel-${panelName}`);


    if (panel) {

        panel.classList.add(
            "active"
        );

    }

}


/* =========================================================
   POLLING
   ========================================================= */

function startPolling() {

    if (pollingTimer) {

        return;

    }


    fetchData();


    pollingTimer =
        setInterval(
            fetchData,
            1200
        );

}


function stopPolling() {

    if (!pollingTimer) {

        return;

    }


    clearInterval(
        pollingTimer
    );


    pollingTimer =
        null;

}


/* =========================================================
   GET DATA
   ========================================================= */

async function fetchData() {

    try {

        const response =
            await fetch(
                "/get_logs"
            );


        if (!response.ok) {

            throw new Error(
                "Failed to fetch"
            );

        }


        const data =
            await response.json();


        const stats =
            data.stats ||
            {};


        updateHeader(
            stats
        );


        updateMetrics(
            stats
        );


        updateScene(
            data.logs ||
            []
        );


        updateTimeline(
            stats.detection_timeline ||
            []
        );


        updateFrequency(
            stats.object_frequency ||
            {}
        );


        updateLogs(
            data.logs ||
            []
        );


        updateSpeechUI(
            Boolean(
                stats.speech_enabled
            )
        );


        if (
            stats.language &&
            $("sel-lang")
        ) {

            $("sel-lang").value =
                stats.language;

        }


    } catch (error) {

        console.debug(
            "Polling:",
            error.message
        );

    }

}


/* =========================================================
   HEADER
   ========================================================= */

function updateHeader(
    stats
) {

    if ($("fps-val")) {

        $("fps-val")
            .textContent =
            `${stats.fps || 0} FPS`;

    }


    if ($("stage-fps")) {

        $("stage-fps")
            .textContent =
            `${stats.fps || 0} FPS`;

    }


    if ($("stage-classes")) {

        $("stage-classes")
            .textContent =
            `${stats.vocabulary_size || 0} CLASSES`;

    }


    if ($("uptime")) {

        $("uptime")
            .textContent =
            stats.uptime ||
            "00:00:00";

    }


    if ($("model-name")) {

        $("model-name")
            .textContent =
            (
                stats.model_name ||
                "yolov8s-worldv2"
            ).replace(
                ".pt",
                ""
            );

    }

}


/* =========================================================
   METRICS
   ========================================================= */

function updateMetrics(
    stats
) {

    $("b-total").textContent =
        stats.total_detections ||
        0;


    $("b-unique").textContent =
        stats.unique_objects ||
        0;


    $("b-conf").textContent =
        `${Math.round(
            (
                stats.avg_confidence ||
                0
            ) * 100
        )}%`;


    $("b-last").textContent =
        stats.last_detection_time ||
        "—";


    $("s-total").textContent =
        stats.total_detections ||
        0;


    $("s-unique").textContent =
        stats.unique_objects ||
        0;


    $("s-frames").textContent =
        stats.frames_processed ||
        0;


    $("s-conf").textContent =
        `${Math.round(
            (
                stats.avg_confidence ||
                0
            ) * 100
        )}%`;

}


/* =========================================================
   SCENE
   ========================================================= */

function updateScene(
    logs
) {

    if (
        !logs ||
        !logs.length
    ) {

        $("scene-summary")
            .textContent =
            "No active detections";


        $("scene-sub")
            .textContent =
            "Start detection to analyze the environment.";


        return;

    }


    const last =
        logs[logs.length - 1];


    const objects =
        last.objects ||
        [];


    if (!objects.length) {

        $("scene-summary")
            .textContent =
            "No active detections";

        return;

    }


    const counts =
        {};


    objects.forEach(
        object => {

            const name =
                object.name ||
                "Unknown";


            counts[name] =
                (
                    counts[name] ||
                    0
                ) + 1;

        }
    );


    const summary =
        Object
            .entries(
                counts
            )
            .slice(
                0,
                4
            )
            .map(
                ([name, count]) =>
                    `${count} ${name}`
            )
            .join(
                " · "
            );


    const nearest =
        [...objects]
            .sort(
                (a, b) =>
                    (
                        a.distance ||
                        999999
                    ) -
                    (
                        b.distance ||
                        999999
                    )
            )[0];


    $("scene-summary")
        .textContent =
        summary;


    if (nearest) {

        $("scene-sub")
            .textContent =
            `Nearest: ${
                nearest.name
            } · ${
                Math.round(
                    nearest.distance ||
                    0
                )
            } cm · ${
                Math.round(
                    (
                        nearest.confidence ||
                        0
                    ) * 100
                )
            }% confidence`;


        const preview =
            `Scene: ${summary}. ` +
            `Nearest: ${
                nearest.name
            }, ${
                Math.round(
                    nearest.distance ||
                    0
                )
            } cm.`;


        if (
            preview !==
            lastSpeechPreview
        ) {

            lastSpeechPreview =
                preview;


            $("speech-preview")
                .textContent =
                preview;

        }

    }

}


/* =========================================================
   TIMELINE
   ========================================================= */

function updateTimeline(
    timeline
) {

    const chart =
        $("timeline-chart");


    if (
        !chart ||
        !timeline.length
    ) {

        if (chart) {

            chart.innerHTML =
                "";

        }

        return;

    }


    const max =
        Math.max(
            ...timeline.map(
                item =>
                    Number(
                        item.count
                    ) || 0
            ),
            1
        );


    chart.innerHTML =
        timeline
            .map(
                item => {

                    const count =
                        Number(
                            item.count
                        ) || 0;


                    const height =
                        Math.max(
                            5,
                            (
                                count /
                                max
                            ) * 100
                        );


                    return `

                        <div
                            class="mini-bar"
                            style="
                                height:${height}%;
                            "
                            title="${escapeHtml(
                                item.time ||
                                ""
                            )}: ${count}"
                        ></div>

                    `;

                }
            )
            .join("");

}


/* =========================================================
   FREQUENCY
   ========================================================= */

function updateFrequency(
    frequency
) {

    const element =
        $("freq-list");


    if (!element) {

        return;

    }


    const entries =
        Object.entries(
            frequency ||
            {}
        )
        .slice(
            0,
            6
        );


    if (!entries.length) {

        element.innerHTML =
            `
                <div class="empty-state">
                    Waiting for detection data
                </div>
            `;

        return;

    }


    const max =
        Math.max(
            ...entries.map(
                item =>
                    Number(
                        item[1]
                    ) || 0
            ),
            1
        );


    element.innerHTML =
        entries
            .map(
                ([name, count]) => {

                    const percentage =
                        (
                            (
                                Number(count) ||
                                0
                            ) /
                            max
                        ) * 100;


                    return `

                        <div class="freq-item">

                            <span
                                class="freq-name"
                                title="${escapeHtml(name)}"
                            >
                                ${escapeHtml(name)}
                            </span>


                            <div class="freq-bar">

                                <div
                                    class="freq-fill"
                                    style="
                                        width:${percentage}%;
                                    "
                                ></div>

                            </div>


                            <span class="freq-count">
                                ${count}
                            </span>

                        </div>

                    `;

                }
            )
            .join("");

}


/* =========================================================
   LOGS
   ========================================================= */

function updateLogs(
    logs
) {

    const element =
        $("log-list");


    if (!element) {

        return;

    }


    if (
        !logs ||
        !logs.length
    ) {

        element.innerHTML =
            `
                <div class="empty-state">
                    No events recorded yet.
                </div>
            `;

        return;

    }


    element.innerHTML =
        logs
            .slice(
                -25
            )
            .reverse()
            .map(
                entry => {

                    const objects =
                        entry.objects ||
                        [];


                    return `

                        <div class="log-entry">

                            <div class="log-meta">

                                <span class="log-time">
                                    ${escapeHtml(
                                        entry.timestamp ||
                                        ""
                                    )}
                                </span>

                                <span class="log-count">
                                    ${
                                        entry.total_in_frame ||
                                        objects.length ||
                                        0
                                    }
                                    objects
                                </span>

                            </div>


                            <div class="log-tags">

                                ${
                                    objects
                                        .map(
                                            object => `

                                                <span class="tag">

                                                    ${
                                                        escapeHtml(
                                                            object.name ||
                                                            "Unknown"
                                                        )
                                                    }

                                                    <span class="dist">

                                                        ${
                                                            Math.round(
                                                                object.distance ||
                                                                0
                                                            )
                                                        }cm

                                                    </span>

                                                </span>

                                            `
                                        )
                                        .join("")
                                }

                            </div>

                        </div>

                    `;

                }
            )
            .join("");

}


/* =========================================================
   LANGUAGES
   ========================================================= */

async function loadLanguages() {

    try {

        const response =
            await fetch(
                "/get_languages"
            );


        if (!response.ok) {

            throw new Error(
                "Language request failed"
            );

        }


        const data =
            await response.json();


        const select =
            $("sel-lang");


        select.innerHTML =
            "";


        function addGroup(
            label,
            languages
        ) {

            if (
                !languages ||
                !languages.length
            ) {

                return;

            }


            const group =
                document.createElement(
                    "optgroup"
                );


            group.label =
                label;


            languages.forEach(
                language => {

                    const option =
                        document.createElement(
                            "option"
                        );


                    option.value =
                        language;


                    option.textContent =
                        language;


                    group.appendChild(
                        option
                    );

                }
            );


            select.appendChild(
                group
            );

        }


        addGroup(
            "Indian Languages",
            data.indian ||
            []
        );


        addGroup(
            "International Languages",
            data.international ||
            []
        );


        select.value =
            data.current ||
            "English";


    } catch (error) {

        console.error(
            error
        );


        $("sel-lang").innerHTML =
            `
                <option value="English">
                    English
                </option>
            `;

    }

}


/* =========================================================
   CLASSES
   ========================================================= */

async function loadClasses() {

    try {

        const response =
            await fetch(
                "/get_classes"
            );


        if (!response.ok) {

            throw new Error(
                "Class request failed"
            );

        }


        const data =
            await response.json();


        const container =
            $("alert-tags");


        container.innerHTML =
            "";


        (
            data.classes ||
            []
        ).forEach(
            name => {

                const button =
                    document.createElement(
                        "button"
                    );


                button.className =
                    "alert-tag";


                button.textContent =
                    name;


                if (
                    alertObjects.has(
                        name
                    )
                ) {

                    button.classList.add(
                        "active"
                    );

                }


                button.onclick =
                    () => {

                        toggleAlert(
                            name,
                            button
                        );

                    };


                container.appendChild(
                    button
                );

            }
        );


    } catch (error) {

        console.error(
            error
        );


        $("alert-tags").innerHTML =
            `
                <span class="empty-inline">
                    Unable to load classes
                </span>
            `;

    }

}


/* =========================================================
   ALERT TOGGLE
   ========================================================= */

async function toggleAlert(
    name,
    button
) {

    if (
        alertObjects.has(
            name
        )
    ) {

        alertObjects.delete(
            name
        );


        button.classList.remove(
            "active"
        );

    } else {

        alertObjects.add(
            name
        );


        button.classList.add(
            "active"
        );

    }


    try {

        await post(
            "/set_alerts",
            {
                objects:
                    [...alertObjects]
            }
        );

    } catch (error) {

        console.error(
            error
        );

        showToast(
            "Alert update failed",
            "error"
        );

    }

}


/* =========================================================
   SNAPSHOT
   ========================================================= */

function snapshot() {

    window.open(
        "/snapshot",
        "_blank"
    );


    showToast(
        "Snapshot captured"
    );

}


/* =========================================================
   HEATMAP
   ========================================================= */

function showHeatmap() {

    const image =
        $("heatmap-img");


    image.src =
        `/heatmap?t=${Date.now()}`;


    $("modal")
        .classList
        .add("show");

}


function hideHeatmap() {

    $("modal")
        .classList
        .remove("show");

}


function closeModal(
    event
) {

    if (
        event.target ===
        event.currentTarget
    ) {

        hideHeatmap();

    }

}


/* =========================================================
   FULLSCREEN
   ========================================================= */

function goFull() {

    const element =
        $("vid-frame");


    if (
        !document.fullscreenElement
    ) {

        if (
            element.requestFullscreen
        ) {

            element
                .requestFullscreen()
                .catch(
                    console.error
                );

        }

    } else {

        document
            .exitFullscreen()
            .catch(
                console.error
            );

    }

}


/* =========================================================
   EXPORT
   ========================================================= */

function exportLogs() {

    window.open(
        "/export_logs",
        "_blank"
    );


    showToast(
        "Logs exported"
    );

}


/* =========================================================
   CLEAR LOGS
   ========================================================= */

async function clearLogs() {

    try {

        await post(
            "/clear_logs"
        );


        await fetchData();


        showToast(
            "Session cleared"
        );


    } catch (error) {

        console.error(
            error
        );


        showToast(
            "Unable to clear logs",
            "error"
        );

    }

}


/* =========================================================
   KEYBOARD
   ========================================================= */

document.addEventListener(
    "keydown",
    event => {

        if (
            event.key ===
            "Escape"
        ) {

            hideHeatmap();

        }


        if (
            event.key.toLowerCase() ===
            "h"
        ) {

            showHeatmap();

        }


        if (
            event.key.toLowerCase() ===
            "f"
        ) {

            goFull();

        }


        if (
            event.ctrlKey &&
            event.key.toLowerCase() ===
            "s"
        ) {

            event.preventDefault();

            snapshot();

        }

    }
);


/* =========================================================
   INITIALIZATION
   ========================================================= */

async function init() {

    console.log(
        "%cTRINEXIS",
        "font-size:22px;font-weight:bold;"
    );


    await loadLanguages();


    await loadClasses();


    await fetchData();


    startPolling();

}


/* =========================================================
   START
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    init
);