const signupForm = document.querySelector('#signup-form');
if (signupForm) {
  signupForm.addEventListener('submit', async (event) => {
    const honeypot = signupForm.querySelector('input[name="extra_info"]');
    if (honeypot && honeypot.value.trim()) {
      event.preventDefault();
      alert('Signup blocked by honeypot security.');
      return;
    }
  });
}
