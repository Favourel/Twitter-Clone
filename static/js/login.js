const togglePassword = document.querySelector('#togglePassword');
const password = document.querySelector('#id_password');

togglePassword.addEventListener('click', function (e) {
    // toggle the type attribute
    const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
    password.setAttribute('type', type);
    // toggle the eye slash icon
});
let paymentForm = document.getElementById('login-form');
	if (paymentForm) {
		paymentForm.addEventListener('submit', function () {
		    console.log("login button clicked");
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