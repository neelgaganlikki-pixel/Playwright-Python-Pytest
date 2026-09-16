pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Users\\NEELGAGAN B R\\AppData\\Local\\Programs\\Python\\Python314\\python.exe'
        PYTHONUNBUFFERED = '1'

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

        BROWSER = 'chromium'
        HEADLESS = 'true'
        SLOW_MO = '0'

        SCREENSHOT_ON_FAILURE = 'true'
        VIDEO_ON_FAILURE = 'true'
        TRACE_ON_FAILURE = 'true'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out Playwright-Pytest project...'
            }
        }

        stage('Check Python') {
            steps {
                bat '''
                    "%PYTHON%" --version
                '''
            }
        }

        stage('Create Environment File') {
            steps {
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

                    echo Environment configuration created for Jenkins.
                '''
            }
        }

        stage('Setup Python Environment') {
            steps {
                bat '''
                    if exist .jenkins-venv rmdir /s /q .jenkins-venv

                    "%PYTHON%" -m venv .jenkins-venv

                    .jenkins-venv\\Scripts\\python.exe -m pip install --upgrade pip
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                    .jenkins-venv\\Scripts\\python.exe -m pip install -r requirements.txt
                '''
            }
        }

        stage('Install Playwright Browsers') {
            steps {
                bat '''
                    .jenkins-venv\\Scripts\\python.exe -m playwright install chromium
                '''
            }
        }

        stage('Run Tests') {
            steps {
                catchError(
                    buildResult: 'FAILURE',
                    stageResult: 'FAILURE'
                ) {
                    bat '''
                        if not exist test-results mkdir test-results

                        .jenkins-venv\\Scripts\\python.exe -m pytest tests -v -s --junitxml=test-results\\pytest-results.xml
                    '''
                }
            }
        }

        stage('Test Summary') {
            steps {
                bat '''
                    echo.
                    echo ==========================================
                    echo       PLAYWRIGHT TEST SUMMARY
                    echo ==========================================

                    powershell -NoProfile -Command "$xml = [xml](Get-Content 'test-results\\pytest-results.xml'); $testCases = @($xml.testsuites.testsuite.testcase); $modules = @{}; foreach ($test in $testCases) { $className = [string]$test.classname; if ($className -match 'tests[\\\\/.]([^\\\\/.]+)') { $moduleName = $Matches[1]; if (-not $modules.ContainsKey($moduleName)) { $modules[$moduleName] = @() }; $modules[$moduleName] += $test } }; $moduleNames = @($modules.Keys | Sort-Object); $passedModules = 0; $failedModules = 0; $skippedModules = 0; foreach ($moduleName in $moduleNames) { $moduleTests = @($modules[$moduleName]); $failed = @($moduleTests | Where-Object { $_.failure -or $_.error }).Count; $skipped = @($moduleTests | Where-Object { $_.skipped }).Count; if ($failed -gt 0) { $status = 'FAILED'; $failedModules++ } elseif ($skipped -eq $moduleTests.Count) { $status = 'SKIPPED'; $skippedModules++ } else { $status = 'PASSED'; $passedModules++ }; $displayName = (Get-Culture).TextInfo.ToTitleCase($moduleName.Replace('_',' ')); Write-Host ($displayName.PadRight(12) + ' -> ' + $status) }; Write-Host ''; Write-Host '=========================================='; Write-Host '       PLAYWRIGHT TEST SUMMARY'; Write-Host '=========================================='; $totalModules = $moduleNames.Count; Write-Host ('Total Tests : ' + $totalModules); Write-Host ('Passed      : ' + $passedModules); Write-Host ('Failed      : ' + $failedModules); Write-Host ('Skipped     : ' + $skippedModules); Write-Host '=========================================='"
                '''
            }
        }

        // --- NEW AI PIPELINE STAGES ---

        stage('Run AI Data Parser') {
            steps {
                bat '''
                    .jenkins-venv\\Scripts\\python.exe ml/parse_results.py
                '''
            }
        }

        stage('Train AI Failure Prediction Model') {
            steps {
                bat '''
                    .jenkins-venv\\Scripts\\python.exe ml/train_model.py
                '''
            }
        }
    }

    post {
        always {
            echo 'Jenkins test execution completed.'

            bat '''
                if exist .env del /q .env
            '''
        }

        success {
            echo 'All Playwright-Pytest test areas passed successfully.'
        }

        failure {
            echo 'Playwright-Pytest execution failed. Check the console output.'
        }
    }
}