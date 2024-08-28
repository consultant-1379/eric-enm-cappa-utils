////////////////////////
//  String Constants  //
////////////////////////
const COMMAND = "Command",
      COMMAND_ENTRYPOINT = "Command Entrypoint",
      CAPABILITY = "Capability",
      SYSCALL_ID = "SyscallID",
      SYSCALL_NAME = "SyscallName",
      RETVAL = "Retval",
      CRED_OVER_ACTIVE = "Cred Over Active",
      CONTAINER_CAPS = "Container Caps"
      IA32 = "IA32",
      FILENAME = "Filename",
      FLAGS_I = "Flags_i",
      FLAGS = "Flags",
      MODE_I = "Mode_i",
      MODE = "Mode",
      COUNT = "Count",
      UID = "Uid",
      EUID = "Euid",
      GID = "Gid",
      EGID = "Egid",
      FAMILY = "Family",
      PROTOCOL = "Protocol";

////////////////////////
//   DOM Constants    //
////////////////////////
const mainContent = document.querySelector("#main-content"),
      MenuButtons = document.getElementsByTagName("button"),
      sidebar = document.createElement("ul"),
      pod_wrapper_container = document.createElement("div"),
      sidemaincontent = document.createElement("div"),
      sidemain = document.createElement("div"),
      resizer = document.createElement("div"),
      pod_wrapper = document.createElement("div");

var default_table,
    main_table,
    monitoring_table,
    waitinit_table,
    httpd_table,
    sysctl_table,
    interestingfiles_table,
    sockets_table,
    rootprocesses_table,
    folder_list = [],
    folder_list_includes = [],
    sg_list = [];

/////////////////////////
//  Class Definitions  //
/////////////////////////

class table_container {
    constructor(table_container_class_name){
        let table_container = document.createElement("div");
        table_container.className = table_container_class_name;
        table_container.style.display = 'none';
        this.table_container = table_container;        
    }
}

class table_row {
    constructor(table_row_class_name) {
        let row = document.createElement("tr");
        row.className = table_row_class_name;
        this.row = row;
    }
}

class table_cell {
    constructor(text) {
        let cell = document.createElement("td"),
            celltext = document.createTextNode(text);
        cell.appendChild(celltext);
        this.cell = cell;
        this.text = celltext;
    }    
}

class table_head {
    constructor(text) {
        let cell = document.createElement("th"),
            celltext = document.createTextNode(text);
        cell.appendChild(celltext);
        this.cell = cell;
        this.text = celltext;
    }
}

class table_with_header extends table_container {
    constructor(title, title_colspan, table_container_class_name){
        let table = document.createElement("table"),
            thead = document.createElement("thead"),
            tbody = document.createElement("tbody"),
            title_row = document.createElement("tr"),
            title_heading = document.createElement("th"),
            title_text = document.createTextNode(title);
        super(table_container_class_name, table);
        title_heading.setAttribute("colspan",title_colspan);        
        title_heading.appendChild(title_text);
        title_row.appendChild(title_heading);
        thead.appendChild(title_row);
        table.appendChild(thead);
        table.appendChild(tbody);
        this.table = table;
        this.table_header = thead;
        this.title = title;
        this.BodyRows = [];
        this.tbody = tbody;        
        this.table_container.appendChild(table);
    }
}

class caps_table_row extends table_row {
    constructor(table_row_class_name, command, commandEntrypoint, capability, syscall, ia32, syscallName, retval, count, credOverActive, containerCaps) {
        super(table_row_class_name);
        let commandCell = new table_cell(command),
            commandEntrypointCell = new table_cell(commandEntrypoint),
            capabilityCell = new table_cell(capability),syscallCell = new table_cell((syscall)),
            ia32Cell = new table_cell(ia32), syscallNameCell = new table_cell(syscallName),
            retvalCell = new table_cell(retval),
            countCell = new table_cell(count),
            credOverActiveCell = new table_cell(credOverActive),
            containerCapsCell = new table_cell(containerCaps);
        this.Command = commandCell;this.row.appendChild(commandCell.cell);
        this.CommandEntrypoint = commandEntrypointCell;this.row.appendChild(commandEntrypointCell.cell);
        this.Capability = capabilityCell;this.row.appendChild(capabilityCell.cell);
        this.Syscall = syscallCell;this.row.appendChild(syscallCell.cell);
        this.Ia32 = ia32Cell;this.row.appendChild(ia32Cell.cell);
        this.SyscallName = syscallNameCell;this.row.appendChild(syscallNameCell.cell);
        this.Retval = retvalCell;this.row.appendChild(retvalCell.cell);
        this.Count = countCell;this.row.appendChild(countCell.cell);
        this.CredOverActive = credOverActiveCell;this.row.appendChild(credOverActiveCell.cell);
        this.ContainerCaps = containerCapsCell;this.row.appendChild(containerCapsCell.cell);
    }
}

