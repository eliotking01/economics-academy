// Extract Edexcel A (9EC0) A-Level Paper 1 and Paper 2 Section B and Section C
// questions into JSON, one file per paper.
//
//   swift scripts/extract_past_paper_questions.swift <question-paper.pdf> ...
//
// Writes past-paper-questions-data/edexcel-a/<paper>-<series>.json and prints a
// one-line summary per paper to stderr.
//
// Why Swift: this repo has no Python PDF library, no requirements.txt and no
// venv, but macOS ships PDFKit. QUESTIONS_PROGRESS.md section 7 already
// established Swift + PDFKit as the working method for these PDFs. Zero new
// dependencies.
//
// This script NEVER invents, paraphrases or reconstructs question text. If a
// question cannot be located or its mark scheme page cannot be verified, the
// question is emitted with confidence "low" and a note, or omitted entirely and
// recorded in "problems". Both are then chased by hand in the QA report.
//
// Topic and keyword tagging is deliberately NOT done here. It lives in
// past-paper-questions-data/tags.json, hand-written, so that re-running this
// extractor can never destroy it.

import Foundation
import PDFKit

// ------------------------------------------------------------------ helpers

func rx(_ pattern: String, _ opts: NSRegularExpression.Options = []) -> NSRegularExpression {
    // swiftlint:disable:next force_try
    return try! NSRegularExpression(pattern: pattern, options: opts)
}

extension NSRegularExpression {
    func firstMatch(_ s: String) -> [String?]? {
        let ns = s as NSString
        guard let m = firstMatch(in: s, range: NSRange(location: 0, length: ns.length)) else {
            return nil
        }
        return (0..<m.numberOfRanges).map { i in
            m.range(at: i).location == NSNotFound ? nil : ns.substring(with: m.range(at: i))
        }
    }

    func allMatches(_ s: String) -> [[String?]] {
        let ns = s as NSString
        return matches(in: s, range: NSRange(location: 0, length: ns.length)).map { m in
            (0..<m.numberOfRanges).map { i in
                m.range(at: i).location == NSNotFound ? nil : ns.substring(with: m.range(at: i))
            }
        }
    }

    func matches(_ s: String) -> Bool {
        let ns = s as NSString
        return firstMatch(in: s, range: NSRange(location: 0, length: ns.length)) != nil
    }
}

/// Page furniture that appears on every page and is never part of a question.
///
/// The margin warnings are rotated 90 degrees in the artwork, so PDFKit drops
/// them into the reading order at arbitrary points — mid-sentence, or ahead of
/// the question number. They therefore cannot be anchored to a line.
let furniture: [NSRegularExpression] = [
    rx("\\*[A-Z]\\d{5,6}[A-Z]?\\d{4,6}\\*"),   // *P57190A01032*
    rx("DO NOT WRITE IN THIS AREA"),
    rx("BLANK PAGE"),
    rx("(?m)^\\s*Turn over\\s*$"),
    rx("(?m)^\\s*\\d{1,3}\\s*$"),               // bare page number on its own line
]

/// A space inside a URL is always a line-wrap artefact — URLs cannot contain
/// one — so joining them back up repairs the link rather than altering wording.
/// Only whitespace directly after a URL-punctuation character is removed, and
/// only inside a run that started with http:// or https://.
/// A run of non-space characters, admitting a space only where the character
/// before it is URL punctuation and a non-space follows. Written as an
/// alternation inside the repeat so the engine cannot settle on a greedy
/// prefix and skip the wrapped remainder.
let urlSpan = rx("https?://(?:\\S|(?<=[-/._?=&])\\s(?=\\S))+")
let urlWrap = rx("(?<=[-/._?=&])\\s+")

func repairURLs(_ s: String) -> String {
    let ns = s as NSString
    var result = ""
    var cursor = 0
    for m in urlSpan.matches(in: s, range: NSRange(location: 0, length: ns.length)) {
        result += ns.substring(with: NSRange(location: cursor, length: m.range.location - cursor))
        let span = ns.substring(with: m.range)
        result += urlWrap.stringByReplacingMatches(
            in: span, range: NSRange(location: 0, length: (span as NSString).length),
            withTemplate: "")
        cursor = m.range.location + m.range.length
    }
    result += ns.substring(from: cursor)
    return result
}

