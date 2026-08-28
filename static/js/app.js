function getCookie(name) { return document.cookie.split('; ').find(row => row.startsWith(name + '='))?.split('=')[1]; }
document.querySelectorAll('.save-button').forEach(button => button.addEventListener('click', async () => {
  const response = await fetch(button.dataset.saveUrl, {method: 'POST', headers: {'X-CSRFToken': getCookie('csrftoken'), 'X-Requested-With': 'XMLHttpRequest'}});
  if (!response.ok) return;
  const data = await response.json();
  button.dataset.saved = data.saved;
  button.querySelector('.save-label').textContent = data.saved ? 'Saved' : 'Save for later';
}));
const uploads = document.querySelector('input[name="images"]');
if (uploads) uploads.addEventListener('change', () => { const target = document.querySelector('#image-preview'); target.innerHTML = ''; [...uploads.files].slice(0, 5).forEach(file => { const image = document.createElement('img'); image.src = URL.createObjectURL(file); image.alt = 'Selected photo preview'; target.append(image); }); });
