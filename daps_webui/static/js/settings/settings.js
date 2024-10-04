document.addEventListener("DOMContentLoaded", function() {
    attachNewInstance("radarr");
    attachNewInstance("sonarr");
    attachNewInstance("plex");
    attachPosterRenamer();
});

window.addEventListener("DOMContentLoaded", () => {
    fetch("/get-settings")
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                preFillForm(data.settings);
                console.log(data.settings);
            } else {
                console.error("Error fetching settings: " + data.message);
            }
        })
        .catch((error) => {
            console.error("Error", error);
        });
});

function createInstanceFromSettings(data, settingsVar, htmlVar) {
    for (let i = 1; i < data[settingsVar].length; i++) {
        attachNewInstance(htmlVar);
    }
    const instanceInputs = document.querySelectorAll(
        `input[name="${htmlVar}_instance[]"]`,
    );
    const urlInputs = document.querySelectorAll(`input[name="${htmlVar}_url[]"]`);
    const apiInputs = document.querySelectorAll(`input[name="${htmlVar}_api[]"]`);

    instanceInputs.forEach((input, index) => {
        input.value = data[settingsVar][index]?.instanceName || "";
    });
    urlInputs.forEach((input, index) => {
        input.value = data[settingsVar][index]?.url || "";
    });
    apiInputs.forEach((input, index) => {
        input.value = data[settingsVar][index]?.apiKey || "";
    });
}
function createInputFromSettings(data, settingsVar, htmlVar) {
    for (let i = 1; i < data[settingsVar].length; i++) {
        createAdditonalInput(htmlVar, placeholders[settingsVar]);
    }
    const dynamicInput = document.querySelectorAll(`input[name="${htmlVar}[]"]`);
    dynamicInput.forEach((input, index) => {
        input.value = data[settingsVar][index] || "";
    });
}

function preFillForm(data) {
    document.querySelector('input[name="target_path"]').value =
        data.targetPath || "";

    createInputFromSettings(data, "sourceDirs", "source_dir");
    createInputFromSettings(data, "libraryNames", "library_name");
    createInputFromSettings(data, "instances", "instance");
    document.getElementById("asset_folders").checked = data.assetFolders || false;
    document.getElementById("border_replacer").checked =
        data.borderReplacer || false;

    createInstanceFromSettings(data, "radarrInstances", "radarr");
    createInstanceFromSettings(data, "sonarrInstances", "sonarr");
    createInstanceFromSettings(data, "plexInstances", "plex");
}

function attachPosterRenamer() {
    const wrapperDiv = document.getElementById("poster-renamer-form");
    const formGroup = createPosterRenamer();
    wrapperDiv.appendChild(formGroup);
}

function createLabel(labelName, inputName) {
    const label = document.createElement("label");
    label.classList.add("form-label");
    label.setAttribute("for", `${inputName}`);
    label.textContent = `${labelName}`;
    return label;
}

function createInput(inputType, placeholder) {
    const input = document.createElement("input");
    input.type = "text";
    input.name = `${inputType}[]`;
    input.placeholder = placeholder;
    input.classList.add("form-input");
    return input;
}
function createSpan(inputType, input) {
    const span = document.createElement("span");
    span.classList.add("span-group");
    span.id = `${inputType}_${inputCounters[inputType]}`;

    const removeButton = document.createElement("button");
    if (inputCounters[inputType] === 1) {
        removeButton.style.display = "none";
    }
    removeButton.classList.add("btn", "btn-primary", "btn-remove");
    removeButton.type = "button";

    const trashIcon = document.createElement("i");
    trashIcon.classList.add("fas", "fa-trash-alt");

    removeButton.appendChild(trashIcon);
    span.appendChild(input);
    span.appendChild(removeButton);

    return span;
}

function createCheckboxInput(labelName, inputId) {
    const label = document.createElement("label");
    label.textContent = `${labelName}`;
    label.classList.add("custom-checkbox-label", "form-label");
    label.setAttribute("for", inputId);

    const input = document.createElement("input");
    input.type = "checkbox";
    input.id = inputId;

    const span = document.createElement("span");
    span.classList.add("checkmark-icon");

    const icon = document.createElement("i");
    icon.classList.add("fas", "fa-check");

    span.appendChild(icon);
    label.appendChild(input);
    label.appendChild(span);

    return label;
}

