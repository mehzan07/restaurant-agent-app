const form = document.querySelector('#reservation-form');
const status = document.querySelector('.form-status');
const dateInput = form?.querySelector('[name="reservation_date"]');

if (dateInput) dateInput.min = new Date().toISOString().split('T')[0];

form?.addEventListener('submit', async (event) => {
  event.preventDefault();
  status.className = 'form-status';
  status.textContent = '';
  if (!form.checkValidity()) {
    form.reportValidity();
    status.classList.add('error');
    status.textContent = 'Please complete the required fields.';
    return;
  }
  const button = form.querySelector('button');
  button.disabled = true;
  button.textContent = 'Sending…';
  try {
    const response = await fetch('/api/reservations', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(Object.fromEntries(new FormData(form))) });
    const result = await response.json();
    if (!response.ok) throw new Error(Object.values(result.errors || {})[0] || 'Please check your details.');
    status.classList.add('success');
    status.textContent = result.message;
    form.reset();
  } catch (error) {
    status.classList.add('error');
    status.textContent = error.message || 'Something went wrong. Please try again.';
  } finally {
    button.disabled = false;
    button.innerHTML = 'Request a reservation <span aria-hidden="true">↗</span>';
  }
});
