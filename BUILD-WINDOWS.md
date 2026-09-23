# Windows packaged build

The `Build Windows Scanner` GitHub Actions workflow builds `JevGemScanner.exe` on a native Windows runner, runs the repository test suite first, and packages the executable as `JevGemScanner-Windows.zip`.

The executable starts the Solana scanner, outcome tracker, and local dashboard together in shadow mode. It stores its SQLite database in a `data` directory beside the executable and opens the dashboard at `http://127.0.0.1:8787`.
