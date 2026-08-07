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

/// Pearson's provenance note, printed under the stimulus paragraph of a
/// Section C question: `(Source adapted from: https://...)`, and three other
/// orderings of the same words. It is where the stimulus came from, not part of
/// what the candidate is asked to do, so it is lifted out into its own field
/// rather than left in the middle of the question.
///
/// The URL is required, which is what keeps ordinary prose safe - these
/// questions use the word freely ("a source of market failure"), and none of
/// those sit in brackets around a link. `[^()]` rather than `.` so a citation
/// can never swallow a later bracket.
///
/// Run after repairURLs, so a citation whose URL wrapped across a line is one
/// span by the time this sees it. Mirrors `clean()` in extract_aqa_questions.py,
/// which drops AQA's equivalent `Sources:` line.
let attribution = rx("\\(\\s*Sources?\\b[^()]*https?://[^()]*\\)")

/// Returns the text without its citation, and the citation itself.
func stripAttribution(_ s: String) -> (text: String, attribution: String?) {
    let ns = s as NSString
    let all = attribution.matches(in: s, range: NSRange(location: 0, length: ns.length))
    guard !all.isEmpty else { return (s, nil) }

    let found = all.map { ns.substring(with: $0.range) }.joined(separator: " ")
    var out = attribution.stringByReplacingMatches(
        in: s, range: NSRange(location: 0, length: ns.length), withTemplate: " ")
    // The citation sits between the stimulus and the question sentence, so
    // taking it out leaves two spaces mid-string and one at the end.
    out = rx("\\s{2,}").stringByReplacingMatches(
        in: out, range: NSRange(location: 0, length: (out as NSString).length),
        withTemplate: " ")
    out = rx("\\s+([.,;:!?])").stringByReplacingMatches(
        in: out, range: NSRange(location: 0, length: (out as NSString).length),
        withTemplate: "$1")
    return (out.trimmingCharacters(in: .whitespacesAndNewlines), found)
}

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
    // A lone full stop left behind by the answer-line leaders. The leader run is
    // stripped by dotLeader, but where the PDF spaces the first dot away from
    // the rest ("workers. . . . . . . . .") that first one survives on its own.
    // Only ever removed at the very end of the text, so an ellipsis or a
    // decimal point mid-sentence cannot be touched.
    s = rx("\\s+\\.\\s*$").stringByReplacingMatches(
        in: s, range: NSRange(location: 0, length: (s as NSString).length), withTemplate: "")
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
    /// Pearson's citation for the stimulus, lifted out of questionText. Kept so
    /// the provenance is not destroyed, but never emitted into questions.json,
    /// so it stays out of the card and out of the search index.
    var sourceAttribution: String?
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
    var qualification: String
    /// "a-level" or "as-level". Drives the output directory as well as the
    /// record, because both qualifications have a Paper 1 in the same series and
    /// the filenames would otherwise collide.
    var level: String
    var isAS: Bool { level == "as-level" }
}

// The 2024 covers abbreviate two of these ("Market and Business Behaviour",
// "Micro and Macro Economics"); the specification names are used instead.
let paperNames = [
    1: "Markets and Business Behaviour",
    2: "The National and Global Economy",
    3: "Microeconomics and Macroeconomics",
]

/// 8EC0 is a different qualification with different papers, not a subset of
/// 9EC0: two papers, both named differently from their A Level counterparts.
/// Taken from the covers. The 2016 covers set them in sentence case; the
/// specification's title case is used, matching how paperNames treats 9EC0.
let asPaperNames = [
    1: "Introduction to Markets and Market Failure",
    2: "The UK Economy – Performance and Policies",
]

let seriesNames = ["june": "June", "october": "October", "november": "November"]

