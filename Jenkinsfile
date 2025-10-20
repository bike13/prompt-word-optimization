pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'prompt-word-optimization'
        DOCKER_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    // 构建Docker镜像
                    sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                    sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
                }
            }
        }
        
 
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                script {
                    // 停止旧容器
                    sh "docker stop prompt-optimization || true"
                    sh "docker rm prompt-optimization || true"
                    
                    // 启动新容器
                    sh """
                        docker run -d \\
                            --name prompt-optimization \\
                            --restart unless-stopped \\
                            -p 9080:9080 \\
                            ${DOCKER_IMAGE}:${DOCKER_TAG}
                    """
                }
            }
        }
    }
    
    post {
        always {
 
            
            // 清理旧镜像（保留最近5个版本）
            sh """
                docker images ${DOCKER_IMAGE} --format "table {{.Tag}}" | tail -n +2 | head -n -5 | xargs -r docker rmi ${DOCKER_IMAGE}: || true
            """
        }
        
        success {
            echo 'Build successful!'
        }
        
        failure {
            echo 'Build failed!'
        }
    }
}
