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
        // INSTALL PLAYWRIGHT
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

                echo 'GENERATING TEST FAILURE SUMMARY'

                echo '=========================================='


                bat '''

                    powershell -NoProfile -ExecutionPolicy Bypass -Command ^

                    "$xmlPath = 'test-results\\pytest-results.xml'; ^

                    if (!(Test-Path $xmlPath)) { ^

                        Write-Host ''; ^

                        Write-Host 'JUnit XML report was not generated.' -ForegroundColor Red; ^

                        exit 0 ^

                    }; ^


                    [xml]$xml = Get-Content $xmlPath; ^


                    $testCases = @($xml.testsuites.testsuite.testcase); ^


                    $total = $testCases.Count; ^

                    $passed = 0; ^

                    $failed = 0; ^

                    $skipped = 0; ^


                    foreach ($test in $testCases) { ^

                        if ($test.failure -or $test.error) { ^

                            $failed++ ^

                        } ^

                        elseif ($test.skipped) { ^

                            $skipped++ ^

                        } ^

                        else { ^

                            $passed++ ^

                        } ^

                    }; ^


                    Write-Host ''; ^

                    Write-Host '============================================================'; ^

                    Write-Host '              PLAYWRIGHT TEST EXECUTION SUMMARY'; ^

                    Write-Host '============================================================'; ^

                    Write-Host ''; ^

                    Write-Host ('TOTAL TESTS : ' + $total); ^

                    Write-Host ('PASSED      : ' + $passed); ^

                    Write-Host ('FAILED      : ' + $failed); ^

                    Write-Host ('SKIPPED     : ' + $skipped); ^

                    Write-Host ''; ^


                    if ($failed -gt 0) { ^

                        Write-Host '============================================================' -ForegroundColor Red; ^

                        Write-Host '                    FAILED TESTS' -ForegroundColor Red; ^

                        Write-Host '============================================================' -ForegroundColor Red; ^

                        Write-Host ''; ^


                        $counter = 1; ^


                        foreach ($test in $testCases) { ^

                            if ($test.failure -or $test.error) { ^

                                Write-Host '------------------------------------------------------------'; ^

                                Write-Host ($counter.ToString() + '. TEST: ' + [string]$test.name) -ForegroundColor Red; ^

                                Write-Host ('   CLASS : ' + [string]$test.classname); ^


                                $failureMessage = ''; ^


                                if ($test.failure) { ^

                                    $failureMessage = [string]$test.failure.message ^

                                } ^

                                elseif ($test.error) { ^

                                    $failureMessage = [string]$test.error.message ^

                                }; ^


                                if ([string]::IsNullOrWhiteSpace($failureMessage)) { ^

                                    $failureMessage = 'Failure message not available' ^

                                }; ^


                                Write-Host ('   ERROR : ' + $failureMessage) -ForegroundColor Yellow; ^


                                $details = ''; ^


                                if ($test.failure) { ^

                                    $details = [string]$test.failure.'#text' ^

                                } ^

                                elseif ($test.error) { ^

                                    $details = [string]$test.error.'#text' ^

                                }; ^


                                $fileFound = $false; ^


                                if ($details -match 'File \"([^\"]+)\", line ([0-9]+)') { ^

                                    Write-Host ('   FILE  : ' + $Matches[1]) -ForegroundColor Cyan; ^

                                    Write-Host ('   LINE  : ' + $Matches[2]) -ForegroundColor Cyan; ^

                                    $fileFound = $true ^

                                }; ^


                                if (!$fileFound) { ^

                                    if ($details -match '([A-Za-z0-9_./\\\\-]+\\.py):([0-9]+)') { ^

                                        Write-Host ('   FILE  : ' + $Matches[1]) -ForegroundColor Cyan; ^

                                        Write-Host ('   LINE  : ' + $Matches[2]) -ForegroundColor Cyan; ^

                                        $fileFound = $true ^

                                    } ^

                                }; ^


                                if (!$fileFound) { ^

                                    Write-Host '   FILE  : See traceback below' -ForegroundColor DarkYellow; ^

                                    Write-Host '   LINE  : See traceback below' -ForegroundColor DarkYellow ^

                                }; ^


                                Write-Host ''; ^


                                if (![string]::IsNullOrWhiteSpace($details)) { ^

                                    Write-Host '   TRACEBACK:'; ^

                                    Write-Host $details ^

                                }; ^


                                Write-Host ''; ^


                                $counter++ ^

                            } ^

                        } ^


                        Write-Host '============================================================' -ForegroundColor Red; ^

                    } ^

                    else { ^

                        Write-Host '============================================================' -ForegroundColor Green; ^

                        Write-Host '               NO FAILED TESTS' -ForegroundColor Green; ^

                        Write-Host '============================================================' -ForegroundColor Green ^

                    }; ^


                    Write-Host ''; ^

                    Write-Host 'Test summary generation completed.'"

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
        // TRAIN AI MODEL
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
        // AI PREDICTION REPORT
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

One or more Playwright tests failed.

Check:

1. Test Summary
2. Failed Test Name
3. File
4. Line Number
5. Error Message
6. Traceback

==========================================

'''
        }
    }
}
