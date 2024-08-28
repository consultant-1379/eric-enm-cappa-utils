const { contextBridge, ipcRenderer } = require("electron");
const os = require ('os');
const username = os.userInfo().username;

contextBridge.exposeInMainWorld(
    "api", {
        setCredentials: (password) => {            
            ipcRenderer.send("setCredentials", { username, password });
        },
        username: username
    }
);