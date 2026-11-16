// Independently verify the Edexcel A and Edexcel B extraction data
// (past-paper-questions-data/edexcel-{a,a-as,b,b-as}/*.json) against the PDFs.
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
//   4. The Section B context page really is part of the extract block: before
//      the question, or - on a Source Booklet paper, June 2025 onwards - in the
//      booklet block for the question's own section.
//
// Edexcel B (9EB0 / 8EB0) adds four, because its single 20-mark questions are
// numbered "2" and "3" and a bare digit on a mark-scheme page proves nothing,
// and because its records carry a lead-in printed above the part label:
//
//   5. The question paper page also holds the CLOSING words of the text, so a
//      lead-in or body cut short or run on is caught at either end.
//   6. The mark scheme page opens a line with the label (or prints it straight
//      after the table's "Number"/"Answer" header), and "Knowledge" - the
//      first assessment objective every B heading names - is on that line or
//      the three after it. Three, because two short questions often share a
//      page and interleave their headers ("1(c) Question / Number / 1(d)
//      Answer Knowledge..."), and the 2022-24 schemes reprint the question
//      around the label. Line-by-line string scan, no regex. A heading that
//      drops the question number ("(d)") is a warning, as in check 3.
//   7. Each question's marks sum to the "(Total for Question N = M marks)"
//      line printed on the question paper.
//   8. The context page carries an extract, and nothing has a choiceGroup
//      (B has no optional questions).
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

/// Last n words, for the Edexcel B closing-words check.
func closing(_ text: String, words: Int) -> String {
    return text.components(separatedBy: " ").suffix(words).joined(separator: " ")
}

/// A page squashed, with the rotated margin warning taken out: PDFKit drops it
/// into the reading order mid-sentence, so it can split any run of words.
func squashedPage(_ s: String) -> String {
    return squashed(s).replacingOccurrences(of: "DONOTWRITEINTHISAREA", with: "")
}

/// Check 6: does this Edexcel B mark-scheme page head a row with `label`?
func bSchemeNames(_ page: String, label: String) -> Bool {
    let lines = page.components(separatedBy: .newlines).map(squashed)
    for (i, line) in lines.enumerated() {
        var rest: Substring? = nil
        if line.hasPrefix(label) {
            rest = line.dropFirst(label.count)
        } else {
            for header in ["Number", "Answer"] {
                if let r = line.range(of: header + label) { rest = line[r.upperBound...] }
            }
        }
        // "2" must not be the start of "2(a)" or "20"; "1(a)" must not be "1(a)(i)".
        guard let after = rest, !(after.first.map { $0.isNumber || $0 == "(" } ?? false)
        else { continue }
        let window = lines[i..<min(i + 4, lines.count)].joined().lowercased()
        if window.contains("knowledge") { return true }
    }
    return false
}

