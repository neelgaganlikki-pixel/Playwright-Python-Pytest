pipeline {

    agent any

    environment {

        // ============================================================
        // PYTHON
        // ============================================================

        PYTHON = 'C:\\Users\\NEELGAGAN B R\\AppData\\Local\\Programs\\Python\\Python314\\python.exe'

        PYTHONUNBUFFERED = '1'


        // ============================================================
        // TEST ENVIRONMENT
        // ============================================================

        TEST_ENV = 'dev'

        DEV_BASE_URL = 'https://opensource-demo.orangehrmlive.com'
        DEV_USERNAME = 'Admin'
        DEV_PASSWORD = 'admin123'

        QA_BASE_URL = 'https://opensource-demo.orangehrmlive.com'
        QA_USERNAME = 'Admin'
        QA_PASSWORD = 'admin123'

        UAT_BASE_URL = 'https://opensource-demo.orangehrmlive.com'
        UAT_USERNAME = 'Admin'
        UAT_PASSWORD = 'admin123'

        PROD_BASE_URL = 'https://opensource-demo.orangehrmlive.com'
        PROD_USERNAME = 'Admin'
        PROD_PASSWORD = 'admin123'


        // ============================================================
        // PLAYWRIGHT
        // ============================================================

        BROWSER = 'chromium'
        HEADLESS = 'true'
        SLOW_MO = '0'


        // ============================================================
        // FAILURE ARTIFACTS
        // ============================================================

        SCREENSHOT_ON_FAILURE = 'true'
        VIDEO_ON_FAILURE = 'true'
        TRACE_ON_FAILURE = 'true'
    }


    stages {


        // ============================================================
        // CHECKOUT
        // ============================================================

        stage('Checkout') {

            steps {

                echo '=========================================='
                echo 'CHECKING OUT PROJECT'
                echo '=========================================='

                echo 'Jenkins SCM checkout is being used.'
            }
        }


        // ============================================================
        // CHECK PYTHON
        // ============================================================

        stage('Check Python') {

            steps {

                echo '=========================================='
                echo 'CHECKING PYTHON'
                echo '=========================================='

                bat '''
                    "%PYTHON%" --version

                    "%PYTHON%" -m pip --version
                '''
            }
        }


        // ============================================================
        // CREATE ENVIRONMENT FILE
        // ============================================================

        stage('Create Environment File') {

            steps {

                echo 'Creating Jenkins environment configuration...'

                bat '''
                    (
                        echo TEST_ENV=%TEST_ENV%

                        echo DEV_BASE_URL=%DEV_BASE_URL%
                        echo DEV_USERNAME=%DEV_USERNAME%
                        echo DEV_PASSWORD=%DEV_PASSWORD%

                        echo QA_BASE_URL=%QA_BASE_URL%
                        echo QA_USERNAME=%QA_USERNAME%
                        echo QA_PASSWORD=%QA_PASSWORD%

                        echo UAT_BASE_URL=%UAT_BASE_URL%
                        echo UAT_USERNAME=%UAT_USERNAME%
                        echo UAT_PASSWORD=%UAT_PASSWORD%

                        echo PROD_BASE_URL=%PROD_BASE_URL%
                        echo PROD_USERNAME=%PROD_USERNAME%
                        echo PROD_PASSWORD=%PROD_PASSWORD%

                        echo BROWSER=%BROWSER%
                        echo HEADLESS=%HEADLESS%
                        echo SLOW_MO=%SLOW_MO%

                        echo SCREENSHOT_ON_FAILURE=%SCREENSHOT_ON_FAILURE%
                        echo VIDEO_ON_FAILURE=%VIDEO_ON_FAILURE%
                        echo TRACE_ON_FAILURE=%TRACE_ON_FAILURE%

                    ) > .env

                    echo Environment configuration created.
                '''
            }
        }


        // ============================================================
        // CREATE PYTHON VIRTUAL ENVIRONMENT
        // ============================================================

        stage('Setup Python Environment') {

            steps {

                echo '=========================================='
                echo 'CREATING PYTHON VIRTUAL ENVIRONMENT'
                echo '=========================================='

                bat '''
                    if exist .jenkins-venv rmdir /s /q .jenkins-venv

                    "%PYTHON%" -m venv .jenkins-venv

                    .jenkins-venv\\Scripts\\python.exe -m pip install --upgrade pip
                '''
            }
        }


        // ============================================================
        // INSTALL DEPENDENCIES
        // ============================================================

        stage('Install Dependencies') {

            steps {

                echo '=========================================='
                echo 'INSTALLING PYTHON DEPENDENCIES'
                echo '=========================================='

                bat '''
                    .jenkins-venv\\Scripts\\python.exe -m pip install -r requirements.txt
                '''
            }
        }


        // ============================================================
        // INSTALL PLAYWRIGHT BROWSER
        // ============================================================

        stage('Install Playwright Browsers') {

            steps {

                echo '=========================================='
                echo 'INSTALLING PLAYWRIGHT CHROMIUM'
                echo '=========================================='

                bat '''
                    .jenkins-venv\\Scripts\\python.exe -m playwright install chromium
                '''
            }
        }


        // ============================================================
        // RUN TESTS
        // ============================================================

        stage('Run Tests') {

            steps {

                catchError(
                    buildResult: 'FAILURE',
                    stageResult: 'FAILURE'
                ) {

                    bat '''

                        echo.
                        echo ==========================================
                        echo       STARTING PLAYWRIGHT TESTS
                        echo ==========================================

                        if not exist test-results mkdir test-results

                        if not exist screenshots mkdir screenshots


                        .jenkins-venv\\Scripts\\python.exe -m pytest tests -v -s --tb=long --junitxml=test-results\\pytest-results.xml


                        echo.
                        echo ==========================================
                        echo       PYTEST EXECUTION COMPLETED
                        echo ==========================================

                    '''
                }
            }
        }


        // ============================================================
        // TEST SUMMARY
        // ============================================================

        stage('Test Summary') {

            steps {

                echo '=========================================='
                echo 'GENERATING TEST SUMMARY'
                echo '=========================================='


                bat '''

                    if not exist test-results\\pytest-results.xml (

                        echo.
                        echo ==========================================
                        echo ERROR: JUnit XML REPORT NOT FOUND
                        echo ==========================================

                        exit /b 0
                    )


                    echo.
                    echo ==========================================
                    echo       PLAYWRIGHT TEST SUMMARY
                    echo ==========================================


                    .jenkins-venv\\Scripts\\python.exe -c "import xml.etree.ElementTree as ET; root=ET.parse('test-results\\\\pytest-results.xml').getroot(); tests=root.findall('.//testcase'); failed=[t for t in tests if t.find('failure') is not None or t.find('error') is not None]; skipped=[t for t in tests if t.find('skipped') is not None]; passed=len(tests)-len(failed)-len(skipped); print(''); print('TOTAL TESTS :',len(tests)); print('PASSED      :',passed); print('FAILED      :',len(failed)); print('SKIPPED     :',len(skipped)); print(''); print('=========================================='); print('FAILED TESTS'); print('=========================================='); [(print(''), print('TEST :',t.get('name')), print('CLASS:',t.get('classname')), print('FILE :',t.get('file','Not available')), print('LINE :',t.get('line','Not available')), print('ERROR:',(t.find('failure').get('message') if t.find('failure') is not None else t.find('error').get('message') if t.find('error') is not None else 'Unknown')), print('TRACEBACK:'), print((t.find('failure').text if t.find('failure') is not None else t.find('error').text if t.find('error') is not None else 'Not available')), print('------------------------------------------')) for t in failed]; print(''); print('=========================================='); print('END OF TEST SUMMARY'); print('==========================================')"


                    echo.

                '''
            }
        }


        // ============================================================
        // AI DATA PARSER
        // ============================================================

        stage('Run AI Data Parser') {

            steps {

                echo '=========================================='
                echo 'RUNNING AI DATA PARSER'
                echo '=========================================='

                bat '''

                    .jenkins-venv\\Scripts\\python.exe ml/parse_results.py

                '''
            }
        }


        // ============================================================
        // TRAIN AI FAILURE PREDICTION MODEL
        // ============================================================

        stage('Train AI Failure Prediction Model') {

            steps {

                echo '=========================================='
                echo 'TRAINING AI FAILURE PREDICTION MODEL'
                echo '=========================================='

                bat '''

                    .jenkins-venv\\Scripts\\python.exe ml/train_model.py

                '''
            }
        }


        // ============================================================
        // GENERATE AI PREDICTION REPORT
        // ============================================================

        stage('Generate AI Prediction Report') {

            steps {

                echo '=========================================='
                echo 'AI TEST FAILURE RISK PREDICTION'
                echo '=========================================='

                bat '''

                    .jenkins-venv\\Scripts\\python.exe ml/predict.py

                '''
            }
        }
    }


    // ================================================================
    // POST BUILD
    // ================================================================

    post {

        always {

            echo '=========================================='
            echo 'JENKINS EXECUTION COMPLETED'
            echo '=========================================='


            bat '''

                if exist .env del /q .env

            '''
        }


        success {

            echo '''

==========================================
       BUILD SUCCESSFUL
==========================================

All Playwright tests passed successfully.

==========================================

'''
        }


        failure {

            echo '''

==========================================
          BUILD FAILED
==========================================

One or more Playwright tests failed,
or a pipeline stage failed.

Check the Jenkins Console Output.

The failure summary contains:

1. Test Name
2. Test Class
3. Test File
4. Test Line
5. Error Message
6. Traceback

==========================================

'''
        }
    }
}
