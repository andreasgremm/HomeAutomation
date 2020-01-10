pipeline {
    agent none
    parameters {
        string(name: 'BUILDSTAGE', defaultValue: 'Not defined', description: 'Build Stage Name')
        string(name: 'JENKINSPATH', defaultValue: 'Not defined', description: 'Directory where Jenkins should build (Dockfile location)')
        string(name: 'DOCKERTAG', defaultValue: 'Not defined', description: 'Name of the Container: TAG')
    }
    stages {
        stage("${params.BUILDSTAGE}") {
            agent { 
                dockerfile {
                    dir "${params.JENKINSPATH}"
                    additionalBuildArgs  "--tag=${params.DOCKERTAG}"
                }
            }
            steps {
                sh 'python --version'
            }
        }
    }
}
