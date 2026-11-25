// Independently verify the Edexcel A and Edexcel B extraction data
// (past-paper-questions-data/edexcel-{a,a-as,b,b-as}/*.json), and AQA's
// Paper 3 multiple choice (aqa/p3-*.json), against the PDFs.
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
// A question paper with no text layer (Edexcel B AS Paper 2 June 2019, a scan)
// is checked against this script's OWN OCR of the PDF - Apple Vision at a
// higher resolution than ocr_pdf_pages.swift and with language correction off
// - never against the reviewed transcript the extractor read. The two readings
// must agree - the whole question, not just its opening and closing words
// (check 9) - so a mistake in the transcript fails here. On those pages quotes
// and dashes are folded (‘ ’ “ ” – to ' " -) on both sides, because OCR does
// not see the difference and the transcript was corrected to the printed glyph.
//
// Phase 7 adds the multiple-choice cards (type "mcq"): Edexcel A Papers 1-2
// Section A, one per question, and AQA Paper 3 Section A, thirty per paper -
// the only AQA records this script reads. Both extractors place an MCQ's
// options by geometry (PDFKit line positions for Edexcel, pdfplumber
// characters for AQA); this script never does. It searches the plain page
// text PDFKit returns, in which options can come out reversed or split from
// their letters, so a misplaced or invented option shows up as words the page
// does not hold:
//
//   M1. Shape: marks 1; options null or exactly A, B, C, D in order, each
//       {letter, text} with text; usesFigure a boolean, and true whenever
//       options is null; and NO answer key - no field of the record or of an
//       option names one (D67: search-only cards).
//   M2. The question text comes off the pages in runs (A1's rule), on the
//       question's page for AQA, from the stem's page to the part's for
//       Edexcel (checks A1 and A2 run for Edexcel as for every Section A card).
//   M3. Each option's letter and text are printed together, whole, on the
//       part's page or the next. Letters glued to digits are compared with
//       the digits removed on both sides, because AQA sets subscripts below
//       the line and PDFKit returns them detached ("SRAS1" against "SRAS ...
//       1"); a word is never dropped, only a subscript's position.
//   M4. Counts: thirty AQA Paper 3 MCQs numbered 1-30 in Section A, twenty
//       on each AQA AS paper (D71: Q1-Q20, read from aqa-as/); exactly one MCQ
//       in each Edexcel Section A question, and the question's cards now sum
//       to its printed total (A5, tightened from "one mark short").
//   M5. The AQA mark-scheme page holds the SECTION A KEY LIST.
//
// Exit status is non-zero if any check fails. Nothing is written.

import AppKit
import Foundation
import PDFKit
import Vision

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

/// Quotes and dashes folded to ASCII, for comparisons against an OCR reading.
func folded(_ s: String) -> String {
    var o = s
    for (a, b) in [("‘", "'"), ("’", "'"), ("“", "\""), ("”", "\""), ("–", "-"), ("—", "-")] {
        o = o.replacingOccurrences(of: a, with: b)
    }
    return o
}

/// This verifier's own OCR of a page: margins cropped (the rotated margin
/// warning), 4x render, accurate recognition, language correction off.
func ocrPage(_ page: PDFPage) -> String {
    let box = page.bounds(for: .mediaBox)
    let image = page.thumbnail(of: NSSize(width: box.width * 4, height: box.height * 4), for: .mediaBox)
    var rect = CGRect(origin: .zero, size: image.size)
    guard let cg = image.cgImage(forProposedRect: &rect, context: nil, hints: nil) else { return "" }
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = false
    request.regionOfInterest = CGRect(x: 0.05, y: 0, width: 0.9, height: 1)
    try? VNImageRequestHandler(cgImage: cg).perform([request])
    let lines = (request.results ?? []).sorted { a, b in
        abs(a.boundingBox.midY - b.boundingBox.midY) > 0.008
            ? a.boundingBox.midY > b.boundingBox.midY : a.boundingBox.minX < b.boundingBox.minX
    }
    return lines.compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\n")
}

/// Question papers read by OCR because they have no text layer.
var ocrRead: Set<String> = []

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

