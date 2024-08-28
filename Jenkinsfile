pipeline {
  agent {
    node {
      label 'CN_Design_RFA'
      }
    }
  stages {
     stage('Create Config Files and Update File permissions'){
	    steps{
	      sh 'mkdir -p config > /dev/null 2>&1'
        sh "echo ${params.config_B64_file} | base64 --decode > config/${params.config_file}"
        sh "echo ${params.director_node_B64} | base64 --decode > ${params.director_node_pem_file}"
        sh "echo ${params.kubeconfig_B64} | base64 --decode > ${params.kubeconfig_file}"
        sh '''chmod +x bin/cappa_extract.bsh
            chmod +x bin/cappa_exempt.bsh'''
        sh '''ls -l'''
		 }
	     }
    stage('Installing Cappa'){
        when { 
            expression{
	        params.InstallCappa == true
		}
	     }
	    steps{
	        sh "python python/cappa_install.py install_cappa --upload_kubeconfig ${params.upload_kubeconfig_file} --kubeconfig ${params.kubeconfig_file} --hostname ${params.hostname} --username ${params.username} --password ${params.password} --rpms ${params.rpms} --kernel_rpms ${params.kernel_rpms} --cappa_tgz ${params.cappa_tgz} --cappa_namespace ${params.cappa_namespace} --use_keyfile ${params.use_keyfile} --director_node_pem_file ${params.director_node_pem_file} --cappa_create_kernel_symlinks ${params.cappa_create_kernel_symlinks} --old_kernel_version ${params.old_kernel_version} --new_kernel_version ${params.new_kernel_version}"
		 }
	     }
    stage('Running Cappactl commands') {
      steps {
        sh '''ls -l'''
        sh 'rm -rf output > /dev/null 2>&1'
        sh 'mkdir -p output > /dev/null 2>&1'
        sh "python python/cappa_running_tool.py run_cappa --upload_kubeconfig ${params.upload_kubeconfig_file} --kubeconfig ${params.kubeconfig_file} --kubeconfig_location ${params.kubeconfig_location} --podname ${params.podname} --hostname ${params.hostname} --username ${params.username} --password ${params.password} --cappa_namespace ${params.cappa_namespace} --use_keyfile ${params.use_keyfile} --director_node_pem_file ${params.director_node_pem_file}  --cappa_running_time ${params.cappa_running_time}"
  }
      }
    stage ('Running RFA250 job') {
       when { 
            expression{
	        params.TriggerRFA250 == true
		  }
    }
    steps{
      script {
            try {
                build job: 'cENM_Design_Teams_RFA250', parameters: [
                  string(name: 'test_phase', value: "${params.test_phase}"),
                  string(name: 'drop', value: "${params.drop}"),
                  string(name: 'product_set_version', value: "${params.product_set_version}"),
                  string(name: 'cluster_id', value: "${params.cluster_id}"),
                  string(name: 'taf_version', value: "${params.taf_version}"),
                  string(name: 'central_csv_version', value: "${params.central_csv_version}"),
                  string(name: 'taf_scheduler_version', value: "${params.taf_scheduler_version}"),
                  string(name: 'send_confidence_level', value: "${params.send_confidence_level}"),
                  string(name: 'mt_utils_version', value: "${params.mt_utils_version}"),
                  string(name: 'cenm_product_set_version', value: "${params.cenm_product_set_version}")
                ]
            } catch (err) {
                echo err.getMessage()
            }
        }
		 }
    }
    stage('Stop cappactl') {
      steps {
        sh "python python/cappa_running_tool.py stop_cappa --upload_kubeconfig ${params.upload_kubeconfig_file} --kubeconfig ${params.kubeconfig_file} --kubeconfig_location ${params.kubeconfig_location} --podname ${params.podname} --hostname ${params.hostname} --username ${params.username} --password ${params.password} --cappa_namespace ${params.cappa_namespace} --use_keyfile ${params.use_keyfile} --director_node_pem_file ${params.director_node_pem_file}  --cappa_running_time ${params.cappa_running_time}"
  }
      }
    stage('Generating Reports') {
      steps {
        script {
            try {
                sh "chmod +x cappa_query && ./cappa_query"
            } catch (err) {
                echo err.getMessage()
            }
        }
	}
    }
    stage('Archive any artifacts') {
      steps {
        sh "cp /var/tmp/report_db output/report_db"
        archiveArtifacts(artifacts: 'output/**', allowEmptyArchive: true)
	    }
    }
    stage('Security Context Diff'){
        when { 
            expression{
	        params.Security_Context_Diff == true
		}
	     }
	    steps{
	        sh "touch output/security_context_diff.yaml"
	        sh "echo ${params.Security_Context_File} | base64 --decode >> Security_Context_File.yaml"
	        sh "python python/cappa_query_tool.py gen_pod_sec_context_diff --pod_name ${params.podname} --pod_spec_file Security_Context_File.yaml > output/security_context_diff.yaml"
            archiveArtifacts(artifacts: 'output/**', allowEmptyArchive: true)
		 }
	     }
      stage('Cleanup') {
        steps {
          sh "rm config/${params.config_file}"
          sh "rm ${params.director_node_pem_file}"
          sh "rm ${params.kubeconfig_file}"
          sh "rm /var/tmp/report_db"
          sh "rm -rf /var/tmp/cappa_out"
          sh "rm -rf /var/tmp/cappa_exempt"
        }
      }
    }
    
  parameters {    
    booleanParam(name: 'upload_kubeconfig_file', defaultValue: false, description: 'Mark true if you want to upload a kubeconfig or false to use kubeconfig on eccd')
    string(name: 'kubeconfig_file' ,defaultValue: 'ccd-c15a042.admin.conf' ,description: 'kubeconfig file')
    string(name: 'kubeconfig_B64' ,defaultValue: 'Null' ,description: 'Your kubeconfig file converted to Base64')
    string(name: 'kubeconfig_location' ,defaultValue: '/home/eccd/.kube/config' ,description: 'Your kubeconfig file converted to Base64')
    string(name: 'podname', defaultValue: 'all', description: 'The pod you want to run cappa against')
    string(name: 'grouping', defaultValue: 'accesscontrol,amos,apserv,autoidservice,cellserv,cmserv,cmevents,cmutilities,comecimpolicy,consul,dc-history,dlms,domain-proxy,dp-mediation,elex,elasticsearch,elementmanager,eventbasedclient,flowautomation,flsserv,fmalarmprocessing,fm-history,fmserv,general-scripting,gossiprouter-cache,gossiprouter-eap7,gossiprouter-remoting,haproxy,impexpserv,jms,ipsmserv,itservices,kpicalcserv,kpiserv,kvstore,lcmserv,medrouter,Modeldeployservice,models,msap,mscmip,msapgfm,mspmip,mscm,mscmapg,mscmce,mskpirt,msfm,msnetlog,mspm,mssnmpfm,mssnmpcm,nbalarmirp,nb-fm-snmp,nbi-bnsi-fm,nedoserv,netex,neo4j,nodecli,nodeplugins,ops,openidm,opendj,pkiraserv,pmrouterpolicy,pmserv,postgres,secserv,sentinel,shmcoreserv,shmserv,smrsserv,sps,sso,supervc,saserv,solr,solrautoid,eric-enm-troubleshooting-utils,uiserv,visinamingnb,visinamingsb,vaultserv,winfiol,wpserv', description: 'A csv of all podnames you want capabilities grouped for')
    string(name: 'hostname', defaultValue: '10.232.182.135' ,description: 'The hostname or IP address of eccd')
    string(name: 'username', defaultValue: 'eccd' ,description: 'The username on eccd to use')
    string(name: 'password', defaultValue: 'none' ,description: 'The password for eccd if applicable')
    booleanParam(name: 'InstallCappa', defaultValue: false, description: 'Mark True if you want to automate cappa install')
    string(name: 'rpms', defaultValue: 'audit,bcc-tools,libelf-devel,python3-bcc,python3-future,bcc-docs,sqlite3,zlib-devel,libstdc++-devel,libLLVM7,libclang7,libbcc0' ,description: 'CSV of RPMs to install and their versions with "=" if required')
    string(name: 'kernel_rpms', defaultValue: 'kernel-macros,kernel-devel,kernel-default-devel=5.3.18-24.75.3,kernel-source' ,description: 'The Kernel RPMs to install and their versions with "=" if required')
    string(name: 'cappa_tgz', defaultValue: 'eric-cbo-cappa-0.5.0-1.tgz' ,description: 'The helm chart tgz of cappa to install')
    string(name: 'cappa_namespace', defaultValue: 'test-deployment-namespace' ,description: 'The namespace to deploy cappa to this is not ENM please refer to ADP')
    string(name: 'cappa_running_time', defaultValue: '450' ,description: 'The minimum length of time to run cappa for (passed to python time.sleep())')
    booleanParam(name: 'use_keyfile', defaultValue: false, description: 'Boolean to use either a password or pem file to connect to eccd')
    string(name: 'director_node_pem_file', defaultValue: 'ccd-c15a042.director.pem', description: 'Pem File for your cENM environment')
    string(name: 'director_node_B64', defaultValue: 'asdf', description: 'Your Pem File Converted to Base64')   
    booleanParam(name: 'cappa_create_kernel_symlinks', defaultValue: false, description: 'Create symlink for inconsistent kernel version generally caused by PTF install')
    string(name: 'old_kernel_version' ,defaultValue: '5.3.18-24.75.3.22935.1.PTF.1190467-default' ,description: 'Old kernel version to remove')
    string(name: 'new_kernel_version' ,defaultValue: '5.3.18-24.75.3' ,description: 'new kernel version to install')
    booleanParam(name: 'Security_Context_Diff', defaultValue: false, description: 'Mark True if you want to run the security context diff')
    string(name: 'Security_Context_File' ,defaultValue: 'Null' ,description: 'Security Context File used to compare against')
    booleanParam(name: 'ArchiveEntireDatabase' ,defaultValue: true ,description: 'Boolean to save the entire generated cappa database. Note these files can be quite large please dont pollute artifactory unless necessary.')
 
    booleanParam(name: 'TriggerRFA250' ,defaultValue: true ,description: 'In order to get a good reading of the capabilities for ENM this Boolean will trigger RFA 250')
    string(name: 'test_phase', defaultValue: 'MTE', description:'The test phase being run')
    string(name: 'drop', defaultValue: '21.18', description:'Drop for upgrade')
    string(name: 'product_set_version', defaultValue: '21.18.3', description:'The Product Set version of vENM to upgrade to')
    string(name: 'cluster_id', defaultValue: 'ieatenmc15a042', description:'Deployment name of cENM Cloud Deployment')
    string(name: 'taf_version', defaultValue: 'AUTO', description:'Version of the TAF to use')
    string(name: 'central_csv_version', defaultValue: 'AUTO', description:'	Version of the Central CSV to use')
    string(name: 'taf_scheduler_version', defaultValue: 'AUTO', description:'	Version of the TAF Scheduler to use')
    string(name: 'send_confidence_level', defaultValue: 'NO', description:'')
    string(name: 'mt_utils_version', defaultValue: 'RELEASE', description:'')
    string(name: 'cenm_product_set_version', defaultValue: '21.18.3', description:'')
  }
}
