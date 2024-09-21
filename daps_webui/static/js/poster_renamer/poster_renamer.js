
// method 1
// function checkSomething() {
//     // logic
//     console.log("checking back end");
// }

// const intervalId = setInterval(checkSomething, 1000);

// clear loop
// clearInterval(intervalId)


// method 2
// function checkSomething() {
//     // logic
//     console.log("checking");

//     // recursive set on the timer
//     setTimeout(checkSomething, 1000);
// }

// checkSomething();

const runButton = document.getElementById('run-renamer').addEventListener('click', function() {
    fetch(`/run-renamer`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        }
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            alert(data.message);
          } else {
            alert(data.message);
          }
        })
        .catch((error) => {
          console.error("Error", error);
          alert("An unexpected error occured.");          
        });
})