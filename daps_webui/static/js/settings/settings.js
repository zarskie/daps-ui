// function to create input group for source dir and library name
function createInput(name, value = "") {
  const inputDeleteButtonDiv = document.createElement("div");
  inputDeleteButtonDiv.classList.add("dynamic-input-group");

  const input = document.createElement("input");
  input.type = "text";
  input.name = `${name}[]`;
  input.value = value;
  input.classList.add("form-input");

  const removeButton = document.createElement("button");
  removeButton.type = "button";
  removeButton.classList.add("btn", "btn-primary");
  removeButton.innerHTML = '<i class="fas fa-trash-alt"></i>';

  inputDeleteButtonDiv.appendChild(input);
  inputDeleteButtonDiv.appendChild(removeButton);

  removeButton.addEventListener("click", function () {
    inputDeleteButtonDiv.remove();
  });
  return inputDeleteButtonDiv;
}

// Add extra source dir input
document
  .getElementById("add-source-dir")
  .addEventListener("click", function () {
    const sourceDirDivParent = document.getElementById(
      "source-dir-input-group"
    );
    const newInputGroup = createInput("source_dirs");
    sourceDirDivParent.appendChild(newInputGroup);
  });

// Add extra library names input
document
  .getElementById("add-library-name")
  .addEventListener("click", function () {
    const libraryNamesDivParent = document.getElementById(
      "library-names-input-group"
    );
    const newInputGroup = createInput("library_names");
    libraryNamesDivParent.appendChild(newInputGroup);
  });

  // Add extra instance input
document
  .getElementById("add-instance")
  .addEventListener("click", function () {
    const sourceDirDivParent = document.getElementById(
      "instances-input-group"
    );
    const newInputGroup = createInput("instances");
    sourceDirDivParent.appendChild(newInputGroup);
  });

  // function to create a new instance group
function createInstance(name, counter) {
  const wrapperDiv = document.createElement("div");
  const originalFormGroup = document.getElementById(`${name}-group`);
  const clonedFormGroup = originalFormGroup.cloneNode(true);

  clonedFormGroup.id = `${name}-group-${counter}}`;

  const inputs = clonedFormGroup.querySelectorAll("input");
  inputs.forEach((input) => {
    input.value = "";
    input.placeholder = "";
  });

  const testButton = clonedFormGroup.querySelector(".btn-test");

  const removeButton = document.createElement("button");
  removeButton.type = "button";
  removeButton.classList.add("btn", "btn-primary");
  removeButton.innerHTML = '<i class="fas fa-trash-alt"></i>';

  const instanceBtnGroup = clonedFormGroup.querySelector(".instance-btn-group");
  instanceBtnGroup.appendChild(removeButton);

  removeButton.addEventListener("click", function () {
    wrapperDiv.remove();
  });

  const seperator = document.createElement("hr");
  seperator.classList.add("seperator");

  wrapperDiv.appendChild(seperator);
  wrapperDiv.appendChild(clonedFormGroup);
  attachTestButtonListener(testButton, name);

  return wrapperDiv;
}

// Add extra Radarr instance
let radarrGroupCounter = 0;

document.getElementById("add-radarr").addEventListener("click", function () {
  const newInstance = createInstance("radarr", radarrGroupCounter++);
  const dynamicRadarrInstanceDiv = document.getElementById(
    "dynamic-radarr-instance-div"
  );
  dynamicRadarrInstanceDiv.appendChild(newInstance);
});

// Add Sonarr instance
let sonarrGroupCounter = 0;

document.getElementById("add-sonarr").addEventListener("click", function () {
  const newInstance = createInstance("sonarr", sonarrGroupCounter++);
  const dynamicSonarrInstanceDiv = document.getElementById(
    "dynamic-sonarr-instance-div"
  );
  dynamicSonarrInstanceDiv.appendChild(newInstance);
});

// Add Plex instance
let plexGroupCounter = 0;

document.getElementById("add-plex").addEventListener("click", function () {
  const newInstance = createInstance("plex", plexGroupCounter++);
  const dynamicPlexInstanceDiv = document.getElementById(
    "dynamic-plex-instance-div"
  );
  dynamicPlexInstanceDiv.appendChild(newInstance);
});

// Save settings to db
document.getElementById("save-settings").addEventListener("click", function () {
  const targetPath = document.getElementById("target-path").value;
  const sourceDirs = Array.from(
    document.querySelectorAll('input[name="source_dirs[]"]')
  ).map((input) => input.value);
  const libraryNames = Array.from(
    document.querySelectorAll('input[name="library_names[]"]')
  ).map((input) => input.value);
  const instances = Array.from(
    document.querySelectorAll('input[name="instances[]"]')
  ).map((input) => input.value);  
  const assetFolders = document.getElementById("asset-folders").checked;
  const borderReplacerr = document.getElementById("border-replacerr").checked;

  // radarr
  const radarrInstanceNames = Array.from(
    document.querySelectorAll('input[name="radarr[instance-name][]"]')
  ).map((input) => input.value);
  const radarrUrls = Array.from(
    document.querySelectorAll('input[name="radarr[url][]"]')
  ).map((input) => input.value);
  const radarrApiKeys = Array.from(
    document.querySelectorAll('input[name="radarr[api-key][]"]')
  ).map((input) => input.value);

  const radarrInstances = radarrInstanceNames.map((name, index) => ({
    instanceName: name,
    url: radarrUrls[index],
    apiKey: radarrApiKeys[index],
  }));

  // sonarr
  const sonarrInstanceNames = Array.from(
    document.querySelectorAll('input[name="sonarr[instance-name][]"]')
  ).map((input) => input.value);
  const sonarrUrls = Array.from(
    document.querySelectorAll('input[name="sonarr[url][]"]')
  ).map((input) => input.value);
  const sonarrApiKeys = Array.from(
    document.querySelectorAll('input[name="sonarr[api-key][]"]')
  ).map((input) => input.value);

  const sonarrInstances = sonarrInstanceNames.map((name, index) => ({
    instanceName: name,
    url: sonarrUrls[index],
    apiKey: sonarrApiKeys[index],
  }));

  // plex
  const plexInstanceNames = Array.from(
    document.querySelectorAll('input[name="plex[instance-name][]"]')
  ).map((input) => input.value);
  const plexUrls = Array.from(
    document.querySelectorAll('input[name="plex[url][]"]')
  ).map((input) => input.value);
  const plexApiKeys = Array.from(
    document.querySelectorAll('input[name="plex[api-key][]"]')
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
  testButton.addEventListener("click", function (event) {
    const parentGroup = event.target.closest(".form-group");
    const url = parentGroup.querySelector(
      `input[name="${instanceType}[url][]"]`
    ).value;
    const apiKey = parentGroup.querySelector(
      `input[name="${instanceType}[api-key][]"]`
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
