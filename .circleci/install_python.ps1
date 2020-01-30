cd ~
nuget install $PYTHON_NAME -Version $PYTHON_VERSION -ExcludeVersion -OutputDirectory .
$PYTHON_NAME\tools\python.exe -m pip install virtualenv
$PYTHON_NAME\tools\python.exe -m virtualenv garlic
garlic\Scripts\activate.ps1
cd project
pip install -r requirements.txt