/// Runs of the dotted answer-line leaders, plus any line made only of dots.
let dotLeader = rx("\\.{6,}[\\s\\.]*")

func stripFurniture(_ raw: String) -> String {
    var s = raw
    for r in furniture {
        s = r.stringByReplacingMatches(
            in: s, range: NSRange(location: 0, length: (s as NSString).length),
            withTemplate: " ")
    }
    s = dotLeader.stringByReplacingMatches(
        in: s, range: NSRange(location: 0, length: (s as NSString).length), withTemplate: " ")
    return s
}

/// Collapse a question's text to a single clean paragraph-preserving string.
/// Line breaks inside a PDF are typographic, not semantic, so they are joined.
func normalise(_ raw: String) -> String {
    var s = stripFurniture(raw)
    s = s.replacingOccurrences(of: "\u{00A0}", with: " ")
    s = s.components(separatedBy: .newlines)
        .map { $0.trimmingCharacters(in: .whitespaces) }
        .filter { !$0.isEmpty }
        .joined(separator: " ")
    s = rx("\\s{2,}").stringByReplacingMatches(
        in: s, range: NSRange(location: 0, length: (s as NSString).length), withTemplate: " ")
    s = repairURLs(s)
    return s.trimmingCharacters(in: .whitespacesAndNewlines)
}

// ------------------------------------------------------------------ model

struct QuestionOut {
    var id: String
    var section: String
    var questionNumber: String
    var parentQuestion: String?
    var choiceGroup: String?
    var marks: Int
    var questionText: String
    var contextPage: Int?
    var qpPage: Int
    var msPage: Int?
    var msVerified: Bool
    var confidence: String
    var notes: [String]
}

struct PaperMeta {
    var paper: Int
    var paperName: String
    var year: Int
    var series: String
    var seriesSlug: String
    var qpPath: String
    var msPath: String
    var idStem: String
}

let paperNames = [
    1: "Markets and Business Behaviour",
    2: "The National and Global Economy",
]

let seriesNames = ["june": "June", "october": "October", "november": "November"]

func parseMeta(_ path: String) -> PaperMeta? {
    let file = (path as NSString).lastPathComponent
    guard
        let m = rx("paper-(\\d)-([a-z]+)-(\\d{4})-question-paper\\.pdf$").firstMatch(file),
        let paper = Int(m[1]!), let year = Int(m[3]!),
        let seriesName = seriesNames[m[2]!], let paperName = paperNames[paper]
    else { return nil }

    let seriesSlug = "\(m[2]!)-\(year)"
    let msPath = path.replacingOccurrences(
        of: "-question-paper.pdf", with: "-mark-scheme.pdf")
    let short = String(seriesName.lowercased().prefix(3))
    return PaperMeta(
        paper: paper, paperName: paperName, year: year, series: seriesName,
        seriesSlug: seriesSlug, qpPath: path, msPath: msPath,
        idStem: "edexcel-a-p\(paper)-\(year)-\(short)")
}

// ------------------------------------------------------------------ mark scheme

/// Mark allocations that always follow a question label in an Edexcel scheme.
/// Used as the signature that a bare label really is a scheme heading.
let allocation = "(?:Knowledge|Analysis|Application|Evaluation|Indicative|The only correct)"

/// Find the first mark-scheme page whose heading names this question.
///
/// Three layouts occur across the sixteen schemes and all three are handled:
///
///  1. PDFKit returns the table header in reading order, interleaving the column
///     labels: "Question Indicative content Mark Number 6(c)". The anchor is
///     "Number" followed by the label, not the contiguous phrase "Question Number".
///  2. Where a question's row spills onto a new page the header stays behind, so
///     the page opens on the bare label: "6(a) Knowledge 1, Application 1".
///     (Paper 1 June 2024.)
///  3. Some schemes space the label: "6 (a)" not "6(a)". (Paper 2 October 2020.)
///
/// Page 1 and 2 are skipped because the cover carries a publications code that
/// can otherwise collide ("Question Paper Log Number 73999").
func markSchemePage(_ pages: [String], question: String, part: String?) -> Int? {
    // Tolerate "6(a)" and "6 (a)"; reject a longer number ("7" must not hit "70").
    let label: String
    if let part = part {
        label = "\(question)\\s*\\(\\s*\(part)\\s*\\)"
    } else {
        label = "\(question)(?![0-9])"
    }

    // The class holds a literal non-breaking space: ICU's \s does not match one.
    let byHeader = rx("Number[\\s\u{00A0}]*\(label)")
    let byBareLabel = rx("(?m)^[ \\t]*\(label)[ \\t]+\(allocation)")

    for (i, page) in pages.enumerated() where i >= 2 {
        if byHeader.matches(page) || byBareLabel.matches(page) { return i + 1 }
    }
    return nil
}