// ---- Edexcel A Papers 1 and 2, Section A (Phase 6). Checked against the PDF
// in ways the extractor does not use, because the extractor drops figure text
// and joins the stem, lead-ins and the part's own text into one string:
//
//   A1. Every word comes off the pages from the question's first page (the
//       context page) to the part's, in contiguous runs of at least two
//       words: the extractor may drop lines between sentences, never join
//       half-lines into wording no page holds. This replaces check 2, whose
//       fixed six-word window straddles the join of a stem and a short part.
//   A2. The text's closing run - at least three words, or all of it - is on
//       the part's own page, tariffs and answer lines taken out (a
//       sub-part's "(2)" sits between "(i) workers" and "(ii)").
//   A3. (folded into A1 and A2: the page claims are the run claims.)
//   A4. No written card is a multiple-choice question ("which one of the
//       following"); the MCQ itself is its own card since Phase 7.
//   A5. For each question, the recorded marks equal the printed total: the
//       written parts plus the one MCQ (Phase 7; in Phase 6, total less 1).

/// A page squashed for the run search: margin warnings, answer boxes (private
/// use glyphs), answer-line leaders, barcode references and tariffs removed.
func runPage(_ s: String) -> String {
    var o = squashedPage(s)
    // AQA's margin warning, set in the reading order the same way (Paper 3
    // June 2018 Q30: "over six" / "Do not write outside the box" / "quarters.").
    o = o.replacingOccurrences(of: "Donotwriteoutsidethebox", with: "")
    // Answer boxes (private use) and the BEL control character some option
    // lines carry after their letter (Paper 1 June 2025 3(a)): neither prints.
    o = String(String.UnicodeScalarView(o.unicodeScalars.filter {
        !(0xE000...0xF8FF).contains($0.value) && $0.value >= 0x20
    }))
    for p in ["\\.{4,}", "\\*[A-Z]\\d{5,6}[A-Z]?\\d{4,6}\\*", "\\(\\d{1,2}\\)"] {
        o = o.replacingOccurrences(of: p, with: "", options: .regularExpression)
    }
    return o
}

/// Cards whose closing words the text layer prints out of order, so no run
/// of three ends the text on the page. Each was read against the rendered
/// page (2026-11-25) and prints exactly as the card does; A1 still holds
/// every word to its runs.
///   Paper 1 June 2019 2(b): "... such as Hurricane" / "Harvey?" - the last
///     word is set among the four diagrams' titles ("Option A", "A B").
///   Paper 2 June 2019 1(a): "... an increase in credit" / "card lending?" -
///     the second line comes out of the layer before the first.
var closingStillOut = Set<String>()
let closingOutOfOrder: Set<String> = [
    "edexcel-a-p1-2019-jun-q2b",
    "edexcel-a-p2-2019-jun-q1a",
]

func sectionACheck(id: String, text: String, pages: [String], from: Int, to: Int, mcq: Bool = false) {
    guard from >= 1, to <= pages.count, from <= to else {
        failures.append(Failure(id: id, check: "a-page-order", detail: "stem p\(from), part p\(to)"))
        return
    }
    // Stripping the answer-line leaders takes a printed full stop with them
    // where the leaders start straight after it ("(ii) 2016............").
    func on(_ hay: String, _ s: String) -> Bool {
        hay.contains(s) || (s.hasSuffix(".") && hay.contains(String(s.dropLast())))
    }
    let words = text.split(separator: " ").map(String.init)
    let partPage = runPage(pages[to - 1])
    var k = words.count
    while k > 0 && on(partPage, squashed(words[(k - 1)...].joined())) { k -= 1 }
    if words.count - k < min(3, words.count) && closingOutOfOrder.contains(id) {
        closingStillOut.insert(id)
    }
    if words.count - k < min(3, words.count) && !closingOutOfOrder.contains(id) {
        failures.append(Failure(id: id, check: "a-closing-not-on-page", detail: "p\(to) lacks: \(closing(text, words: 3))"))
    }
    if !mcq && text.lowercased().contains("which one of the following") {
        failures.append(Failure(id: id, check: "a-mcq-text", detail: "card reads as a multiple-choice question"))
    }
    let hay = (from...to).map { runPage(pages[$0 - 1]) }.joined()
    var i = 0
    while i < words.count {
        var j = i
        while j < words.count && on(hay, squashed(words[i...j].joined())) { j += 1 }
        let run = j - i
        if run == 0 {
            failures.append(Failure(id: id, check: "a-word-not-on-pages", detail: "'\(words[i])' is on none of p\(from)-p\(to)"))
            return
        }
        if run < 2 && j < words.count {
            failures.append(Failure(id: id, check: "a-short-run", detail: "'\(words[i])' is joined to text it is not printed beside"))
            return
        }
        i = j
    }
}