class caps_table_class extends table_with_header {
    constructor(title, table_container_class_name) {
        super(title, 10, table_container_class_name);
        let table_header_row = document.createElement("tr"),
            command = new table_head(COMMAND),
            commandEntrypoint = new table_head(COMMAND_ENTRYPOINT),
            capability = new table_head(CAPABILITY),
            syscallID = new table_head(SYSCALL_ID),
            ia32 = new table_head(IA32),
            syscallName = new table_head(SYSCALL_NAME),
            retval = new table_head(RETVAL),
            count = new table_head(COUNT),
            credOverActive = new table_head(CRED_OVER_ACTIVE),
            containerCaps = new table_head(CONTAINER_CAPS);
        this.Command = command;table_header_row.appendChild(command.cell);
        this.CommandEntrypoint = commandEntrypoint;table_header_row.appendChild(commandEntrypoint.cell);
        this.Capability = capability;table_header_row.appendChild(capability.cell);
        this.SyscallID = syscallID;table_header_row.appendChild(syscallID.cell);
        this.Ia32 = ia32;table_header_row.appendChild(ia32.cell);
        this.SyscallName = syscallName;table_header_row.appendChild(syscallName.cell);
        this.Retval = retval;table_header_row.appendChild(retval.cell);
        this.Count = count;table_header_row.appendChild(count.cell);
        this.CredOverActive = credOverActive;table_header_row.appendChild(credOverActive.cell);
        this.ContainerCaps = containerCaps;table_header_row.appendChild(containerCaps.cell);
        this.headerRow = table_header_row;
        this.table_header.appendChild(table_header_row);
    }
    appendRows(rootprocesses_data){
        let JsonData = JSON.parse(rootprocesses_data);
        try {
            this.table_container.removeChild(this.table); 
        } catch (error) {
            console.error("failed to remove table from dom");
        }
        for (let k in JsonData) {
            try {
                let table_row = new caps_table_row("sockets_row", 
                    JsonData[k].Command, // Command
                    JsonData[k].CommandEntrypoint, // CommandEntrypoint
                    JsonData[k].Capability, // Capability
                    JsonData[k].SyscallID, // SyscallID
                    JsonData[k].IA32, // IA32
                    JsonData[k].SyscallName, // SyscallName
                    JsonData[k].Retval, // Retval
                    JsonData[k].Count, // Count
                    JsonData[k].CredOverActive, // CredOverActive
                    JsonData[k].ContainerCaps  // ContainerCaps
                )
                this.BodyRows.push(table_row)
                this.tbody.appendChild(table_row.row);
            } catch(error) {
                console.error(error);
                console.log(JsonData[k])
            }
        }
        try {
            this.table_container.appendChild(this.table);
            this.table_container.style.display = 'block';
        } catch (error) {
            console.error("failed to append table to dom");
        }        
    }
}

class interestingfiles_table_row extends table_row {
    constructor(table_row_class_name, command, filename, flags_i, flags, mode_i, mode, count) {
        console.log("interestingfiles_table_row")
        super(table_row_class_name);
        let commandCell = new table_cell(command), filenameCell = new table_cell(filename),
            flags_iCell = new table_cell(flags_i), flagsCell = new table_cell(flags),
            mode_iCell = new table_cell(mode_i), modeCell = new table_cell(mode),
            countCell = new table_cell(count);
        this.Command = commandCell;this.row.appendChild(commandCell.cell);
        this.Filename = filenameCell;this.row.appendChild(filenameCell.cell);
        this.Flags_i = flags_iCell;this.row.appendChild(flags_iCell.cell);
        this.Flags = flagsCell;this.row.appendChild(flagsCell.cell);
        this.Mode_i = mode_iCell;this.row.appendChild(mode_iCell.cell);
        this.Mode = modeCell;this.row.appendChild(modeCell.cell);
        this.Count = countCell;this.row.appendChild(countCell.cell);
    }
}