// ------------------------------------------------------------------ section C

/// Section C is one 25-mark essay chosen from two, always Q7 and Q8.
/// Layout: "EITHER  7 <text> (Total for Question 7 = 25 marks)  OR  8 <text> ..."
func extractSectionC(pages: [String], meta: PaperMeta, msPages: [String])
    -> ([QuestionOut], [String])
{
    var problems: [String] = []

    guard
        let idx = pages.firstIndex(where: {
            $0.contains("SECTION C") && ($0.contains("EITHER") || $0.contains("Answer ONE"))
        })
    else {
        return ([], ["Section C page not found"])
    }

    let page = pages[idx]
    var out: [QuestionOut] = []
    let group = "\(meta.idStem)-sec-c"

    for (n, opener) in [(7, "EITHER"), (8, "OR")] {
        let total = "(Total for Question \(n) = 25 marks)"
        guard let totalRange = page.range(of: total) else {
            problems.append("Q\(n): '(Total for Question \(n) = 25 marks)' not found")
            continue
        }
        // Start after the opener keyword that precedes this question's total.
        let before = String(page[page.startIndex..<totalRange.lowerBound])
        guard let openerRange = before.range(of: opener, options: .backwards) else {
            problems.append("Q\(n): opener '\(opener)' not found before its total line")
            continue
        }
        var body = String(before[openerRange.upperBound...])
        body = normalise(body)
        // Strip the leading question number.
        body = rx("^\(n)\\s+").stringByReplacingMatches(
            in: body, range: NSRange(location: 0, length: (body as NSString).length),
            withTemplate: "")

        var notes: [String] = []
        var confidence = "high"
        if body.count < 60 {
            confidence = "low"
            notes.append("extracted text is suspiciously short (\(body.count) chars)")
        }
        if body.contains("....") {
            confidence = "low"
            notes.append("answer-line leaders survived cleaning")
        }

        let ms = markSchemePage(msPages, question: String(n), part: nil)
        if ms == nil {
            confidence = "low"
            notes.append("mark scheme page for Q\(n) could not be verified")
        }

        out.append(
            QuestionOut(
                id: "\(meta.idStem)-q\(n)", section: "C", questionNumber: String(n),
                parentQuestion: nil, choiceGroup: group, marks: 25, questionText: body,
                contextPage: nil, qpPage: idx + 1, msPage: ms, msVerified: ms != nil,
                confidence: confidence, notes: notes))
    }

    if out.count != 2 {
        problems.append("expected 2 Section C questions, got \(out.count)")
    }
    return (out, problems)
}

// ------------------------------------------------------------------ section B