/// Digits set straight after a letter taken out, on both sides of a
/// comparison: AQA's subscripts (SRAS1, OWmin's "min" is letters and stays).
func unscripted(_ s: String) -> String {
    return s.replacingOccurrences(of: "(?<=[A-Za-z])[0-9]+", with: "", options: .regularExpression)
}

/// M2 for AQA: every word of the stem is on the page, in runs of two or more.
func runCheck(id: String, text: String, hay: String) -> String? {
    let words = text.split(separator: " ").map(String.init)
    var i = 0
    while i < words.count {
        var j = i
        while j < words.count && hay.contains(unscripted(squashed(words[i...j].joined()))) { j += 1 }
        if j == i { return "'\(words[i])' is not on the page" }
        if j - i < 2 && j < words.count && words.count > 1 { return "'\(words[i])' is joined to text it is not printed beside" }
        i = j
    }
    return nil
}

let keyFields: Set<String> = ["answer", "answers", "key", "correct", "correctAnswer", "correctOption", "answerKey", "solution"]

/// M1 and M3 for one MCQ record. `hay` is the squashed, unscripted text of
/// the part's page and the next.
func mcqCheck(id: String, q: [String: Any], hay: String) {
    if let k = q.keys.first(where: { keyFields.contains($0) }) {
        failures.append(Failure(id: id, check: "mcq-has-key", detail: "field '\(k)'"))
    }
    if (q["marks"] as? Int) != 1 {
        failures.append(Failure(id: id, check: "mcq-marks", detail: "\(q["marks"] ?? "nil")"))
    }
    guard let fig = q["usesFigure"] as? Bool else {
        failures.append(Failure(id: id, check: "mcq-usesFigure", detail: "missing or not a boolean"))
        return
    }
    if q["options"] is NSNull {
        if !fig { failures.append(Failure(id: id, check: "mcq-null-options", detail: "options null but usesFigure false")) }
        return
    }
    guard let opts = q["options"] as? [[String: Any]] else {
        failures.append(Failure(id: id, check: "mcq-options-shape", detail: "options is neither null nor a list"))
        return
    }
    let letters = opts.compactMap { $0["letter"] as? String }
    if letters != ["A", "B", "C", "D"] {
        failures.append(Failure(id: id, check: "mcq-letters", detail: letters.joined()))
    }
    var seen = Set<String>()
    for o in opts {
        if Set(o.keys) != ["letter", "text"] {
            failures.append(Failure(id: id, check: "mcq-option-fields", detail: o.keys.sorted().joined(separator: ",")))
        }
        let letter = o["letter"] as? String ?? "?"
        guard let text = o["text"] as? String, !text.isEmpty else {
            failures.append(Failure(id: id, check: "mcq-option-empty", detail: letter))
            continue
        }
        if !seen.insert(text).inserted {
            failures.append(Failure(id: id, check: "mcq-option-repeated", detail: "\(letter): \(text)"))
        }
        if !hay.contains(unscripted(squashed(letter + text))) {
            failures.append(Failure(id: id, check: "mcq-option-not-on-page", detail: "\(letter) \(text)"))
        }
    }
}

/// The context page of a Section A record, whose context is its stem's page.
func ctxOf(_ q: [String: Any]) -> Int? {
    guard let c = q["context"] as? [String: Any], (c["type"] as? String) == "question" else { return nil }
    return c["page"] as? Int
}