class interestingfiles_table_class extends table_with_header {
    constructor(title, table_container_class_name) {
        super(title, 7, table_container_class_name);
        let table_header_row = document.createElement("tr"),
        commandHeader = new table_head(COMMAND),
        filenameHeader = new table_head(FILENAME),
        flags_iHeader = new table_head(FLAGS_I),
        flagsHeader = new table_head(FLAGS),
        mode_iHeader = new table_head(MODE_I),
        modeHeader = new table_head(MODE),
        countHeader = new table_head(COUNT);
        this.Command = commandHeader;table_header_row.appendChild(commandHeader.cell);
        this.Filename = filenameHeader;table_header_row.appendChild(filenameHeader.cell);
        this.Flags_i = flags_iHeader;table_header_row.appendChild(flags_iHeader.cell);
        this.Flags = flagsHeader;table_header_row.appendChild(flagsHeader.cell);
        this.Mode_i = mode_iHeader;table_header_row.appendChild(mode_iHeader.cell);
        this.Mode = modeHeader;table_header_row.appendChild(modeHeader.cell);
        this.Count = countHeader;table_header_row.appendChild(countHeader.cell);        
        this.headerRow = table_header_row;
        this.table_header.appendChild(table_header_row);
    }
    appendRows(rootprocesses_data){
        let JsonData = JSON.parse(rootprocesses_data);
        try {
            this.table_container.removeChild(this.table); 
        } catch (error) {
            console.error("failed to remove table from dom");
        }
        for (let k in JsonData) {
            try {
                let table_row = new interestingfiles_table_row("sockets_row", 
                    JsonData[k].Command,
                    JsonData[k].Filename,
                    JsonData[k].Flags_i,
                    JsonData[k].Flags,
                    JsonData[k].Mode_i,
                    JsonData[k].Mode,
                    JsonData[k].Count
                )
                this.BodyRows.push(table_row);
                this.tbody.appendChild(table_row.row);
            } catch(error) {
                console.error(error);
                console.error(JsonData[k])
            }
            
        }
        try {
            this.table_container.appendChild(this.table);
            this.table_container.style.display = 'block';
        } catch (error) {
            console.error("failed to append table to dom");
        }
    }
}

class sockets_table_row extends table_row {
    constructor(table_row_class_name, family, protocol) {
        super(table_row_class_name);
        let familyCell = new table_cell(family),
            protocolCell = new table_cell(protocol);
        this.family = familyCell.cell;
        this.protocol = protocolCell.cell;
        this.row.appendChild(familyCell.cell);
        this.row.appendChild(protocolCell.cell);
    }
}

class sockets_table_class extends table_with_header {
    constructor(title, table_container_class_name) {
        super(title, 2, table_container_class_name);
        let table_header_row = document.createElement("tr"),
            family = new table_head(FAMILY),
            protocol = new table_head(PROTOCOL)
        this.Family = family;table_header_row.appendChild(family.cell);
        this.Protocol = protocol;table_header_row.appendChild(protocol.cell);
        this.headerRow = table_header_row;
        this.table_header.appendChild(table_header_row);
    }
    appendRows(rootprocesses_data){
        let JsonData = JSON.parse(rootprocesses_data);
        try {
            this.table_container.removeChild(this.table); 
        } catch (error) {
            console.error("failed to remove table from dom");
        }
        for (let k in JsonData) {
            try {
                let table_row = new sockets_table_row("sockets_row", 
                    JsonData[k].Family,
                    JsonData[k].Protocol
                )
                this.BodyRows.push(table_row)
                this.tbody.appendChild(table_row.row);
            } catch(error) {
                console.error(error);
                console.error(JsonData[k])
            }
        }
        try {
            this.table_container.appendChild(this.table);
            this.table_container.style.display = 'block';
        } catch (error) {
            console.error("failed to append table to dom");
        }
    }
}

