const { contextBridge, ipcRenderer } = require("electron");
const os = require ('os');
const username = os.userInfo ().username;
const fs = require('fs');

contextBridge.exposeInMainWorld(
    "api", {
        setCredentials: (password) => {            
            ipcRenderer.send("setCredentials", { username, password });
        },
        min: () => {ipcRenderer.send('min');},
        max: () => {ipcRenderer.send('max');},
        max_receive: (func) => {
            ipcRenderer.on("max", (event, ...args) => func(...args));
        },
        min_receive: (func) => {
            ipcRenderer.on("min", (event, ...args) => func(...args));
        },
        restore: () => {ipcRenderer.send('restore');},
        close: () => {ipcRenderer.send('close');},
        readdir: (dirname, func, directory) => {
            fs.readdir(dirname, (err, files) => {
                func(files, dirname)
            })
        },
        readfile: (filename, encoding, func, reportfile) => {
            fs.readFile(filename, encoding , (err, data) => func(err, data, reportfile));
        },
        directory_open_dialog: () => {
            ipcRenderer.send('directory_open_dialog', "test");
        },
        directory_open_dialog_receive: (func) => {
            ipcRenderer.on("directory_open_dialog_reply", (event, ...args) => func(...args));
        },
        username: username
    },
);