let fm = FileManager.default
// Both Edexcel qualifications. They are separate directories because 9EC0 and
// 8EC0 each have a Paper 1 in the same series, so the filenames collide.
let dataDirs = [
    "past-paper-questions-data/edexcel-a",
    "past-paper-questions-data/edexcel-a-as",
    "past-paper-questions-data/edexcel-b",
    "past-paper-questions-data/edexcel-b-as",
    // Phase 7: AQA's Paper 3 MCQs only. Its written records are not checked
    // here (see the AQA guard in the loop).
    "past-paper-questions-data/aqa",
]
var files: [(dir: String, name: String)] = []
for dir in dataDirs {
    guard let names = try? fm.contentsOfDirectory(atPath: dir) else {
        FileHandle.standardError.write("cannot read \(dir)\n".data(using: .utf8)!)
        exit(2)
    }
    // AQA: Paper 3 only, the one paper with multiple choice.
    let wanted = names.filter { $0.hasSuffix(".json") && (!dir.hasSuffix("/aqa") || $0.hasPrefix("p3-")) }
    files += wanted.sorted().map { (dir, $0) }
}

var failures: [Failure] = []
var warnings: [String] = []
var checked = 0
var pdfCache: [String: [String]] = [:]

func pages(_ url: String) -> [String]? {
    let path = String(url.dropFirst())  // "/past-papers/..." -> "past-papers/..."
    if let c = pdfCache[path] { return c }
    guard let doc = PDFDocument(url: URL(fileURLWithPath: path)) else { return nil }
    var p = (0..<doc.pageCount).map { doc.page(at: $0)?.string ?? "" }
    if p.allSatisfy({ $0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }) {
        p = (0..<doc.pageCount).map { doc.page(at: $0).map(ocrPage) ?? "" }
        ocrRead.insert(path)
    }
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
    let isEdexcelAP12 = (root["board"] as? String) == "edexcel" && (root["paper"] as? Int) != 3
    var marksByQuestionA: [String: Int] = [:]
    var mcqsByQuestionA: [String: Int] = [:]
    var paperUrlA: String? = nil
    let isAQA = (root["board"] as? String) == "aqa"
    // Section A's length: thirty on Paper 3, twenty on each AS paper (D71).
    let aqaMCQCount = (root["level"] as? String) == "as-level" ? 20 : 30
    var aqaMCQNumbers: [String] = []

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
        let isMCQ = (q["type"] as? String) == "mcq"
        // AQA's written records are outside this script (see the header).
        if isAQA && !isMCQ { continue }
        if !isMCQ && (q["options"] != nil || q["usesFigure"] != nil) {
            failures.append(Failure(id: id, check: "written-has-mcq-fields", detail: "options or usesFigure on a written card"))
        }
        checked += 1
        let isSectionA = isEdexcelAP12 && (q["section"] as? String) == "A"

        // ---- 1 & 2: question paper page holds the text we extracted
        guard let qpPages = pages(qpUrl) else {
            failures.append(Failure(id: id, check: "qp-open", detail: qpUrl))
            continue
        }
        if qpPage < 1 || qpPage > qpPages.count {
            failures.append(
                Failure(id: id, check: "qp-page-range", detail: "p\(qpPage) of \(qpPages.count)"))
        } else {
            // Folding is the identity on a text-layer paper.
            let ocr = ocrRead.contains(String(qpUrl.dropFirst()))
            let fold: (String) -> String = { ocr ? folded($0) : $0 }
            // A Section A card joins its stem to its part's own text, so a
            // fixed six-word window can straddle a join no page prints as one
            // run; A1-A3 check it run by run instead.
            let openPage = isSectionA ? (ctxOf(q) ?? qpPage) : qpPage
            let needle = fold(squashed(opening(text, words: 6)))
            // ---- M2, M3 (AQA): the stem in runs, and the options, on the page
            if isAQA {
                let hay = unscripted(runPage(qpPages[qpPage - 1]))
                if let why = runCheck(id: id, text: text, hay: hay) {
                    failures.append(Failure(id: id, check: "mcq-stem-not-on-page", detail: "p\(qpPage): \(why)"))
                }
                let both = (qpPage...min(qpPage + 1, qpPages.count)).map { unscripted(runPage(qpPages[$0 - 1])) }.joined()
                mcqCheck(id: id, q: q, hay: both)
                if (q["section"] as? String) != "A" {
                    failures.append(Failure(id: id, check: "mcq-section", detail: "\(q["section"] ?? "nil")"))
                }
                aqaMCQNumbers.append(number)
            }
            if !isSectionA && !isAQA && !fold(squashed(qpPages[qpPage - 1])).contains(needle) {
                failures.append(
                    Failure(
                        id: id, check: "qp-text-not-on-page",
                        detail: "p\(openPage) lacks: \(opening(text, words: 6))"))
            }
            if isSectionA {
                sectionACheck(id: id, text: text, pages: qpPages, from: openPage, to: qpPage, mcq: isMCQ)
                let parent = (q["parentQuestion"] as? String) ?? number
                marksByQuestionA[parent, default: 0] += (q["marks"] as? Int) ?? 0
                paperUrlA = qpUrl
                // ---- M1, M3 (Edexcel): shape, and options on the page
                if isMCQ {
                    mcqsByQuestionA[parent, default: 0] += 1
                    let both = (qpPage...min(qpPage + 1, qpPages.count)).map { unscripted(runPage(qpPages[$0 - 1])) }.joined()
                    mcqCheck(id: id, q: q, hay: both)
                }
            } else if isMCQ && !isAQA {
                failures.append(Failure(id: id, check: "mcq-outside-section-a", detail: "an MCQ outside Edexcel A Papers 1-2 Section A"))
            }
            // ---- 5 (B): and its closing words
            // ---- 9 (OCR): on a scanned paper the WHOLE text must be in this
            // script's own reading of the page - a misread mid-question would
            // pass the opening and closing checks. Part labels are taken out
            // of the page first, because a lead-in prints above its label.
            if ocr {
                let page = fold(squashedPage(qpPages[qpPage - 1])).replacingOccurrences(
                    of: "\\([a-h]\\)", with: "", options: .regularExpression)
                if !page.contains(fold(squashed(text))) {
                    failures.append(
                        Failure(
                            id: id, check: "ocr-full-text-not-on-page",
                            detail: "p\(qpPage): the verifier's own OCR does not contain the whole text"))
                }
            }
            if isB && !fold(squashedPage(qpPages[qpPage - 1])).contains(fold(squashed(closing(text, words: 6)))) {
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
            } else if isAQA {
                // ---- M5 (AQA): the page holding the Section A key list
                let page = squashed(msPages[msPage - 1]).uppercased()
                if !page.contains("KEYLIST") || !page.contains("SECTIONA") {
                    failures.append(Failure(id: id, check: "mcq-ms-not-key-list", detail: "p\(msPage)"))
                }
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

    // ---- A5: each Section A question is short by exactly its one MCQ mark
    if let url = paperUrlA, let qpPages = pages(url) {
        let all = qpPages.joined(separator: "\n")
        for (n, sum) in marksByQuestionA.sorted(by: { $0.key < $1.key }) {
            let marker = "(Total for Question \(n) = "
            guard let r = all.range(of: marker),
                let printed = Int(all[r.upperBound...].prefix(while: { $0.isNumber }))
            else {
                failures.append(Failure(id: file, check: "a-total-missing", detail: "Q\(n)"))
                continue
            }
            if printed != sum {
                failures.append(
                    Failure(
                        id: file, check: "a-total",
                        detail: "Q\(n) records \(sum) of \(printed) marks; expected all of them, the MCQ included"))
            }
            // ---- M4 (Edexcel): exactly one MCQ per question
            if mcqsByQuestionA[n, default: 0] != 1 {
                failures.append(Failure(id: file, check: "a-mcq-count", detail: "Q\(n) has \(mcqsByQuestionA[n, default: 0]) MCQ cards"))
            }
        }
        if marksByQuestionA.count != 5 {
            failures.append(Failure(id: file, check: "a-question-count", detail: "\(marksByQuestionA.count) of 5 questions have a written part"))
        }
    }

    // ---- M4 (AQA): thirty MCQs (twenty on AS), numbered from 1, in order
    if isAQA && aqaMCQNumbers != (1...aqaMCQCount).map(String.init) {
        failures.append(Failure(id: file, check: "aqa-mcq-count", detail: "numbers \(aqaMCQNumbers.joined(separator: ","))"))
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
// An exception that no longer fails is stale: the layout it describes changed.
for id in closingOutOfOrder.sorted() where !closingStillOut.contains(id) {
    failures.append(Failure(id: id, check: "stale-exception", detail: "closingOutOfOrder entry no longer needed"))
}
for path in ocrRead.sorted() {
    print("OCR   \(path) has no text layer; checked against this script's own OCR")
}
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