let fm = FileManager.default
// Both Edexcel qualifications. They are separate directories because 9EC0 and
// 8EC0 each have a Paper 1 in the same series, so the filenames collide.
let dataDirs = [
    "past-paper-questions-data/edexcel-a",
    "past-paper-questions-data/edexcel-a-as",
    "past-paper-questions-data/edexcel-b",
    "past-paper-questions-data/edexcel-b-as",
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

/// The section whose Source Booklet block holds this page, or nil when the page
/// is not in a booklet. Walks back to the nearest "Sources for use with SECTION"
/// heading - plain substring search, not the extractor's regex.
func bookletBlock(_ pages: [String], page: Int) -> String? {
    let marker = "Sources for use with SECTION "
    for i in stride(from: page - 1, through: 0, by: -1) {
        guard let r = pages[i].range(of: marker) else { continue }
        return pages[i][r.upperBound...].first.map(String.init)
    }
    return nil
}

for (dir, file) in files {
    guard let raw = try? Data(contentsOf: URL(fileURLWithPath: "\(dir)/\(file)")),
        let root = try? JSONSerialization.jsonObject(with: raw) as? [String: Any],
        let questions = root["questions"] as? [[String: Any]]
    else {
        failures.append(Failure(id: file, check: "parse", detail: "cannot read JSON"))
        continue
    }

    let isB = (root["board"] as? String) == "edexcel-b"
    var marksByQuestion: [String: Int] = [:]
    var paperUrl: String? = nil

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
            // ---- 5 (B): and its closing words
            if isB && !squashedPage(qpPages[qpPage - 1]).contains(squashed(closing(text, words: 6))) {
                failures.append(
                    Failure(
                        id: id, check: "b-qp-closing-not-on-page",
                        detail: "p\(qpPage) lacks: \(closing(text, words: 6))"))
            }
        }

        if isB {
            paperUrl = qpUrl
            let parent = (q["parentQuestion"] as? String) ?? number
            marksByQuestion[parent, default: 0] += (q["marks"] as? Int) ?? 0
            // ---- 8 (B): no optional questions
            if !(q["choiceGroup"] is NSNull) {
                failures.append(Failure(id: id, check: "b-choice-group", detail: "B has no choices"))
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
            } else if isB {
                // ---- 6 (B): the label heads a row on that page
                let label = squashed(number)
                let bare = label.contains("(") ? String(label[label.firstIndex(of: "(")!...]) : ""
                if bSchemeNames(msPages[msPage - 1], label: label) {
                    // named in full
                } else if !bare.isEmpty && bSchemeNames(msPages[msPage - 1], label: bare) {
                    warnings.append(
                        "\(id): mark scheme p\(msPage) labels this \(bare), "
                            + "omitting the question number")
                } else {
                    failures.append(
                        Failure(
                            id: id, check: "b-ms-label-not-heading",
                            detail: "p\(msPage) has no row headed \(number)"))
                }
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
            } else if let block = bookletBlock(qpPages, page: ctxPage) {
                // A Source Booklet paper (June 2025 onwards) binds the extracts
                // at the back, so the context page is meant to follow the
                // question. It must then sit in the block for the question's
                // own section, and that page must actually carry source material.
                let section = q["section"] as? String ?? "?"
                let headed = qpPages.contains { $0.contains("Sources for use with SECTION \(section)") }
                if block != section && isB && !headed
                    && qpPages[ctxPage - 1].contains("Extract")
                {
                    // Edexcel B Paper 1 June 2025 prints no "Sources for use
                    // with SECTION B" heading, so Extract G sits under Section
                    // A's. Accepted only when the PDF has no heading for the
                    // question's section anywhere, and reported.
                    warnings.append(
                        "\(id): the booklet prints no SECTION \(section) heading; "
                            + "context p\(ctxPage) accepted as an extract page")
                } else if block != section {
                    failures.append(
                        Failure(
                            id: id, check: "context-wrong-booklet-block",
                            detail: "p\(ctxPage) is in the SECTION \(block) sources, "
                                + "question is in Section \(section)"))
                } else if !qpPages[ctxPage - 1].contains("Extract")
                    && !qpPages[ctxPage - 1].contains("Figure")
                {
                    failures.append(
                        Failure(
                            id: id, check: "context-not-source",
                            detail: "booklet p\(ctxPage) has no extract or figure"))
                }
            } else if isB && !qpPages[ctxPage - 1].contains("Extract") {
                // ---- 8 (B): the context page is an extract page
                failures.append(
                    Failure(id: id, check: "b-context-not-extract", detail: "p\(ctxPage) has no extract"))
            } else if ctxPage >= qpPage {
                failures.append(
                    Failure(
                        id: id, check: "context-after-question",
                        detail: "extract p\(ctxPage) is not before question p\(qpPage)"))
            }
        }
    }

    // ---- 7 (B): marks per question match the printed total
    if isB, let url = paperUrl, let qpPages = pages(url) {
        let all = qpPages.joined(separator: "\n")
        for (n, sum) in marksByQuestion {
            let marker = "(Total for Question \(n) = "
            guard let r = all.range(of: marker),
                let printed = Int(all[r.upperBound...].prefix(while: { $0.isNumber }))
            else {
                failures.append(Failure(id: file, check: "b-total-missing", detail: "Q\(n)"))
                continue
            }
            if printed != sum {
                failures.append(
                    Failure(
                        id: file, check: "b-total-mismatch",
                        detail: "Q\(n) records \(sum) marks, paper prints \(printed)"))
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
