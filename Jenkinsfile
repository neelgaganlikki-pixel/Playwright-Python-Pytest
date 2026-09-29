pipeline {

    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {

        // =====================================================
        // PYTHON
        // =====================================================

        PYTHON = 'C:\\Users\\NEELGAGAN B R\\AppData\\Local\\Programs\\Python\\Python314\\python.exe'


        // =====================================================
        // TEST ENVIRONMENT
        // =====================================================

        TEST_ENV = 'dev'


        // =====================================================
        // ORANGEHRM
        // =====================================================

        DEV_BASE_URL = 'https://opensource-demo.orangehrmlive.com'
        DEV_USERNAME = 'Admin'
        DEV_PASSWORD = 'admin123'


        // =====================================================
        // PLAYWRIGHT
        // =====================================================

        BROWSER = 'chromium'
        HEADLESS = 'true'
        SLOW_MO = '0'


        // =====================================================
        // RESULT DIRECTORIES
        // =====================================================

        TEST_RESULTS_DIR = 'test-results'
        SCREENSHOTS_DIR = 'screenshots'
    }


    stages {

        // =====================================================
        // 1. CHECKOUT
        // =====================================================

        stage('Checkout') {

            steps {

                echo '========================================'
                echo 'CHECKOUT'
                echo '========================================'

                checkout scm
            }
        }


        // =====================================================
        // 2. CHECK PYTHON
        // =====================================================

        stage('Check Python') {

            steps {

                echo '========================================'
                echo 'PYTHON INFORMATION'
                echo '========================================'

                bat '''
                    "%PYTHON%" --version

                    echo.

                    "%PYTHON%" -m pip --version
                '''
            }
        }


        // =====================================================
        // 3. CREATE ENVIRONMENT FILE
        // =====================================================

        stage('Create Environment File') {

            steps {

                echo '========================================'
                echo 'CREATING .ENV FILE'
                echo '========================================'

                bat '''
                    (
                        echo TEST_ENV=%TEST_ENV%
                        echo DEV_BASE_URL=%DEV_BASE_URL%
                        echo DEV_USERNAME=%DEV_USERNAME%
                        echo DEV_PASSWORD=%DEV_PASSWORD%
                        echo BROWSER=%BROWSER%
                        echo HEADLESS=%HEADLESS%
                        echo SLOW_MO=%SLOW_MO%
                    ) > .env

                    echo .env created successfully.
                '''
            }
        }


        // =====================================================
        // 4. SETUP PYTHON ENVIRONMENT
        // =====================================================

        stage('Setup Python Environment') {

            steps {

                echo '========================================'
                echo 'SETTING UP PYTHON ENVIRONMENT'
                echo '========================================'

                bat '''
                    if exist .jenkins-venv (
                        echo Existing virtual environment found.
                    ) else (
                        echo Creating virtual environment...
                        "%PYTHON%" -m venv .jenkins-venv
                    )

                    echo.

                    .jenkins-venv\\Scripts\\python.exe --version

                    echo.

                    .jenkins-venv\\Scripts\\python.exe -m pip install --upgrade pip
                '''
            }
        }


        // =====================================================
        // 5. INSTALL DEPENDENCIES
        // =====================================================

        stage('Install Dependencies') {

            steps {

                echo '========================================'
                echo 'INSTALLING PYTHON DEPENDENCIES'
                echo '========================================'

                bat '''
                    .jenkins-venv\\Scripts\\python.exe -m pip install -r requirements.txt
                '''
            }
        }


        // =====================================================
        // 6. INSTALL PLAYWRIGHT BROWSERS
        // =====================================================

        stage('Install Playwright Browsers') {

            steps {

                echo '========================================'
                echo 'INSTALLING PLAYWRIGHT CHROMIUM'
                echo '========================================'

                bat '''
                    .jenkins-venv\\Scripts\\python.exe -m playwright install chromium
                '''
            }
        }


        // =====================================================
        // 7. CREATE RESULT DIRECTORIES
        // =====================================================

        stage('Create Result Directories') {

            steps {

                echo '========================================'
                echo 'CREATING TEST RESULT DIRECTORIES'
                echo '========================================'

                bat '''
                    if not exist "%TEST_RESULTS_DIR%" mkdir "%TEST_RESULTS_DIR%"

                    if not exist "%SCREENSHOTS_DIR%" mkdir "%SCREENSHOTS_DIR%"
                '''
            }
        }


        // =====================================================
        // 8. RUN TESTS
        // =====================================================

        stage('Run Tests') {

            steps {

                script {

                    echo '========================================'
                    echo 'RUNNING PLAYWRIGHT PYTEST TESTS'
                    echo '========================================'

                    def result = bat(
                        script: '''
                            .jenkins-venv\\Scripts\\python.exe -m pytest tests -v -s ^
                                --tb=long ^
                                --junitxml=test-results\\pytest-results.xml
                        ''',
                        returnStatus: true
                    )

                    env.PYTEST_EXIT_CODE = result.toString()

                    echo ''
                    echo "Pytest Exit Code: ${env.PYTEST_EXIT_CODE}"
                    echo ''

                    /*
                     * Do not fail the pipeline here.
                     *
                     * Test results will still be archived
                     * in the Post Actions section.
                     */
                }
            }
        }
    }


    // =========================================================
    // POST ACTIONS
    // =========================================================

    post {

        always {

            echo ''
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
        }


        success {

            echo ''
            echo '========================================'
            echo 'PIPELINE COMPLETED'
            echo '========================================'

            echo 'Jenkins pipeline completed successfully.'
        }


        failure {

            echo ''
            echo '========================================'
            echo 'PIPELINE FAILED'
            echo '========================================'

            echo "Pytest Exit Code: ${env.PYTEST_EXIT_CODE}"

            echo ''
            echo 'Check the archived test-results for details.'
        }


        cleanup {

            echo ''
            echo '========================================'
            echo 'CLEANUP'
            echo '========================================'

            bat '''
                if exist __pycache__ (
                    rmdir /s /q __pycache__ 2>nul
                )
            '''
        }
    }
}
