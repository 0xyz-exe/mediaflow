const analyzeForm = document.querySelector('#analyze-form');
const analyzeButton = analyzeForm.querySelector('button[type="submit"]');
const result = document.querySelector('#result');
document.querySelector('#clear').addEventListener('click', () => { document.querySelector('#url').value = ''; result.textContent = ''; result.className = 'result'; document.querySelector('#url').focus(); });
analyzeForm.addEventListener('submit', async event => {
  event.preventDefault(); result.className = 'result'; result.textContent = 'Checking the direct media link…'; analyzeButton.disabled = true;
  try {
    const response = await fetch('/api/analyze', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ url: document.querySelector('#url').value.trim() }) });
    const payload = await response.json(); if (!response.ok) throw new Error(payload.error || 'Unable to analyze this link.');
    const media = payload.data; result.replaceChildren();
    const text = document.createElement('p'); text.textContent = `${media.host} · ${media.type}${media.size ? ` · ${(media.size / 1048576).toFixed(1)} MiB` : ''}`; result.append(text);
    const link = document.createElement('a'); link.href = media.url; link.textContent = 'Open direct media'; link.rel = 'noopener noreferrer'; link.download = ''; result.append(link);
  } catch (error) { result.className = 'result error'; result.textContent = error.message; } finally { analyzeButton.disabled = false; }
});
const fileInput = document.querySelector('#file');
fileInput.addEventListener('change', () => { document.querySelector('#file-name').textContent = fileInput.files[0]?.name || 'Choose a media file'; });
const convertForm = document.querySelector('#convert-form');
const convertButton = convertForm.querySelector('button[type="submit"]');
const convertStatus = document.querySelector('#convert-status');
convertForm.addEventListener('submit', async event => {
  event.preventDefault(); const file = fileInput.files[0]; if (!file) return;
  if (file.size > 250 * 1024 * 1024) { convertStatus.className = 'result error'; convertStatus.textContent = 'File exceeds the 250 MiB limit.'; return; }
  convertButton.disabled = true; convertStatus.className = 'result'; convertStatus.textContent = 'Converting locally…';
  try {
    const body = new FormData(); body.append('file', file); body.append('format', document.querySelector('#format').value);
    const response = await fetch('/api/convert', { method: 'POST', body });
    if (!response.ok) { const message = await response.json(); throw new Error(message.error || 'Conversion failed.'); }
    const blob = await response.blob(); const url = URL.createObjectURL(blob); const link = document.createElement('a'); link.href = url; link.download = response.headers.get('Content-Disposition')?.match(/filename="([^"]+)"/)?.[1] || `mediaflow.${document.querySelector('#format').value}`; link.click(); URL.revokeObjectURL(url); convertStatus.textContent = 'Done. Your converted file has been downloaded.';
  } catch (error) { convertStatus.className = 'result error'; convertStatus.textContent = error.message; } finally { convertButton.disabled = false; }
});