/// Section B is one data-response question, always Q6, parts (a) to (e), that
/// depends on extracts and figures printed before it.
///
/// Most papers print a consolidated list of all five parts on one page. Two
/// (Paper 2 June 2017 and June 2019) do not, and print each part above its own
/// answer space instead. Both layouts are handled by scanning every Section B
/// page for part openers and keeping the FIRST occurrence of each letter, which
/// is the consolidated list where one exists and the answer page where it does not.
func extractSectionB(pages: [String], meta: PaperMeta, msPages: [String])
    -> ([QuestionOut], [String])
{
    var problems: [String] = []

    guard
        let startIdx = pages.firstIndex(where: {
            $0.contains("SECTION B") && $0.contains("before answering Question")
        })
    else {
        return ([], ["Section B page not found"])
    }

    let header = pages[startIdx]
    guard let qm = rx("before answering Question\\s+(\\d+)").firstMatch(header),
        let qnum = qm[1]
    else {
        return ([], ["Section B question number not found"])
    }

    let endIdx =
        pages.firstIndex(where: { $0.contains("SECTION C") }) ?? pages.count

    // The extract block a student must read. "Extract A" is its first page; if a
    // paper labels its stimulus differently, fall back to the Section B opener.
    let extractPage =
        (startIdx..<endIdx).first(where: { pages[$0].contains("Extract A") }).map { $0 + 1 }
        ?? (startIdx + 1)

    // "(a) <text> (5)" — text is non-greedy up to the tariff in its own brackets.
    let partRe = rx(
        "\\(([a-e])\\)\\s*(.+?)\\s*\\((\\d{1,2})\\)", [.dotMatchesLineSeparators])

    var seen: [String: QuestionOut] = [:]
    var order: [String] = []

    for i in startIdx..<endIdx {
        let cleaned = stripFurniture(pages[i])
        for m in partRe.allMatches(cleaned) {
            guard let letter = m[1], let rawBody = m[2], let marksStr = m[3],
                let marks = Int(marksStr), seen[letter] == nil
            else { continue }

            let body = normalise(rawBody)
            // A match spanning a page break can swallow the next part; reject
            // bodies that still contain another part opener or a stray tariff.
            if body.isEmpty || body.count < 15 { continue }
            if rx("\\([a-e]\\)").matches(body) { continue }

            var notes: [String] = []
            var confidence = "high"
            if body.count > 400 {
                confidence = "low"
                notes.append("extracted text is unusually long; may span two parts")
            }

            let label = "\(qnum)(\(letter))"
            let ms = markSchemePage(msPages, question: qnum, part: letter)
            if ms == nil {
                confidence = "low"
                notes.append("mark scheme page for \(label) could not be verified")
            }

            seen[letter] = QuestionOut(
                id: "\(meta.idStem)-q\(qnum)\(letter)", section: "B",
                questionNumber: label, parentQuestion: qnum, choiceGroup: nil,
                marks: marks, questionText: body, contextPage: extractPage,
                qpPage: i + 1, msPage: ms, msVerified: ms != nil,
                confidence: confidence, notes: notes)
            order.append(letter)
        }
    }

    let out = ["a", "b", "c", "d", "e"].compactMap { seen[$0] }
    if out.count != 5 {
        let missing = ["a", "b", "c", "d", "e"].filter { seen[$0] == nil }
        problems.append("Section B: missing part(s) \(missing.joined(separator: ", "))")
    }
    return (out, problems)
}

// ------------------------------------------------------------------ emit

func jsonEscape(_ s: String) -> String {
    var o = ""
    for c in s.unicodeScalars {
        switch c {
        case "\"": o += "\\\""
        case "\\": o += "\\\\"
        case "\n": o += "\\n"
        case "\r": o += "\\r"
        case "\t": o += "\\t"
        default:
            if c.value < 0x20 {
                o += String(format: "\\u%04x", c.value)
            } else {
                o.unicodeScalars.append(c)
            }
        }
    }
    return o
}

func urlFor(_ path: String) -> String {
    guard let r = path.range(of: "past-papers/") else { return path }
    return "/" + String(path[r.lowerBound...])
}

