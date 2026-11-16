// OCR a question paper that has no text layer, page by page.
//
//   swift scripts/ocr_pdf_pages.swift <question-paper.pdf> > <transcript.txt>
//
// For the one paper in the bank that Pearson publishes only as an image-only
// scan - Edexcel B AS Paper 2 June 2019 ("Microsoft: Print To PDF"; PDFKit
// reads 24 blank pages, and no text-layer copy exists anywhere, checked by
// Eliot 2026-11-16). Uses Apple's Vision framework, which ships with macOS as
// PDFKit does: no new dependency.
//
// The output is a DRAFT. It becomes the source for that paper only after it is
// checked word by word against the page images and its quotes and dashes are
// set to the printed ones (‘ ’ –, which OCR reads as ' and -), and is then
// committed under past-paper-questions-data/ocr/, where
// extract_past_paper_questions.swift reads it in place of the empty text
// layer. It is NOT re-run as part of any build: OCR output can shift between
// macOS versions, and the bank's text must not drift with it.
//
// Each page is printed under the same "=== PAGE n ===" marker the extractor's
// transcript reader expects. The outer 5.5% of each side is cropped before
// recognition: that is where the rotated "DO NOT WRITE IN THIS AREA" warnings
// sit, and OCR otherwise scatters fragments of them ("KARE", "ISAREA") into
// the question text.

import AppKit
import Foundation
import PDFKit
import Vision

let args = Array(CommandLine.arguments.dropFirst())
guard args.count == 1, let doc = PDFDocument(url: URL(fileURLWithPath: args[0])) else {
    FileHandle.standardError.write(
        "usage: swift scripts/ocr_pdf_pages.swift <question-paper.pdf>\n".data(using: .utf8)!)
    exit(2)
}

let scale: CGFloat = 3
let margin: CGFloat = 0.055

for i in 0..<doc.pageCount {
    guard let page = doc.page(at: i) else { continue }
    let box = page.bounds(for: .mediaBox)
    let image = page.thumbnail(
        of: NSSize(width: box.width * scale, height: box.height * scale), for: .mediaBox)
    var rect = CGRect(origin: .zero, size: image.size)
    guard let cg = image.cgImage(forProposedRect: &rect, context: nil, hints: nil) else { continue }

    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    request.recognitionLanguages = ["en-GB"]
    // Normalised coordinates, origin bottom-left: drop both side margins.
    request.regionOfInterest = CGRect(x: margin, y: 0, width: 1 - 2 * margin, height: 1)
    try? VNImageRequestHandler(cgImage: cg).perform([request])

    // Reading order: top to bottom, then left to right within a line.
    let lines = (request.results ?? []).sorted { a, b in
        abs(a.boundingBox.midY - b.boundingBox.midY) > 0.008
            ? a.boundingBox.midY > b.boundingBox.midY
            : a.boundingBox.minX < b.boundingBox.minX
    }
    print("=================== PAGE \(i + 1) ===================")
    for line in lines {
        if let text = line.topCandidates(1).first?.string { print(text) }
    }
}