class sysctl_table_row extends table_row {
    constructor(table_row_class_name, command, filename, flags_i, mode_i, mode, count) {
        super(table_row_class_name);
        let CommandCell = new table_cell(command),
            FilenameCell = new table_cell(filename),
            Flags_iCell = new table_cell(flags_i),
            Mode_iCell = new table_cell(mode_i),
            ModeCell = new table_cell(mode),
            CountCell = new table_cell(count);
        this.Command = CommandCell;this.row.appendChild(CommandCell.cell);
        this.Filename = FilenameCell;this.row.appendChild(FilenameCell.cell);
        this.Flags_i = Flags_iCell;this.row.appendChild(Flags_iCell.cell);
        this.Mode_i = Mode_iCell;this.row.appendChild(Mode_iCell.cell);
        this.Mode = ModeCell;this.row.appendChild(ModeCell.cell);
        this.Count = CountCell;this.row.appendChild(CountCell.cell);
    }
}


class sysctl_table_class extends table_with_header {
    constructor(title, table_container_class_name) {
        super(title, 7, table_container_class_name);
        let table_header_row = document.createElement("tr"),
        commandHeader = new table_head(COMMAND),filenameHeader = new table_head(FILENAME),
        flags_iHeader = new table_head(FLAGS_I),flagsHeader = new table_head(FLAGS),
        mode_iHeader = new table_head(FLAGS),modeHeader = new table_head(MODE),
        countHeader = new table_head(COUNT);
        this.Command = commandHeader;table_header_row.appendChild(commandHeader.cell);
        this.Filename = filenameHeader;table_header_row.appendChild(filenameHeader.cell);
        this.Flags_i = flags_iHeader;table_header_row.appendChild(flags_iHeader.cell);
        this.Flags = flagsHeader;table_header_row.appendChild(flagsHeader.cell);
        this.Mode_i = mode_iHeader;table_header_row.appendChild(mode_iHeader.cell);
        this.Mode = modeHeader;table_header_row.appendChild(modeHeader.cell);
        this.Count = countHeader;table_header_row.appendChild(countHeader.cell);
        this.headerRow = table_header_row;
        this.table_header.appendChild(table_header_row);
    }
    appendRows(rootprocesses_data){
        let JsonData = JSON.parse(rootprocesses_data);
        try {
            this.table_container.removeChild(this.table); 
        } catch (error) {
            console.error("failed to remove table from dom");
        }
        for (let k in JsonData) {
            try {
                let table_row = new sysctl_table_row("rootprocesses_row", 
                    JsonData[k].Command,
                    JsonData[k].CommandEntrypoint,
                    JsonData[k].Uid,
                    JsonData[k].Euid,
                    JsonData[k].Gid,
                    JsonData[k].Egid,
                    JsonData[k].Count
                )
                this.BodyRows.push(table_row);
                this.tbody.appendChild(table_row.row);
            } catch(error) {
                console.error(error);
                console.error(JsonData[k])
            }
        }
        try {
            this.table_container.appendChild(this.table);
            this.table_container.style.display = 'block';
        } catch (error) {
            console.error("failed to append table to dom");
        }
    }
}


class rootprocesses_table_row extends table_row {
    constructor(table_row_class_name, command, commandEntrypoint, uid, euid, gid, egid, count) {
        super(table_row_class_name);
        let CommandCell = new table_cell(command),
            CommandEntrypointCell = new table_cell(commandEntrypoint),
            UidCell = new table_cell(uid),
            EuidCell = new table_cell(euid),
            GidCell = new table_cell(gid),
            EgidCell = new table_cell(egid),
            CountCell = new table_cell(count);
        this.Command = CommandCell;this.row.appendChild(CommandCell.cell);
        this.CommandEntrypoint = CommandEntrypointCell;this.row.appendChild(CommandEntrypointCell.cell);
        this.Uid = UidCell;this.row.appendChild(UidCell.cell);
        this.Euid = EuidCell;this.row.appendChild(EuidCell.cell);
        this.Gid = GidCell;this.row.appendChild(GidCell.cell);
        this.Egid = EgidCell;this.row.appendChild(EgidCell.cell);
        this.Count = CountCell;this.row.appendChild(CountCell.cell);
    }
}

