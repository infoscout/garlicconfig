~\garlic\Scripts\activate.ps1
cget init --std=c++ --static
cget install -DCMAKE_GENERATOR_PLATFORM=$ARCH --file=native_requirements.txt
