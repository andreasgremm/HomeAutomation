pipeline {
    agent none
    parameters {
        string(name: 'JENKINSPATH', defaultValue: 'Not defined', description: 'Directory where Jenkins should build (Dockfile location)')
        string(name: 'DOCKERTAG', defaultValue: 'Not defined', description: 'Name of the Container: TAG')
    }
    stages {
        stage("Build Docker Container") {
            agent { 
                dockerfile {
                    dir "${JENKINSPATH}"
                    additionalBuildArgs  "--tag=${DOCKERTAG}"
                }
            }
            steps {
                sh 'python --version'
            }
        }
    }
}