class rootprocesses_table_class extends table_with_header {
    constructor(title, table_container_class_name) {
        super(title, 7, table_container_class_name);
        let table_header_row = document.createElement("tr"),
            commandHeader = new table_head(COMMAND),
            commandEntrypointHeader = new table_head(COMMAND_ENTRYPOINT),
            uidHeader = new table_head(UID),
            euidHeader = new table_head(EUID),
            gidHeader = new table_head(GID),
            egidHeader = new table_head(EGID),
            countHeader = new table_head(COUNT);
        this.Command = commandHeader;table_header_row.appendChild(commandHeader.cell);
        this.CommandEntrypoint = commandEntrypointHeader;table_header_row.appendChild(commandEntrypointHeader.cell);
        this.Uid = uidHeader;table_header_row.appendChild(uidHeader.cell);
        this.Euid = euidHeader;table_header_row.appendChild(euidHeader.cell);
        this.Gid = gidHeader;table_header_row.appendChild(gidHeader.cell);
        this.Egid = egidHeader;table_header_row.appendChild(egidHeader.cell);
        this.Count = countHeader;table_header_row.appendChild(countHeader.cell);
        this.headerRow = table_header_row;
        this.table_header.appendChild(table_header_row);
    }
    appendRows(rootprocesses_data){
        let JsonData = JSON.parse(rootprocesses_data);
        try {
            this.table_container.removeChild(this.table); 
        } catch (error) {
            console.error("failed to remove table from dom");
        }
        for (let k in JsonData) {
            try {
                let table_row = new rootprocesses_table_row("rootprocesses_row", 
                    JsonData[k].Command,
                    JsonData[k].CommandEntrypoint,
                    JsonData[k].Uid,
                    JsonData[k].Euid,
                    JsonData[k].Gid,
                    JsonData[k].Egid,
                    JsonData[k].Count
                )
                this.BodyRows.push(table_row)
                this.tbody.appendChild(table_row.row);
            } catch(error) {
                console.error(error);
                console.error(JsonData[k])
            }
        }
        try {
            this.table_container.appendChild(this.table);
            this.table_container.style.display = 'block';
        } catch (error) {
            console.error("failed to append table to dom");
        }
    }
}




      

sidebar.id= "sidebar";
resizer.id = "resizer";
sidemain.id = "sidemain";
sidemaincontent.id = "sidemain-content";
pod_wrapper_container.id = "container";
pod_wrapper.id  = "wrapper";

sidemain.appendChild(sidemaincontent);
pod_wrapper_container.appendChild(sidebar);
pod_wrapper_container.appendChild(resizer);
pod_wrapper_container.appendChild(sidemain);
pod_wrapper.appendChild(pod_wrapper_container);

resizer.addEventListener("mousedown", (event) => {
    sidemain.style.display = "none";
    document.addEventListener("mousemove", resize, false);
    document.addEventListener("mouseup", () => {
        document.removeEventListener("mousemove", resize, false);
        sidemain.style.display = "flex";
        if (parseInt(sidebar.style.flexBasis.replace("/.px/g","")) < 150){
            sidebar.style.flexBasis = "0px";
        }
    }, false);
});
function resize(e) {
    sidebar.style.flexBasis = `${e.x}px`;
}
sidebar.style.flexBasis = '325px';


function report_file_data_callback(err, data, reportfile){
    if (err) {console.error(err); return }
    console.log(data)
    switch(reportfile.split("_")[1]){
        case ".json": default_table.appendRows(data); break;
        case "interestingfiles.json": interestingfiles_table.appendRows(data); break;
        case "main.json": main_table.appendRows(data); break;
        case "waitinit.json": waitinit_table.appendRows(data); break;
        case "httpd.json": httpd_table.appendRows(data); break;
        case "monitoring.json": monitoring_table.appendRows(data); break;
        case "sockets.json": sockets_table.appendRows(data); break;
        case "rootprocesses.json": rootprocesses_table.appendRows(data); break;
        default: return
    }
}

