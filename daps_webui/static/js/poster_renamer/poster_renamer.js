const runButton = document.getElementById("run-renamer");

runButton.addEventListener("click", function() {
    runButton.disabled = true;
    fetch(`/run-renamer-job`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.job_id) {
                console.log("Job started", data);
                const jobId = data.job_id;
                checkProgress(jobId);
            } else {
                console.error("Job ID missing from response", data);
                runButton.disabled = false;
            }
        })
        .catch((error) => {
            console.error("Error starting job", error);
            runButton.disabled = false;
        });
});

function checkProgress(jobId) {
    fetch(`/progress/${jobId}`)
        .then((response) => response.json())
        .then((data) => {
            const progress = data.value || 0;
            const state = data.state || "Pending";
            const progressBar = document.getElementById("progress");
            progressBar.style.width = progress + "%";
            progressBar.textContent = progress + "%";
            
            if (progress > 0) {
                progressBar.style.backgroundColor = "#4caf50";
            } else {
                progressBar.style.backgroundColor = "transparent";
            }

            if (state !== "Completed") {
                setTimeout(() => checkProgress(jobId), 1000);
            } else {
                console.log("Job Complete");
                progressBar.textContent = "100%";
                runButton.disabled = false;
            }
        })
        .catch((error) => {
            console.error("Error checking progress", error);
            runButton.disabled = false;
        });
}