function createAddButton(name, text) {
    const addButton = document.createElement("button");
    addButton.classList.add("btn", "btn-primary", "btn-add");
    addButton.type = "button";
    addButton.id = `add_input_${name}`;

    const plusIcon = document.createElement("i");
    plusIcon.classList.add("fa", "fa-plus");
    addButton.appendChild(plusIcon);
    const textNode = document.createTextNode(` ${text}`);
    addButton.appendChild(textNode);
    return addButton;
}

let inputCounters = {
    source_dir: 1,
    library_name: 1,
    instance: 1,
};

let placeholders = {
    targetPath: "/kometa/assets",
    sourceDir: "/posters/Drazzilb08",
    libraryName: "Movies (HD)",
    instance: "radarr_1",
};

function createAdditonalInput(inputType, placeholder) {
    inputCounters[inputType]++;
    const wrapperDiv = document.getElementById(`${inputType}_div`);
    const labelElement = wrapperDiv.querySelector("label");
    const buttons = wrapperDiv.querySelectorAll(".btn-remove");
    if (inputCounters[inputType] > 1) {
        buttons.forEach((button) => {
            button.style.display = "block";
        });
    }
    const input = createInput(inputType, placeholder);
    const span = createSpan(inputType, input);
    const removeButton = span.querySelector("button");
    attachRemoveButtonListener(wrapperDiv, inputType, removeButton);
    labelElement.appendChild(span);
}

function attachRemoveButtonListener(wrapperDiv, inputType, removeButton) {
    removeButton.addEventListener("click", function() {
        inputCounters[inputType]--;
        const parentElement = removeButton.parentElement;
        parentElement.remove();
        const buttons = wrapperDiv.querySelectorAll(".btn-remove");
        if (inputCounters[inputType] === 1) {
            buttons.forEach((button) => {
                button.style.display = "none";
            });
        }
        updateSpanId(wrapperDiv, inputType);
    });
}
function updateSpanId(wrapperDiv, inputType) {
    const spans = wrapperDiv.querySelectorAll(".span-group");
    spans.forEach((span, index) => {
        span.id = `${inputType}_${index + 1}`;
    });
}

