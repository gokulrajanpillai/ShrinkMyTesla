const $ = (s)=>document.querySelector(s);
const listEl = $("#list");
const statusEl = $("#status");
let sourceDir = null;
let outputDir = null;
let files = []; // [{filename,timestamp,size,folder_name,selected}]

function fmtBytes(n) {
  if (n < 1024) return n + " B";
  const u = ["KB","MB","GB","TB"];
  let i = -1;
  do { n /= 1024; i++; } while (n >= 1024 && i < u.length-1);
  return n.toFixed(1) + " " + u[i];
}

function renderList() {
  listEl.innerHTML = '';
  files.forEach((f, idx) => {
    const div = document.createElement('div');
    div.className = 'item';
    div.innerHTML = `
      <div>
        <label><input type="checkbox" data-idx="${idx}" ${f.selected?'checked':''} /> ${f.filename}</label>
        <div class="meta">📁 ${f.folder_name} · 🕒 ${f.timestamp} · 💾 ${fmtBytes(f.size)}</div>
      </div>
      <div class="badge">${f.selected ? 'Selected' : '—'}</div>
    `;
    div.querySelector('input[type=checkbox]').addEventListener('change', (e)=>{
      files[idx].selected = e.target.checked;
      renderList();
    });
    listEl.appendChild(div);
  });
}

$("#pickSource").addEventListener('click', async ()=>{
  const dir = await window.api.chooseSource();
  if (dir) { sourceDir = dir; statusEl.textContent = 'Source: ' + dir; }
});

$("#scan").addEventListener('click', async ()=>{
  if (!sourceDir) { statusEl.textContent = 'Pick TeslaCam folder first.'; return; }
  const res = await window.api.listVideos(sourceDir);
  if (!res.ok) { statusEl.textContent = 'Scan failed: ' + res.error; return; }
  files = res.items.map(x => ({...x, selected: true}));
  renderList();
  console.log(JSON.stringify(res.items, null, 2));
});

$("#pickOutput").addEventListener('click', async ()=>{
  const dir = await window.api.chooseOutput();
  if (dir) { outputDir = dir; statusEl.textContent = 'Output: ' + dir; }
});

$("#shrink").addEventListener('click', async ()=>{
  if (!sourceDir || !outputDir) { statusEl.textContent = 'Select source and output folders.'; return; }
  const chosen = files.filter(f => f.selected).map(f => f.filename);
  if (!chosen.length) { statusEl.textContent = 'Nothing selected.'; return; }

  const ok = await window.api.confirmBackup();
  if (!ok) { statusEl.textContent = 'Backup not confirmed. Aborted.'; return; }

  statusEl.textContent = 'Encoding...';
  window.api.onProgress(({current, total, file, ok})=>{
    statusEl.textContent = `Encoding ${current}/${total}: ${file} ${ok?'✅':'❌'}`;
  });

  const payload = {
    files: chosen,
    source: sourceDir,
    output: outputDir,
    quality: $("#quality").value,
    overwrite: $("#overwrite").checked,
    deleteOriginals: $("#deleteOriginals").checked
  };
  const res = await window.api.compress(payload);
  statusEl.textContent = res.ok ? 'Done.' : ('Error: ' + res.error);
});
