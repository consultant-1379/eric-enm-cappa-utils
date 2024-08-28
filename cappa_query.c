#include <stdio.h>
#include <stdlib.h>
#include <sqlite3.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/stat.h>

/////////////////////////
/// CAPPA SQL HEADERS //////////////////////////////////////////////
/////////////////////////

#define PODNAME "Podname"
#define COMMAND "Command"
#define EXECUTOR "CommandEntrypoint"
#define CAP "Capability"
#define SYSCALL_ID "SyscallID"
#define IA32 "IA32"
#define SYSCALL_NAME "SyscallName"
#define RETVAL "Retval"
#define SYSCALL_COUNT "Count"
#define CRED_OVER_ACTIVE "CredOverActive"
#define IN_CONTAINER_CAPS "ContainerCaps"
#define UID "Uid"
#define EUID "Euid"
#define GID "Gid"
#define EGID "Egid"
#define COUNT "Count"

/////////////////////////
/// CAPPA SQL QUERIES //////////////////////////////////////////////
/////////////////////////

#define RUN_HOOK_INFO "SELECT DISTINCT NODE_NAME FROM RUNC_HOOK_INFO"

#define GET_CAPABILITIES ""\
"SELECT DISTINCT ca.COMMAND as COMM, GROUP_CONCAT(DISTINCT r.NODE_NAME) as PODNAMES, ca.EXECUTOR as EXECUTOR, c.NAME AS CAP, "\
                "ca.SYSCALL_NUM AS SYSCALL_ID, ca.IA32, s.NAME AS SYSCALL_NAME, ca.RETVAL, ca.COUNT, ca.CRED_OVERR_ACTIVE, ca.IN_CONTAINER_CAPS "\
"FROM CAPS_ASKED_FOR ca "\
"LEFT JOIN (SELECT * FROM RUNC_HOOK_INFO GROUP BY NETWORK_NS, PID_NS, GEN, NODE) AS r "\
     "ON r.NETWORK_NS = ca.NETWORK_NS "\
     "AND r.PID_NS = ca.PID_NS "\
     "AND r.GEN = ca.GEN "\
     "AND r.NODE = ca.NODE "\
"LEFT JOIN CAPABILITIES c ON ca.CAP_ID = c.CAP_ID "\
"LEFT JOIN "\
     "(SELECT 1 AS IA32, SYSCALL_NUM, NAME FROM SYSCALL32 "\
     "UNION "\
     "SELECT 0 AS IA32, SYSCALL_NUM, NAME FROM SYSCALL) AS s "\
     "ON s.SYSCALL_NUM = ca.SYSCALL_NUM AND s.IA32 = ca.IA32 "\
"GROUP BY ca.COMMAND ORDER BY CAP, r.NODE_NAME, ca.COMMAND, ca.EXECUTOR "


#define GET_INTERESTING_FILES ""\
"SELECT DISTINCT if.COMMAND as COMM, GROUP_CONCAT(DISTINCT r.NODE_NAME) as PODNAMES, if.FILENAME, if.FLAGS_I, if.FLAGS, if.MODE_I, if.MODE, if.COUNT "\
"FROM INTERESTING_FILES if "\
"LEFT JOIN (SELECT * FROM RUNC_HOOK_INFO GROUP BY NETWORK_NS, PID_NS, GEN, NODE) AS r ON r.NETWORK_NS = if.NETWORK_NS AND r.PID_NS = if.PID_NS AND r.GEN = if.GEN AND r.NODE = if.NODE "\
"GROUP BY if.COMMAND "\
"ORDER BY r.NODE_NAME, if.FILENAME, if.EXECUTOR "

#define GET_32BIT_SYSCALLS ""\
"SELECT DISTINCT sa.EXECUTOR, GROUP_CONCAT(DISTINCT r.NODE_NAME) as PODNAMES, sa.SYSCALL_NUM, sa.IA32, s.NAME AS SYSCALL_NAME, "\
  "sa.ERRNO, e.ENAME as ERRNO_NAME, sa.COUNT "\