function report_files_callback(reportfiles, directory) {
    reportfiles.forEach(reportfile => {
        window.api.readfile(directory + "\\" + reportfile, 'utf8', report_file_data_callback, reportfile);          
    })
}

function callback(files){
    console.log(files);
    files.forEach(file => {
        if (file.indexOf("unknown")==-1){
            let currentFile = file;
            if(!sg_list.includes(file)){
                sg_list.push(file);
                let report_item = document.createElement("li");
                report_item_text = document.createTextNode(file);
                report_item.appendChild(report_item_text);
                report_item.addEventListener("click", function(){
                    sidemaincontent.innerHTML = "";
                    default_table = new caps_table_class("unknown capabilities", "table_container"),
                    main_table = new caps_table_class("main container capabilities", "table_container"),
                    monitoring_table = new caps_table_class("monitoring container capabilities", "table_container"),
                    waitinit_table = new caps_table_class("wait init container capabilities", "table_container"),
                    httpd_table = new caps_table_class("httpd container capabilities", "table_container"),
                    sysctl_table = new sysctl_table_class("sysctls", "table_container"),
                    interestingfiles_table = new interestingfiles_table_class("interesting files", "table_container"),
                    sockets_table = new sockets_table_class("interesting files", "table_container"),
                    rootprocesses_table = new rootprocesses_table_class("interesting files", "table_container");
                    sidemaincontent.appendChild(default_table.table_container);
                    sidemaincontent.appendChild(main_table.table_container);
                    sidemaincontent.appendChild(monitoring_table.table_container);
                    sidemaincontent.appendChild(waitinit_table.table_container);
                    sidemaincontent.appendChild(httpd_table.table_container);
                    sidemaincontent.appendChild(sysctl_table.table_container);
                    sidemaincontent.appendChild(interestingfiles_table.table_container);
                    sidemaincontent.appendChild(sockets_table.table_container);
                    sidemaincontent.appendChild(rootprocesses_table.table_container);
                    for(let k = 0; k < folder_list.length; k++){
                        if (folder_list_includes[k]){
                            console.log(folder_list[k] + "\\" + currentFile);
                            window.api.readdir(folder_list[k] + "\\" + currentFile, report_files_callback);
                        }
                    }
                });
                sidebar.appendChild(report_item);
            }
        }
    });
}
const main = document.getElementById("main");
const show_pods_button = document.getElementById("show_pods_button")
var Current = MenuButtons[0];
var current_container;

var folder_select_table = document.createElement("table");
    folder_select_table.id="folder_select_table";
var folder_select_table_header = document.createElement("tr");
var folder_select_table_header_file_name = document.createElement("th");
    folder_select_table_header_file_name.textContent = "Folderpath";
var folder_select_table_header_include = document.createElement("th");
    folder_select_table_header_include.textContent = "Include";
var folder_select_table_header_delete = document.createElement("th");
    folder_select_table_header_delete.textContent = "";
    folder_select_table_header.appendChild(folder_select_table_header_file_name);
    folder_select_table_header.appendChild(folder_select_table_header_include);
    folder_select_table_header.appendChild(folder_select_table_header_delete);
    folder_select_table.appendChild(folder_select_table_header);
folder_select_table.style.display= "none";

var folder_select_button = document.createElement("button");
folder_select_button.textContent = "folder select button";
folder_select_button.id = "folder_select_button"
folder_select_button.addEventListener("click", function(){
    window.api.directory_open_dialog();
})
const file_select_wrapper_container = document.createElement("div");
file_select_wrapper_container.id = "container2";
const file_select_wrapper = document.createElement("div");
file_select_wrapper.id  = "wrapper2";
file_select_wrapper.appendChild(file_select_wrapper_container);
file_select_wrapper_container.appendChild(folder_select_button);
file_select_wrapper_container.appendChild(folder_select_table);
main.appendChild(file_select_wrapper);
current_container = file_select_wrapper;


