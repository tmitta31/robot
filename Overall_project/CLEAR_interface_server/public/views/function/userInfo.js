// DISTRIBUTION STATEMENT A. Approved for public release. Distribution is unlimited.

// This material is based upon work supported by the Under Secretary of Defense for 
// Research and Engineering under Air Force Contract No. FA8702-15-D-0001. Any opinions,
// findings, conclusions or recommendations expressed in this material are those 
// of the author(s) and do not necessarily reflect the views of the Under 
// Secretary of Defense for Research and Engineering.

// © 2023 Massachusetts Institute of Technology.

// Subject to FAR52.227-11 Patent Rights - Ownership by the contractor (May 2014)

// The software/firmware is provided to you on an As-Is basis

// Delivered to the U.S. Government with Unlimited Rights, as defined in DFARS Part 
// 252.227-7013 or 7014 (Feb 2014). Notwithstanding any copyright notice, 
// U.S. Government rights in this work are defined by DFARS 252.227-7013 or 
// DFARS 252.227-7014 as detailed above. Use of this work other than as specifically
// authorized by the U.S. Government may violate any copyrights that exist in this work.

let usersName;

function getUsersName() {
  return usersName;
}

function getUserInformation() {
    // Check if a name cookie already exists
    usersName = getCookie("username");
  
    if (usersName) {
      alert("Welcome back " + usersName + "!");
    } else {
        usersName = prompt("Please enter your name:", "");
  
      if (usersName != null && usersName != "") {
        saveCookie("username", usersName)
        alert("Welcome " + usersName + "!");
      } else {
        alert("Welcome, guest!");
      }
    }
  }
  
  function saveCookie(varName, varValue) {
    var daysToExpire = 7;
    var date = new Date();
    date.setTime(date.getTime() + (daysToExpire * 24 * 60 * 60 * 1000));
    var expires = "expires=" + date.toUTCString();
    document.cookie = varName + "=" + varValue + ";" + expires + ";path=/";
  }

  // Function to retrieve a cookie by name
  function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i < ca.length; i++) {
      var c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
  }

// Only add the event listener after the window has loaded.
document.addEventListener('DOMContentLoaded', (event) => {
    console.log("hello friends");

    getUserInformation();
});