"FROM ALL_SYSCALLS sa "\
"LEFT JOIN (SELECT * FROM RUNC_HOOK_INFO GROUP BY NETWORK_NS, PID_NS, GEN, NODE) AS r ON r.NETWORK_NS = sa.NETWORK_NS AND r.PID_NS = sa.PID_NS AND r.GEN = sa.GEN AND r.NODE = sa.NODE "\
"LEFT JOIN "\
	"(SELECT 1 AS IA32, SYSCALL_NUM, NAME from SYSCALL32 "\
	 "UNION "\
	 "SELECT 0 AS IA32, SYSCALL_NUM, NAME from SYSCALL) AS s "\
	"ON s.SYSCALL_NUM = sa.SYSCALL_NUM AND s.IA32 = sa.IA32 "\
"LEFT JOIN ERRNO e ON sa.ERRNO = e.ERRNO "\
"GROUP BY sa.EXECUTOR "\
"ORDER BY r.NODE_NAME, s.SYSCALL_NUM, e.ERRNO "

#define GET_SOCKET_OVERVIEW ""\
"SELECT DISTINCT(sp.NAME) AS PROTOCOL, GROUP_CONCAT(DISTINCT r.NODE_NAME) as PODNAMES, sf.NAME AS FAMILY "\
"FROM ALL_SOCKETS als "\
"LEFT JOIN (SELECT * FROM RUNC_HOOK_INFO GROUP BY NETWORK_NS, PID_NS, GEN, NODE) AS r ON r.NETWORK_NS = als.NETWORK_NS AND r.PID_NS = als.PID_NS AND r.GEN = als.GEN AND r.NODE = als.NODE "\
"LEFT JOIN SOCKET_FAMILY   sf ON als.FAMILY = sf.FAMILY "\
"LEFT JOIN SOCKET_PROTOCOL sp ON als.PROTOCOL = sp.PROTOCOL "\
"GROUP BY sp.NAME "\
"ORDER BY r.NODE_NAME, als.FAMILY, als.PROTOCOL "

#define GET_ROOT_PROCESSES ""\
"SELECT pas.COMM, GROUP_CONCAT(DISTINCT r.NODE_NAME) as PODNAMES, pas.EXECUTOR, pas.UID, pas.EUID, pas.GID, pas.EGID, pas.COUNT "\
"FROM PROCESSES_RUN_AS_ROOT pas "\
"LEFT JOIN (SELECT * FROM RUNC_HOOK_INFO GROUP BY NETWORK_NS, PID_NS, GEN, NODE) AS r ON r.NETWORK_NS = pas.NETWORK_NS AND r.PID_NS = pas.PID_NS AND r.GEN = pas.GEN AND r.NODE = pas.NODE "\
"GROUP BY pas.COMM "\
"ORDER BY r.NODE_NAME, pas.COMM, pas.EXECUTOR "

/////////////////////////////
/// Added for readability //////////////////////////////////////////////
/////////////////////////////

#define DIRECTORY_PERMISSIONS 0770
#define OUTPUT_DIR "output"
#define MAIN_CONTAINER_FILE_DESCRIPTOR_INDEX 1
#define MONITORING_FILE_DESCRIPTOR_INDEX 2
#define HTTPD_FILE_DESCRIPTOR_INDEX 3
#define WAIT_INIT_FILE_DESCRIPTOR_INDEX 4
#define SYSLOG_FILE_DESCRIPTOR_INDEX 5

/////////////////////
/// Error Handles //////////////////////////////////////////////
/////////////////////

#define DATABASE_OPEN_ERROR "Can't open database file: %s\n"
#define DATABASE_OPEN_SUCCESSFUL "Opened database successfully\n"
#define EXIT_PROGRAM_DEFAULT 0
#define EXIT_PROGRAM_ERROR -1
#define FATAL_FILE_OPEN_ERROR "We couldnt open the file !"
#define SQL_QUERY_ERROR "SQL query failed"


