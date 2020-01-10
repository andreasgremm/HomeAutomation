pipeline {
    agent none
    parameters {
        string(name: 'BUILDSTAGE', defaultValue: 'Not defined', description: 'Build Stage Name')
        string(name: 'JENKINSPATH', defaultValue: 'Not defined', description: 'Directory where Jenkins should build (Dockfile location)')
        string(name: 'DOCKERTAG', defaultValue: 'Not defined', description: 'Name of the Container: TAG')
    }
    stages {
        stage(${BUILDSTAGE}) {
            agent { 
                dockerfile {
                    dir ${JENKINSPATH}
                    additionalBuildArgs  "--tag=${DOCKERTAG}"
                }
            }
            steps {
                sh 'python --version'
            }
        }
    }
}