const settings_wrapper_container = document.createElement("div");
settings_wrapper_container.id = "container2";
const settings_wrapper = document.createElement("div");
settings_wrapper.id  = "wrapper2";
settings_wrapper.appendChild(settings_wrapper_container);
const themes = ["lightMode","darkMode"];
var selectedTheme = themes[0];
const themeLabel = document.createElement("label");
themeLabel.textContent = "Select theme";
themeLabel.for = "themeSelect";
settings_wrapper_container.appendChild(themeLabel);
const themeSelect = document.createElement("select");
themeSelect.id = "themeSelect";
settings_wrapper_container.appendChild(themeSelect);
for (var i = 0; i < themes.length; i++) {
    var option = document.createElement("option");
    option.value = themes[i];
    option.text = themes[i];
    themeSelect.appendChild(option);
}
themeSelect.addEventListener("change", function(){
   if(themeSelect.value == selectedTheme){return}
   document.body.classList.add(themeSelect.value);
   document.body.classList.remove(selectedTheme);
   selectedTheme = themeSelect.value;
})

function show_pods(e){
    main.removeChild(current_container);
    main.appendChild(pod_wrapper);        
    current_container = pod_wrapper;
    Current.className="";
    MenuButtons[1].className="active";
    Current = MenuButtons[1];    
    for(let k = 0; k < folder_list.length; k++){
        window.api.readdir(folder_list[k], callback)
    }
}
function show_folder_conf(e){
    Current.className="";
    MenuButtons[0].className="active";
    Current = MenuButtons[0];
    main.removeChild(current_container);
    main.appendChild(file_select_wrapper);
    current_container = file_select_wrapper;
}

function show_settings(e){
    Current.className="";
    MenuButtons[2].className="active";
    Current = MenuButtons[2];
    main.removeChild(current_container);
    main.appendChild(settings_wrapper);
    current_container = settings_wrapper;
}

window.api.directory_open_dialog_receive(function(args) {
    console.log("test")
    let results = args.body;          
    for(var i = 0; i < args.length; i++ ){
        let tr = document.createElement("tr");
        let td = document.createElement("td");
        let text = document.createTextNode(args[i]);
        
        if(!folder_list.includes(args[i])){
            folder_list.push(args[i]);
            folder_list_includes.push(true);
            td.appendChild(text);
            tr.appendChild(td);

            let td2 = document.createElement("td");
            let td2_input = document.createElement("input");
            let includeEvent = function(){
                let index = folder_list.indexOf(td.textContent);
                console.log(folder_list);
                if (index > -1) {
                    folder_list_includes[index] = this.checked
                }
            }
            td2_input.type="checkbox";
            td2_input.checked = true;
            td2_input.addEventListener("click", includeEvent)
            td2.appendChild(td2_input);
            tr.appendChild(td2);

            let td3 = document.createElement("td");
            let deleteEvent = function(){
                try{
                    let index = folder_list.indexOf(td.textContent);
                    console.log(folder_list);
                    if (index > -1) {
                        folder_list.splice(index, 1);
                        folder_list_includes.splice(index, 1);
                        folder_select_table.removeChild(tr);
                    }
                } catch (error) {
                    console.error(error);
                }                
            }
            td3.textContent = "Delete";
            td3.addEventListener("click", deleteEvent)
            tr.appendChild(td3);
            folder_select_table.appendChild(tr);
        }
        folder_select_table.style.display="table";
        show_pods_button.style.display="initial";
    }
});




document.onreadystatechange = (event) => {
    if (document.readyState == "complete") {
        var isMaximized = false;
        var isDarkMode = true;
        const min = function(){window.api.min();},
            max = function(){window.api.max();},
            restore = function(){window.api.restore();},
            close = function(){window.api.close();},
            toggleMaxRestoreButtons = function(){
                isMaximized = !isMaximized;
                if (isMaximized) {
                    document.body.classList.add('maximized');
                } else {
                    document.body.classList.remove('maximized');
                }
            }
        toggleMaxRestoreButtons();
        document.getElementById('min-button').addEventListener("click", min);
        document.getElementById('max-button').addEventListener("click", max);    
        document.getElementById('restore-button').addEventListener("click", restore);    
        document.getElementById('close-button').addEventListener("click", close);
        window.api.max_receive(toggleMaxRestoreButtons);
        window.api.min_receive("min_receive", toggleMaxRestoreButtons);
    }
};