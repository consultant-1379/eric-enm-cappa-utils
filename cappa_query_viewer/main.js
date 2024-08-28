const { app, BrowserWindow, ipcMain, nativeTheme, dialog } = require('electron')
app.disableHardwareAcceleration()

app.on("login", (event, webContents, request, authInfo, callback) => {
    event.preventDefault();
  
    createAuthWindow().then(credentials => {
      callback(credentials.username, credentials.password);
    });
  });


const path = require('path')
var win;
function createMainWindow() {
    win = new BrowserWindow({
        width: 800,
        height: 600,
        show: false,
        frame: false,
        backgroundColor: '#FFF',
        icon:__dirname + '/logo/ECON_RGB.png',
        webPreferences: {
            nodeIntegration: false,
            enableRemoteModule: false,
            preload: path.join(__dirname, '/build/js/preload.js'),
            contextIsolation: true
        }
    })
    win.setMenuBarVisibility(false)
    win.loadFile(path.join(__dirname, '/build/index.html'))

    ipcMain.handle('dark-mode:toggle', () => {
        if (nativeTheme.shouldUseDarkColors) {
            nativeTheme.themeSource = 'light'
        } else {
            nativeTheme.themeSource = 'dark'
        }
        return nativeTheme.shouldUseDarkColors
    })

    ipcMain.handle('dark-mode:system', () => {
        nativeTheme.themeSource = 'system'
    })
    ipcMain.on('file_open_dialog', (event, err, data) => {
      dialog.showOpenDialog(null, {
        properties: ['openFile', 'multiSelections']
      }).then((filePaths) => {
        console.log(filePaths.filePaths);
        event.sender.send('file_open_dialog_reply', filePaths.filePaths) 
        return filePaths.filePaths[0]
      });
    });
    ipcMain.on('directory_open_dialog', (event, err, data) => {
      dialog.showOpenDialog(null, {
        properties: ['openDirectory', 'multiSelections']
      }).then((filePaths) => {
        console.log(filePaths.filePaths);
        event.sender.send('directory_open_dialog_reply', filePaths.filePaths) 
        return filePaths.filePaths[0]
      });
    });


    ipcMain.on('max', (event) => {
        win.maximize()
        event.sender.send('max')
    })
    ipcMain.on('min', (event) => {
        win.minimize()
        event.sender.send('min')
    })
    ipcMain.on('restore', () => {
        win.restore()
    })
    ipcMain.on('close', () => {
        win.close()
    })
}

function createAuthWindow() {
    authWindow = new BrowserWindow({
      show: false,
      width: 300, 
      height: 400,
      frame: false,
      resizable: false,
      icon:__dirname + '/logo/ECON_RGB.png',
      webPreferences: {
        nodeIntegration: false,
        enableRemoteModule: false,
        preload: path.join(__dirname, '/build/js/auth_preload.js'),
        contextIsolation: true
      },
      title: "Authentication",
    });
    authWindow.setMenuBarVisibility(false)
  
    authWindow.on('ready-to-show', function (){
      authWindow.show();
    });
  
    authWindow.loadFile(path.join(__dirname, '/build/auth.html'));
    ipcMain.on('setCredentials', (event, username, password) => {
      // const electron = require('electron');
      // const { ClientRequest } = require('http');
      // const axios = require('axios');
      // let res = axios.get('https://fem16s11-eiffel004.eiffel.gic.ericsson.se:8443/jenkins/job/cappa_multibranch_pipeline/job/dTORF-571531/100/artifact/output/amos/amos_main.json/*view*/', {
      // auth: {
      //     username: username,
      //     password: ''
      // }
      // }).then((response) => {
      //     console.log(response);
      //   }, (error) => {
      //     console.log(error);
      //   });
      const credentials = {
        username,
        password
      };
      win.show();
      win.maximize();
      authWindow.close();
    });

  }

app.whenReady().then(() => {
  createMainWindow();
  createAuthWindow()
  
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
      createAuthWindow()
      
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

