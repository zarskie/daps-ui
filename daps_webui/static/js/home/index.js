var myPTag = document.getElementById("my-p-tag");
var button = document.getElementById("mybutton");

button.addEventListener("click", function() {
    changeText();
});

function changeText() {
    myPTag.innerText = myFirstName;    
}


// setTimeout(() => {
//     myPTag.innerText = "CHANGED!!";
// }, 5000);

