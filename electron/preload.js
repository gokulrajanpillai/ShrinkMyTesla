const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  chooseSource: () => ipcRenderer.invoke('choose-source'),
  listVideos: (source) => ipcRenderer.invoke('list-videos', { source }),
  chooseOutput: () => ipcRenderer.invoke('choose-output'),
  confirmBackup: () => ipcRenderer.invoke('confirm-backup'),
  compress: (payload) => ipcRenderer.invoke('compress', payload),
  onProgress: (cb) => ipcRenderer.on('progress', (_e, data) => cb(data)),
  openExternal: (url) => ipcRenderer.send('open-external', url)
});
