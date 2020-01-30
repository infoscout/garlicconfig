~\garlic\Scripts\activate.ps1
cget init --std=c++ --static
if ($env:ARCH) {
	cget install -DCMAKE_GENERATOR_PLATFORM=x64 --file=native_requirements.txt
} else {
	cget install --file=native_requirements.txt
}