function attachAddButtonListener(button, inputType, placeholder) {
    button.addEventListener("click", function() {
        createAdditonalInput(inputType, placeholder);
    });
}
function createPosterRenamer() {
    const formGroup = document.createElement("div");
    const buttonDiv = document.createElement("div");
    buttonDiv.id = "button_div";
    buttonDiv.classList.add("button-div");
    const sourceDirsDiv = document.createElement("div");
    sourceDirsDiv.id = "source_dir_div";
    const instancesDiv = document.createElement("div");
    instancesDiv.id = "instance_div";
    const libraryNamesDiv = document.createElement("div");
    libraryNamesDiv.id = "library_name_div";
    const checkboxDiv = document.createElement("div");
    checkboxDiv.classList.add("form-group-checkbox");

    const targetPathInput = document.createElement("input");
    targetPathInput.name = "target_path";
    targetPathInput.type = "text";
    targetPathInput.classList.add("form-input");
    targetPathInput.placeholder = placeholders["targetPath"];
    const targetPathLabel = createLabel("Target Path", `${targetPathInput.name}`);
    targetPathLabel.appendChild(targetPathInput);

    const sourceDirInput = createInput("source_dir", placeholders["sourceDir"]);
    const sourceDirLabel = createLabel(
        "Source Directories",
        `${sourceDirInput.name}`,
    );
    const sourceDirSpan = createSpan("source_dir", sourceDirInput);
    const sourceDirRemoveButton = sourceDirSpan.querySelector(".btn-remove");
    attachRemoveButtonListener(
        sourceDirsDiv,
        "source_dir",
        sourceDirRemoveButton,
    );
    sourceDirLabel.appendChild(sourceDirSpan);

    const libraryNameInput = createInput(
        "library_name",
        placeholders["libraryName"],
    );
    const libraryNamesLabel = createLabel(
        "Library Names",
        `${libraryNameInput.name}`,
    );
    const libraryNameSpan = createSpan("library_name", libraryNameInput);
    libraryNamesLabel.appendChild(libraryNameSpan);
    const libraryNameRemoveButton = libraryNameSpan.querySelector(".btn-remove");
    attachRemoveButtonListener(
        libraryNamesDiv,
        "library_name",
        libraryNameRemoveButton,
    );

    const instanceInput = createInput("instance", placeholders["instance"]);
    const instanceLabel = createLabel("Instances", `${instanceInput.name}`);
    const instanceSpan = createSpan("instance", instanceInput);
    instanceLabel.appendChild(instanceSpan);
    const instanceRemoveButton = instanceSpan.querySelector(".btn-remove");
    attachRemoveButtonListener(instancesDiv, "instance", instanceRemoveButton);

    const assetFoldersCheckbox = createCheckboxInput(
        "Asset Folders",
        "asset_folders",
    );
    const borderReplacerCheckbox = createCheckboxInput(
        "Border Replacerr",
        "border_replacer",
    );

    const addSourceDirButton = createAddButton("source_dir", "Add Source Dir");
    attachAddButtonListener(
        addSourceDirButton,
        "source_dir",
        placeholders["sourceDir"],
    );
    const addLibraryNamesButton = createAddButton("library_name", "Add Library");
    attachAddButtonListener(
        addLibraryNamesButton,
        "library_name",
        placeholders["libraryName"],
    );
    const addInstancesButton = createAddButton("instances", "Add Instance");
    attachAddButtonListener(
        addInstancesButton,
        "instance",
        placeholders["instance"],
    );
    buttonDiv.appendChild(addSourceDirButton);
    buttonDiv.appendChild(addLibraryNamesButton);
    buttonDiv.appendChild(addInstancesButton);

    sourceDirsDiv.appendChild(sourceDirLabel);
    libraryNamesDiv.appendChild(libraryNamesLabel);
    instancesDiv.appendChild(instanceLabel);

    checkboxDiv.appendChild(assetFoldersCheckbox);
    checkboxDiv.appendChild(borderReplacerCheckbox);

    formGroup.appendChild(targetPathLabel);
    formGroup.appendChild(sourceDirsDiv);
    formGroup.appendChild(libraryNamesDiv);
    formGroup.appendChild(instancesDiv);
    formGroup.appendChild(checkboxDiv);
    formGroup.appendChild(buttonDiv);

    return formGroup;
}
let counters = {
    sonarr: 0,
    radarr: 0,
    plex: 0,
};

function updateCounter(name) {
    const wrapperDiv = document.getElementById(`${name}-group-wrapper`);

    const formGroups = wrapperDiv.querySelectorAll(".form-group");
    const instanceInputs = wrapperDiv.querySelectorAll(
        `input[name="${name}_instance\\[\\]"]`,
    );
    counters[name] = formGroups.length;
    instanceInputs.forEach((input, index) => {
        input.placeholder = `${name}_${index + 1}`;
    });
    formGroups.forEach((group, index) => {
        group.id = `${name}-group-${index + 1}`;
    });
}
function createInstanceSpan(instanceLabel, name) {
    const instanceSpan = document.createElement("span");
    instanceSpan.classList.add("span-group");
    const instanceInput = instanceLabel.querySelector("input");

    const testBtn = document.createElement("button");
    testBtn.id = `test-${name}`;
    testBtn.type = "button";
    testBtn.classList.add("btn", "btn-test");
    testBtn.textContent = "Test";
    instanceSpan.appendChild(instanceInput);
    instanceSpan.appendChild(testBtn);

    instanceLabel.appendChild(instanceSpan);
    return instanceLabel;
}

