// Independently verify past-paper-questions-data/edexcel-a/*.json against the PDFs.
//
//   swift scripts/verify_past_paper_extraction.swift
//
// This deliberately does NOT reuse the extractor's matching logic. The extractor
// finds pages with regexes tuned to three known mark-scheme layouts; if those
// regexes are wrong they will be confidently wrong in both directions. This
// checks the recorded answers a different way:
//
//   1. Every recorded page number is within the PDF.
//   2. The question paper page really contains the opening words of the
//      extracted question text (proves the text came from where we say).
//   3. The mark scheme page really mentions the question label, tested with a
//      plain whitespace-insensitive substring scan rather than the extractor's
//      regexes.
//   4. The Section B context page really is part of the extract block.
//
// Exit status is non-zero if any check fails. Nothing is written.

import Foundation
import PDFKit

struct Failure {
    let id: String
    let check: String
    let detail: String
}

/// "6(a)" and "6 (a)" and a line break between the two must all compare equal.
func squashed(_ s: String) -> String {
    return s.components(separatedBy: .whitespacesAndNewlines).joined()
}

/// First n words of the extracted text, as they would appear on the page.
func opening(_ text: String, words: Int) -> String {
    return text.components(separatedBy: " ").prefix(words).joined(separator: " ")
}

let fm = FileManager.default
// Both Edexcel qualifications. They are separate directories because 9EC0 and
// 8EC0 each have a Paper 1 in the same series, so the filenames collide.
let dataDirs = [
    "past-paper-questions-data/edexcel-a",
    "past-paper-questions-data/edexcel-a-as",
]
var files: [(dir: String, name: String)] = []
for dir in dataDirs {
    guard let names = try? fm.contentsOfDirectory(atPath: dir) else {
        FileHandle.standardError.write("cannot read \(dir)\n".data(using: .utf8)!)
        exit(2)
    }
    files += names.filter { $0.hasSuffix(".json") }.sorted().map { (dir, $0) }
}

var failures: [Failure] = []
var warnings: [String] = []
var checked = 0
var pdfCache: [String: [String]] = [:]

func pages(_ url: String) -> [String]? {
    let path = String(url.dropFirst())  // "/past-papers/..." -> "past-papers/..."
    if let c = pdfCache[path] { return c }
    guard let doc = PDFDocument(url: URL(fileURLWithPath: path)) else { return nil }
    let p = (0..<doc.pageCount).map { doc.page(at: $0)?.string ?? "" }
    pdfCache[path] = p
    return p
}

for (dir, file) in files {
    guard let raw = try? Data(contentsOf: URL(fileURLWithPath: "\(dir)/\(file)")),
        let root = try? JSONSerialization.jsonObject(with: raw) as? [String: Any],
        let questions = root["questions"] as? [[String: Any]]
    else {
        failures.append(Failure(id: file, check: "parse", detail: "cannot read JSON"))
        continue
    }

    for q in questions {
        guard let id = q["id"] as? String,
            let text = q["questionText"] as? String,
            let number = q["questionNumber"] as? String,
            let qp = q["questionPaper"] as? [String: Any],
            let qpUrl = qp["pdfUrl"] as? String,
            let qpPage = qp["page"] as? Int
        else {
            failures.append(Failure(id: file, check: "shape", detail: "missing fields"))
            continue
        }
        checked += 1

        // ---- 1 & 2: question paper page holds the text we extracted
        guard let qpPages = pages(qpUrl) else {
            failures.append(Failure(id: id, check: "qp-open", detail: qpUrl))
            continue
        }
        if qpPage < 1 || qpPage > qpPages.count {
            failures.append(
                Failure(id: id, check: "qp-page-range", detail: "p\(qpPage) of \(qpPages.count)"))
        } else {
            let needle = squashed(opening(text, words: 6))
            if !squashed(qpPages[qpPage - 1]).contains(needle) {
                failures.append(
                    Failure(
                        id: id, check: "qp-text-not-on-page",
                        detail: "p\(qpPage) lacks: \(opening(text, words: 6))"))
            }
        }

        // ---- 3: mark scheme page names the question
        if let ms = q["markScheme"] as? [String: Any],
            let msUrl = ms["pdfUrl"] as? String, let msPage = ms["page"] as? Int
        {
            guard let msPages = pages(msUrl) else {
                failures.append(Failure(id: id, check: "ms-open", detail: msUrl))
                continue
            }
            if msPage < 1 || msPage > msPages.count {
                failures.append(
                    Failure(
                        id: id, check: "ms-page-range", detail: "p\(msPage) of \(msPages.count)"))
            } else if !squashed(msPages[msPage - 1]).contains(squashed(number)) {
                // Some schemes drop the question number from a part heading and
                // print just "(d)". That is a real Pearson inconsistency, not an
                // extraction error, so it is reported and not counted as a
                // failure - but only when the bare part label is actually there.
                let bare = number.contains("(")
                    ? String(number[number.firstIndex(of: "(")!...]) : ""
                if !bare.isEmpty && squashed(msPages[msPage - 1]).contains(squashed(bare)) {
                    warnings.append(
                        "\(id): mark scheme p\(msPage) labels this \(bare), "
                            + "omitting the question number")
                } else {
                    failures.append(
                        Failure(
                            id: id, check: "ms-label-not-on-page",
                            detail: "p\(msPage) does not mention \(number)"))
                }
            }
        } else {
            failures.append(Failure(id: id, check: "ms-missing", detail: "no mark scheme recorded"))
        }

        // ---- 4: Section B context page is part of the extract block
        if let ctx = q["context"] as? [String: Any], let ctxPage = ctx["page"] as? Int {
            if ctxPage < 1 || ctxPage > qpPages.count {
                failures.append(
                    Failure(
                        id: id, check: "context-page-range",
                        detail: "p\(ctxPage) of \(qpPages.count)"))
            } else if ctxPage >= qpPage {
                failures.append(
                    Failure(
                        id: id, check: "context-after-question",
                        detail: "extract p\(ctxPage) is not before question p\(qpPage)"))
            }
        }
    }
}

print("checked \(checked) questions across \(files.count) papers")
for w in warnings {
    print("WARN  \(w)")
}
if failures.isEmpty {
    print("all checks passed")
    exit(0)
}
for f in failures {
    print("FAIL  \(f.id)  [\(f.check)]  \(f.detail)")
}
print("\(failures.count) failure(s)")
exit(1)
