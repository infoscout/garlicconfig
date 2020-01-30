cd ~
nuget install $env:PYTHON_NAME -Version $env:PYTHON_VERSION -ExcludeVersion -OutputDirectory .
& "$env:PYTHON_NAME\tools\python.exe" -m pip install virtualenv
& "$env:PYTHON_NAME\tools\python.exe" -m virtualenv garlic
garlic\Scripts\activate.ps1
cd project
pip install -r requirements.txt
