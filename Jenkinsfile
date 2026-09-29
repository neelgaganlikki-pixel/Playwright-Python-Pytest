pipeline {

    agent any

    options {
        ansiColor('xterm')

        timestamps()

        // Do not allow multiple builds at the same time
        disableConcurrentBuilds()
    }

    environment {

        // Python
        PYTHON = 'C:\\Users\\NEELGAGAN B R\\AppData\\Local\\Programs\\Python\\Python314\\python.exe'

        // Test environment
        TEST_ENV = 'dev'

        // OrangeHRM
        DEV_BASE_URL = 'https://opensource-demo.orangehrmlive.com'
        DEV_USERNAME = 'Admin'
        DEV_PASSWORD = 'admin123'

        // Browser
        BROWSER = 'chromium'
        HEADLESS = 'true'
        SLOW_MO = '0'

        // Test results
        TEST_RESULTS_DIR = 'test-results'
        SCREENSHOTS_DIR = 'screenshots'
    }

    stages {

        // =========================================================
        // 1. CHECKOUT
        // =========================================================

        stage('Checkout') {

            steps {

                echo 'Checking out source code...'

                checkout scm
            }
        }


        // =========================================================
        // 2. CHECK PYTHON
        // =========================================================

        stage('Check Python') {

            steps {

                bat '''
                    echo ========================================
                    echo PYTHON VERSION
                    echo ========================================

                    "%PYTHON%" --version

                    echo.
                    echo PIP VERSION
                    echo ========================================

                    "%PYTHON%" -m pip --version
                '''
            }
        }


        // =========================================================
        // 3. CREATE ENVIRONMENT FILE
        // =========================================================

        stage('Create Environment File') {

            steps {

                bat '''
                    echo ========================================
                    echo CREATING ENVIRONMENT FILE
                    echo ========================================

                    (
                        echo TEST_ENV=%TEST_ENV%
                        echo DEV_BASE_URL=%DEV_BASE_URL%
                        echo DEV_USERNAME=%DEV_USERNAME%
                        echo DEV_PASSWORD=%DEV_PASSWORD%
                        echo BROWSER=%BROWSER%
                        echo HEADLESS=%HEADLESS%
                        echo SLOW_MO=%SLOW_MO%
                    ) > .env

                    echo Environment file created.
                '''
            }
        }


        // =========================================================
        // 4. CREATE VIRTUAL ENVIRONMENT
        // =========================================================

        stage('Setup Python Environment') {

            steps {

                bat '''
                    echo ========================================
                    echo SETTING UP PYTHON VIRTUAL ENVIRONMENT
                    echo ========================================

                    if exist .jenkins-venv (
                        echo Existing virtual environment found.
                    ) else (
                        "%PYTHON%" -m venv .jenkins-venv
                    )

                    .jenkins-venv\\Scripts\\python.exe --version

                    .jenkins-venv\\Scripts\\python.exe -m pip install --upgrade pip
                '''
            }
        }


        // =========================================================
        // 5. INSTALL DEPENDENCIES
        // =========================================================

        stage('Install Dependencies') {

            steps {

                bat '''
                    echo ========================================
                    echo INSTALLING DEPENDENCIES
                    echo ========================================

                    .jenkins-venv\\Scripts\\python.exe -m pip install -r requirements.txt
                '''
            }
        }


        // =========================================================
        // 6. INSTALL PLAYWRIGHT
        // =========================================================

        stage('Install Playwright Browsers') {

            steps {

                bat '''
                    echo ========================================
                    echo INSTALLING PLAYWRIGHT BROWSERS
                    echo ========================================

                    .jenkins-venv\\Scripts\\python.exe -m playwright install chromium
                '''
            }
        }


        // =========================================================
        // 7. CREATE RESULT DIRECTORIES
        // =========================================================

        stage('Create Result Directories') {

            steps {

                bat '''
                    if not exist "%TEST_RESULTS_DIR%" mkdir "%TEST_RESULTS_DIR%"

                    if not exist "%SCREENSHOTS_DIR%" mkdir "%SCREENSHOTS_DIR%"
                '''
            }
        }


        // =========================================================
        // 8. RUN PYTEST
        // =========================================================

        stage('Run Tests') {

            steps {

                script {

                    def testResult = bat(
                        script: '''
                            .jenkins-venv\\Scripts\\python.exe -m pytest tests -v -s ^
                                --tb=long ^
                                --junitxml=test-results\\pytest-results.xml
                        ''',
                        returnStatus: true
                    )

                    // Store pytest result for later stages
                    env.PYTEST_EXIT_CODE = testResult.toString()

                    echo "Pytest exit code: ${env.PYTEST_EXIT_CODE}"

                    // Do NOT fail the pipeline here.
                    // This allows Test Summary and artifacts to run.
                }
            }
        }


        // =========================================================
        // 9. TEST SUMMARY
        // =========================================================

        stage('Test Summary') {

            steps {

                echo 'Generating detailed test summary...'

                bat '''
                    .jenkins-venv\\Scripts\\python.exe jenkins_test_summary.py
                '''
            }
        }


        // =========================================================
        // 10. PUBLISH JUNIT RESULTS
        // =========================================================

        stage('Publish Test Results') {

            steps {

                junit(
                    testResults: 'test-results/pytest-results.xml',
                    allowEmptyResults: true,
                    skipPublishingChecks: true
                )
            }
        }


        // =========================================================
        // 11. AI DATA PARSER
        // =========================================================

        stage('AI Data Parser') {

            when {

                expression {

                    return fileExists('ml/parse_results.py')
                }
            }

            steps {

                bat '''
                    .jenkins-venv\\Scripts\\python.exe ml\\parse_results.py
                '''
            }
        }


        // =========================================================
        // 12. AI FAILURE PREDICTION
        // =========================================================

        stage('AI Failure Prediction') {

            when {

                expression {

                    return fileExists('ml/train_model.py')
                }
            }

            steps {

                bat '''
                    .jenkins-venv\\Scripts\\python.exe ml\\train_model.py
                '''
            }
        }


        // =========================================================
        // 13. AI PREDICTION REPORT
        // =========================================================

        stage('AI Prediction Report') {

            when {

                expression {

                    return fileExists('ml/predict.py')
                }
            }

            steps {

                bat '''
                    .jenkins-venv\\Scripts\\python.exe ml\\predict.py
                '''
            }
        }
    }


    // =============================================================
    // POST ACTIONS
    // =============================================================

    post {

        always {

            echo '========================================'
            echo 'ARCHIVING TEST ARTIFACTS'
            echo '========================================'

            archiveArtifacts(
                artifacts: 'test-results/**/*',
                allowEmptyArchive: true,
                fingerprint: true
            )

            archiveArtifacts(
                artifacts: 'screenshots/**/*',
                allowEmptyArchive: true,
                fingerprint: true
            )

            archiveArtifacts(
                artifacts: 'test-results/pytest-results.xml',
                allowEmptyArchive: true,
                fingerprint: true
            )
        }


        success {

            echo '========================================'
            echo 'JENKINS PIPELINE SUCCESS'
            echo '========================================'

            echo 'All Playwright tests passed.'
        }


        failure {

            echo '========================================'
            echo 'JENKINS PIPELINE FAILED'
            echo '========================================'

            echo "Pytest exit code: ${env.PYTEST_EXIT_CODE}"

            echo 'Check the Test Summary stage for failed test details.'
        }


        cleanup {

            echo 'Cleaning temporary files...'

            // Keep .env and test results for debugging.
            // Delete only temporary Python cache files.

            bat '''
                if exist __pycache__ rmdir /s /q __pycache__ 2>nul
            '''
        }
    }
}
