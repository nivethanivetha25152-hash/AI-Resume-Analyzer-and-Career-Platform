// AI Resume Analyzer

document.addEventListener("DOMContentLoaded", function () {

    console.log("AI Resume Analyzer Loaded Successfully");

});

// Validate Resume Upload

function validateResume() {

    let file = document.querySelector('input[type="file"]').value;

    if (file === "") {

        alert("Please Select Resume");

        return false;

    }

    return true;

}

// Logout Confirmation

function logoutConfirm() {

    return confirm("Are you sure you want to Logout?");

}

// Success Message

function uploadSuccess() {

    alert("Resume Uploaded Successfully");

}

// Simple Score Animation

function scoreAnimation(score) {

    let current = 0;

    let interval = setInterval(function () {

        current++;

        document.getElementById("score").innerHTML = current;

        if (current >= score) {

            clearInterval(interval);

        }

    }, 20);
    
}
// AI Resume Analyzer

document.addEventListener("DOMContentLoaded", function () {

    console.log("AI Resume Analyzer Loaded Successfully");

});

// Validate Resume Upload

function validateResume() {

    let file = document.querySelector('input[type="file"]').value;

    if (file === "") {

        alert("Please Select Resume");

        return false;

    }

    return true;

}

// Logout Confirmation

function logoutConfirm() {

    return confirm("Are you sure you want to Logout?");

}

// Success Message

function uploadSuccess() {

    alert("Resume Uploaded Successfully");

}

// Simple Score Animation

function scoreAnimation(score) {

    let current = 0;

    let interval = setInterval(function () {

        current++;

        document.getElementById("score").innerHTML = current;

        if (current >= score) {

            clearInterval(interval);

        }

    }, 20);
    
}