function createInstance(name, counter) {
    let dynamicUrlPlaceholder;
    let dynamicApiPlaceholder;

    if (name === "radarr") {
        dynamicUrlPlaceholder = "http://localhost:7878";
    } else if (name === "sonarr") {
        dynamicUrlPlaceholder = "http://localhost:8989";
    } else {
        dynamicUrlPlaceholder = "http://localhost:32400";
    }
    if ((name === "radarr") | (name === "sonarr")) {
        dynamicApiPlaceholder = "api-key";
    } else {
        dynamicApiPlaceholder = "plex-token";
    }

    const formGroup = document.createElement("div");
    formGroup.id = `${name}-group-${counter}`;
    formGroup.classList.add("form-group");

    const separator = document.createElement("hr");
    separator.classList.add("separator");

    const instanceInput = createInput(`${name}_instance`, `${name}_${counter}`);
    const instanceLabel = createLabel("Instance", instanceInput.name);
    instanceLabel.appendChild(instanceInput);

    const urlInput = createInput(`${name}_url`, dynamicUrlPlaceholder);
    const urlLabel = createLabel("URL", urlInput.name);
    urlLabel.appendChild(urlInput);

    const apiInput = createInput(`${name}_api`, dynamicApiPlaceholder);
    const apiLabel = createLabel("API", apiInput.name);
    apiLabel.appendChild(apiInput);

    const instanceSpan = createInstanceSpan(instanceLabel, name);

    if (counters[name] > 1) {
        formGroup.appendChild(separator);
    }
    formGroup.appendChild(instanceSpan);
    formGroup.appendChild(urlLabel);
    formGroup.appendChild(apiLabel);

    return formGroup;
}

// Add extra Radarr instance

function attachNewInstance(name) {
    counters[name]++;
    const wrapperDiv = document.getElementById(`${name}-group-wrapper`);
    const newInstance = createInstance(name, counters[name]);
    const testButton = newInstance.querySelector(".btn-test");
    attachTestButtonListener(testButton, name);

    wrapperDiv.appendChild(newInstance);
    attachRemoveButton(wrapperDiv, name, newInstance);
    if (counters[name] === 1) {
        hideAllRemoveButtons(name);
    } else {
        removeButtons = wrapperDiv.querySelectorAll(".btn-remove");
        removeButtons.forEach((button) => {
            button.style.display = "block";
        });
    }
}

function attachRemoveButton(wrapperDiv, name, formGroup) {
    const instanceSpans = wrapperDiv.querySelectorAll(".span-group");
    instanceSpans.forEach((group) => {
        if (!group.querySelector(".btn-remove")) {
            const removeButton = document.createElement("button");
            removeButton.type = "button";
            removeButton.classList.add("btn", "btn-primary", "btn-remove");
            removeButton.innerHTML = '<i class="fas fa-trash-alt"></i>';
            group.appendChild(removeButton);
            removeButton.addEventListener("click", function() {
                const isFirstInstance = formGroup === wrapperDiv.firstElementChild;
                const nextSibling = formGroup.nextElementSibling;
                if (isFirstInstance && nextSibling) {
                    const nextSeparator = nextSibling.querySelector(".separator");
                    if (nextSeparator) {
                        nextSeparator.remove();
                    }
                }
                formGroup.remove();
                counters[name]--;
                updateCounter(name);
                if (counters[name] === 1) {
                    hideAllRemoveButtons(name);
                }
            });
        }
    });
}

function hideAllRemoveButtons(name) {
    const wrapperDiv = document.getElementById(`${name}-group-wrapper`);
    const removeButtons = wrapperDiv.querySelectorAll(".btn-remove");
    removeButtons.forEach((button) => {
        button.style.display = "none";
    });
}

document.getElementById("add-radarr").addEventListener("click", function() {
    attachNewInstance("radarr");
});

// Add Sonarr instance

document.getElementById("add-sonarr").addEventListener("click", function() {
    attachNewInstance("sonarr");
});

// Add Plex instance

document.getElementById("add-plex").addEventListener("click", function() {
    attachNewInstance("plex");
});

