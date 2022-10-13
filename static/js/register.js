$("#username").change(function () {
  var username = $(this).val();
  var email = $(this).attr('#email');

  $.ajax({
    url: '/ajax/validate_username/',
    data: {
      'username': username,
      'email': email,
    },
    dataType: 'json',
    success: function (data) {
    console.log(data)
      if (data.is_taken) {
        $("#username_result").text("Username has been used");
        $("#username_result").addClass("text-danger");
      } else {
        $("#username_result").text("");
        $("#username_result").addClass("text-success");
      }
      if (data.is_taken_email) {
        $("#email_result").text("Email has been used");
        $("#email_result").addClass("text-danger");
      }
    }
  });

});


$("#email").change(function () {
  var email = $(this).val();

  $.ajax({
    url: '/ajax/validate_username/',
    data: {
      'email': email,
    },
    dataType: 'json',
    success: function (data) {
    console.log(data)
      if (data.is_taken_email) {
        $("#email_result").text("Email has been used");
        $("#email_result").addClass("text-danger");
      }
      else {
        $("#email_result").text("");
        $("#email_result").addClass("text-success");
      }
    }
  });

});

const togglePassword = document.querySelector('#togglePassword');
const password = document.querySelector('#myInput');
const password_confirm = document.querySelector('#myInputConfirm');

togglePassword.addEventListener('click', function (e) {
    // toggle the type attribute
    const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
    const password_confirm_type = password_confirm.getAttribute('type') === 'password' ? 'text' : 'password';
    password.setAttribute('type', type);
    password_confirm.setAttribute('type', password_confirm_type);
    // toggle the eye slash icon
});


    let paymentForm = document.getElementById('signup-form');
	if (paymentForm) {
		paymentForm.addEventListener('submit', function () {
		    console.log("signup button clicked");
			changeLoadingState(true);

	    }
	  );
	}

    var changeLoadingState = function(isLoading) {
        if (isLoading) {
            document.getElementById("submit").disabled = true;
            document.querySelector("#spinner").classList.remove("hidden");
            document.querySelector("#button-text").classList.add("hidden");
        } else {
            document.getElementById("submit").disabled = false;
            document.querySelector("#spinner").classList.add("hidden");
            document.querySelector("#button-text").classList.remove("hidden");
        }
    };

 $("#username").change(function () {
      var username = $(this).val();
      var email = $(this).attr('#email');

      $.ajax({
        url: '/ajax/validate_username/',
        data: {
          'username': username,
          'email': email,
        },
        dataType: 'json',
        success: function (data) {
        console.log(data)
          if (data.is_taken) {
            $("#username_result").text("Username has been used");
            $("#username_result").addClass("text-danger");
          } else {
            $("#username_result").text("");
            $("#username_result").addClass("text-success");
          }
          if (data.is_taken_email) {
            $("#email_result").text("Email has been used");
            $("#email_result").addClass("text-danger");
          }
          if (data.not_equal) {
            $("#password_result").text("Password doesn't match");
            $("#password_result").addClass("text-danger");
          }
        }
      });

    });