const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const Store = require('electron-store');
const fg = require('fast-glob');
const fs = require('fs');
const dayjs = require('dayjs');

const store = new Store();
let win;

function ffmpegPath() {
  try {
    const dev = require('@ffmpeg-installer/ffmpeg').path;
    return process.env.FFMPEG_PATH_OVERRIDE || dev;
  } catch {
    return path.join(process.resourcesPath, 'ffmpeg');
  }
}
function ffprobePath() {
  try {
    const dev = require('@ffprobe-installer/ffprobe').path;
    return dev;
  } catch {
    return path.join(process.resourcesPath, 'ffprobe');
  }
}

function createWindow() {
  win = new BrowserWindow({
    width: 1100,
    height: 720,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true
    }
  });
  win.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'));
}

app.whenReady().then(() => {
  createWindow();
  app.on('activate', () => BrowserWindow.getAllWindows().length === 0 && createWindow());
});
app.on('window-all-closed', () => process.platform !== 'darwin' && app.quit());

function looksLikeTeslaRoot(p) {
  return fs.existsSync(path.join(p, 'RecentClips'))
      || fs.existsSync(path.join(p, 'SavedClips'))
      || fs.existsSync(path.join(p, 'SentryClips'));
}
function parseTimestamp(name, statMtime) {
  const m = name.match(/(\d{4}-\d{2}-\d{2})[_T-](\d{2})[-_:](\d{2})[-_:](\d{2})/);
  if (m) return dayjs(`${m[1]} ${m[2]}:${m[3]}:${m[4]}`).toISOString();
  return dayjs(statMtime).toISOString();
}
function bytesOf(p) { try { return fs.statSync(p).size; } catch { return 0; } }
function folderNameOf(p, root) {
  const rel = path.relative(root, p);
  return rel.split(path.sep)[0] || path.basename(path.dirname(p));
}

ipcMain.handle('choose-source', async () => {
  const res = await dialog.showOpenDialog(win, { properties: ['openDirectory'] });
  if (res.canceled || !res.filePaths?.[0]) return null;
  const dir = res.filePaths[0];
  if (!looksLikeTeslaRoot(dir)) {
    const cont = await dialog.showMessageBox(win, {
      type: 'warning', buttons: ['Use Anyway', 'Cancel'], defaultId: 0,
      message: 'Selected folder does not look like a TeslaCam root. Continue?'
    });
    if (cont.response !== 0) return null;
  }
  store.set('source', dir);
  return dir;
});

ipcMain.handle('list-videos', async (_e, { source }) => {
  const src = source || store.get('source');
  if (!src) return { ok: false, error: 'No source selected' };

  const patterns = [
    path.join(src, 'RecentClips/**/*.{mp4,mov,mkv}'),
    path.join(src, 'SavedClips/**/*.{mp4,mov,mkv}'),
    path.join(src, 'SentryClips/**/*.{mp4,mov,mkv}'),
    path.join(src, '**/*.{mp4,mov,mkv}')
  ];
  const files = await fg(patterns, { onlyFiles: true, unique: true });
  const items = files.map(f => ({
    filename: f,
    timestamp: parseTimestamp(path.basename(f), fs.statSync(f).mtime),
    size: bytesOf(f),
    folder_name: folderNameOf(f, src)
  }));
  return { ok: true, items };
});

ipcMain.handle('choose-output', async () => {
  const res = await dialog.showOpenDialog(win, { properties: ['openDirectory', 'createDirectory'] });
  if (res.canceled || !res.filePaths?.[0]) return null;
  store.set('output', res.filePaths[0]);
  return res.filePaths[0];
});

ipcMain.handle('confirm-backup', async () => {
  const r = await dialog.showMessageBox(win, {
    type: 'warning',
    buttons: ['I made a backup', 'Cancel'],
    defaultId: 0, cancelId: 1,
    message: 'IMPORTANT: Back up your TeslaCam videos BEFORE shrinking.',
    detail: 'Shrinking re-encodes your videos. Keep a separate backup.'
  });
  return r.response === 0;
});

ipcMain.handle('compress', async (_e, payload) => {
  const { files, source, output, quality, overwrite, deleteOriginals } = payload;
  if (!files?.length) return { ok: false, error: 'No files selected' };

  const ff = ffmpegPath();
  if (!ff || !fs.existsSync(ff)) return { ok: false, error: 'FFmpeg not found or not bundled' };

  const cfg = quality === 'sd'
    ? { vf: 'scale=-2:480', crf: '30' }
    : { vf: 'scale=-2:720', crf: '27' };

  const results = [];
  for (let i = 0; i < files.length; i++) {
    const src = files[i];
    const rel = path.relative(source, src);
    const out = path.join(output, path.dirname(rel), path.basename(src, path.extname(src)) + '_compressed.mp4');
    fs.mkdirSync(path.dirname(out), { recursive: true });

    const args = [
      '-hide_banner', '-loglevel', 'error',
      '-i', src,
      '-map', '0:v:0', '-map', '0:a?',
      '-c:v', 'libx265', '-crf', cfg.crf, '-vf', cfg.vf,
      '-preset', 'medium', '-pix_fmt', 'yuv420p',
      '-c:a', 'aac', '-b:a', '128k',
      overwrite ? '-y' : '-n',
      out
    ];

    const proc = spawn(ff, args, { windowsHide: true });
    const ok = await new Promise((resolve) => proc.on('close', (code) => resolve(code === 0)));
    results.push({ src, out, ok });

    if (ok && deleteOriginals) { try { fs.unlinkSync(src); } catch {} }
    win.webContents.send('progress', { current: i + 1, total: files.length, file: path.basename(src), ok });
  }
  return { ok: true, results };
});

ipcMain.on('open-external', (_e, url) => shell.openExternal(url));