// Save settings to db
document.getElementById("save-settings").addEventListener("click", function() {
    const targetPath = document.querySelector('input[name="target_path"]').value;
    const sourceDirs = Array.from(
        document.querySelectorAll('input[name="source_dir[]"]'),
    ).map((input) => input.value);
    const libraryNames = Array.from(
        document.querySelectorAll('input[name="library_name[]"]'),
    ).map((input) => input.value);
    const instances = Array.from(
        document.querySelectorAll('input[name="instance[]"]'),
    ).map((input) => input.value);
    const assetFolders = document.getElementById("asset_folders").checked;
    const borderReplacerr = document.getElementById("border_replacer").checked;

    // radarr
    const radarrInstanceNames = Array.from(
        document.querySelectorAll('input[name="radarr_instance[]"]'),
    ).map((input) => input.value);
    const radarrUrls = Array.from(
        document.querySelectorAll('input[name="radarr_url[]"]'),
    ).map((input) => input.value);
    const radarrApiKeys = Array.from(
        document.querySelectorAll('input[name="radarr_api[]"]'),
    ).map((input) => input.value);

    const radarrInstances = radarrInstanceNames.map((name, index) => ({
        instanceName: name,
        url: radarrUrls[index],
        apiKey: radarrApiKeys[index],
    }));

    // sonarr
    const sonarrInstanceNames = Array.from(
        document.querySelectorAll('input[name="sonarr_instance[]"]'),
    ).map((input) => input.value);
    const sonarrUrls = Array.from(
        document.querySelectorAll('input[name="sonarr_url[]"]'),
    ).map((input) => input.value);
    const sonarrApiKeys = Array.from(
        document.querySelectorAll('input[name="sonarr_api[]"]'),
    ).map((input) => input.value);

    const sonarrInstances = sonarrInstanceNames.map((name, index) => ({
        instanceName: name,
        url: sonarrUrls[index],
        apiKey: sonarrApiKeys[index],
    }));

    // plex
    const plexInstanceNames = Array.from(
        document.querySelectorAll('input[name="plex_instance[]"]'),
    ).map((input) => input.value);
    const plexUrls = Array.from(
        document.querySelectorAll('input[name="plex_url[]"]'),
    ).map((input) => input.value);
    const plexApiKeys = Array.from(
        document.querySelectorAll('input[name="plex_api[]"]'),
    ).map((input) => input.value);

    const plexInstances = plexInstanceNames.map((name, index) => ({
        instanceName: name,
        url: plexUrls[index],
        apiKey: plexApiKeys[index],
    }));

    fetch("/save-settings", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            targetPath: targetPath,
            sourceDirs: sourceDirs,
            libraryNames: libraryNames,
            instances: instances,
            assetFolders: assetFolders,
            borderReplacerr: borderReplacerr,
            radarrInstances: radarrInstances,
            sonarrInstances: sonarrInstances,
            plexInstances: plexInstances,
        }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                alert("Settings saved succesfully!");
            } else {
                alert("Error saving settings: " + data.message);
            }
        })
        .catch((error) => {
            console.error("Error", error);
            alert("An unexpected error occured.");
        });
});

function attachTestButtonListener(testButton, instanceType) {
    testButton.addEventListener("click", function(event) {
        const parentGroup = event.target.closest(".form-group");
        const url = parentGroup.querySelector(
            `input[name="${instanceType}_url[]"]`,
        ).value;
        const apiKey = parentGroup.querySelector(
            `input[name="${instanceType}_api[]"]`,
        ).value;

        fetch(`/test-connection`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                url: url,
                apiKey: apiKey,
                instanceType: instanceType,
            }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    flashButton(testButton, "green");
                } else {
                    flashButton(testButton, "red");
                }
            })
            .catch((error) => {
                console.error("Error", error);
                flashButton(testButton, "red");
            });
    });
}

function flashButton(button, color) {
    const originalBackgroundColor = button.style.backgroundColor;

    button.style.backgroundColor = color;

    setTimeout(() => {
        button.style.backgroundColor = originalBackgroundColor;
    }, 2000);
}