func parseMeta(_ path: String) -> PaperMeta? {
    let file = (path as NSString).lastPathComponent
    let isAS = path.contains("/as-level/")
    guard
        let m = rx("paper-(\\d)-([a-z]+)-(\\d{4})-question-paper\\.pdf$").firstMatch(file),
        let paper = Int(m[1]!), let year = Int(m[3]!),
        let seriesName = seriesNames[m[2]!],
        let paperName = (isAS ? asPaperNames : paperNames)[paper]
    else { return nil }

    let seriesSlug = "\(m[2]!)-\(year)"
    let msPath = path.replacingOccurrences(
        of: "-question-paper.pdf", with: "-mark-scheme.pdf")
    let short = String(seriesName.lowercased().prefix(3))
    // "edexcel-as-" rather than "edexcel-a-as-": the ids are the visible anchor
    // on every card, and the two stems have to be told apart at a glance.
    let stem = isAS ? "edexcel-as" : "edexcel-a"
    return PaperMeta(
        paper: paper, paperName: paperName, year: year, series: seriesName,
        seriesSlug: seriesSlug, qpPath: path, msPath: msPath,
        idStem: "\(stem)-p\(paper)-\(year)-\(short)",
        qualification: isAS
            ? "AS Level Economics A (8EC0)" : "A Level Economics A (9EC0)",
        level: isAS ? "as-level" : "a-level")
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
/// Page number, and whether the question label was matched exactly or by the
/// looser fallback described below.
func markSchemePage(_ pages: [String], question: String, part: String?)
    -> (page: Int, exact: Bool)?
{
    // Tolerate "6(a)" and "6 (a)"; reject a longer number ("7" must not hit "70").
    let label: String
    if let part = part {
        label = "\(question)\\s*\\(\\s*\(part)\\s*\\)"
    } else {
        label = "\(question)(?![0-9])"
    }

    // The class holds a literal non-breaking space: ICU's \s does not match one.
    let byHeader = rx("Number[\\s\u{00A0}]*\(label)")
    // \s rather than [ \t] between the label and its allocation: where a
    // question's row spills onto a new page the allocation often wraps onto the
    // line below the label (Paper 3 June 2024, question 1(b)).
    let byBareLabel = rx("(?m)^[ \\t]*\(label)\\s+\(allocation)")

    for (i, page) in pages.enumerated() where i >= 2 {
        if byHeader.matches(page) || byBareLabel.matches(page) {
            return (i + 1, true)
        }
    }

    // Fallback for a scheme that drops the question number from a part heading.
    // Paper 3 November 2021 labels question 2(d) as just "(d)". The "Number"
    // anchor plus a bare part label is still a scheme heading and nothing else,
    // but the match is weaker, so it is reported rather than passed off as exact.
    if let part = part {
        let bare = rx("Number[\\s\u{00A0}]*\\(\\s*\(part)\\s*\\)")
        for (i, page) in pages.enumerated() where i >= 2 {
            if bare.matches(page) { return (i + 1, false) }
        }
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
        // Section C is where Pearson prints the citation, between the stimulus
        // and the instruction. Lift it out before the length checks below, so
        // confidence reflects the question rather than the URL padding it.
        let cited = stripAttribution(body)
        body = cited.text

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

        let hit = markSchemePage(msPages, question: String(n), part: nil)
        let ms = hit?.page
        if hit == nil {
            confidence = "low"
            notes.append("mark scheme page for Q\(n) could not be verified")
        }

        out.append(
            QuestionOut(
                id: "\(meta.idStem)-q\(n)", section: "C", questionNumber: String(n),
                parentQuestion: nil, choiceGroup: group, marks: 25, questionText: body,
                sourceAttribution: cited.attribution,
                contextPage: nil, qpPage: idx + 1, msPage: ms, msVerified: ms != nil,
                confidence: confidence, notes: notes))
    }

    if out.count != 2 {
        problems.append("expected 2 Section C questions, got \(out.count)")
    }
    return (out, problems)
}

// ------------------------------------------------------------- parted questions

/// Extract one lettered data-response question, parts (a) onwards, from a run of
/// pages. Used for three different things, because they are the same shape:
///
///   Papers 1 and 2, Section B  - Q6, parts (a) to (e), all compulsory.
///   Paper 3, Section A         - Q1, (a) to (c) compulsory, then (d) OR (e).
///   Paper 3, Section B         - Q2, same again.
///
/// Most papers print a consolidated list of all the parts on one page. Some do
/// not - Paper 2 June 2017 and June 2019 print each part above its own answer
/// space instead. Both layouts are handled by scanning every page in the range
/// for part openers and keeping the FIRST occurrence of each letter, which is
/// the consolidated list where one exists and the answer page where it does not.
///
/// `choiceLetters` names parts that are alternatives to each other. They are all
/// extracted - a student revising wants both - and share a choiceGroup so the UI
/// can say only one was sat.
///
/// `letters` is the full run of parts the question is expected to have. 9EC0
/// runs (a) to (e) everywhere; 8EC0 Section B runs (a) to (g), because AS keeps
/// its 20-mark essay choice inside Section B instead of splitting it out into a
/// Section C the way the A Level does.
func extractParts(
    pages: [String], from startIdx: Int, to endIdx: Int, question qnum: String,
    section: String, choiceLetters: [String], letters: [String] = ["a", "b", "c", "d", "e"],
    meta: PaperMeta, msPages: [String]
) -> ([QuestionOut], [String]) {
    var problems: [String] = []

    // The extract block a student must read. "Extract A" is normally its first
    // page; some Paper 3 sections label theirs C or D, so fall back to the first
    // page carrying any "Extract <letter>" and then to the section opener.
    let extractPage =
        (startIdx..<endIdx).first(where: { pages[$0].contains("Extract A") }).map { $0 + 1 }
        ?? (startIdx..<endIdx).first(where: {
            rx("Extract [A-H]\\b").matches(pages[$0])
        }).map { $0 + 1 }
        ?? (startIdx + 1)

    // "(a) <text> (5)" — text is non-greedy up to the tariff in its own brackets.
    // The class is built from `letters` so an AS paper's (f) and (g) are seen
    // and an A Level paper's are still ignored.
    let partRe = rx(
        "\\(([\(letters.first ?? "a")-\(letters.last ?? "e")])\\)\\s*(.+?)\\s*\\((\\d{1,2})\\)",
        [.dotMatchesLineSeparators])

    var seen: [String: QuestionOut] = [:]

    for i in startIdx..<endIdx {
        let cleaned = stripFurniture(pages[i])
        for m in partRe.allMatches(cleaned) {
            guard let letter = m[1], let rawBody = m[2], let marksStr = m[3],
                let marks = Int(marksStr), seen[letter] == nil
            else { continue }

            // Section B keeps its citations on the extract pages, which are not
            // extracted, so this finds nothing on 9EC0 today. Applied anyway:
            // it costs one pass and means a paper that does print one inline
            // cannot reintroduce the problem.
            let cited = stripAttribution(normalise(rawBody))
            let body = cited.text
            // A match spanning a page break can swallow the next part; reject
            // bodies that still contain another part opener or a stray tariff.
            if body.isEmpty || body.count < 15 { continue }
            if rx("\\([a-e]\\)").matches(body) { continue }

            var notes: [String] = []
            var confidence = "high"
            if body.count > 600 {
                confidence = "low"
                notes.append("extracted text is unusually long; may span two parts")
            }

            let label = "\(qnum)(\(letter))"
            let hit = markSchemePage(msPages, question: qnum, part: letter)
            let ms = hit?.page
            if hit == nil {
                confidence = "low"
                notes.append("mark scheme page for \(label) could not be verified")
            } else if hit!.exact == false {
                notes.append(
                    "mark scheme heading for \(label) omits the question number; "
                        + "matched on the bare part label")
            }

            let group =
                choiceLetters.contains(letter)
                ? "\(meta.idStem)-q\(qnum)-choice" : nil

            seen[letter] = QuestionOut(
                id: "\(meta.idStem)-q\(qnum)\(letter)", section: section,
                questionNumber: label, parentQuestion: qnum, choiceGroup: group,
                marks: marks, questionText: body, sourceAttribution: cited.attribution,
                contextPage: extractPage,
                qpPage: i + 1, msPage: ms, msVerified: ms != nil,
                confidence: confidence, notes: notes)
        }
    }

    let out = letters.compactMap { seen[$0] }
    if out.count != letters.count {
        let missing = letters.filter { seen[$0] == nil }
        problems.append(
            "Q\(qnum): missing part(s) \(missing.joined(separator: ", "))")
    }
    return (out, problems)
}

/// Papers 1 and 2: Section B is a single data-response question, always Q6.
func extractSectionB(pages: [String], meta: PaperMeta, msPages: [String])
    -> ([QuestionOut], [String])
{
    guard
        let startIdx = pages.firstIndex(where: {
            $0.contains("SECTION B") && $0.contains("before answering Question")
        })
    else {
        return ([], ["Section B page not found"])
    }

    guard let qm = rx("before answering Question\\s+(\\d+)").firstMatch(pages[startIdx]),
        let qnum = qm[1]
    else {
        return ([], ["Section B question number not found"])
    }

    // 9EC0 Section B ends where Section C begins. 8EC0 has no Section C - the
    // section runs to the end of the paper - and its last two parts are the
    // 20-mark either/or, which the A Level prints as Section C instead.
    let endIdx =
        meta.isAS
        ? pages.count
        : (pages.firstIndex(where: { $0.contains("SECTION C") }) ?? pages.count)

    return extractParts(
        pages: pages, from: startIdx, to: endIdx, question: qnum, section: "B",
        choiceLetters: meta.isAS ? ["f", "g"] : [],
        letters: meta.isAS
            ? ["a", "b", "c", "d", "e", "f", "g"] : ["a", "b", "c", "d", "e"],
        meta: meta, msPages: msPages)
}

// ------------------------------------------------------------------ paper 3

/// Paper 3 is two 50-mark case studies: Section A is Q1, Section B is Q2. Each
/// runs (a) to (c) compulsory then a choice of (d) or (e). Uniform across all
/// eight papers.
func extractPaper3(pages: [String], meta: PaperMeta, msPages: [String])
    -> ([QuestionOut], [String])
{
    var out: [QuestionOut] = []
    var problems: [String] = []

    // A section is located by its instruction line, not by a "SECTION x"
    // heading. Paper 3 June 2024 prints no "SECTION B" heading above its second
    // case study at all — the words appear only in the "TOTAL FOR SECTION B"
    // line on the last page — so keying off the heading loses half that paper.
    let opener = rx("before answering Question\\s+(\\d+)")
    var starts: [(page: Int, question: String)] = []
    for (i, page) in pages.enumerated() {
        guard let m = opener.firstMatch(page), let n = m[1] else { continue }
        if starts.contains(where: { $0.question == n }) { continue }
        starts.append((i, n))
    }

    if starts.isEmpty {
        return ([], ["Paper 3: no section openers found"])
    }
    if starts.count != 2 {
        problems.append(
            "Paper 3: expected 2 sections, found \(starts.count) "
                + "(questions \(starts.map { $0.question }.joined(separator: ", ")))")
    }

    for (idx, start) in starts.enumerated() {
        let end = idx + 1 < starts.count ? starts[idx + 1].page : pages.count
        // Section A carries Q1 and Section B carries Q2 in all eight papers, but
        // the label is derived from position rather than assumed from the number.
        let section = idx == 0 ? "A" : "B"
        let (qs, ps) = extractParts(
            pages: pages, from: start.page, to: end, question: start.question,
            section: section, choiceLetters: ["d", "e"], meta: meta, msPages: msPages)
        out += qs
        problems += ps
    }

    if out.count != 10 {
        problems.append("expected 10 Paper 3 questions, got \(out.count)")
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
    lines.append("  \"qualification\": \"\(jsonEscape(meta.qualification))\",")
    lines.append("  \"board\": \"edexcel\",")
    lines.append("  \"boardName\": \"Edexcel\",")
    lines.append("  \"level\": \"\(meta.level)\",")
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
        // Omitted entirely when there is no citation, so the 420 questions that
        // never had one keep the shape they already have on disk.
        if let attr = q.sourceAttribution {
            f.append("      \"sourceAttribution\": \"\(jsonEscape(attr))\"")
        }
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

// Two directories, because both qualifications have a Paper 1 in the same
// series and "p1-june-2017.json" would otherwise mean two different papers.
let outDirs = [
    "a-level": URL(fileURLWithPath: "past-paper-questions-data/edexcel-a"),
    "as-level": URL(fileURLWithPath: "past-paper-questions-data/edexcel-a-as"),
]
for dir in outDirs.values {
    try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
}

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

    var questions: [QuestionOut] = []
    var problems: [String] = []

    if meta.paper == 3 {
        // Paper 3 has no Section C and its sections mean something different,
        // which is why `section` is a free string on the record rather than an
        // enum shared with Papers 1 and 2.
        (questions, problems) = extractPaper3(
            pages: qpPages, meta: meta, msPages: msPages)
    } else if meta.isAS {
        // 8EC0 has no Section C at all. Its Section B carries the whole of the
        // paper bar Section A: Q6(a) to (g), 60 of the 80 marks.
        (questions, problems) = extractSectionB(
            pages: qpPages, meta: meta, msPages: msPages)
    } else {
        let (b, bProblems) = extractSectionB(pages: qpPages, meta: meta, msPages: msPages)
        let (c, cProblems) = extractSectionC(pages: qpPages, meta: meta, msPages: msPages)
        questions = b + c
        problems = bProblems + cProblems
    }

    let name = "p\(meta.paper)-\(meta.seriesSlug).json"
    let dest = outDirs[meta.level]!.appendingPathComponent(name)
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
