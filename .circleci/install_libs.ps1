~\garlic\Scripts\activate.ps1
cget init --std=c++ --static
cget install -DCMAKE_GENERATOR_PLATFORM=$env:ARCH --file=native_requirements.txt
