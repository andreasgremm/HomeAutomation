pipeline {
    agent none

    stages {
        stage('${params.BUILDSTAGE}') {
            agent { 
                dockerfile {
                    dir '${params.JENKINSPATH}'
                    additionalBuildArgs  '--tag=${params.DOCKERTAG}'
                }
            }
            steps {
                sh 'python --version'
            }
        }
    }
}