func emit(meta: PaperMeta, questions: [QuestionOut], problems: [String]) -> String {
    let qpUrl = urlFor(meta.qpPath)
    let msUrl = urlFor(meta.msPath)

    var lines: [String] = []
    lines.append("{")
    lines.append("  \"qualification\": \"A Level Economics A (9EC0)\",")
    lines.append("  \"board\": \"edexcel\",")
    lines.append("  \"boardName\": \"Edexcel\",")
    lines.append("  \"level\": \"a-level\",")
    lines.append("  \"paper\": \(meta.paper),")
    lines.append("  \"paperName\": \"\(jsonEscape(meta.paperName))\",")
    lines.append("  \"year\": \(meta.year),")
    lines.append("  \"series\": \"\(meta.series)\",")
    lines.append("  \"seriesSlug\": \"\(meta.seriesSlug)\",")
    lines.append("  \"questionPaperUrl\": \"\(jsonEscape(qpUrl))\",")
    lines.append("  \"markSchemeUrl\": \"\(jsonEscape(msUrl))\",")
    lines.append(
        "  \"problems\": [\(problems.map { "\"\(jsonEscape($0))\"" }.joined(separator: ", "))],")
    lines.append("  \"questions\": [")

    for (i, q) in questions.enumerated() {
        var f: [String] = []
        f.append("      \"id\": \"\(jsonEscape(q.id))\"")
        f.append("      \"section\": \"\(q.section)\"")
        f.append("      \"questionNumber\": \"\(jsonEscape(q.questionNumber))\"")
        f.append(
            "      \"parentQuestion\": "
                + (q.parentQuestion.map { "\"\($0)\"" } ?? "null"))
        f.append("      \"choiceGroup\": " + (q.choiceGroup.map { "\"\($0)\"" } ?? "null"))
        f.append("      \"marks\": \(q.marks)")
        f.append("      \"questionText\": \"\(jsonEscape(q.questionText))\"")
        if let cp = q.contextPage {
            f.append(
                "      \"context\": { \"type\": \"extracts\", "
                    + "\"label\": \"Extracts and figures for Question \(q.parentQuestion ?? "6")\", "
                    + "\"pdfUrl\": \"\(jsonEscape(qpUrl))\", \"page\": \(cp) }")
        } else {
            f.append("      \"context\": null")
        }
        f.append(
            "      \"questionPaper\": { \"pdfUrl\": \"\(jsonEscape(qpUrl))\", "
                + "\"page\": \(q.qpPage) }")
        if let ms = q.msPage {
            f.append(
                "      \"markScheme\": { \"pdfUrl\": \"\(jsonEscape(msUrl))\", "
                    + "\"page\": \(ms), \"verified\": \(q.msVerified) }")
        } else {
            f.append("      \"markScheme\": null")
        }
        f.append("      \"modelAnswer\": null")
        f.append("      \"extractionConfidence\": \"\(q.confidence)\"")
        f.append(
            "      \"extractionNotes\": [\(q.notes.map { "\"\(jsonEscape($0))\"" }.joined(separator: ", "))]"
        )
        lines.append("    {")
        lines.append(f.joined(separator: ",\n"))
        lines.append("    }" + (i == questions.count - 1 ? "" : ","))
    }

    lines.append("  ]")
    lines.append("}")
    return lines.joined(separator: "\n") + "\n"
}

// ------------------------------------------------------------------ main

func pageTexts(_ path: String) -> [String]? {
    guard let doc = PDFDocument(url: URL(fileURLWithPath: path)) else { return nil }
    return (0..<doc.pageCount).map { doc.page(at: $0)?.string ?? "" }
}

let args = Array(CommandLine.arguments.dropFirst())
guard !args.isEmpty else {
    FileHandle.standardError.write(
        "usage: swift scripts/extract_past_paper_questions.swift <question-paper.pdf> ...\n"
            .data(using: .utf8)!)
    exit(2)
}

let outDir = URL(fileURLWithPath: "past-paper-questions-data/edexcel-a")
try? FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)

var exitCode: Int32 = 0

for path in args {
    guard let meta = parseMeta(path) else {
        FileHandle.standardError.write("SKIP (unparseable name): \(path)\n".data(using: .utf8)!)
        exitCode = 1
        continue
    }
    guard let qpPages = pageTexts(meta.qpPath) else {
        FileHandle.standardError.write("FAIL (cannot open QP): \(path)\n".data(using: .utf8)!)
        exitCode = 1
        continue
    }
    guard let msPages = pageTexts(meta.msPath) else {
        FileHandle.standardError.write(
            "FAIL (cannot open MS): \(meta.msPath)\n".data(using: .utf8)!)
        exitCode = 1
        continue
    }

    let (b, bProblems) = extractSectionB(pages: qpPages, meta: meta, msPages: msPages)
    let (c, cProblems) = extractSectionC(pages: qpPages, meta: meta, msPages: msPages)
    let questions = b + c
    let problems = bProblems + cProblems

    let name = "p\(meta.paper)-\(meta.seriesSlug).json"
    let dest = outDir.appendingPathComponent(name)
    try! emit(meta: meta, questions: questions, problems: problems)
        .write(to: dest, atomically: true, encoding: .utf8)

    let low = questions.filter { $0.confidence != "high" }.count
    let unver = questions.filter { !$0.msVerified }.count
    var summary = "\(name): \(questions.count) questions"
    if low > 0 { summary += ", \(low) low-confidence" }
    if unver > 0 { summary += ", \(unver) unverified MS" }
    if !problems.isEmpty { summary += ", PROBLEMS: \(problems.joined(separator: "; "))" }
    FileHandle.standardError.write((summary + "\n").data(using: .utf8)!)
    if !problems.isEmpty || low > 0 { exitCode = 1 }
}

exit(exitCode)
