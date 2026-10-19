let profile = null;


async function loadProfile() {
    const response = await fetch("/profile.json");
    profile = await response.json();

    renderFrameList();
}


function milliseconds(seconds) {
    if (seconds == null) {
        return "-";
    }

    return (seconds * 1000).toFixed(3);
}


function renderFrameList() {
    const container = document.getElementById("frames");

    container.innerHTML = "";

    profile.slow_runs.forEach((run) => {
        const button = document.createElement("button");

        const frame = run.metadata.frame ?? "?";

        button.textContent =
            `Frame ${frame} — ${milliseconds(run.duration)} ms`;

        button.addEventListener(
            "click",
            () => renderTrace(run),
        );

        container.appendChild(button);
    });
}


function renderTrace(run) {
    const title = document.getElementById("trace-title");

    title.textContent =
        `Frame ${run.metadata.frame ?? "?"} — ` +
        `${milliseconds(run.duration)} ms`;

    const container = document.getElementById("trace");

    container.innerHTML = "";

    container.appendChild(
        renderRun(run)
    );
}


function renderRun(run) {
    const details = document.createElement("details");

    details.open = run.run_type === "frame";

    const summary = document.createElement("summary");

    summary.innerHTML = `
        <span class="run-name">${run.name}</span>
        <span>${milliseconds(run.duration)} ms</span>
        <span>work ${milliseconds(run.work_duration)} ms</span>
    `;

    details.appendChild(summary);

    // Events: !
    run.events.forEach((event) => {
        details.appendChild(
            renderEvent(event)
        );
    });

    // Children
    run.children.forEach((child) => {
        details.appendChild(
            renderRun(child)
        );
    });

    // Metrics: ·
    if (Object.keys(run.metrics).length > 0) {
        details.appendChild(
            renderMetrics(run.metrics)
        );
    }

    // Metadata: @
    const metadata = Object.fromEntries(
        Object.entries(run.metadata).filter(
            ([key]) => !["frame", "completed"].includes(key)
        )
    );

    if (Object.keys(metadata).length > 0) {
        details.appendChild(
            renderMetadata(metadata)
        );
    }

    return details;
}


function renderMetadata(metadata) {
    const row = document.createElement("div");

    row.className = "trace-extra metadata";

    const values = Object.entries(metadata)
        .map(([key, value]) => `${key}=${value}`)
        .join(" ");

    row.textContent = `@ ${values}`;

    return row;
}


function renderMetrics(metrics) {
    const row = document.createElement("div");

    row.className = "trace-extra metrics";

    const values = Object.entries(metrics)
        .map(([key, value]) => `${key}=${value}`)
        .join(" ");

    row.textContent = `· ${values}`;

    return row;
}


function renderEvent(event) {
    const row = document.createElement("div");

    row.className = "trace-extra event";

    const metadata = Object.entries(event.metadata ?? {})
        .map(([key, value]) => `${key}=${value}`)
        .join(" ");

    const duration = milliseconds(event.duration);

    row.textContent =
        `! ${event.name}` +
        (metadata ? ` ${metadata}` : "") +
        ` — ${duration} ms`;

    return row;
}


function renderObject(title, value) {
    const container = document.createElement("div");

    container.className = "properties";

    const heading = document.createElement("strong");
    heading.textContent = title;

    container.appendChild(heading);

    const list = document.createElement("dl");

    Object.entries(value).forEach(([key, item]) => {
        const dt = document.createElement("dt");
        const dd = document.createElement("dd");

        dt.textContent = key;
        dd.textContent = item;

        list.appendChild(dt);
        list.appendChild(dd);
    });

    container.appendChild(list);

    return container;
}


loadProfile();