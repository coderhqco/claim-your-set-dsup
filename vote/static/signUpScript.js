
// ckeck the district and validate on mouse leave.
var district = document.querySelector("input[name='district']");

district.addEventListener('change', (event) => {
  let district_code = event.target.value;
  $.ajax({
    url:'votePortal-api/districts',
    method:'get',
    success:function(res){
      for(let i=0; i<res.length; i++){
        if(district_code.toUpperCase() === res[i].code.toUpperCase()){
          validate_valid(event);
          break
        }else{
          i == res.length-1 ? validate_invalid(event) : '';
        }
      }
    },
    error:function(err){
      console.log(err)
    },
  })
});

function validate_valid(e){
  e.target.style.borderColor = 'green';
  let errorField = e.target.nextElementSibling;
  errorField.innerHTML = ``;
  errorField.classList.add('hide');
}
function validate_invalid(e){
  e.target.style.borderColor = 'red';
  let errorField = e.target.nextElementSibling
  errorField.innerHTML = `<strong>Not a valid district number.  If you don’t know the number of your district, ask someone.</strong>`
  errorField.classList.remove('hide')
}

// check email for and formating and validate it on mouse leave

var email = document.querySelector("input[name='email']");
email.addEventListener('change', (event)=>{
  let val = event.target.value;
  if(validateEmail(val) == null){
    event.target.style.borderColor = 'red';
    let errorField = event.target.nextElementSibling;
    errorField.innerHTML = `<strong>Not a valid email address.</strong>`;
    errorField.classList.remove('hide');
  }else{
    event.target.style.borderColor = 'green';
    let errorField = event.target.nextElementSibling;
    errorField.innerHTML = `<strong></strong>`;
    errorField.classList.add('hide');
  }
})

const validateEmail = (email) => {
  return String(email)
    .toLowerCase()
    .match(
      /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
    );
};


const generatePss = document.getElementById('generatePassoword');

generatePss.addEventListener('click', (Event)=>{

  // generate a password and show it on password labal
  let  pass = generatePassword();
  // add the generated password into password input field as well
   document.querySelector("input[name='password']").value = pass;
   document.querySelector("input[name='confirmation']").value = pass;
   document.querySelector("input[name='password']").type='text';
   document.getElementById('basic-addon2').innerHTML = 'Hide';
})
function generatePassword() {
  var length = 8,
      charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
      retVal = "";
  for (var i = 0, n = charset.length; i < length; ++i) {
      retVal += charset.charAt(Math.floor(Math.random() * n));
  }
  return retVal;
}

// toggle the show passoword

let show = document.getElementById('basic-addon2')
show.style.cursor = "pointer";
show.addEventListener('click', function(event){
  let inpt = document.querySelector("input[name='password']");
  if (inpt.type === "password") {
    inpt.type = "text";
    event.target.innerHTML = 'Hide';
  } else {
    inpt.type = "password";
    event.target.innerHTML = 'Show';
  }
})