int get_distinct_caps_json(sqlite3 *db) {
    sqlite3_stmt *stmt; FILE *f; struct stat st = {0};    
    char *token, *str, filename[565], file_descriptors[9][30] = {
        ".json","_main.json","_monitoring.json", 
        "_httpd.json","_waitinit.json","_sysctl.json", 
        "_interestingfiles.json", "_sockets.json", "_rootprocesses.json"
    }, unknown_file_descriptors[5][40] = {
        "unknown_capabilities.json","unknown_interestingfiles.json","unknown_syscalls.json", "unknown_sockets.json","unknown_root_processes.json"
    }, string_comparitors[12][60] = {
        "/ericsson/3pp/jboss","/usr/lib/systemd/","enm_healthcheck","monitorTasks",
        "ProxyPassRules.sh","/entry-point.sh","/post-start.sh","httpd",
        "/pre-start.sh", "wait-vaultdb", "check_service","sysctl"
    };
    int file_descriptors_length = sizeof(file_descriptors)/sizeof(file_descriptors[0]), 
        unknown_file_descriptors_length = sizeof(unknown_file_descriptors)/sizeof(unknown_file_descriptors[0]), file_descriptor_index = 0,
        podname_counter = 0, comparitor_index = 0, podname_index = 0,
        comparitor_descriptors[12] = {
        MAIN_CONTAINER_FILE_DESCRIPTOR_INDEX,MAIN_CONTAINER_FILE_DESCRIPTOR_INDEX,MAIN_CONTAINER_FILE_DESCRIPTOR_INDEX,MONITORING_FILE_DESCRIPTOR_INDEX,
        HTTPD_FILE_DESCRIPTOR_INDEX,HTTPD_FILE_DESCRIPTOR_INDEX,HTTPD_FILE_DESCRIPTOR_INDEX,HTTPD_FILE_DESCRIPTOR_INDEX,
        HTTPD_FILE_DESCRIPTOR_INDEX,WAIT_INIT_FILE_DESCRIPTOR_INDEX,WAIT_INIT_FILE_DESCRIPTOR_INDEX,SYSLOG_FILE_DESCRIPTOR_INDEX 
    }; 
    unsigned char write_buffer[1000], podnames[500][255], caps[500][400], executor[255], comm[255],
    grouping[117][255] = {
        "accesscontrol","amos","apserv","autoidservice","brocli",
        "calico-kube-controllers","cellserv","cmevents","cmserv", "cmutilities",
        "comecimpolicy","cts","dc-history","dlms","domainproxy",
        "elasticsearch","elasticsearch-data","elasticsearch-ingest","elasticsearch-master","elect",
        "elect-one-minute-cronjob","elementmanager","elex","eric-cnom-document-database-mg","eric-cnom-server",
        "eric-ctrl-bro","eric-data-document-database-pg","eric-data-search-engine-curator","eric-enm-credm-controller-cron-job","eric-enm-credm-controller",
        "eric-enm-modeldeployservice","eric-enm-monitoring-master-trigger","eric-log-transformer","eric-oss-ingress-controller-nx","eric-pm-alert-manager",
        "eric-pm-server-external","eric-pm-server","eshistory-data","eshistory-ingest","eshistory-master",
        "eshistory","eventbasedclient","flowautomation","flsserv","fmalarmprocessing",
        "fmalertparser","fmhistory","fmserv","general-scripting","gossiprouter-cache",
        "gossiprouter-eap7","gossiprouter-remoting","idmserv","impexpserv","ipsmserv",
        "itservices","jms","kpicalcserv","kpiserv","kvstore",
        "kvstore-bragent","lcmserv","medrouter","msap","msapgfm",
        "mscm","mscmapg","mscmce","mscmip","msfm",
        "mskpirt","msnetlog","mspm","mspmip","mssnmpcm",
        "mssnmpfm","nbalarmirp","nbfmsnmp","nbi-bnsi-fm","nedoserv",
        "neo4j","neo4j-bragent","netex","nodecli","nodeplugins",
        "omnidaemon","opendj","opendj-bragent","openidm","pkiraserv",
        "pmrouterpolicy","pmserv","pool1-n116-vpod1-pool1","postgres","postgres-bragent",
        "remotedesktop","remotewriter","rwxpvc-bragent","saserv","secserv",
        "sentinel","shmcoreserv","shmserv","smrsserv","solrautoid",
        "solr","sps","sso","supervc","troubleshooting-utils",
        "uiserv","vaultserv","visinamingnb","visinamingsb","websps",
        "worker","wpserv"
    };
    if (stat(OUTPUT_DIR, &st) == -1) {mkdir(OUTPUT_DIR, DIRECTORY_PERMISSIONS);}
    sqlite3_prepare_v2(db, RUN_HOOK_INFO, -1, &stmt, NULL);

    ///////////////////////
    /// Init JSON files //////////////////////////////////////////////
    ///////////////////////

	while (sqlite3_step(stmt) != SQLITE_DONE) { 
        strcpy(podnames[podname_counter], sqlite3_column_text(stmt, 0));
        podname_index = 0;
        while(podname_index < 117){            
            if (strstr(podnames[podname_counter], grouping[podname_index])){
                strcpy(podnames[podname_counter], grouping[podname_index]);
            }
            podname_index++;
        }
        sprintf(filename, "%s/%s", OUTPUT_DIR, podnames[podname_counter]);
        if (stat(filename, &st) == -1) {mkdir(filename, DIRECTORY_PERMISSIONS);}
        file_descriptor_index = 0;
        while(file_descriptor_index < file_descriptors_length){
            sprintf(filename, "%s/%s/%s%s", OUTPUT_DIR, podnames[podname_counter], podnames[podname_counter], file_descriptors[file_descriptor_index]);
            f = fopen(filename, "w");
            if(f) { fwrite("[",1,1,f); fclose(f); }
            else {
                puts(FATAL_FILE_OPEN_ERROR);
                puts(filename);
                exit(0);
            }
            file_descriptor_index++;
        } podname_counter++;
    }
    file_descriptor_index = 0;
    while(file_descriptor_index < unknown_file_descriptors_length){
        sprintf(filename, "%s/%s", OUTPUT_DIR, unknown_file_descriptors[file_descriptor_index]);
        f = fopen(filename, "w");
        if(f) { fwrite("[",1,1,f); fclose(f); }
        else {
            puts(FATAL_FILE_OPEN_ERROR);
            puts(filename);
            exit(0);
        } file_descriptor_index++;
    }
    sprintf(filename, "%s/unknown_root_process.json", OUTPUT_DIR);
    f = freopen(filename, "w", stdout);
    puts(write_buffer);
    fclose(f);

    //////////////////////////////
    /// Get Capabilities QUERY //////////////////////////////////////////////
    //////////////////////////////

	sqlite3_finalize(stmt);
    if (sqlite3_prepare_v2(db, GET_CAPABILITIES, -1, &stmt, NULL) != SQLITE_OK) {
        puts(SQL_QUERY_ERROR);
        exit(0);
    }
    while(sqlite3_step(stmt) != SQLITE_DONE){
        sprintf(write_buffer,""); comparitor_index = 0, file_descriptor_index = 0;
        strcpy(executor, sqlite3_column_text(stmt, 2));
        strcpy(comm, sqlite3_column_text(stmt, 0));
        sprintf(
            write_buffer + strlen(write_buffer),
            "{"\
                "\t\"%s\":\"%s\",\r\n"\
                // Executor
                "\t\"%s\":\"%s\",\r\n"\
                // Capability
                "\t\"%s\":\"%s\",\r\n"\
                // Syscall ID
                "\t\"%s\":\"%d\",\r\n"\
                // IA32
                "\t\"%s\":\"%d\",\r\n"\
                // SYSCALL NAME
                "\t\"%s\":\"%s\",\r\n"\
                // SYSCALL Return Value
                "\t\"%s\":\"%d\",\r\n"\
                // SYSCALL Count
                "\t\"%s\":\"%d\",\r\n"\
                // SYSCALL Credential Over Active
                "\t\"%s\":\"%d\",\r\n"\
                // SYSCALL in container capabilities (rwx)
                "\t\"%s\":\"%s\"\r\n"\
            "},",
            COMMAND, comm,
            EXECUTOR, executor,
            CAP, sqlite3_column_text(stmt, 3),
            SYSCALL_ID, sqlite3_column_text(stmt, 4), 
            IA32, sqlite3_column_text(stmt, 5), 
            SYSCALL_NAME, sqlite3_column_text(stmt, 6),
            RETVAL, sqlite3_column_text(stmt, 7), 
            SYSCALL_COUNT, sqlite3_column_text(stmt, 8), 
            CRED_OVER_ACTIVE, sqlite3_column_text(stmt, 9), 
            IN_CONTAINER_CAPS, sqlite3_column_text(stmt, 10)
        );
        if (sqlite3_column_text(stmt, 1)) {
            str = strdup(sqlite3_column_text(stmt, 1));
            while(comparitor_index < 12){
                if (strstr(executor, string_comparitors[comparitor_index])) {
                    file_descriptor_index = comparitor_descriptors[comparitor_index]; break;
                } comparitor_index++;
            }
            while ((token = strsep(&str, ","))){
                podname_index = podname_counter;
                while(podname_index > 0){
                    if (strstr(token, podnames[--podname_index])){break;}
                }
                sprintf(filename, "%s/%s/%s%s", OUTPUT_DIR, podnames[podname_index], podnames[podname_index], file_descriptors[file_descriptor_index]);
                f = freopen(filename, "a", stdout);
                puts(write_buffer);
                fclose(f);
            }
        } else{
            sprintf(filename, "%s/%s", OUTPUT_DIR, unknown_file_descriptors[0]);
            f = freopen(filename, "a", stdout);
            puts(write_buffer);
            fclose(f);
        }
       
    }
    sqlite3_finalize(stmt);

    ///////////////////////////////
    /// INTERESTING FILES QUERY //////////////////////////////////////////////
    ///////////////////////////////

    if (sqlite3_prepare_v2(db, GET_INTERESTING_FILES, -1, &stmt, NULL) != SQLITE_OK) {
        puts(SQL_QUERY_ERROR);
        exit(0);
    }
    while(sqlite3_step(stmt) != SQLITE_DONE){
        sprintf(write_buffer,""); comparitor_index = 0, file_descriptor_index = 0;
        strcpy(comm, sqlite3_column_text(stmt, 0));
        sprintf(
            write_buffer + strlen(write_buffer),
            "{\r\n"\
                // Command
                "\t\"%s\":\"%s\",\r\n"\
                // FILENAME
                "\t\"%s\":\"%s\",\r\n"\
                // FLAGS_I
                "\t\"%s\":\"%d\",\r\n"\
                // FLAGS
                "\t\"%s\":\"%s\",\r\n"\
                // MODE_I
                "\t\"%s\":\"%d\",\r\n"\
                // MODE
                "\t\"%s\":\"%s\",\r\n"\
                // COUNT
                "\t\"%s\":\"%d\"\r\n"\
            "},",
            "Command", sqlite3_column_text(stmt, 0), 
            "Filename", sqlite3_column_text(stmt, 2),
            "Flags_i", sqlite3_column_text(stmt, 3),
            "Flags", sqlite3_column_text(stmt, 4),
            "Mode_i", sqlite3_column_text(stmt, 5), 
            "Mode", sqlite3_column_text(stmt, 6), 
            "Count", sqlite3_column_text(stmt, 7)
        );
        if (sqlite3_column_text(stmt, 1)) {
            str = strdup(sqlite3_column_text(stmt, 1));
            while ((token = strsep(&str, ","))){
                podname_index = podname_counter;
                while(podname_index > 0){
                    if (strstr(token, podnames[--podname_index])){break;}
                }
                sprintf(filename, "%s/%s/%s%s", OUTPUT_DIR, podnames[podname_index], podnames[podname_index], file_descriptors[5]);
                f = freopen(filename, "a", stdout);
                puts(write_buffer);
                fclose(f);
            }
        } else{
            sprintf(filename, "%s/%s", OUTPUT_DIR, unknown_file_descriptors[1]);
            f = freopen(filename, "a", stdout);
            puts(write_buffer);
            fclose(f);
        }        
    }
    sqlite3_finalize(stmt);

    //////////////////////
    /// Syscall QUERY  //////////////////////////////////////////////
    //////////////////////

    if (sqlite3_prepare_v2(db, GET_32BIT_SYSCALLS, -1, &stmt, NULL) != SQLITE_OK) {
        puts(SQL_QUERY_ERROR);
        exit(0);
    }
    while(sqlite3_step(stmt) != SQLITE_DONE){
        sprintf(write_buffer,""); comparitor_index = 0, file_descriptor_index = 0;
        strcpy(comm, sqlite3_column_text(stmt, 0));        
        sprintf(
            write_buffer + strlen(write_buffer),
            "{\r\n"\
                // EXECUTOR
                "\t\"%s\":\"%s\",\r\n"\
                // SYSCALL_NUM
                "\t\"%s\":\"%d\",\r\n"\
                // IA32
                "\t\"%s\":\"%d\",\r\n"\
                // SYSCALL_NAME
                "\t\"%s\":\"%s\",\r\n"\
                // ERRNO
                "\t\"%s\":\"%d\",\r\n"\
                // ERRNO_NAME
                "\t\"%s\":\"%s\",\r\n"\
                // COUNT
                "\t\"%s\":\"%d\"\r\n"\
            "},",
            "Command", sqlite3_column_text(stmt, 0), 
            "Filename", sqlite3_column_text(stmt, 2),
            "Flags_i", sqlite3_column_text(stmt, 3),
            "Flags", sqlite3_column_text(stmt, 4),
            "Mode_i", sqlite3_column_text(stmt, 5), 
            "Mode", sqlite3_column_text(stmt, 6), 
            "Count", sqlite3_column_text(stmt, 7)
        );        
        if (sqlite3_column_text(stmt, 1)) {
            str = strdup(sqlite3_column_text(stmt, 1));
            while ((token = strsep(&str, ","))){
                podname_index = podname_counter;
                while(podname_index > 0){
                    if (strstr(token, podnames[--podname_index])){break;}
                }
                sprintf(filename, "%s/%s/%s%s", OUTPUT_DIR, podnames[podname_index], podnames[podname_index], file_descriptors[6]);
                f = freopen(filename, "a", stdout);
                puts(write_buffer);
                fclose(f);
            }
        } else{
            sprintf(filename, "%s/%s", OUTPUT_DIR, unknown_file_descriptors[2]);
            f = freopen(filename, "a", stdout);
            puts(write_buffer);
            fclose(f);
        }
    }
    sqlite3_finalize(stmt);

    /////////////////////////////
    /// Socket Overview QUERY /////////////////////////////////////////////
    /////////////////////////////

    if (sqlite3_prepare_v2(db, GET_32BIT_SYSCALLS, -1, &stmt, NULL) != SQLITE_OK) {
        puts(SQL_QUERY_ERROR);
        exit(0);
    }
    while(sqlite3_step(stmt) != SQLITE_DONE){
        sprintf(write_buffer,""); comparitor_index = 0, file_descriptor_index = 0;
        strcpy(comm, sqlite3_column_text(stmt, 0));        
        sprintf(
            write_buffer + strlen(write_buffer),
            "{\r\n"\
                // Protocol
                "\t\"%s\":\"%s\",\r\n"\
                // Family
                "\t\"%s\":\"%s\"\r\n"\
            "},",
            "Family", sqlite3_column_text(stmt, 0), 
            "Protocol", sqlite3_column_text(stmt, 2)
        );        
        if (sqlite3_column_text(stmt, 1)) {
            str = strdup(sqlite3_column_text(stmt, 1));
            while ((token = strsep(&str, ","))){
                podname_index = podname_counter;
                while(podname_index > 0){
                    if (strstr(token, podnames[--podname_index])){break;}
                }
                sprintf(filename, "%s/%s/%s%s", OUTPUT_DIR, podnames[podname_index], podnames[podname_index], file_descriptors[7]);
                f = freopen(filename, "a", stdout);
                puts(write_buffer);
                fclose(f);
            }
        } else{
            sprintf(filename, "%s/%s", OUTPUT_DIR, unknown_file_descriptors[3]);
            f = freopen(filename, "a", stdout);
            puts(write_buffer);
            fclose(f);
        }
    }
    sqlite3_finalize(stmt);

    ////////////////////////////
    /// Root Processes QUERY /////////////////////////////////////////////
    ////////////////////////////

    if (sqlite3_prepare_v2(db, GET_ROOT_PROCESSES, -1, &stmt, NULL) != SQLITE_OK) {
        puts(SQL_QUERY_ERROR);
        exit(0);
    }
    while(sqlite3_step(stmt) != SQLITE_DONE){
        sprintf(write_buffer,""); comparitor_index = 0, file_descriptor_index = 0;
        strcpy(comm, sqlite3_column_text(stmt, 0));
        sprintf(
            write_buffer + strlen(write_buffer),
            "{\r\n"\
                // COMM
                "\t\"%s\":\"%s\",\r\n"\
                // EXECUTOR
                "\t\"%s\":\"%s\",\r\n"\
                // UID
                "\t\"%s\":\"%d\",\r\n"\
                // EUID
                "\t\"%s\":\"%d\",\r\n"\
                // GID
                "\t\"%s\":\"%d\",\r\n"\
                // EGID
                "\t\"%s\":\"%d\",\r\n"\
                // COUNT
                "\t\"%s\":\"%s\"\r\n"\
            "},",
            COMMAND, sqlite3_column_text(stmt, 0), 
            EXECUTOR, sqlite3_column_text(stmt, 2),
            UID, sqlite3_column_text(stmt, 3),
            EUID, sqlite3_column_text(stmt, 4),
            GID, sqlite3_column_text(stmt, 5),
            EGID, sqlite3_column_text(stmt, 6),
            COUNT, sqlite3_column_text(stmt, 7)
        );
        if (sqlite3_column_text(stmt, 1)){
            str = strdup(sqlite3_column_text(stmt, 1));
            while ((token = strsep(&str, ","))){
                podname_index = podname_counter;
                while(podname_index > 0){
                    if (strstr(token, podnames[--podname_index])){break;}
                }
                sprintf(filename, "%s/%s/%s%s", OUTPUT_DIR, podnames[podname_index], podnames[podname_index], file_descriptors[8]);
                f = freopen(filename, "a", stdout);
                puts(write_buffer);
                fclose(f);
            }
        } else {
            sprintf(filename, "%s/%s", OUTPUT_DIR, unknown_file_descriptors[4]);
            f = freopen(filename, "a", stdout);
            puts(write_buffer);
            fclose(f);
        }
    }
    sqlite3_finalize(stmt);

    ///////////////////////////
    /// Conclude JSON files //////////////////////////////////////////////
    ///////////////////////////
    
    podname_index = podname_counter;
    while(podname_index > 0){ 
        podname_index = podname_index - 1; file_descriptor_index=0;
        while(file_descriptor_index < file_descriptors_length){
            sprintf(filename, "%s/%s/%s%s", OUTPUT_DIR, podnames[podname_index], podnames[podname_index], file_descriptors[file_descriptor_index]);
            f = freopen(filename, "a", stdout);
            if(f) {
                fseeko(f,-2,SEEK_END);
                int size = ftell(f);
                if (size < 20){
                    fclose(f);
                    remove(filename);
                } else {
                    ftruncate(fileno(f), ftello(f));
                    puts("]");
                    fclose(f);
                }
            } file_descriptor_index++;
        }
    }
    file_descriptor_index = 0;
    while(file_descriptor_index < unknown_file_descriptors_length){
        sprintf(filename, "%s/%s", OUTPUT_DIR, unknown_file_descriptors[file_descriptor_index]);
        f = freopen(filename, "a", stdout);
        if(f) {
            fseeko(f,-2,SEEK_END);
            int size = ftell(f);
            if (size < 20){
                fclose(f);
                remove(filename);
            } else {
                ftruncate(fileno(f), ftello(f));
                puts("]");
                fclose(f);
            }
        }
        file_descriptor_index++;
    }    
}

sqlite3 * open_db(char * db_file_location){
    sqlite3 *db;
    if(sqlite3_open(db_file_location, &db)) {
      fprintf(stderr, DATABASE_OPEN_ERROR, sqlite3_errmsg(db));
      exit(EXIT_PROGRAM_ERROR);
   } fprintf(stderr, DATABASE_OPEN_SUCCESSFUL);
   return db;
}

int main(int argc, char* argv[]) {
   sqlite3 *db = open_db("/var/tmp/report_db");
   get_distinct_caps_json(db);
   sqlite3_close(db);
}