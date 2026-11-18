// Jenkins job name: MIDTERM-FA23-BDS-024
// Required plugins: Pipeline, Git, GitHub, Mailer (for 'mail').
pipeline {
    agent any
    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
        timestamps()
        timeout(time: 12, unit: 'MINUTES')
    }
    triggers {
        githubPush()
    }
    environment {
        IMAGE = 'ali024024/devops-lab-mid'
        CONTAINER = 'midterm-fa23-bds-024'
        STUDENT_ID = 'FA23-BDS-024'
        EC2_PRIVATE_IP = '172.31.18.147'
        EC2_PUBLIC_IP = '54.235.141.196'
        // CHANGE THIS to the actual Gmail/SMTP sender configured in Jenkins.
        SENDER_EMAIL = 'b63256871@gmail.com'
    }
    stages {
        stage('Checkout latest GitHub dataset') {
            steps {
                checkout scm
                script {
                    env.REVISION = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
                    echo "Training from commit ${env.REVISION}"
                }
            }
        }
        stage('Prerequisites') {
            steps {
                sh '''
                    set -eu
                    docker version
                    test -s config.json
                    test -s dataset/train.csv
                    test -f train.py
                    test -f Dockerfile
                '''
            }
        }
        stage('Retrain, test and build Docker image') {
            steps {
                sh '''
                    set -eu
                    docker build --progress=plain \
                      --build-arg BUILD_COMMIT="$REVISION" \
                      -t "$IMAGE:$REVISION" \
                      -t "$IMAGE:latest" .
                '''
            }
        }
        stage('Redeploy only this midterm container') {
            steps {
                sh '''
                    set -eu
                    # Never remove any pre-existing unrelated lab container.
                    if docker container inspect "$CONTAINER" >/dev/null 2>&1; then
                        owner=$(docker inspect --format '{{ index .Config.Labels "devops.midterm.student" }}' "$CONTAINER")
                        if [ "$owner" != "$STUDENT_ID" ]; then
                            echo "ABORT: container name exists but does not belong to this midterm"
                            exit 1
                        fi
                        docker rm -f "$CONTAINER"
                    fi
                    # Bind 8000 on the EC2 private IP, leaving 127.0.0.1:8000 Gunicorn untouched.
                    docker run -d --restart unless-stopped \
                      --name "$CONTAINER" \
                      --label "devops.midterm.student=$STUDENT_ID" \
                      -p "$EC2_PRIVATE_IP:8000:8000" \
                      "$IMAGE:$REVISION"
                '''
            }
        }
        stage('Verify deployed model') {
            steps {
                sh '''
                    set -eu
                    # Must show the current Git SHA, not a stale model.
                    curl -fsS --retry 8 --retry-delay 2 --retry-connrefused \
                      "http://$EC2_PRIVATE_IP:8000/health"
                    curl -fsS --retry 8 --retry-delay 2 --retry-connrefused \
                      "http://$EC2_PRIVATE_IP:8000/metrics" > /tmp/midterm-metrics.json
                    cat /tmp/midterm-metrics.json
                    grep -Fq "$REVISION" /tmp/midterm-metrics.json
                '''
            }
        }
        stage('Publish updated model image to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-ali024024',
                                  usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_TOKEN')]) {
                    sh '''
                        set +x
                        printf '%s' "$DOCKER_TOKEN" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push "$IMAGE:$REVISION"
                        docker push "$IMAGE:latest"
                    '''
                }
            }
        }
    }
    post {
        always {
            script {
                // Notify only the latest Git commit author.
                // GitHub noreply addresses cannot receive SMTP notifications.
                def authorEmail = ''
                try {
                    if (fileExists('.git')) {
                        authorEmail = sh(
                            script: 'git log -1 --format=%ae',
                            returnStdout: true
                        ).trim()
                    }
                } catch (Exception err) {
                    echo "Could not determine commit author email: ${err.message}"
                }

                def usableAuthorEmail = authorEmail.contains('@') &&
                    !authorEmail.contains(' ') &&
                    !authorEmail.toLowerCase().contains('noreply')

                if (usableAuthorEmail) {
                    echo "Notifying commit author: ${authorEmail}"
                    mail to: authorEmail,
                         from: env.SENDER_EMAIL,
                         subject: "${env.STUDENT_ID} Jenkins build ${currentBuild.currentResult}: ${env.BUILD_NUMBER}",
                         body: "Student: ${env.STUDENT_ID}\nResult: ${currentBuild.currentResult}\nCommit author: ${authorEmail}\nCommit: ${env.REVISION ?: 'not checked out'}\nGitHub: https://github.com/muhammad-ali-arshad/Devops-lab-mid\nMetrics: http://${env.EC2_PUBLIC_IP}:8000/metrics\nJob: ${env.BUILD_URL}\n"
                } else {
                    echo "No deliverable email for latest commit author; notification skipped."
                }
            }
        }
    }
}
