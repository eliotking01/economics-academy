// Print the plain text of each PDF, each preceded by an @@@FILE line.
//
//   swift scripts/pdf_text.swift <file.pdf> ...
//
// The four-line Swift + PDFKit extractor docs/QUESTIONS_PROGRESS.md section 7
// describes, committed so the originality corpora can be rebuilt rather than
// hunted for in old scratchpads. scripts/check_originality.py drives it.
// Do not replace it with a stdlib PDF parser: the papers' content streams use
// subsetted fonts with custom encodings, and only PDFKit reads them properly.

import Foundation
import PDFKit

for path in CommandLine.arguments.dropFirst() {
    guard let doc = PDFDocument(url: URL(fileURLWithPath: path)) else {
        FileHandle.standardError.write("cannot open \(path)\n".data(using: .utf8)!)
        continue
    }
    print("@@@FILE \(path)")
    print(doc.string ?? "")
}
