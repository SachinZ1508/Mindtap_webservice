// Toggle navigation menu on mobile
document.addEventListener("DOMContentLoaded", function() {
    const burger = document.querySelector('.burger');
    const navLinks = document.querySelector('.nav-links');
    if (burger && navLinks) {
        burger.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }
});
// Navigation burger toggle (already existing)
document.addEventListener("DOMContentLoaded", function() {
  const burger = document.querySelector('.burger');
  const navLinks = document.querySelector('.nav-links');
  burger.addEventListener('click', () => {
    navLinks.classList.toggle('active');
  });

  // Contact form validation
  const contactForm = document.querySelector('.contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', function(event) {
      let valid = true;
      const name = contactForm.querySelector('#name').value.trim();
      const email = contactForm.querySelector('#email').value.trim();
      const message = contactForm.querySelector('#message').value.trim();

      // Name validation
      if (name.length < 3) {
        alert('Please enter your full name (at least 3 characters).');
        valid = false;
      }

      // Email validation
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailPattern.test(email)) {
        alert('Please enter a valid email address.');
        valid = false;
      }

      // Message validation
      if (message.length < 10) {
        alert('Please enter a message of at least 10 characters.');
        valid = false;
      }

      if (!valid) {
        event.preventDefault(); // Prevent submission
      }
    });
  }
});
